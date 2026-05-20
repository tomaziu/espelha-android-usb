from __future__ import annotations

import json
import os
import queue
import re
import shutil
import subprocess
import tempfile
import threading
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from tkinter import BooleanVar, StringVar, Text, Tk
from tkinter import ttk


APP_DIR = Path(__file__).resolve().parent
TOOLS_DIR = APP_DIR / "tools"
DOWNLOADS_DIR = APP_DIR / "downloads"
GITHUB_API = "https://api.github.com/repos/Genymobile/scrcpy/releases/latest"
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def run_command(args: list[str], timeout: int = 20, cwd: Path | None = None) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            timeout=timeout,
            creationflags=CREATE_NO_WINDOW,
        )
        return completed.returncode, completed.stdout.strip(), completed.stderr.strip()
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    except subprocess.TimeoutExpired:
        return 124, "", "Tempo limite excedido."


def newest(paths: list[Path]) -> Path | None:
    existing = [path for path in paths if path.exists()]
    if not existing:
        return None
    return max(existing, key=lambda path: path.stat().st_mtime)


def find_scrcpy() -> Path | None:
    exe_name = "scrcpy.exe" if os.name == "nt" else "scrcpy"
    local_candidates = list(TOOLS_DIR.rglob(exe_name)) if TOOLS_DIR.exists() else []
    local = newest(local_candidates)
    if local:
        return local

    system = shutil.which("scrcpy")
    return Path(system) if system else None


def find_adb(scrcpy_path: Path | None = None) -> Path | None:
    exe_name = "adb.exe" if os.name == "nt" else "adb"
    candidates: list[Path] = []
    if scrcpy_path:
        candidates.append(scrcpy_path.parent / exe_name)
    if TOOLS_DIR.exists():
        candidates.extend(TOOLS_DIR.rglob(exe_name))

    local = newest(candidates)
    if local:
        return local

    system = shutil.which("adb")
    return Path(system) if system else None


