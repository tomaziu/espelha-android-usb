# Como Contribuir

Obrigado por querer melhorar o Espelha Android USB.

## Antes de começar

- Procure issues e pull requests existentes para evitar trabalho duplicado.
- Mantenha a mudança pequena e fácil de revisar.
- Atualize a documentação quando mudar o comportamento do app.
- Rode os testes antes de enviar.

## Ambiente local

1. Faça um fork ou clone do repositório.
2. Tenha Python 3 instalado no Windows.
3. Abra uma branch para sua mudança.
4. Rode:

```bash
python -m py_compile phone_mirror.py
python -m unittest discover -s tests -v
```

No Windows, você também pode usar:

```bat
run_tests.bat
```

## Pull requests

Ao abrir um pull request, descreva:

- qual problema foi resolvido;
- como a solução funciona;
- como você testou;
- qualquer limitação conhecida.

Se a mudança afetar a interface, prints ou logs ajudam bastante.
