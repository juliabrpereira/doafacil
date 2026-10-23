import pytest
from http.client import HTTPConnection
from http.server import HTTPServer
from threading import Thread
from urllib.parse import urlencode

from app.domain import EstadoDoacao
from app.web import (
    DoaFacilHandler,
    criar_doacao_demo,
    renderizar_formulario,
    renderizar_landing,
    renderizar_pagina,
)


@pytest.fixture
def servidor_web():
    DoaFacilHandler.doacao = [criar_doacao_demo()]
    servidor = HTTPServer(("127.0.0.1", 0), DoaFacilHandler)
    thread = Thread(target=servidor.serve_forever, daemon=True)
    thread.start()

    yield servidor.server_port

    servidor.shutdown()
    thread.join()
    servidor.server_close()


def test_pagina_exibe_formulario_para_criar_doacao():
    pagina = renderizar_landing().decode("utf-8")

    assert 'href="/criar"' in pagina
    assert 'href="/doacoes"' in pagina


def test_pagina_de_doacoes_exibe_confirmacao_para_doacao_pendente():
    pagina = renderizar_pagina(criar_doacao_demo()).decode("utf-8")

    assert 'action="/confirmar/0"' in pagina


def test_formulario_de_criacao_exibe_campos_obrigatorios():
    pagina = renderizar_formulario().decode("utf-8")

    assert 'action="/criar"' in pagina
    assert 'name="nome_doador"' in pagina
    assert 'name="email_doador"' in pagina
    assert 'name="ong"' in pagina
    assert 'name="valor"' in pagina


def test_formulario_cria_doacao_pendente_com_dados_normalizados(servidor_web):
    conexao = HTTPConnection("127.0.0.1", servidor_web)
    dados = urlencode(
        {
            "nome_doador": " Ana Silva ",
            "email_doador": " ANA@EXAMPLE.COM ",
            "ong": "Instituto Esperança",
            "valor": "25",
        }
    )
    conexao.request(
        "POST",
        "/criar",
        body=dados,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resposta = conexao.getresponse()

    assert resposta.status == 303
    assert resposta.getheader("Location") == "/doacoes"
    resposta.read()

    conexao.request("GET", "/doacoes")
    pagina = conexao.getresponse().read().decode("utf-8")

    assert DoaFacilHandler.doacoes[-1].nome_doador == "Ana Silva"
    assert DoaFacilHandler.doacoes[-1].email_doador == "ana@example.com"
    assert DoaFacilHandler.doacoes[-1].estado is EstadoDoacao.PENDENTE
    assert "Ana Silva" in pagina
    assert "Instituto Esperança" in pagina
    assert "R$ 25.00" in pagina
    assert "PENDENTE" in pagina


def test_formulario_informa_erro_do_dominio_para_email_invalido(servidor_web):
    conexao = HTTPConnection("127.0.0.1", servidor_web)
    dados = urlencode(
        {
            "nome_doador": "Ana Silva",
            "email_doador": "email-invalido",
            "ong": "Instituto Esperança",
            "valor": "25",
        }
    )
    conexao.request(
        "POST",
        "/criar",
        body=dados,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resposta = conexao.getresponse()
    pagina = resposta.read().decode("utf-8")

    assert resposta.status == 400
    assert "E-mail do doador deve ser válido." in pagina


def test_pagina_exibe_botao_para_doacao_pendente():
    pagina = renderizar_pagina(criar_doacao_demo()).decode("utf-8")

    assert 'action="/confirmar/0"' in pagina
    assert "Confirmar doação" in pagina


def test_pagina_informa_confirmacao_sem_exibir_botao():
    doacao = criar_doacao_demo()
    doacao.estado = EstadoDoacao.CONFIRMADA

    pagina = renderizar_pagina(doacao).decode("utf-8")

    assert "Doação confirmada." in pagina
    assert "Confirmar doação</button>" not in pagina

def _post(porta, caminho, campos=None):
    conexao = HTTPConnection("127.0.0.1", porta)
    conexao.request(
        "POST",
        caminho,
        body=urlencode(campos or {}),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resposta = conexao.getresponse()
    return resposta.status, resposta.read().decode("utf-8")


CAMPOS_VALIDOS = {
    "nome_doador": "Ana Silva",
    "email_doador": "ana@example.com",
    "ong": "Instituto Esperança",
    "valor": "25",
}


def test_formulario_informa_erro_para_valor_nao_finito(servidor_web):
    status, pagina = _post(servidor_web, "/criar", {**CAMPOS_VALIDOS, "valor": "NaN"})

    assert status == 400
    assert "Valor da doação deve ser um número válido." in pagina


def test_formulario_rejeita_ong_em_branco(servidor_web):
    status, pagina = _post(servidor_web, "/criar", {**CAMPOS_VALIDOS, "ong": "   "})

    assert status == 400
    assert "Nome da ONG deve ser informado." in pagina


def test_servidor_comeca_cada_teste_com_apenas_a_doacao_de_demonstracao(servidor_web):
    assert len(DoaFacilHandler.doacoes) == 1
    _post(servidor_web, "/criar", CAMPOS_VALIDOS)
    assert len(DoaFacilHandler.doacoes) == 2


def test_confirmar_pela_interface_altera_estado_e_bloqueia_duplicidade(servidor_web):
    status, _ = _post(servidor_web, "/confirmar/0")
    assert status == 303
    assert DoaFacilHandler.doacoes[0].estado is EstadoDoacao.CONFIRMADA

    status, pagina = _post(servidor_web, "/confirmar/0")
    assert status == 400
    assert "Doação já está confirmada." in pagina


def test_confirmar_doacao_inexistente_retorna_404(servidor_web):
    status, _ = _post(servidor_web, "/confirmar/99")

    assert status == 404


def test_rota_desconhecida_retorna_404(servidor_web):
    conexao = HTTPConnection("127.0.0.1", servidor_web)
    conexao.request("GET", "/nao-existe")

    assert conexao.getresponse().status == 404
