from decimal import Decimal

import pytest

from app.domain import DomainError, Doacao, EstadoDoacao, ONG, confirmar_doacao, criar_doacao


def test_ong_e_criada_ativa_por_padrao():
    ong = ONG(nome="Instituto Esperança")

    assert ong.nome == "Instituto Esperança"
    assert ong.ativa is True


def test_ong_pode_ser_criada_inativa():
    ong = ONG(nome="Instituto Esperança", ativa=False)

    assert ong.ativa is False


def test_doacao_e_criada_pendente_com_dados_normalizados():
    ong = ONG(nome="Instituto Esperança")

    doacao = criar_doacao(
        nome_doador=" Ana Silva ",
        email_doador="  ANA@EXAMPLE.COM ",
        ong=ong,
        valor="25",
    )

    assert doacao.nome_doador == "Ana Silva"
    assert doacao.email_doador == "ana@example.com"
    assert doacao.ong is ong
    assert doacao.valor == Decimal("25.00")
    assert doacao.estado is EstadoDoacao.PENDENTE


@pytest.mark.parametrize(
    "nome_doador,email_doador,valor,erro",
    [
        ("   ", "ana@example.com", 25, "Nome do doador"),
        ("Ana Silva", "ana@invalid", 25, "E-mail do doador"),
        ("Ana Silva", "ana@example.com", 0, "maior que zero"),
        ("Ana Silva", "ana@example.com", -5, "maior que zero"),
    ],
)
def test_criar_doacao_rejeita_dados_invalidos(nome_doador, email_doador, valor, erro):
    ong = ONG(nome="Instituto Esperança")

    with pytest.raises(DomainError, match=erro):
        criar_doacao(nome_doador=nome_doador, email_doador=email_doador, ong=ong, valor=valor)


def test_criar_doacao_rejeita_ong_inativa():
    ong = ONG(nome="Instituto Esperança", ativa=False)

    with pytest.raises(DomainError, match="ONG inativa"):
        criar_doacao("Ana Silva", "ana@example.com", ong, 25)


def test_confirmar_doacao_altera_estado():
    ong = ONG(nome="Instituto Esperança")
    doacao = criar_doacao("Ana Silva", "ana@example.com", ong, Decimal("25.00"))

    doacao = confirmar_doacao(doacao)

    assert doacao.estado is EstadoDoacao.CONFIRMADA


def test_confirmar_doacao_rejeita_confirmacao_duplicada():
    ong = ONG(nome="Instituto Esperança")
    doacao = criar_doacao("Ana Silva", "ana@example.com", ong, Decimal("25.00"))
    confirmar_doacao(doacao)

    with pytest.raises(DomainError, match="já está confirmada"):
        confirmar_doacao(doacao)

@pytest.mark.parametrize("valor", ["NaN", "sNaN", "Infinity", "-Infinity"])
def test_criar_doacao_rejeita_valor_nao_finito(valor):
    ong = ONG(nome="Instituto Esperança")

    with pytest.raises(DomainError, match="número válido"):
        criar_doacao("Ana Silva", "ana@example.com", ong, valor)


@pytest.mark.parametrize("valor", ["abc", "1,50", None])
def test_criar_doacao_rejeita_valor_nao_numerico(valor):
    ong = ONG(nome="Instituto Esperança")

    with pytest.raises(DomainError, match="número válido"):
        criar_doacao("Ana Silva", "ana@example.com", ong, valor)


def test_criar_doacao_aceita_menor_valor_positivo_e_rejeita_abaixo_dele():
    ong = ONG(nome="Instituto Esperança")

    assert criar_doacao("Ana Silva", "ana@example.com", ong, "0.01").valor == Decimal("0.01")
    with pytest.raises(DomainError, match="maior que zero"):
        criar_doacao("Ana Silva", "ana@example.com", ong, "0.004")


@pytest.mark.parametrize("nome_ong", ["", "   "])
def test_criar_doacao_rejeita_ong_sem_nome(nome_ong):
    with pytest.raises(DomainError, match="Nome da ONG"):
        criar_doacao("Ana Silva", "ana@example.com", ONG(nome=nome_ong), 25)


def test_criar_doacao_rejeita_ong_que_nao_e_ong():
    with pytest.raises(DomainError, match="ONG inválida"):
        criar_doacao("Ana Silva", "ana@example.com", "Instituto Esperança", 25)
