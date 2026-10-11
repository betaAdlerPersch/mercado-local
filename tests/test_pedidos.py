import pytest


def test_cria_pedido_e_calcula_total_com_frete(cliente, novo_pedido):
    resposta = cliente.post("/api/pedidos", json=novo_pedido())
    assert resposta.status_code == 201
    pedido = resposta.json()
    # 2 kg de tomate a R$ 9,90 + frete de R$ 12,00
    assert pedido["subtotal"] == pytest.approx(19.80)
    assert pedido["frete"] == pytest.approx(12.00)
    assert pedido["total"] == pytest.approx(31.80)
    assert pedido["estado"] == "Recebido"
    assert pedido["codigo"].startswith("ML-")
    assert pedido["cep"] == "01310-100"


def test_preco_enviado_pelo_navegador_e_ignorado(cliente, novo_pedido):
    corpo = novo_pedido(itens=[{"produto_id": 1, "quantidade": 1, "preco": 0.01}])
    pedido = cliente.post("/api/pedidos", json=corpo).json()
    assert pedido["itens"][0]["preco_unitario"] == pytest.approx(9.90)


def test_frete_gratis_para_pedidos_grandes(cliente, novo_pedido):
    # 6 cafés a R$ 29,90 = R$ 179,40
    pedido = cliente.post("/api/pedidos", json=novo_pedido(itens=[{"produto_id": 11, "quantidade": 6}])).json()
    assert pedido["frete"] == 0
    assert pedido["total"] == pytest.approx(179.40)


def test_agrupa_itens_repetidos(cliente, novo_pedido):
    corpo = novo_pedido(itens=[{"produto_id": 1, "quantidade": 1}, {"produto_id": 1, "quantidade": 2}])
    pedido = cliente.post("/api/pedidos", json=corpo).json()
    assert len(pedido["itens"]) == 1
    assert pedido["itens"][0]["quantidade"] == 3


def test_recusa_quantidade_acima_do_estoque(cliente, novo_pedido):
    # Pão tem 10 unidades em estoque
    resposta = cliente.post("/api/pedidos", json=novo_pedido(itens=[{"produto_id": 10, "quantidade": 11}]))
    assert resposta.status_code == 400
    assert "Estoque insuficiente" in resposta.json()["detail"]


def test_recusa_produto_inexistente(cliente, novo_pedido):
    resposta = cliente.post("/api/pedidos", json=novo_pedido(itens=[{"produto_id": 999, "quantidade": 1}]))
    assert resposta.status_code == 404


def test_recusa_cesta_vazia(cliente, novo_pedido):
    assert cliente.post("/api/pedidos", json=novo_pedido(itens=[])).status_code == 422


@pytest.mark.parametrize("cep", ["123", "1234567890", "abcde-fgh"])
def test_recusa_cep_invalido(cliente, novo_pedido, cep):
    assert cliente.post("/api/pedidos", json=novo_pedido(cep=cep)).status_code == 422


def test_recusa_email_invalido(cliente, novo_pedido):
    corpo = novo_pedido()
    corpo["cliente"]["email"] = "maria-sem-arroba"
    assert cliente.post("/api/pedidos", json=corpo).status_code == 422


def test_recusa_endereco_muito_curto(cliente, novo_pedido):
    assert cliente.post("/api/pedidos", json=novo_pedido(endereco="Rua")).status_code == 422


def test_reaproveita_cliente_pelo_email(cliente, novo_pedido):
    cliente.post("/api/pedidos", json=novo_pedido())
    corpo = novo_pedido()
    corpo["cliente"]["nome"] = "Maria Silva Santos"
    pedido = cliente.post("/api/pedidos", json=corpo).json()
    assert pedido["cliente"] == "Maria Silva Santos"


def test_acompanha_pedido_pelo_codigo(cliente, novo_pedido):
    codigo = cliente.post("/api/pedidos", json=novo_pedido()).json()["codigo"]
    resposta = cliente.get(f"/api/pedidos/{codigo.lower()}")
    assert resposta.status_code == 200
    assert resposta.json()["codigo"] == codigo


def test_codigo_inexistente_retorna_404(cliente):
    assert cliente.get("/api/pedidos/ML-000000").status_code == 404


def test_mensagens_de_validacao_em_portugues(cliente, novo_pedido):
    corpo = novo_pedido(cep="123", endereco="Rua")
    corpo["cliente"]["email"] = "sem-arroba"
    mensagens = {e["loc"][-1]: e["msg"] for e in cliente.post("/api/pedidos", json=corpo).json()["detail"]}
    assert mensagens == {
        "email": "e-mail inválido",
        "cep": "CEP deve ter 8 dígitos",
        "endereco": "muito curto (mínimo 5 caracteres)",
    }


def test_recusa_quantidade_zero(cliente, novo_pedido):
    """Regressão do bug #1: item com quantidade 0 era gravado no pedido."""
    corpo = novo_pedido(itens=[{"produto_id": 1, "quantidade": 0}])
    assert cliente.post("/api/pedidos", json=corpo).status_code == 422


def test_compra_desconta_estoque(cliente, novo_pedido):
    """Regressão do bug #3: o estoque não diminuía depois da compra."""
    cliente.post("/api/pedidos", json=novo_pedido(itens=[{"produto_id": 9, "quantidade": 12}]))
    mel = next(p for p in cliente.get("/api/produtos").json() if p["id"] == 9)
    assert mel["estoque"] == 0
    resposta = cliente.post("/api/pedidos", json=novo_pedido(itens=[{"produto_id": 9, "quantidade": 1}]))
    assert resposta.status_code == 400


def test_pedido_recusado_nao_desconta_estoque(cliente, novo_pedido):
    """Se um item do pedido falha, o estoque dos outros itens não pode mudar."""
    corpo = novo_pedido(itens=[{"produto_id": 1, "quantidade": 5}, {"produto_id": 10, "quantidade": 11}])
    assert cliente.post("/api/pedidos", json=corpo).status_code == 400
    tomate = next(p for p in cliente.get("/api/produtos").json() if p["id"] == 1)
    assert tomate["estoque"] == 40


@pytest.mark.parametrize("telefone", ["abcdefghij", "1234", "11 9999-999a"])
def test_recusa_telefone_invalido(cliente, novo_pedido, telefone):
    """Regressão do bug #4: o telefone aceitava letras."""
    corpo = novo_pedido()
    corpo["cliente"]["telefone"] = telefone
    assert cliente.post("/api/pedidos", json=corpo).status_code == 422
