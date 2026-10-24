# Especificação Técnica (SDD) — DOA FÁCIL

## 1. Problema

Doadores individuais frequentemente possuem itens em bom estado (móveis,
alimentos não perecíveis, roupas) que poderiam ajudar ONGs, mas não há um
canal simples para conectar quem doa a quem precisa. O processo hoje é
informal, disperso em grupos de WhatsApp ou redes sociais, o que gera
desperdício de itens e perda de tempo de ambos os lados.

## 2. Objetivo da sprint (Entrega 1) e refinamento (Entrega 2)

Validar as regras centrais do domínio de doações — criação e confirmação —
de forma independente de persistência ou integrações externas. O critério de
sucesso desta entrega é um núcleo de domínio testável que implemente
corretamente as regras de negócio descritas abaixo. O repositório também
inclui uma interface web mínima, em memória e sem framework, para demonstrar
localmente a criação e a confirmação de uma doação; ela não faz parte do
núcleo de domínio.

Na Entrega 2, a especificação foi refinada a partir dos erros lógicos
registrados em [`docs/ERROS.md`](ERROS.md). As mudanças estão na seção 8.

## 3. Requisitos Funcionais (RF)

| ID | Descrição |
|---|---|
| RF01 | O sistema deve permitir criar uma doação vinculando doador e ONG. |
| RF02 | O sistema deve validar os dados do doador antes de criar a doação. |
| RF03 | O sistema deve impedir doações para ONGs inativas. |
| RF04 | O sistema deve permitir confirmar uma doação pendente. |
| RF05 | O sistema deve impedir a confirmação duplicada de uma doação. |
| RF06 | A interface web deve permitir criar uma doação por formulário e exibir o erro de domínio quando um dado for inválido. |
| RF07 | A interface web deve listar as doações em memória e permitir confirmar cada doação pendente. |

## 4. Requisitos Não Funcionais (RNF)

| ID | Descrição |
|---|---|
| RNF01 | O domínio não deve depender de banco de dados, web framework ou gateway de pagamento. |
| RNF02 | Valores monetários devem ser representados com `Decimal`, nunca `float`. |
| RNF03 | O núcleo de domínio deve ser executável e testável em menos de 1 segundo. |
| RNF04 | O núcleo de domínio (`app/domain.py`) deve ter 100% de cobertura por testes automatizados. A interface de demonstração (`app/web.py`) tem a cobertura medida e registrada, sem meta de 100%. |

## 5. Regras de negócio

- **RN01** — Uma doação só pode ser criada se o nome do doador for informado
  (não vazio após remoção de espaços).
- **RN02** — O e-mail do doador deve respeitar um formato mínimo válido
  (`texto@texto.texto`).
- **RN03** — A ONG de destino precisa estar com `ativa = True`.
- **RN04** — O valor da doação deve ser maior que zero.
- **RN05** — O e-mail é normalizado para letras minúsculas e sem espaços nas
  extremidades antes de ser persistido em memória.
- **RN06** — O valor monetário é convertido para `Decimal` com duas casas
  decimais.
- **RN07** — Toda doação nasce no estado `PENDENTE`.
- **RN08** — Uma doação `PENDENTE` pode ser confirmada, mudando o estado
  para `CONFIRMADA`.
- **RN09** — Uma doação `CONFIRMADA` não pode ser confirmada novamente; a
  tentativa deve levantar um erro de domínio (`DomainError`).
- **RN10** — A ONG de destino deve ter nome informado (não vazio após remoção
  de espaços).
- **RN11** — O valor deve ser um número finito. `NaN`, `Infinity` e textos não
  numéricos são rejeitados com `DomainError`.

## 6. Contratos de entrada e saída

### 6.1 `criar_doacao(nome_doador, email_doador, ong, valor) -> Doacao`

**Entrada**
```
nome_doador: str   # obrigatório, não vazio (RN01)
email_doador: str  # obrigatório, formato mínimo válido (RN02)
ong: ONG            # deve estar ativa (RN03) e ter nome não vazio (RN10)
valor: int | float | str | Decimal  # número finito (RN11) e > 0 (RN04)
```

**Saída (sucesso)**: objeto `Doacao` com `estado = PENDENTE`, `email_doador`
normalizado e `valor` como `Decimal` com duas casas.

**Saída (erro)**: `DomainError` com mensagem descritiva, quando qualquer
regra de RN01 a RN04, RN10 ou RN11 for violada, ou quando `ong` não for uma
instância de `ONG`. Para entradas dos tipos declarados acima, nenhuma outra
exceção escapa de `criar_doacao`.

### 6.2 `confirmar_doacao(doacao) -> Doacao`

**Entrada**: instância de `Doacao` no estado `PENDENTE`.

**Saída (sucesso)**: a mesma instância, agora com `estado = CONFIRMADA`.

**Saída (erro)**: `DomainError`, se a doação já estiver `CONFIRMADA`.

