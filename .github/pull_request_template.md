## O que este PR faz
(resumo + "Closes #N")

## Critérios de aceitação
- [ ] Implementa exatamente o que a SPEC define (citar seção/RF/RN)
- [ ] `pytest -q` 100% verde (colar o resumo)
- [ ] Nenhum teste foi alterado só para passar
- [ ] `app/domain.py` continua sem dependência de framework, banco ou pagamento
- [ ] Erros relevantes registrados em `docs/ERROS.md`; mudança de regra registrada em SPEC §8

## Colaboração com IA
(ferramenta usada, o que foi gerado, o que foi ajustado à mão e por quê)

## Como validar
`docker compose run --rm tests`