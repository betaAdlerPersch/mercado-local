from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import EstadoPedido


class ItemPedidoEntrada(BaseModel):
    produto_id: int
    quantidade: int = Field(ge=1, le=50)


class ClienteEntrada(BaseModel):
    nome: str = Field(min_length=3, max_length=120)
    email: EmailStr
    telefone: str = Field(min_length=8, max_length=30)

    @field_validator("telefone")
    @classmethod
    def validar_telefone(cls, valor: str) -> str:
        if any(c.isalpha() for c in valor):
            raise ValueError("não pode conter letras")
        digitos = "".join(c for c in valor if c.isdigit())
        if len(digitos) not in (10, 11):
            raise ValueError("informe DDD + número (10 ou 11 dígitos)")
        return digitos


class PedidoEntrada(BaseModel):
    cliente: ClienteEntrada
    endereco: str = Field(min_length=5, max_length=200)
    cidade: str = Field(min_length=2, max_length=80)
    cep: str
    itens: list[ItemPedidoEntrada] = Field(min_length=1)

    @field_validator("cep")
    @classmethod
    def validar_cep(cls, valor: str) -> str:
        digitos = "".join(c for c in valor if c.isdigit())
        if len(digitos) != 8:
            raise ValueError("CEP deve ter 8 dígitos")
        return f"{digitos[:5]}-{digitos[5:]}"


class ItemPedidoSaida(BaseModel):
    produto: str
    quantidade: int
    preco_unitario: float
    subtotal: float


class PedidoSaida(BaseModel):
    codigo: str
    estado: EstadoPedido
    criado_em: datetime
    cliente: str
    endereco: str
    cidade: str
    cep: str
    itens: list[ItemPedidoSaida]
    subtotal: float
    frete: float
    total: float


class AtualizarEstado(BaseModel):
    estado: EstadoPedido


class LoginEntrada(BaseModel):
    email: str
    senha: str
