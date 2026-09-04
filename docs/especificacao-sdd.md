# Especificação Técnica (SDD) — DOA FÁCIL

## 1. Problema

Doadores individuais frequentemente possuem itens em bom estado (móveis,
alimentos não perecíveis, roupas) que poderiam ajudar ONGs, mas não há um
canal simples para conectar quem doa a quem precisa. O processo hoje é
informal, disperso em grupos de WhatsApp ou redes sociais, o que gera
desperdício de itens e perda de tempo de ambos os lados.

## 2. Objetivo da sprint (Entrega 1)

Validar as regras centrais do domínio de doações — criação e confirmação —
antes de investir em interface, persistência ou integrações externas. O
critério de sucesso desta entrega é um núcleo de domínio testável que
implemente corretamente as regras de negócio descritas abaixo.

## 3. Requisitos Funcionais (RF)

| ID | Descrição |
|---|---|
| RF01 | O sistema deve permitir criar uma doação vinculando doador e ONG. |
| RF02 | O sistema deve validar os dados do doador antes de criar a doação. |
| RF03 | O sistema deve impedir doações para ONGs inativas. |
| RF04 | O sistema deve permitir confirmar uma doação pendente. |
| RF05 | O sistema deve impedir a confirmação duplicada de uma doação. |

## 4. Requisitos Não Funcionais (RNF)

| ID | Descrição |
|---|---|
| RNF01 | O domínio não deve depender de banco de dados, web framework ou gateway de pagamento. |
| RNF02 | Valores monetários devem ser representados com `Decimal`, nunca `float`. |
| RNF03 | O núcleo de domínio deve ser executável e testável em menos de 1 segundo. |
| RNF04 | O código deve ser 100% coberto por testes automatizados nesta entrega. |

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

## 6. Contratos de entrada e saída

### 6.1 `criar_doacao(nome_doador, email_doador, ong, valor) -> Doacao`

**Entrada**
```
nome_doador: str   # obrigatório, não vazio
email_doador: str  # obrigatório, formato mínimo válido
ong: ONG            # deve estar ativa
valor: int | float | str | Decimal  # deve ser > 0
```

**Saída (sucesso)**: objeto `Doacao` com `estado = PENDENTE`, `email_doador`
normalizado e `valor` como `Decimal` com duas casas.

**Saída (erro)**: `DomainError` com mensagem descritiva, quando qualquer
regra de RN01 a RN04 for violada.

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

| Data | Alteração | Motivo |
|---|---|---|
| Sprint 1 | Definição inicial das regras RN01–RN09 | Escopo mínimo necessário para o MVP de domínio |
| Sprint 1 | Inclusão da normalização de e-mail (minúsculas, trim) | Evitar duplicidade de cadastro por variação de digitação, identificada ao escrever os testes de borda |
| Sprint 1 | Uso obrigatório de `Decimal` em vez de `float` para valores | Ponto flutuante binário pode gerar erros de arredondamento em valores monetários |
