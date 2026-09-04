"""Entidades centrais do domínio do DOA FÁCIL.

Este módulo não depende de infraestrutura ou frameworks externos.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


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
