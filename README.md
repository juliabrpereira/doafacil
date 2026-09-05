# DOA FÁCIL

Gerenciador de doações que intermedeia doadores individuais e ONGs,
reduzindo o desperdício de itens doáveis. Este repositório contém a
**Entrega 1 (Bootcamp III)**: ambiente de desenvolvimento, especificação
técnica orientada a SDD e um harness de testes automatizados para o núcleo
de domínio.

> Nesta primeira entrega o sistema **não movimenta dinheiro real**. A
> "confirmação" de uma doação é apenas uma mudança de estado validada pelo
> domínio, sem integração de pagamento, banco de dados ou interface.

## Estrutura do repositório

```
doa-facil/
├── app/
│   └── domain.py              # Entidades e regras de negócio
├── tests/
│   └── test_domain.py         # Testes unitários e casos de borda
├── docs/
│   └── especificacao-sdd.md   # Especificação técnica completa (SDD)
├── adr/
│   └── ADR-001.md             # Decisão arquitetural do MVP
├── .github/workflows/
│   └── tests.yml              # Pipeline de CI (roda pytest a cada push/PR)
├── .cursorrules                # Diretrizes para agentes de IA
├── Dockerfile                  # Ambiente reproduzível
├── requirements.txt             # Dependências do projeto
└── README.md
```

## Pré-requisitos

- Python 3.11 ou superior
- `pip` e `git`
- Docker (opcional, para execução padronizada)

## Como executar localmente

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
```

Resultado esperado:

```text
12 passed in 0.08s
```

## Interface de demonstração

Para abrir uma tela local com o botão **Confirmar doação**, execute:

```bash
python -m app.web
```

Depois, acesse `http://localhost:8000` no navegador. A tela exibe uma doação
de exemplo; ao clicar no botão, ela chama `confirmar_doacao` e altera o estado
para `CONFIRMADA`. Os dados permanecem somente em memória enquanto o servidor
está em execução.

## Como executar com Docker

```bash
docker build -t doa-facil .
docker run --rm doa-facil
```

## Agente de IA utilizado

O arquivo [`.cursorrules`](.cursorrules) documenta o contexto funcional do
projeto e as regras seguidas por agentes de auxílio de código (Cursor,
Claude Code ou Codex CLI) durante o desenvolvimento: leitura prévia da
especificação, independência do domínio em relação a frameworks, uso de
`Decimal` para valores monetários, exigência de testes para toda alteração e
obrigatoriedade de revisão humana antes do merge.

## Governança e fluxo de trabalho

- `main`: branch protegida, recebe apenas merges via Pull Request aprovado.
- `develop`: branch de integração das features.
- `feature/<tarefa>`: branches de desenvolvimento, uma por tarefa.

```bash
git checkout develop
git pull origin develop
git checkout -b feature/nome-da-tarefa
# alterações...
git add .
git commit -m "feat: descrição da alteração"
git push -u origin feature/nome-da-tarefa
```

Depois do push, abrir um Pull Request para `develop`, com revisão de outro
integrante antes do merge. Tarefas são organizadas em Issues e em um GitHub
Project.

## Decisões arquiteturais (ADRs)

- [ADR-001](adr/ADR-001.md) — Núcleo de domínio Python independente para o MVP.

## Especificação técnica

A especificação completa (problema, requisitos funcionais e não funcionais,
regras de negócio, contratos de entrada/saída e histórico de refinamentos)
está em [`docs/especificacao-sdd.md`](docs/especificacao-sdd.md).

## Limitações atuais (escopo futuro)

Interface gráfica, API HTTP, banco de dados, autenticação, notificações e
pagamento real ainda não foram implementados. Essas frentes estão descritas
no `Backlog do Produto - DoaFácil` e serão endereçadas em sprints futuras.
