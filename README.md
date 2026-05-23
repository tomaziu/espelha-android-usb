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
- Espelha via USB ou via rede/Wi-Fi.

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

## Espelhar via rede/Wi-Fi

O celular e o PC precisam estar na mesma rede. Na maioria dos aparelhos, a primeira configuração ainda precisa do cabo USB.

### Modo automático

1. Conecte o celular por USB.
2. Confirme que a depuração USB está autorizada.
3. Marque **Via rede/Wi-Fi**.
4. Deixe **IP:porta** vazio.
5. Clique em **Iniciar espelhamento**.

O `scrcpy` vai tentar encontrar o IP do celular, ativar o ADB por rede e iniciar o espelhamento. Depois que a janela abrir, você pode desconectar o cabo.

### Preparar e conectar por IP

1. Conecte o celular por USB.
2. Marque **Via rede/Wi-Fi**.
3. Clique em **Preparar rede**.
4. O app tenta preencher o campo **IP:porta**, por exemplo `192.168.1.50:5555`.
5. Desconecte o cabo USB.
6. Clique em **Iniciar espelhamento**.

Se você já sabe o IP do celular, pode digitar direto em **IP:porta**. Se digitar só o IP, o app usa a porta `5555`.

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
- **Via rede/Wi-Fi**: inicia o espelhamento usando ADB por TCP/IP.
- **IP:porta**: endereço do celular na rede, como `192.168.1.50:5555`.

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

### A conexão via rede não funciona

- Confirme que PC e celular estão na mesma rede.
- Faça a primeira configuração com o cabo USB.
- Clique em **Preparar rede** novamente depois de reiniciar o celular.
- Verifique se o IP do celular mudou.
- Algumas redes públicas ou de convidados bloqueiam comunicação entre dispositivos.

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
