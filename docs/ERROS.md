# Registro de Erros Lógicos — DOA FÁCIL

> **Como usar este arquivo.** Cada entrada abaixo parte de um teste, commit ou PR **reais** do repositório
> (https://github.com/juliabpreira/doafacil). A parte "Detecção" já está ancorada em evidência.
> Os campos marcados **[CONFIRMAR]** devem ser verificados por quem implementou, olhando o histórico
> (`git log -p`, aba *Commits* do PR, aba *Files changed*). **Mantenha apenas o que de fato aconteceu;**
> apague ou reescreva qualquer entrada que a equipe não consiga comprovar.
> Dica: `git log --oneline --all -- tests/` e `git show <hash>` mostram em qual commit cada teste nasceu e se algo foi ajustado depois.

Critério de classificação (apostila, §4.2): *"um programador perfeito, lendo só a SPEC, teria escrito o código certo?"*
Se **sim** → erro de implementação (só aqui). Se **não** → defeito de especificação (aqui **e** no SPEC §8).

---

## E-01 · Confirmação duplicada de uma doação

- **Detecção:** harness — `tests/test_domain.py::test_confirmar_doacao_rejeita_confirmacao_duplicada`. Regra implementada na issue #3, commit `07bdcee` ("implementa regra de confirmação de doação"), branch `feature/regra-confirmacao-de-doacao`.
- **O quê:** uma doação já `CONFIRMADA` poderia ser confirmada novamente, repetindo a transição `PENDENTE → CONFIRMADA`.
- **Causa:** **[CONFIRMAR]** — a primeira versão de `confirmar_doacao` verificava o estado antes de alterar? Se o teste nasceu junto com a regra, registrar como "erro prevenido por teste de borda", não como falha ocorrida.
- **Correção:** **[CONFIRMAR]** commit/PR (candidatos: `07bdcee`, PR #15 ou #16).
- **Prevenção:** todo fluxo de estados tem teste para a transição inválida, não só para a válida.
- **Classificação:** **[CONFIRMAR]** implementação ou especificação (a SPEC dizia o que acontece na segunda confirmação?).

## E-02 · Valor da doação: zero e negativo

- **Detecção:** harness — `test_criar_doacao_rejeita_dados_invalidos` parametrizado, com casos `0` e `-5` ("maior que zero") visíveis na Figura 9. Regra de criação: issue #2, commit `21e2928`.
- **O quê:** a regra de criação precisa rejeitar valores `<= 0`. A fronteira é o ponto clássico de erro (`>` vs `>=`).
- **Causa:** **[CONFIRMAR]** houve operador de comparação errado (`>= 0` aceitaria zero)? Se sim, em qual commit?
- **Correção:** **[CONFIRMAR]** commit/PR (candidato: PR #13, de NelsonRibeiroFelix).
- **Prevenção:** um teste por fronteira numérica (0 e -5 já cobrem a borda e o caso interno).
- **Classificação:** **[CONFIRMAR]**.

## E-03 · Dados de entrada não normalizados (espaços em branco)

- **Detecção:** harness — `test_doacao_e_criada_com_dados_normalizados` e os casos parametrizados com nome em branco e e-mail com espaços/inválido (Figura 9).
- **O quê:** nome ou e-mail com espaços nas pontas, ou só espaços, precisam ser tratados (normalizados ou rejeitados).
- **Causa:** **[CONFIRMAR]** a validação aceitava string vazia/espaços antes do ajuste?
- **Correção:** **[CONFIRMAR]** commit/PR (candidatos: PR #13, #14).
- **Prevenção:** casos de borda de texto (vazio, só espaços, espaços nas pontas) obrigatórios para todo campo de entrada.
- **Classificação:** **[CONFIRMAR]**.

## E-04 · Doação aceita para ONG inativa

- **Detecção:** harness — `test_criar_doacao_rejeita_ong_inativa`; contrapartida `test_ong_pode_ser_criada_inativa`. Entidades: issue #1, commit `355d577`; regra: issue #2, commit `21e2928`.
- **O quê:** garantir que uma ONG inativa não receba doações (regra de negócio entre duas entidades).
- **Causa:** **[CONFIRMAR]** a regra de criação checava `ong.ativa`? Foi esquecida em alguma versão?
- **Correção:** **[CONFIRMAR]**.
- **Prevenção:** teste que verifica o **efeito** (a doação não é criada), não só a mensagem de erro.
- **Classificação:** **[CONFIRMAR]**.

## E-05 · Interface exibia botão de confirmação no estado errado

- **Detecção:** harness — `test_web.py::test_pagina_exibe_botao_para_doacao_pendente` e `test_pagina_informa_confirmacao_sem_exibir_botao` (Figura 9). Interface de confirmação: issue #17, PR #16 (VictorS4-byte).
- **O quê:** o botão "Confirmar" só deve aparecer para doações `PENDENTE`; para `CONFIRMADA` deve mostrar a informação, sem botão.
- **Causa:** **[CONFIRMAR]** houve versão em que o botão aparecia nos dois estados?
- **Correção:** **[CONFIRMAR]** commit dentro do PR #16.
- **Prevenção:** teste de interface para **cada** estado do fluxo `PENDENTE → CONFIRMADA`.
- **Classificação:** **[CONFIRMAR]**.

---

## Erro detectado por revisão humana (campo recomendado pela apostila)

A apostila pede, se houver, ao menos um erro **pego por humano onde não havia teste**. Procurem nos comentários dos PRs
(#13, #15, #16, #21, #22, #24, #25) por qualquer apontamento de revisor que mudou o código.

- **PR / revisor:** **[PREENCHER]**
- **O que o revisor percebeu:** **[PREENCHER]**
- **Por que nenhum teste pegou:** **[PREENCHER]**
- **Teste criado depois:** **[PREENCHER]**

> Se **nenhum** erro puder ser comprovado, escreva isto no relatório em vez de forçar entradas:
> *"Durante a Entrega 2 não identificamos erros lógicos comprovados por registro; as entradas acima
> documentam os pontos de risco cobertos pelo harness e o que verificamos no histórico."*
> Isso é honesto e é melhor que inventar.

## Evidência final

- Execução: `docker compose run --rm tests | tee logs_testes_final.txt` → **17 passed** **[REPETIR NO DOCKER]**
- Arquivo `logs_testes_final.txt` versionado e citado no README.
