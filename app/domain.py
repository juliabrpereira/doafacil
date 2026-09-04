"""Entidades centrais do domínio do DOA FÁCIL.

Este módulo não depende de infraestrutura ou frameworks externos.
"""

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum


class DomainError(ValueError):
    """Erro de regra de negócio do domínio."""


class EstadoDoacao(str, Enum):
    """Estados possíveis de uma doação."""

    PENDENTE = "PENDENTE"
    CONFIRMADA = "CONFIRMADA"


@dataclass
class ONG:
    """Organização que pode receber doações."""

    nome: str
    ativa: bool = True


@dataclass
class Doacao:
    """Registro de uma doação destinada a uma ONG."""

    nome_doador: str
    email_doador: str
    ong: ONG
    valor: Decimal
    estado: EstadoDoacao = EstadoDoacao.PENDENTE


EMAIL_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def criar_doacao(nome_doador, email_doador, ong, valor):
    """Cria uma nova doação validando regras de negócio do domínio."""
    nome = (nome_doador or "").strip()
    if not nome:
        raise DomainError("Nome do doador deve ser informado.")

    email = (email_doador or "").strip().lower()
    if not EMAIL_VALIDO.match(email):
        raise DomainError("E-mail do doador deve ser válido.")

    if not isinstance(ong, ONG):
        raise DomainError("ONG inválida.")
    if not ong.ativa:
        raise DomainError("ONG inativa não pode receber doações.")

    try:
        valor_decimal = Decimal(str(valor)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise DomainError("Valor da doação deve ser um número válido.") from exc

    if valor_decimal <= 0:
        raise DomainError("Valor da doação deve ser maior que zero.")

    return Doacao(
        nome_doador=nome,
        email_doador=email,
        ong=ong,
        valor=valor_decimal,
        estado=EstadoDoacao.PENDENTE,
    )


def confirmar_doacao(doacao):
    """Confirma uma doação pendente."""
    if doacao.estado is EstadoDoacao.CONFIRMADA:
        raise DomainError("Doação já está confirmada.")

    doacao.estado = EstadoDoacao.CONFIRMADA
    return doacao
