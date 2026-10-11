from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Categoria, Produto
from app.schemas.produto import CategoriaSaida, ProdutoSaida

router = APIRouter(prefix="/api", tags=["Produtos"])


def _para_saida(produto: Produto) -> ProdutoSaida:
    return ProdutoSaida(
        id=produto.id,
        nome=produto.nome,
        descricao=produto.descricao,
        produtor=produto.produtor,
        unidade=produto.unidade,
        preco=float(produto.preco),
        estoque=produto.estoque,
        icone=produto.icone,
        categoria=produto.categoria.nome,
    )


@router.get("/produtos", response_model=list[ProdutoSaida])
def listar_produtos(
    busca: str | None = Query(default=None, max_length=60),
    categoria_id: int | None = None,
    db: Session = Depends(get_db),
):
    consulta = (
        select(Produto)
        .options(joinedload(Produto.categoria))
        .where(Produto.ativo.is_(True))
        .order_by(Produto.nome)
    )
    if busca:
        consulta = consulta.where(Produto.nome.like(f"%{busca.strip()}%"))
    if categoria_id:
        consulta = consulta.where(Produto.categoria_id == categoria_id)
    return [_para_saida(p) for p in db.scalars(consulta)]


@router.get("/categorias", response_model=list[CategoriaSaida])
def listar_categorias(db: Session = Depends(get_db)):
    return db.scalars(select(Categoria).order_by(Categoria.nome)).all()