def parse_adb_devices(output: str) -> list[tuple[str, str]]:
    devices: list[tuple[str, str]] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("list of devices"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            devices.append((parts[0], parts[1]))
    return devices


def safe_extract(zip_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    destination_root = destination.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            name = info.filename.replace("\\", "/")
            parts = PurePosixPath(name).parts
            if name.startswith("/") or ".." in parts:
                raise RuntimeError(f"Arquivo inseguro no ZIP: {info.filename}")
            target = (destination / name).resolve()
            try:
                target.relative_to(destination_root)
            except ValueError as exc:
                raise RuntimeError(f"Caminho inseguro no ZIP: {info.filename}")
        archive.extractall(destination)


class MirrorApp:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title("Espelhador USB Android")
        self.root.minsize(760, 520)

        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.process: subprocess.Popen[str] | None = None
        self.busy = False

        self.status_var = StringVar(value="Pronto")
        self.max_size_var = StringVar(value="1080")
        self.bitrate_var = StringVar(value="8M")
        self.no_audio_var = BooleanVar(value=True)
        self.view_only_var = BooleanVar(value=False)
        self.game_mouse_var = BooleanVar(value=False)
        self.stay_awake_var = BooleanVar(value=True)
        self.fullscreen_var = BooleanVar(value=False)

        self.scrcpy_path = find_scrcpy()
        self.adb_path = find_adb(self.scrcpy_path)
        self.buttons: list[ttk.Button] = []

        self.build_ui()
        self.refresh_status()
        self.root.after(100, self.poll_events)

    def build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=18)
        outer.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=1)

        title = ttk.Label(outer, text="Espelhador USB Android", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, sticky="w")

        status = ttk.Label(outer, textvariable=self.status_var)
        status.grid(row=1, column=0, sticky="w", pady=(2, 16))

        actions = ttk.Frame(outer)
        actions.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        for column in range(5):
            actions.columnconfigure(column, weight=1)

        self.add_button(actions, "Verificar celular", self.check_phone_clicked, 0)
        self.add_button(actions, "Baixar/atualizar scrcpy", self.download_clicked, 1)
        self.add_button(actions, "Iniciar espelhamento", self.start_clicked, 2)
        self.add_button(actions, "Parar", self.stop_clicked, 3)
        self.add_button(actions, "Abrir pasta", self.open_folder_clicked, 4)

        body = ttk.Frame(outer)
        body.grid(row=3, column=0, sticky="nsew")
        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        options = ttk.LabelFrame(body, text="Opções", padding=12)
        options.grid(row=0, column=0, sticky="nsw", padx=(0, 14))

        ttk.Label(options, text="Tamanho máximo").grid(row=0, column=0, sticky="w")
        size = ttk.Combobox(
            options,
            textvariable=self.max_size_var,
            values=("720", "1080", "1440", "0"),
            state="readonly",
            width=14,
        )
        size.grid(row=1, column=0, sticky="ew", pady=(2, 10))

        ttk.Label(options, text="Bitrate").grid(row=2, column=0, sticky="w")
        bitrate = ttk.Combobox(
            options,
            textvariable=self.bitrate_var,
            values=("2M", "4M", "8M", "12M", "16M"),
            state="readonly",
            width=14,
        )
        bitrate.grid(row=3, column=0, sticky="ew", pady=(2, 10))

        ttk.Checkbutton(options, text="Sem áudio", variable=self.no_audio_var).grid(
            row=4, column=0, sticky="w", pady=3
        )
        ttk.Checkbutton(options, text="Somente ver", variable=self.view_only_var).grid(
            row=5, column=0, sticky="w", pady=3
        )
        ttk.Checkbutton(options, text="Modo jogo", variable=self.game_mouse_var).grid(
            row=6, column=0, sticky="w", pady=3
        )
        ttk.Checkbutton(options, text="Manter acordado", variable=self.stay_awake_var).grid(
            row=7, column=0, sticky="w", pady=3
        )
        ttk.Checkbutton(options, text="Tela cheia", variable=self.fullscreen_var).grid(
            row=8, column=0, sticky="w", pady=3
        )

        log_frame = ttk.LabelFrame(body, text="Registro", padding=8)
        log_frame.grid(row=0, column=1, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_box = Text(log_frame, height=18, wrap="word", font=("Consolas", 10))
        self.log_box.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_box.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_box.configure(yscrollcommand=scrollbar.set)

        self.log("Conecte um Android por USB, ative a depuração USB e autorize o PC no celular.")
        if self.scrcpy_path:
            self.log(f"scrcpy encontrado: {self.scrcpy_path}")
        else:
            self.log("scrcpy ainda não encontrado. Use o botão de download.")

    def add_button(self, parent: ttk.Frame, text: str, command, column: int) -> None:
        button = ttk.Button(parent, text=text, command=command)
        button.grid(row=0, column=column, sticky="ew", padx=4)
        self.buttons.append(button)

    def poll_events(self) -> None:
        while True:
            try:
                kind, payload = self.events.get_nowait()
            except queue.Empty:
                break

            if kind == "log":
                self.log_box.insert("end", str(payload) + "\n")
                self.log_box.see("end")
            elif kind == "status":
                self.status_var.set(str(payload))
            elif kind == "busy":
                self.busy = bool(payload)
                self.refresh_buttons()
        self.root.after(100, self.poll_events)

    def log(self, message: str) -> None:
        self.events.put(("log", message))

    def set_status(self, message: str) -> None:
        self.events.put(("status", message))

    def set_busy(self, value: bool) -> None:
        self.events.put(("busy", value))

    def refresh_buttons(self) -> None:
        for button in self.buttons:
            label = button.cget("text")
            if label == "Parar":
                button.configure(state="normal")
            else:
                button.configure(state="disabled" if self.busy else "normal")

    def refresh_status(self) -> None:
        scrcpy = "ok" if self.scrcpy_path else "não instalado"
        adb = "ok" if self.adb_path else "não encontrado"
        self.set_status(f"scrcpy: {scrcpy} | adb: {adb}")

    def run_background(self, target) -> None:
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def check_phone_clicked(self) -> None:
        self.run_background(self.check_phone)

    def download_clicked(self) -> None:
        self.run_background(self.download_scrcpy)

    def start_clicked(self) -> None:
        options = {
            "max_size": self.max_size_var.get(),
            "bitrate": self.bitrate_var.get(),
            "no_audio": self.no_audio_var.get(),
            "view_only": self.view_only_var.get(),
            "game_mouse": self.game_mouse_var.get(),
            "stay_awake": self.stay_awake_var.get(),
            "fullscreen": self.fullscreen_var.get(),
        }
        self.run_background(lambda: self.start_mirror(options))

    def stop_clicked(self) -> None:
        process = self.process
        if process and process.poll() is None:
            self.log("Encerrando espelhamento...")
            process.terminate()
            self.set_status("Encerrando")
        else:
            self.log("Nenhum espelhamento em execução.")

    def open_folder_clicked(self) -> None:
        if os.name == "nt":
            os.startfile(APP_DIR)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", str(APP_DIR)])

    def ensure_paths(self) -> tuple[Path | None, Path | None]:
        self.scrcpy_path = find_scrcpy()
        self.adb_path = find_adb(self.scrcpy_path)
        self.refresh_status()
        return self.scrcpy_path, self.adb_path

    def check_phone(self) -> list[tuple[str, str]]:
        self.set_busy(True)
        try:
            scrcpy_path, adb_path = self.ensure_paths()
            if not adb_path:
                if not scrcpy_path:
                    self.log("ADB não encontrado. Baixe o scrcpy primeiro.")
                else:
                    self.log("ADB não encontrado ao lado do scrcpy.")
                return []

            self.log("Verificando dispositivos ADB...")
            code, stdout, stderr = run_command([str(adb_path), "devices"], timeout=25)
            if code != 0:
                self.log(stderr or stdout or "Falha ao executar adb devices.")
                return []

            devices = parse_adb_devices(stdout)
            if not devices:
                self.log("Nenhum celular autorizado apareceu no ADB.")
                self.log("No Android: Opções do desenvolvedor > Depuração USB > permitir este PC.")
                return []

            for serial, state in devices:
                if state == "device":
                    model = self.get_device_model(adb_path, serial)
                    suffix = f" ({model})" if model else ""
                    self.log(f"Celular pronto: {serial}{suffix}")
                elif state == "unauthorized":
                    self.log(f"{serial}: pendente de autorização no celular.")
                elif state == "offline":
                    self.log(f"{serial}: offline. Reconecte o cabo USB.")
                else:
                    self.log(f"{serial}: estado {state}.")

            return devices
        finally:
            self.set_busy(False)

    def get_device_model(self, adb_path: Path, serial: str) -> str:
        code, stdout, _ = run_command(
            [str(adb_path), "-s", serial, "shell", "getprop", "ro.product.model"],
            timeout=8,
        )
        if code != 0:
            return ""
        return stdout.strip()

    def download_scrcpy(self) -> None:
        self.set_busy(True)
        try:
            TOOLS_DIR.mkdir(parents=True, exist_ok=True)
            DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
            self.log("Consultando a versão mais recente do scrcpy...")

            request = urllib.request.Request(
                GITHUB_API,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "espelhador-usb-android",
                },
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                release = json.loads(response.read().decode("utf-8"))

            asset = self.pick_windows_asset(release)
            if not asset:
                self.log("Não encontrei um ZIP Windows x64 na última versão do scrcpy.")
                return

            tag = release.get("tag_name", "latest")
            name = asset["name"]
            url = asset["browser_download_url"]
            version = re.sub(r"[^A-Za-z0-9_.-]", "_", tag)
            zip_path = DOWNLOADS_DIR / name
            target_dir = TOOLS_DIR / f"scrcpy-{version}"

            if target_dir.exists() and list(target_dir.rglob("scrcpy.exe")):
                self.log(f"scrcpy {tag} já está baixado.")
            else:
                self.log(f"Baixando {name}...")
                self.download_file(url, zip_path)
                self.log(f"Extraindo para {target_dir}...")
                safe_extract(zip_path, target_dir)

            self.scrcpy_path = find_scrcpy()
            self.adb_path = find_adb(self.scrcpy_path)
            if self.scrcpy_path:
                self.log(f"Pronto: {self.scrcpy_path}")
            else:
                self.log("Download concluído, mas scrcpy.exe não foi localizado.")
            self.refresh_status()
        except Exception as exc:
            self.log(f"Falha no download: {exc}")
        finally:
            self.set_busy(False)

    def pick_windows_asset(self, release: dict) -> dict | None:
        best: tuple[int, dict] | None = None
        for asset in release.get("assets", []):
            name = str(asset.get("name", "")).lower()
            score = 0
            if name.endswith(".zip"):
                score += 10
            if "win64" in name:
                score += 30
            if "x64" in name:
                score += 20
            if "windows" in name:
                score += 5
            if "source" in name or "server" in name:
                score -= 50
            if score <= 10:
                continue
            if best is None or score > best[0]:
                best = (score, asset)
        return best[1] if best else None

    def download_file(self, url: str, destination: Path) -> None:
        request = urllib.request.Request(url, headers={"User-Agent": "espelhador-usb-android"})
        with urllib.request.urlopen(request, timeout=60) as response:
            total = int(response.headers.get("Content-Length", "0") or 0)
            temp_fd, temp_name = tempfile.mkstemp(prefix="scrcpy-", suffix=".zip")
            downloaded = 0
            last_percent = -1
            with os.fdopen(temp_fd, "wb") as output:
                while True:
                    chunk = response.read(1024 * 256)
                    if not chunk:
                        break
                    output.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        percent = int(downloaded * 100 / total)
                        if percent >= last_percent + 10:
                            last_percent = percent
                            self.log(f"Download: {percent}%")
            shutil.move(temp_name, destination)

    def start_mirror(self, options: dict[str, object]) -> None:
        self.set_busy(True)
        try:
            if self.process and self.process.poll() is None:
                self.log("O espelhamento já está aberto.")
                return

            scrcpy_path, adb_path = self.ensure_paths()
            if not scrcpy_path:
                self.log("scrcpy não encontrado. Use o botão de download primeiro.")
                return

            if adb_path:
                devices = self.check_devices_without_busy(adb_path)
                ready = [serial for serial, state in devices if state == "device"]
                if not ready:
                    self.log("Não há celular autorizado para iniciar o espelhamento.")
                    return

            args = [str(scrcpy_path), "--window-title", "Celular via USB"]

            max_size = str(options["max_size"])
            if max_size and max_size != "0":
                args.extend(["--max-size", max_size])

            bitrate = str(options["bitrate"])
            if bitrate:
                args.extend(["--video-bit-rate", bitrate])

            if options["no_audio"]:
                args.append("--no-audio")
            if options["view_only"]:
                args.append("--no-control")
            elif options["game_mouse"]:
                args.extend(["--mouse=uhid", "--keyboard=uhid"])

            if options["stay_awake"]:
                args.append("--stay-awake")
            if options["fullscreen"]:
                args.append("--fullscreen")

            if options["view_only"] and options["game_mouse"]:
                self.log("Modo jogo ignorado porque 'Somente ver' está ligado.")
            elif options["game_mouse"]:
                self.log("Modo jogo ligado: mouse/teclado serão enviados como dispositivos físicos.")
                self.log("Se o cursor ficar preso na janela, pressione Alt ou a tecla Windows para soltar.")

            self.log("Iniciando scrcpy...")
            process = subprocess.Popen(
                args,
                cwd=str(scrcpy_path.parent),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=CREATE_NO_WINDOW,
            )
            self.process = process
            self.set_status("Espelhando")
            threading.Thread(target=self.watch_scrcpy, args=(process,), daemon=True).start()
        except Exception as exc:
            self.log(f"Falha ao iniciar: {exc}")
        finally:
            self.set_busy(False)

    def check_devices_without_busy(self, adb_path: Path) -> list[tuple[str, str]]:
        self.log("Confirmando celular no USB...")
        code, stdout, stderr = run_command([str(adb_path), "devices"], timeout=25)
        if code != 0:
            self.log(stderr or stdout or "Falha ao executar adb devices.")
            return []
        devices = parse_adb_devices(stdout)
        for serial, state in devices:
            self.log(f"{serial}: {state}")
        return devices

    def watch_scrcpy(self, process: subprocess.Popen[str]) -> None:
        if process.stdout:
            for line in process.stdout:
                line = line.strip()
                if line:
                    self.log(line)

        code = process.wait()
        if self.process is process:
            self.process = None
            self.set_status(f"scrcpy encerrado ({code})")
            self.refresh_status()


def main() -> int:
    root = Tk()
    try:
        root.call("tk", "scaling", 1.15)
    except Exception:
        pass
    MirrorApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
