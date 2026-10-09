from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import EstadoPedido
from app.schemas.pedido import AtualizarEstado, LoginEntrada, PedidoSaida
from app.services import auth_service, pedido_service
from app.services.pedido_service import ErroDeNegocio

router = APIRouter(prefix="/api/admin", tags=["Administração"])


@router.post("/login")
def login(entrada: LoginEntrada, request: Request, db: Session = Depends(get_db)):
    admin = auth_service.autenticar(db, entrada.email, entrada.senha)
    if admin is None:
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")
    request.session["admin_id"] = admin.id
    return {"mensagem": "Login realizado."}


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"mensagem": "Sessão encerrada."}


@router.get("/pedidos", response_model=list[PedidoSaida], dependencies=[Depends(auth_service.exigir_admin)])
def listar_pedidos(estado: EstadoPedido | None = None, db: Session = Depends(get_db)):
    return [pedido_service.para_saida(p) for p in pedido_service.listar_pedidos(db, estado)]


@router.patch(
    "/pedidos/{codigo}/estado",
    response_model=PedidoSaida,
    dependencies=[Depends(auth_service.exigir_admin)],
)
def atualizar_estado(codigo: str, entrada: AtualizarEstado, db: Session = Depends(get_db)):
    try:
        pedido = pedido_service.atualizar_estado(db, codigo, entrada.estado)
        return pedido_service.para_saida(pedido)
    except ErroDeNegocio as erro:
        db.rollback()
        raise HTTPException(status_code=erro.status, detail=erro.mensagem) from erro
