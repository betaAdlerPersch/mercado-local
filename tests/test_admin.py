def test_lista_de_pedidos_exige_login(cliente):
    assert cliente.get("/api/admin/pedidos").status_code == 401


def test_login_com_senha_errada(cliente):
    resposta = cliente.post("/api/admin/login", json={"email": "admin@teste.com", "senha": "errada"})
    assert resposta.status_code == 401


def test_admin_ve_os_pedidos(admin, novo_pedido):
    admin.post("/api/pedidos", json=novo_pedido())
    pedidos = admin.get("/api/admin/pedidos").json()
    assert len(pedidos) == 1
    assert pedidos[0]["cliente"] == "Maria Silva"


def test_logout_encerra_a_sessao(admin):
    admin.post("/api/admin/logout")
    assert admin.get("/api/admin/pedidos").status_code == 401


def test_avanca_estado_do_pedido(admin, novo_pedido):
    codigo = admin.post("/api/pedidos", json=novo_pedido()).json()["codigo"]
    resposta = admin.patch(f"/api/admin/pedidos/{codigo}/estado", json={"estado": "Em preparação"})
    assert resposta.status_code == 200
    assert resposta.json()["estado"] == "Em preparação"


def test_nao_permite_pular_etapas(admin, novo_pedido):
    codigo = admin.post("/api/pedidos", json=novo_pedido()).json()["codigo"]
    resposta = admin.patch(f"/api/admin/pedidos/{codigo}/estado", json={"estado": "Entregue"})
    assert resposta.status_code == 400


def test_pedido_cancelado_nao_muda_mais(admin, novo_pedido):
    codigo = admin.post("/api/pedidos", json=novo_pedido()).json()["codigo"]
    admin.patch(f"/api/admin/pedidos/{codigo}/estado", json={"estado": "Cancelado"})
    resposta = admin.patch(f"/api/admin/pedidos/{codigo}/estado", json={"estado": "Em preparação"})
    assert resposta.status_code == 400


def test_filtra_pedidos_por_estado(admin, novo_pedido):
    primeiro = admin.post("/api/pedidos", json=novo_pedido()).json()["codigo"]
    admin.post("/api/pedidos", json=novo_pedido())
    admin.patch(f"/api/admin/pedidos/{primeiro}/estado", json={"estado": "Em preparação"})

    em_preparacao = admin.get("/api/admin/pedidos?estado=Em preparação").json()
    assert [p["codigo"] for p in em_preparacao] == [primeiro]
    assert len(admin.get("/api/admin/pedidos?estado=Recebido").json()) == 1


def test_estado_invalido_e_recusado(admin, novo_pedido):
    codigo = admin.post("/api/pedidos", json=novo_pedido()).json()["codigo"]
    resposta = admin.patch(f"/api/admin/pedidos/{codigo}/estado", json={"estado": "Perdido"})
    assert resposta.status_code == 422
