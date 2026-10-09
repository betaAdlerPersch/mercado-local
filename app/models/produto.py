from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Produto(Base):
    __tablename__ = "produtos"
    __table_args__ = (
        CheckConstraint("preco > 0", name="ck_produtos_preco_positivo"),
        CheckConstraint("estoque >= 0", name="ck_produtos_estoque_nao_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    descricao: Mapped[str] = mapped_column(Text, default="")
    produtor: Mapped[str] = mapped_column(String(100))
    unidade: Mapped[str] = mapped_column(String(20), default="un")
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    estoque: Mapped[int] = mapped_column(Integer, default=0)
    icone: Mapped[str] = mapped_column(String(10), default="🧺")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))

    categoria: Mapped["Categoria"] = relationship(back_populates="produtos")  # noqa: F821
