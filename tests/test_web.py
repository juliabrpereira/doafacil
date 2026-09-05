from app.domain import EstadoDoacao
from app.web import criar_doacao_demo, renderizar_pagina


def test_pagina_exibe_botao_para_doacao_pendente():
    pagina = renderizar_pagina(criar_doacao_demo()).decode("utf-8")

    assert 'action="/confirmar"' in pagina
    assert "Confirmar doação" in pagina


def test_pagina_informa_confirmacao_sem_exibir_botao():
    doacao = criar_doacao_demo()
    doacao.estado = EstadoDoacao.CONFIRMADA

    pagina = renderizar_pagina(doacao).decode("utf-8")

    assert "Doação confirmada." in pagina
    assert "Confirmar doação</button>" not in pagina
