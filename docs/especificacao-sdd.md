# Especificação Técnica (SDD) — DOA FÁCIL

## 1. Problema

Doadores individuais frequentemente possuem itens em bom estado (móveis,
alimentos não perecíveis, roupas) que poderiam ajudar ONGs, mas não há um
canal simples para conectar quem doa a quem precisa. O processo hoje é
informal, disperso em grupos de WhatsApp ou redes sociais, o que gera
desperdício de itens e perda de tempo de ambos os lados.

## 2. Objetivo e evolução do projeto

Validar as regras centrais do domínio de doações — criação e confirmação —
de forma independente de persistência ou integrações externas. O critério de
sucesso desta entrega é um núcleo de domínio testável que implemente
corretamente as regras de negócio descritas abaixo. O repositório também
inclui uma interface web mínima, em memória e sem framework, para demonstrar
localmente a criação e a confirmação de uma doação; ela não faz parte do
núcleo de domínio.

Na Entrega 2, a especificação foi refinada a partir dos erros lógicos
registrados em [`ERROS.md`](ERROS.md). As mudanças estão na seção 8.

O objetivo da Entrega 3 é documentar e validar a versão final do DOA FÁCIL (As-Built), incluindo sua arquitetura implementada, regras de negócio, contratos, decisões arquiteturais, limitações conhecidas e evidências disponíveis de testes e cobertura.

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

- **RN01** — Uma doação só pode ser criada se o nome do doador for informado (não vazio após remoção de espaços).
- **RN02** — O e-mail do doador deve respeitar um formato mínimo válido (`texto@texto.texto`).
- **RN03** — A ONG de destino precisa estar com `ativa = True`.
- **RN04** — O valor da doação deve ser maior que zero.
- **RN05** — O e-mail é normalizado para letras minúsculas e sem espaços nas extremidades antes de ser persistido em memória.
- **RN06** — O valor monetário é convertido para `Decimal` com duas casas decimais.
- **RN07** — Toda doação nasce no estado `PENDENTE`.
- **RN08** — Uma doação `PENDENTE` pode ser confirmada, mudando o estado para `CONFIRMADA`.
- **RN09** — Uma doação `CONFIRMADA` não pode ser confirmada novamente; a tentativa deve levantar um erro de domínio (`DomainError`).
- **RN10** — A ONG de destino deve ter nome informado (não vazio após remoção de espaços).
- **RN11** — O valor deve ser um número finito. `NaN`, `Infinity` e textos não numéricos são rejeitados com `DomainError`.

## 6. Contratos de entrada e saída

### 6.1 Contrato: `criar_doacao(nome_doador, email_doador, ong, valor)`

**Objetivo:** criar uma doação com estado inicial `PENDENTE`, após validar os dados de entrada.

**Parâmetros:**
- `nome_doador`: nome do doador. Espaços no início e no final são removidos; o campo não pode ficar vazio.
- `email_doador`: e-mail do doador. Espaços externos são removidos, o endereço é convertido para letras minúsculas e deve corresponder ao padrão de validação definido no código.
- `ong`: deve ser uma instância de `ONG`, estar ativa e possuir nome não vazio.
- `valor`: valor conversível para `Decimal`, finito e maior que zero. O valor é arredondado para duas casas decimais por `quantize(Decimal("0.01"))`.

**Retorno:** uma instância de `Doacao`, com os dados validados, o valor em `Decimal` e o estado inicial `EstadoDoacao.PENDENTE`.

**Erros:** lança `DomainError` quando o nome do doador está vazio, o e-mail é inválido, a ONG não é válida, está inativa ou não possui nome, ou o valor não é válido ou é menor ou igual a zero. Erros de conversão do valor tratados pelo código são convertidos em `DomainError`.

**Observação:** a conversão e o arredondamento monetário seguem o comportamento de `Decimal` e `quantize` do Python. O código não define explicitamente um modo de arredondamento, portanto utiliza o padrão do contexto decimal.

### 6.2 Contrato: `confirmar_doacao(doacao) -> Doacao`

**Entrada:** instância de `Doacao`.

**Saída (sucesso):** a mesma instância, com `estado = CONFIRMADA`, desde que ainda não esteja confirmada.

**Saída (erro):** lança `DomainError` se a doação já estiver no estado `CONFIRMADA`.

**Observação:** a função altera o estado da própria instância recebida e retorna essa mesma instância. O código não realiza persistência em banco de dados.

## 7. Decomposição em unidades

| Unidade | Responsabilidade | Isolamento |
|---|---|---|
| `ONG` (entidade) | Representar a organização receptora | Sem dependências externas |
| `Doacao` (entidade) | Representar o registro de uma doação | Sem dependências externas |
| `criar_doacao` (caso de uso) | Validar e instanciar uma nova doação | Depende apenas das entidades acima |
| `confirmar_doacao` (caso de uso) | Validar e aplicar a transição de estado | Depende apenas da entidade `Doacao` |

Essa decomposição permite que, em sprints futuras, cada unidade seja conectada a uma camada de persistência, API HTTP ou fila de eventos sem alterar as regras de negócio já validadas.

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

### 9.1 Rotas e contratos da interface web

A interface web é implementada em `app/web.py`, utilizando `HTTPServer` e `BaseHTTPRequestHandler`, da biblioteca padrão do Python. As operações de negócio são delegadas às funções do módulo `app/domain.py`.

