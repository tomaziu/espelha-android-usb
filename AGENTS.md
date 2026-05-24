# Instruções para Agentes de IA

Este repositório contém um aplicativo Windows em Python/Tkinter que facilita o uso do `scrcpy` para espelhar e controlar celulares Android.

## Caminhos importantes

- `phone_mirror.py`: código principal do app.
- `tests/`: testes unitários.
- `README.md`: documentação para usuários.
- `.github/workflows/ci.yml`: validação no GitHub Actions.

## Fluxo de desenvolvimento

- Preserve o comportamento USB existente ao adicionar recursos.
- Evite dependências externas desnecessárias.
- Não versione `tools/` ou `downloads/`; elas guardam arquivos baixados automaticamente.
- Rode `python -m py_compile phone_mirror.py`.
- Rode `python -m unittest discover -s tests -v`.
- Atualize o README quando mudar opções da interface ou fluxo de uso.

## Observações

Este projeto não é oficial do `scrcpy`; ele é uma interface auxiliar construída por cima de `scrcpy` e `adb`.
