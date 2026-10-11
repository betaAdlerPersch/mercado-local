"""Testes unitários das regras de negócio, sem passar pela API."""
from decimal import Decimal

from app.services.auth_service import gerar_hash, verificar_senha
from app.services.pedido_service import calcular_frete


def test_frete_cobrado_em_pedido_pequeno():
    assert calcular_frete(Decimal("50.00")) == Decimal("12.00")


def test_frete_gratis_em_pedido_grande():
    assert calcular_frete(Decimal("200.00")) == Decimal("0.00")


def test_hash_de_senha_confere():
    senha_hash = gerar_hash("minha-senha")
    assert senha_hash != "minha-senha"
    assert verificar_senha("minha-senha", senha_hash)
    assert not verificar_senha("outra-senha", senha_hash)


def test_hashes_da_mesma_senha_sao_diferentes():
    assert gerar_hash("abc") != gerar_hash("abc")


def test_hash_malformado_nao_quebra():
    assert not verificar_senha("abc", "lixo")


def test_url_do_render_recebe_o_driver_psycopg():
    from app.config import Settings

    assert Settings(database_url="postgres://u:s@host/db").database_url == "postgresql+psycopg://u:s@host/db"
    assert Settings(database_url="postgresql://u:s@host/db").database_url == "postgresql+psycopg://u:s@host/db"
    assert Settings(database_url="postgresql+psycopg://u:s@host/db").database_url == "postgresql+psycopg://u:s@host/db"


def test_frete_gratis_exatamente_no_limite():
    """Regressão do bug #5: pedido de exatamente R$ 150,00 pagava frete."""
    assert calcular_frete(Decimal("150.00")) == Decimal("0.00")
