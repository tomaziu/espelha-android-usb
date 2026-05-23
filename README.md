# Espelha Android USB

Um aplicativo simples para Windows que espelha a tela de um celular Android no PC via cabo USB e permite controlar o celular usando mouse e teclado.

O projeto usa [`scrcpy`](https://github.com/Genymobile/scrcpy) e `adb` por baixo dos panos. A interface ajuda a baixar o `scrcpy`, verificar se o celular foi reconhecido e iniciar o espelhamento sem precisar decorar comandos.

## O que ele faz

- Espelha a tela do Android no PC por cabo USB.
- Permite clicar, arrastar, rolar e digitar pelo computador.
- Baixa automaticamente a versão Windows x64 mais recente do `scrcpy`.
- Verifica se o celular aparece no `adb`.
- Tem modo normal, modo somente visualização e modo jogo.
- Inclui opção para tela cheia, bitrate e tamanho máximo do vídeo.
- Envia arquivos do PC para uma pasta escolhida no celular.

## Requisitos

- Windows.
- Python 3 instalado.
- Celular Android.
- Cabo USB que transfira dados, não apenas carregamento.
- Depuração USB ativada no Android.

> iPhone não é suportado para controle completo via USB com mouse usando `adb/scrcpy`.

## Como usar

1. Baixe ou clone este repositório.
2. Abra `Abrir-Espelhamento.bat`.
3. Clique em **Baixar/atualizar scrcpy**.
4. No Android, ative **Opções do desenvolvedor**.
5. Ative **Depuração USB**.
6. Conecte o celular no PC por USB.
7. Quando aparecer a mensagem no celular, toque em **Permitir depuração USB**.
8. Clique em **Verificar celular**.
9. Clique em **Iniciar espelhamento**.

Com **Somente ver** desligado, o controle por mouse e teclado fica ativo.

## Enviar arquivos para o celular

Você pode enviar arquivos do PC para o Android de duas formas:

- Arraste um arquivo para a janela do espelhamento. Por padrão, o `scrcpy` envia arquivos comuns para `/sdcard/Download/` e instala arquivos `.apk`.
- Use o botão **Enviar arquivo** no app para escolher o arquivo e também a pasta de destino no celular.

Para escolher a pasta pelo app:

1. No campo **Destino no celular**, escolha ou digite uma pasta.
2. Clique em **Enviar arquivo**.
3. Escolha o arquivo no Windows.
4. Aguarde a mensagem de envio concluído no registro.

Destinos úteis:

- `/sdcard/Download/`: Downloads.
- `/sdcard/Documents/`: Documentos.
- `/sdcard/Pictures/`: Imagens.
- `/sdcard/Movies/`: Vídeos.
- `/sdcard/Music/`: Músicas.
- `/sdcard/DCIM/`: Câmera/galeria.

## Modo jogo

Para jogos como Minecraft, marque **Modo jogo** antes de iniciar o espelhamento.

No modo normal, o `scrcpy` envia o mouse como toque na tela. Isso funciona bem para navegar no celular, mas em alguns jogos o mouse vira apenas um "dedo" e não controla a câmera direito.

O **Modo jogo** usa:

```bash
--mouse=uhid --keyboard=uhid
```

Assim, o Android recebe mouse e teclado como dispositivos físicos, o que ajuda jogos com suporte a mouse/teclado real.

Se o cursor ficar preso na janela do espelhamento, pressione `Alt` ou a tecla `Windows` para soltar/capturar novamente.

## Opções da interface

- **Tamanho máximo**: limita a resolução do espelhamento para melhorar desempenho.
- **Bitrate**: controla a qualidade do vídeo.
- **Sem áudio**: inicia o espelhamento sem áudio.
- **Somente ver**: mostra a tela, mas desativa o controle.
- **Modo jogo**: usa mouse e teclado como dispositivos físicos.
- **Manter acordado**: evita que o celular apague a tela durante o uso.
- **Tela cheia**: abre o espelhamento em tela cheia.
- **Destino no celular**: pasta usada pelo botão **Enviar arquivo**.

## Problemas comuns

### O celular não aparece

- Troque o cabo USB.
- Use uma porta USB diferente.
- Mude o modo USB do Android para transferência de arquivos.
- Confirme que a depuração USB está ativada.

### Aparece `unauthorized`

Desbloqueie o celular e aceite a janela **Permitir depuração USB**. Se não aparecer, desative e ative a depuração USB novamente.

### O mouse não controla a câmera em jogos

Marque **Modo jogo** e inicie o espelhamento novamente. O jogo também precisa ter suporte a mouse/teclado físico.

### O espelhamento está travando

Use tamanho máximo `720` e bitrate `4M` ou `2M`.

### O arquivo não aparece no celular

- Abra o app **Arquivos** ou **Downloads** no Android.
- Confirme que o destino está correto, por exemplo `/sdcard/Download/`.
- Se for imagem ou vídeo, pode demorar alguns segundos para aparecer na galeria.
- Verifique se o celular continua autorizado no ADB.

## Estrutura

- `phone_mirror.py`: aplicativo principal em Python/Tkinter.
- `Abrir-Espelhamento.bat`: atalho para abrir o app no Windows.
- `tools/`: pasta criada automaticamente para guardar o `scrcpy` baixado.
- `downloads/`: pasta criada automaticamente para guardar downloads temporários.

As pastas `tools/` e `downloads/` não entram no Git, porque podem conter arquivos grandes baixados automaticamente.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE`.
