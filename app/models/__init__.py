"""Camada MODEL: entidades persistidas no banco de dados."""
from app.models.administrador import Administrador
from app.models.categoria import Categoria
from app.models.cliente import Cliente
from app.models.pedido import EstadoPedido, ItemPedido, Pedido
from app.models.produto import Produto

__all__ = ["Administrador", "Categoria", "Cliente", "EstadoPedido", "ItemPedido", "Pedido", "Produto"]
