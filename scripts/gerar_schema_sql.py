"""Gera database/schema.sql a partir dos models, para a documentação nunca ficar desatualizada.

Uso:
    python -m scripts.gerar_schema_sql
"""
from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

import app.models  # noqa: F401  (registra os models)
from app.database import Base
from app.models.pedido import EstadoPedido

DESTINO = Path(__file__).resolve().parent.parent / "database" / "schema.sql"


def main() -> None:
    dialeto = postgresql.dialect()
    partes = [
        "-- Mercado Local - esquema físico do banco (PostgreSQL)",
        "-- Arquivo gerado por scripts/gerar_schema_sql.py. Não edite à mão.\n",
        "CREATE TYPE estado_pedido AS ENUM ("
        + ", ".join(f"'{e.value}'" for e in EstadoPedido)
        + ");\n",
    ]
    for tabela in Base.metadata.sorted_tables:
        partes.append(str(CreateTable(tabela).compile(dialect=dialeto)).strip() + ";\n")
        for indice in tabela.indexes:
            partes.append(str(CreateIndex(indice).compile(dialect=dialeto)).strip() + ";\n")
    DESTINO.write_text("\n".join(partes), encoding="utf-8")
    print(f"Gerado: {DESTINO}")


if __name__ == "__main__":
    main()
