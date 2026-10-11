from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.pedido import PedidoEntrada, PedidoSaida
from app.services import pedido_service
from app.services.pedido_service import ErroDeNegocio

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos"])


@router.post("", response_model=PedidoSaida, status_code=201)
def criar_pedido(entrada: PedidoEntrada, db: Session = Depends(get_db)):
    try:
        pedido = pedido_service.criar_pedido(db, entrada)
        return pedido_service.para_saida(pedido_service.buscar_por_codigo(db, pedido.codigo))
    except ErroDeNegocio as erro:
        db.rollback()
        raise HTTPException(status_code=erro.status, detail=erro.mensagem) from erro


@router.get("/{codigo}", response_model=PedidoSaida)
def acompanhar_pedido(codigo: str, db: Session = Depends(get_db)):
    """Consulta pública: só quem tem o código do pedido consegue ver."""
    try:
        return pedido_service.para_saida(pedido_service.buscar_por_codigo(db, codigo))
    except ErroDeNegocio as erro:
        raise HTTPException(status_code=erro.status, detail=erro.mensagem) from erro
