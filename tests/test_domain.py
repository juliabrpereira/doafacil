from decimal import Decimal

from app.domain import Doacao, EstadoDoacao, ONG


def test_ong_e_criada_ativa_por_padrao():
    ong = ONG(nome="Instituto Esperança")

    assert ong.nome == "Instituto Esperança"
    assert ong.ativa is True


def test_ong_pode_ser_criada_inativa():
    ong = ONG(nome="Instituto Esperança", ativa=False)

    assert ong.ativa is False


def test_doacao_e_criada_pendente():
    ong = ONG(nome="Instituto Esperança")

    doacao = Doacao(
        nome_doador="Ana Silva",
        email_doador="ana@example.com",
        ong=ong,
        valor=Decimal("25.00"),
    )

    assert doacao.ong is ong
    assert doacao.valor == Decimal("25.00")
    assert doacao.estado is EstadoDoacao.PENDENTE
