import tempfile
import unittest
import zipfile
from pathlib import Path

import phone_mirror


class HelpersTest(unittest.TestCase):
    def test_parse_adb_devices(self):
        output = """List of devices attached
abc123 device
wifi:5555 unauthorized
offline-one offline
"""

        self.assertEqual(
            phone_mirror.parse_adb_devices(output),
            [
                ("abc123", "device"),
                ("wifi:5555", "unauthorized"),
                ("offline-one", "offline"),
            ],
        )

    def test_normalize_android_dir(self):
        cases = {
            "": "/sdcard/Download/",
            "Download": "/sdcard/Download/",
            "Pictures": "/sdcard/Pictures/",
            "sdcard/Movies": "/sdcard/Movies/",
            r"\sdcard\Music": "/sdcard/Music/",
            "/storage/emulated/0/DCIM": "/storage/emulated/0/DCIM/",
        }

        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(phone_mirror.normalize_android_dir(value), expected)

    def test_normalize_tcpip_target(self):
        cases = {
            "": "",
            "192.168.1.20": "192.168.1.20:5555",
            "192.168.1.20:5556": "192.168.1.20:5556",
            "tcp://192.168.1.20": "192.168.1.20:5555",
            "+192.168.1.20": "+192.168.1.20:5555",
            " 192.168.1.20 :5555 ": "192.168.1.20:5555",
        }

        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(phone_mirror.normalize_tcpip_target(value), expected)

    def test_extract_ipv4_from_route(self):
        route = "192.168.1.0/24 dev wlan0 proto kernel scope link src 192.168.1.77"
        self.assertEqual(phone_mirror.extract_ipv4_from_route(route), "192.168.1.77")
        self.assertEqual(phone_mirror.extract_ipv4_from_route("no ip here"), "")


class SafeExtractTest(unittest.TestCase):
    def test_safe_extract_allows_normal_zip_entries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            archive_path = base / "safe.zip"
            destination = base / "out"

            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("folder/file.txt", "ok")

            phone_mirror.safe_extract(archive_path, destination)

            self.assertEqual((destination / "folder" / "file.txt").read_text(), "ok")

    def test_safe_extract_rejects_parent_traversal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            archive_path = base / "unsafe.zip"

            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../evil.txt", "nope")

            with self.assertRaises(RuntimeError):
                phone_mirror.safe_extract(archive_path, base / "out")


if __name__ == "__main__":
    unittest.main()
