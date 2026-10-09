"""Configuração dos testes: usa um banco PostgreSQL separado (mercado_local_test)."""
import os

# Precisa vir ANTES de importar a aplicação, para o engine apontar para o banco de testes
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://mercado:mercado@localhost:5432/mercado_local_test"
)
os.environ["ADMIN_EMAIL"] = "admin@teste.com"
os.environ["ADMIN_PASSWORD"] = "senha-de-teste"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from scripts.init_db import popular  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def criar_estrutura():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def banco_limpo():
    """Cada teste começa com o banco populado e sem pedidos."""
    tabelas = ", ".join(t.name for t in reversed(Base.metadata.sorted_tables))
    with engine.begin() as conexao:
        conexao.execute(text(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE"))
    with SessionLocal() as db:
        popular(db)
    yield


@pytest.fixture
def cliente():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin(cliente):
    resposta = cliente.post("/api/admin/login", json={"email": "admin@teste.com", "senha": "senha-de-teste"})
    assert resposta.status_code == 200
    return cliente


def pedido_valido(**alteracoes) -> dict:
    corpo = {
        "cliente": {"nome": "Maria Silva", "email": "maria@exemplo.com", "telefone": "(11) 91234-5678"},
        "endereco": "Rua das Palmeiras, 100",
        "cidade": "São Paulo",
        "cep": "01310-100",
        "itens": [{"produto_id": 1, "quantidade": 2}],
    }
    corpo.update(alteracoes)
    return corpo


@pytest.fixture
def novo_pedido():
    return pedido_valido
