# PhotoCensus

Projeto da disciplina de Python (UPE): um sistema em console que faz o "censo" dos objetos que aparecem em fotos. A detecção dos objetos é feita por um modelo de IA (YOLO) usado como **caixa-preta**: os grupos constroem toda a lógica em Python sobre os resultados que ela devolve.

As orientações completas (requisitos, datas, critérios e entregas) estão em [`docs/`](docs/).

## Estrutura do repositório

```
PhotoCensus-UPE/
├── README.md              <- este arquivo
├── .gitignore
├── docs/                  <- orientações do projeto (Módulos 1 e 2)
├── kit/                   <- kit do aluno: NÃO ALTERAR
│   ├── black_box.py       <- funções da caixa-preta
│   ├── test_kit.py        <- teste do kit
│   ├── example_module1.py
│   ├── example_module2.py
│   ├── install.py, install_windows.bat, install_linux_mac.sh
│   ├── README.md          <- documentação das funções (inglês)
│   ├── IMAGE_CREDITS.txt
│   ├── data/              <- resultados da IA e modelo
│   └── images/            <- 48 fotos em 6 pastas
└── groups/
    ├── group_00/          <- modelo: copiem para group_XX
    │   ├── main.py
    │   └── README.md
    ├── group_01/          <- código do Grupo 01
    ├── group_02/          <- código do Grupo 02
    └── ...
```

## Como começar

1. Façam o **fork** deste repositório (deixem o fork público) e clonem o fork.
2. Na raiz do repositório, rodem `python kit/test_kit.py`. Se aparecer "Kit OK.", está tudo pronto. Não é preciso instalar nada.
3. Copiem a pasta `groups/group_00/` para `groups/group_XX/` (XX = número do grupo na planilha) e editem o `README.md` dela.
4. Escrevam o projeto em `groups/group_XX/main.py`, mantendo as linhas iniciais que importam o `black_box`.
5. Para rodar, na raiz do repositório: `python groups/group_XX/main.py`.

## Regras do repositório

- Cada grupo altera **somente** a própria pasta `groups/group_XX/`. Não alterem `kit/`, `docs/`, este `README.md` nem as pastas de outros grupos.
- **Não copiem o kit** para a pasta do grupo: ele já vem com o fork e é encontrado pelas linhas iniciais do `main.py`.
- Fotos próprias (extra opcional) ficam em `groups/group_XX/my_photos/`, nunca em `kit/images/`.
- Entrega: um Pull Request para a branch `main` por módulo, com o título `[Module X] - Group XX - Name1, Name2 and Name3`, até as 18h do prazo.
- Recomendamos (não é obrigatório) escrever o código em inglês, como o kit.
