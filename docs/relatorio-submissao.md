# DOA FÁCIL
## Entrega 1 — Ambiente, Especificação Técnica e Test Harness
### Bootcamp III — Desenvolvimento Iterativo, Colaboração com IA e Validação Automatizada

---

## 1. Identificação da equipe

| Integrante | RA |
|---|---|
| Victor Hugo Américo dos Santos Garajau | 22503417 |
| Nelson Ribeiro Felix | 22452653 |
| Júlia Barrozo Rodrigues Pereira | 22452137

## 2. Link do repositório

https://github.com/juliabrpereira/doa-facil


## 3. Resumo do projeto

O **DOA FÁCIL** é um gerenciador de doações que intermedeia doadores
individuais e Organizações Não Governamentais (ONGs), com o objetivo de
reduzir o desperdício de itens doáveis e simplificar o processo de doação e
retirada.

Nesta primeira entrega, o escopo foi deliberadamente limitado a um **MVP
técnico**: o núcleo de domínio, responsável por validar a criação e a
confirmação de doações. Não há interface, persistência em banco de dados,
autenticação ou integração de pagamento — a "confirmação" de uma doação é
apenas uma mudança de estado validada por regras de negócio, sem
movimentação financeira real.

## 4. Ambiente de desenvolvimento

- **Linguagem/versão:** Python 3.11+
- **Framework de testes:** pytest
- **Padronização de ambiente:** Dockerfile, executando `pytest -q` automaticamente
- **Integração contínua:** workflow do GitHub Actions (`.github/workflows/tests.yml`), disparado em push e Pull Request para `main` e `develop`

### Comandos para execução local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

### Comandos para execução padronizada via Docker

```bash
docker build -t doa-facil .
docker run --rm doa-facil
```

## 5. Agente de IA utilizado

O repositório inclui o arquivo `.cursorrules`, compatível com Cursor, Claude
Code e Codex CLI, contendo:

- o contexto funcional do sistema (o que é o DOA FÁCIL e o que está fora de
  escopo nesta entrega);
- a exigência de leitura prévia da especificação SDD antes de qualquer
  alteração;
- a regra de manter o núcleo de domínio independente de frameworks web,
  bancos de dados e SDKs de pagamento;
- a obrigatoriedade de usar `Decimal` para valores monetários;
- a exigência de testes automatizados para toda alteração de comportamento;
- a obrigatoriedade de revisão humana antes de qualquer commit ou merge
  proposto pelo agente;
- a exigência de documentar, em cada Pull Request, qual tarefa foi apoiada
  pelo agente, quais arquivos foram alterados, quais decisões foram
  revisadas pela equipe e qual foi o resultado do harness de testes.

## 6. Especificação técnica (SDD)

A especificação completa está em `docs/especificacao-sdd.md` e cobre:

- o problema e o objetivo da sprint;
- requisitos funcionais (RF01–RF05) e não funcionais (RNF01–RNF04);
- regras de negócio (RN01–RN09);
- contratos de entrada e saída de `criar_doacao` e `confirmar_doacao`;
- decomposição do domínio em unidades isoladas e testáveis;
- histórico de refinamentos realizados durante a escrita dos testes de
  borda (ex.: normalização de e-mail e uso obrigatório de `Decimal`).

A decisão de manter o MVP como um núcleo de domínio Python independente,
sem interface nem persistência, está registrada em `adr/ADR-001.md`.

## 7. Test harness e evidências de execução

A suíte de testes (`tests/test_domain.py`) cobre o caminho feliz e os
seguintes casos de borda:

| Cenário validado | Resultado esperado |
|---|---|
| Criação de doação válida | Doação `PENDENTE` criada com dados normalizados |
| Valor inteiro convertido para moeda | Valor armazenado como `Decimal` com duas casas |
| Valor igual a zero ou negativo | Operação rejeitada (`DomainError`) |
| ONG inativa | Operação rejeitada (`DomainError`) |
| Nome vazio ou e-mail inválido | Operação rejeitada (`DomainError`) |
| Confirmação de doação pendente | Estado alterado para `CONFIRMADA` |
| Confirmação duplicada | Operação rejeitada (`DomainError`) |

### Log da execução local (`pytest -q`)

```text
.......                                                                  [100%]
7 passed in 0.02s
```


## 8. Governança do repositório

- Branch `main` protegida — apenas merges via Pull Request aprovado.
- Branch `develop` para integração contínua das features.
- Branches `feature/<tarefa>` para desenvolvimento individual.
- Tarefas organizadas em Issues e em um GitHub Project.
- Pull Requests com revisão e aprovação de outro integrante antes do merge.


## 9. Decisões e limitações atuais

A versão atual não possui interface gráfica, API HTTP, banco de dados,
autenticação, notificações ou pagamento real. Essas limitações são
intencionais nesta entrega e estão documentadas como escopo futuro no
`Backlog do Produto - DoaFácil`.



