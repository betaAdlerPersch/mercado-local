import pytest


@pytest.mark.parametrize("rota", ["/", "/acompanhar", "/admin"])
def test_paginas_carregam(cliente, rota):
    resposta = cliente.get(rota)
    assert resposta.status_code == 200
    assert "Mercado Local" in resposta.text


def test_arquivos_estaticos(cliente):
    assert cliente.get("/static/css/style.css").status_code == 200
    assert cliente.get("/static/js/loja.js").status_code == 200