## 7. Decomposição em unidades

| Unidade | Responsabilidade | Isolamento |
|---|---|---|
| `ONG` (entidade) | Representar a organização receptora | Sem dependências externas |
| `Doacao` (entidade) | Representar o registro de uma doação | Sem dependências externas |
| `criar_doacao` (caso de uso) | Validar e instanciar uma nova doação | Depende apenas das entidades acima |
| `confirmar_doacao` (caso de uso) | Validar e aplicar a transição de estado | Depende apenas da entidade `Doacao` |

Essa decomposição permite que, em sprints futuras, cada unidade seja
conectada a uma camada de persistência, API HTTP ou fila de eventos sem
alterar as regras de negócio já validadas.

## 8. Histórico de refinamentos

| Sprint | Alteração | Motivo | Referência |
|---|---|---|---|
| Sprint 1 | Definição inicial das regras RN01–RN09 | Escopo mínimo necessário para o MVP de domínio | — |
| Sprint 1 | Inclusão da normalização de e-mail (minúsculas, trim) | Evitar duplicidade de cadastro por variação de digitação, identificada ao escrever os testes de borda | — |
| Sprint 1 | Uso obrigatório de `Decimal` em vez de `float` para valores | Ponto flutuante binário pode gerar erros de arredondamento em valores monetários | — |
| Sprint 2 | RN10 — ONG precisa ter nome informado | A SPEC só exigia `ativa = True`, e a implementação aceitava ONG com nome vazio (omissão da SPEC) | [Erro E-02](ERROS.md#e-02--ong-com-nome-vazio-era-aceita), PR #38 |
| Sprint 2 | RN11 — valor deve ser número finito (e reforço do contrato 6.1) | `NaN` escapava como `decimal.InvalidOperation` e derrubava a requisição web; a SPEC não definia "número válido" | [Erro E-01](ERROS.md#e-01--valor-nan-escapava-como-exceção-não-tratada), PR #38 |
| Sprint 2 | RF06 e RF07 — requisitos da interface web | A interface existia no código e nos testes, mas nenhum requisito a descrevia; os fluxos sem teste apareceram na medição de cobertura | Relacionado ao [Erro E-04](ERROS.md#e-04--cobertura-real-divergia-da-spec-rnf04), PR #38 |
| Sprint 2 | RNF04 — 100% de cobertura apenas para `app/domain.py` | A cobertura medida era 76% no total; a meta de 100% para todo o código não era verdadeira | [Erro E-04](ERROS.md#e-04--cobertura-real-divergia-da-spec-rnf04), PR #38 |

## 9. Arquitetura da versão implementada (As-Built)

A aplicação está organizada em duas partes principais. O módulo `app/domain.py` concentra as regras de negócio, incluindo validações, criação e confirmação de doações. O módulo `app/web.py` disponibiliza uma interface web simples para interação com essas funcionalidades.

Os testes automatizados estão organizados no diretório `tests/` e utilizam `pytest`. A ferramenta `pytest-cov` é utilizada para medir a cobertura do código. Os dados das doações permanecem em memória durante a execução do servidor, sem persistência em banco de dados.

## 10. Decisões arquiteturais

As decisões técnicas do projeto estão registradas nos documentos ADR localizados no diretório `adr/`.

O ADR-004 documenta a utilização de um atributo de classe para manter o estado das doações durante a execução do servidor. O ADR-005 registra o critério de cobertura dos testes automatizados: a meta de 100% aplica-se ao módulo `app/domain.py`, enquanto a cobertura de `app/web.py` deve ser medida e analisada.

## 11. Diferenças e refinamentos da implementação

Durante o refinamento do projeto, foram detalhadas regras de validação para os dados do doador, para a ONG e para o valor da doação. Também foram reforçados o tratamento de valores numéricos inválidos, a prevenção de confirmações duplicadas e os requisitos da interface web.

A cobertura de testes foi definida de acordo com o RNF04, que exige 100% de cobertura do módulo de domínio. A interface web também é avaliada, mas não possui a mesma meta obrigatória.

As alterações e os problemas identificados durante o desenvolvimento devem ser consultados em `docs/ERROS.md` e nos respectivos registros de decisões arquiteturais.

## 12. Limitações conhecidas

- As doações são armazenadas em memória e são perdidas quando o servidor é reiniciado.
- O projeto não implementa autenticação de usuários nem persistência em banco de dados.
- A interface web tem finalidade demonstrativa e possui tratamento de erros limitado ao escopo da entrega.
- A cobertura de testes não garante, isoladamente, a ausência de defeitos.
- Os resultados de cobertura devem ser atualizados após mudanças no código ou nos testes.

A execução local registrada apresentou 20 testes aprovados, com 100% de cobertura em `app/domain.py`, 67% em `app/web.py` e 78% de cobertura total. Esses resultados são da execução local e não comprovam a execução dos testes em Docker.
