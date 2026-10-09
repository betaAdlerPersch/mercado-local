"""Cria as tabelas e popula o banco com dados iniciais.

Uso:
    python -m scripts.init_db            # cria tabelas e dados (se o banco estiver vazio)
    python -m scripts.init_db --reset    # apaga tudo e recria
"""
import sys
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Administrador, Categoria, Produto
from app.services.auth_service import gerar_hash

PRODUTOS = [
    # (nome, categoria, produtor, unidade, preço, estoque, ícone, descrição)
    ("Tomate orgânico", "Hortifrúti", "Sítio Boa Vista", "kg", "9.90", 40, "🍅", "Tomate italiano colhido na semana, sem agrotóxicos."),
    ("Alface crespa", "Hortifrúti", "Sítio Boa Vista", "un", "3.50", 60, "🥬", "Pé de alface crespa hidropônica."),
    ("Cenoura", "Hortifrúti", "Chácara Três Irmãos", "kg", "6.80", 35, "🥕", "Cenoura fresca, ideal para sucos e refogados."),
    ("Morango", "Hortifrúti", "Fazenda Serra Azul", "bandeja", "12.00", 25, "🍓", "Bandeja de 250 g de morangos selecionados."),
    ("Banana prata", "Hortifrúti", "Chácara Três Irmãos", "dúzia", "8.50", 30, "🍌", "Dúzia de banana prata madura no ponto."),
    ("Queijo minas frescal", "Laticínios", "Laticínio Vale Verde", "500 g", "24.90", 15, "🧀", "Queijo artesanal feito com leite de vacas a pasto."),
    ("Iogurte natural", "Laticínios", "Laticínio Vale Verde", "litro", "14.00", 20, "🥛", "Iogurte integral sem açúcar e sem conservantes."),
    ("Ovos caipiras", "Laticínios", "Granja Recanto", "dúzia", "16.00", 30, "🥚", "Ovos de galinhas criadas soltas."),
    ("Mel silvestre", "Empório", "Apiário Flor do Campo", "500 g", "32.00", 12, "🍯", "Mel puro de florada silvestre."),
    ("Pão de fermentação natural", "Empório", "Padaria da Vila", "un", "18.00", 10, "🍞", "Pão rústico de longa fermentação, assado no dia."),
    ("Café especial torrado", "Empório", "Fazenda Serra Azul", "250 g", "29.90", 18, "☕", "Café arábica, torra média, notas de chocolate."),
    ("Geleia de amora", "Empório", "Apiário Flor do Campo", "300 g", "19.50", 14, "🫐", "Geleia artesanal com pedaços da fruta."),
]


def popular(db: Session) -> None:
    if db.scalar(select(Produto.id).limit(1)) is not None:
        print("Banco já possui dados; nada a fazer.")
        return

    categorias: dict[str, Categoria] = {}
    for nome, cat, produtor, unidade, preco, estoque, icone, descricao in PRODUTOS:
        if cat not in categorias:
            categorias[cat] = Categoria(nome=cat)
            db.add(categorias[cat])
        db.add(
            Produto(
                nome=nome,
                categoria=categorias[cat],
                produtor=produtor,
                unidade=unidade,
                preco=Decimal(preco),
                estoque=estoque,
                icone=icone,
                descricao=descricao,
            )
        )

    db.add(Administrador(email=settings.admin_email.lower(), senha_hash=gerar_hash(settings.admin_password)))
    db.commit()
    print(f"Banco populado: {len(PRODUTOS)} produtos, {len(categorias)} categorias, 1 administrador.")


def main() -> None:
    if "--reset" in sys.argv:
        Base.metadata.drop_all(engine)
        print("Tabelas apagadas.")
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        popular(db)


if __name__ == "__main__":
    main()
