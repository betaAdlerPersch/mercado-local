"""Regras de negócio dos pedidos: cálculo de valores, estoque e frete."""
import secrets
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.models import Cliente, EstadoPedido, ItemPedido, Pedido, Produto
from app.schemas.pedido import ItemPedidoSaida, PedidoEntrada, PedidoSaida


class ErroDeNegocio(Exception):
    """Erro de regra de negócio, convertido em resposta 400/404 pelo controller."""

    def __init__(self, mensagem: str, status: int = 400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status


TRANSICOES_PERMITIDAS: dict[EstadoPedido, set[EstadoPedido]] = {
    EstadoPedido.RECEBIDO: {EstadoPedido.EM_PREPARACAO, EstadoPedido.CANCELADO},
    EstadoPedido.EM_PREPARACAO: {EstadoPedido.SAIU_PARA_ENTREGA, EstadoPedido.CANCELADO},
    EstadoPedido.SAIU_PARA_ENTREGA: {EstadoPedido.ENTREGUE},
    EstadoPedido.ENTREGUE: set(),
    EstadoPedido.CANCELADO: set(),
}


def calcular_frete(subtotal: Decimal) -> Decimal:
    """Frete grátis a partir de R$ 150,00; abaixo disso, valor fixo."""
    if subtotal >= settings.frete_gratis_a_partir_de:
        return Decimal("0.00")
    return settings.valor_frete


def _gerar_codigo() -> str:
    return "ML-" + secrets.token_hex(3).upper()


def _obter_ou_criar_cliente(db: Session, dados) -> Cliente:
    cliente = db.scalar(select(Cliente).where(Cliente.email == dados.email.lower()))
    if cliente is None:
        cliente = Cliente(email=dados.email.lower(), nome=dados.nome, telefone=dados.telefone)
        db.add(cliente)
    else:
        cliente.nome = dados.nome
        cliente.telefone = dados.telefone
    return cliente


def criar_pedido(db: Session, entrada: PedidoEntrada) -> Pedido:
    # Agrupa itens repetidos do mesmo produto
    quantidades: dict[int, int] = {}
    for item in entrada.itens:
        quantidades[item.produto_id] = quantidades.get(item.produto_id, 0) + item.quantidade

    produtos = {
        p.id: p
        for p in db.scalars(
            select(Produto)
            .where(Produto.id.in_(quantidades.keys()), Produto.ativo.is_(True))
            .with_for_update()  # trava as linhas para dois pedidos simultâneos não venderem o mesmo estoque
        )
    }

    itens: list[ItemPedido] = []
    subtotal = Decimal("0.00")
    for produto_id, quantidade in quantidades.items():
        produto = produtos.get(produto_id)
        if produto is None:
            raise ErroDeNegocio(f"Produto {produto_id} não encontrado.", 404)
        if quantidade > produto.estoque:
            raise ErroDeNegocio(f"Estoque insuficiente para {produto.nome} (disponível: {produto.estoque}).")

        produto.estoque -= quantidade

        # O preço SEMPRE vem do banco, nunca do navegador
        valor_item = produto.preco * quantidade
        subtotal += valor_item
        itens.append(
            ItemPedido(
                produto_id=produto.id,
                quantidade=quantidade,
                preco_unitario=produto.preco,
                subtotal=valor_item,
            )
        )

    frete = calcular_frete(subtotal)
    pedido = Pedido(
        codigo=_gerar_codigo(),
        cliente=_obter_ou_criar_cliente(db, entrada.cliente),
        endereco=entrada.endereco,
        cidade=entrada.cidade,
        cep=entrada.cep,
        subtotal=subtotal,
        frete=frete,
        total=subtotal + frete,
        itens=itens,
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido


def buscar_por_codigo(db: Session, codigo: str) -> Pedido:
    pedido = db.scalar(
        select(Pedido)
        .where(Pedido.codigo == codigo.strip().upper())
        .options(selectinload(Pedido.itens).selectinload(ItemPedido.produto), selectinload(Pedido.cliente))
    )
    if pedido is None:
        raise ErroDeNegocio("Pedido não encontrado.", 404)
    return pedido


def listar_pedidos(db: Session, estado: EstadoPedido | None = None) -> list[Pedido]:
    consulta = (
        select(Pedido)
        .options(selectinload(Pedido.itens).selectinload(ItemPedido.produto), selectinload(Pedido.cliente))
        .order_by(Pedido.criado_em.desc())
    )
    if estado is not None:
        consulta = consulta.where(Pedido.estado == estado)
    return list(db.scalars(consulta))


def atualizar_estado(db: Session, codigo: str, novo_estado: EstadoPedido) -> Pedido:
    pedido = buscar_por_codigo(db, codigo)
    if novo_estado not in TRANSICOES_PERMITIDAS[pedido.estado]:
        raise ErroDeNegocio(f"Não é possível mudar de '{pedido.estado.value}' para '{novo_estado.value}'.")
    pedido.estado = novo_estado
    db.commit()
    return pedido


def para_saida(pedido: Pedido) -> PedidoSaida:
    return PedidoSaida(
        codigo=pedido.codigo,
        estado=pedido.estado,
        criado_em=pedido.criado_em,
        cliente=pedido.cliente.nome,
        endereco=pedido.endereco,
        cidade=pedido.cidade,
        cep=pedido.cep,
        itens=[
            ItemPedidoSaida(
                produto=item.produto.nome,
                quantidade=item.quantidade,
                preco_unitario=float(item.preco_unitario),
                subtotal=float(item.subtotal),
            )
            for item in pedido.itens
        ],
        subtotal=float(pedido.subtotal),
        frete=float(pedido.frete),
        total=float(pedido.total),
    )