| Método HTTP | Rota | Comportamento |
|---|---|---|
| GET | `/` | Exibe a página inicial com atalhos para criar e consultar doações. |
| GET | `/criar` | Exibe o formulário de criação de doação. |
| POST | `/criar` | Recebe os dados do formulário, chama `criar_doacao_por_formulario` e, se a operação for bem-sucedida, redireciona para `/doacoes` com status HTTP 303. Se ocorrer um `DomainError`, exibe a mensagem de erro e retorna HTTP 400. |
| GET | `/doacoes` | Lista as doações mantidas em memória e permite confirmar aquelas que ainda estão pendentes. |
| POST | `/confirmar/{indice}` | Localiza a doação pelo índice da lista e chama `confirmar_doacao`. Em caso de sucesso, redireciona para `/doacoes` com status HTTP 303. Se houver um erro de domínio, retorna HTTP 400; índices inválidos ou inexistentes resultam em HTTP 404. |

As funções de apoio `criar_doacao_por_formulario`, `renderizar_landing`, `renderizar_formulario`, `renderizar_doacoes` e `renderizar_pagina` organizam o processamento dos dados e a apresentação das páginas.

**Contrato de criação:** a rota `POST /criar` recebe nome do doador, e-mail, nome da ONG e valor da doação. Os dados são encaminhados à função `criar_doacao`, que aplica as validações do domínio. Uma operação válida adiciona a doação à lista em memória; uma operação inválida que gere `DomainError` retorna uma mensagem de erro.

**Contrato de confirmação:** a rota `POST /confirmar/{indice}` recebe o índice da doação na lista em memória e chama `confirmar_doacao`. A regra de negócio permite confirmar uma doação pendente e rejeita uma segunda confirmação por meio de `DomainError`.

**Persistência e limitações:** a lista de doações é mantida em memória na classe `DoaFacilHandler`. Portanto, os registros não constituem armazenamento persistente e são perdidos quando o processo é encerrado. A confirmação utiliza um índice da lista, adequado à demonstração atual, mas sem garantia de identificação persistente do registro. Rotas não reconhecidas retornam HTTP 404.

## 10. Decisões arquiteturais

As decisões arquiteturais do DOA FÁCIL estão registradas nos documentos ADR (*Architecture Decision Records*) armazenados na pasta `adr/`. Esses registros descrevem as escolhas realizadas pela equipe, suas justificativas, alternativas consideradas e limitações aceitas.

- **ADR-001 — Núcleo de domínio Python independente para o MVP:** define o núcleo de negócio em Python puro, independente de frameworks web, ORMs e serviços de pagamento.
- **ADR-002 — Interface web mínima sem framework, dados em memória:** estabelece uma interface demonstrativa com a biblioteca padrão do Python, sem framework web e sem persistência em banco de dados.
- **ADR-003 — Dinheiro com `Decimal`, duas casas e valor finito:** define a representação dos valores monetários com `Decimal`, validação de números finitos e arredondamento para duas casas decimais.
- **ADR-004 — Estado do servidor em atributo de classe:** estabelece o armazenamento temporário da lista de doações no atributo de classe `DoaFacilHandler.doacoes`, compartilhado durante a execução do processo.
- **ADR-005 — Critério de cobertura dos testes automatizados:** estabelece a meta de 100% de cobertura para `app/domain.py` e o acompanhamento e a análise da cobertura de `app/web.py`, sem exigir 100% nesse módulo.

Essas decisões orientam a implementação atual e também registram limitações conhecidas, como ausência de persistência, autenticação e processamento real de pagamentos. Os ADRs devem ser consultados quando houver alterações arquiteturais ou ampliação do escopo do projeto.

## 11. Diferenças e refinamentos em relação à Entrega 2

Em relação à Entrega 2, o DOA FÁCIL passou por refinamentos nas regras de negócio, na interface web, nos testes automatizados e na documentação técnica.

As principais alterações foram:

- **Validação dos dados:** foram reforçadas as verificações dos dados do doador, do nome da ONG e do valor da doação.
- **Tratamento de valores monetários:** foram incluídas validações para rejeitar valores não numéricos e valores especiais, como `NaN` e `Infinity`, evitando exceções fora do contrato previsto.
- **Confirmação de doações:** foi reforçada a regra que impede confirmar novamente uma doação que já esteja confirmada.
- **Interface web:** foram documentadas as rotas para exibir a página inicial, criar doações, consultar os registros e confirmar doações.
- **Testes e cobertura:** o critério de cobertura foi formalizado no ADR-005, mantendo a meta de 100% para `app/domain.py` e o acompanhamento da cobertura de `app/web.py`.
- **Documentação e rastreabilidade:** as regras, os erros identificados e as decisões técnicas foram registrados na especificação, em [`ERROS.md`](ERROS.md) e nos ADRs.

Esses refinamentos buscam manter a implementação alinhada aos requisitos definidos e facilitar a manutenção do projeto. Os registros históricos de testes e correções devem ser interpretados conforme a etapa em que foram produzidos, sem serem confundidos com os resultados da versão atual.

Os resultados atuais de testes e cobertura são apresentados na seção de limitações deste documento e no README, com indicação de que correspondem à execução local.

## 12. Limitações conhecidas

- As doações são armazenadas em memória e são perdidas quando o servidor é reiniciado.
- O projeto não implementa autenticação de usuários nem persistência em banco de dados.
- O sistema não realiza transações financeiras nem processa pagamentos reais.
- A interface web tem finalidade demonstrativa e possui tratamento de erros limitado ao escopo da entrega.
- A cobertura de testes não garante, isoladamente, a ausência de defeitos.
- Os resultados de cobertura devem ser atualizados após mudanças no código ou nos testes.

Na execução local registrada, foram aprovados 20 testes, com 100% de cobertura em `app/domain.py`, 67% em `app/web.py` e 78% de cobertura total. Esses resultados correspondem à execução local e não comprovam a execução dos testes em Docker. Os números devem ser atualizados caso uma nova execução produza resultados diferentes.
