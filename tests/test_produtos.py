def test_lista_todos_os_produtos_ativos(cliente):
    resposta = cliente.get("/api/produtos")
    assert resposta.status_code == 200
    produtos = resposta.json()
    assert len(produtos) == 12
    assert {"id", "nome", "preco", "estoque", "categoria", "produtor"} <= produtos[0].keys()


def test_produtos_vem_em_ordem_alfabetica(cliente):
    nomes = [p["nome"] for p in cliente.get("/api/produtos").json()]
    assert nomes == sorted(nomes)


def test_filtra_por_categoria(cliente):
    categorias = {c["nome"]: c["id"] for c in cliente.get("/api/categorias").json()}
    produtos = cliente.get(f"/api/produtos?categoria_id={categorias['Laticínios']}").json()
    assert len(produtos) == 3
    assert all(p["categoria"] == "Laticínios" for p in produtos)


def test_busca_por_nome(cliente):
    produtos = cliente.get("/api/produtos?busca=Tomate").json()
    assert [p["nome"] for p in produtos] == ["Tomate orgânico"]


def test_busca_sem_resultado(cliente):
    assert cliente.get("/api/produtos?busca=Abacaxi").json() == []


def test_lista_categorias(cliente):
    nomes = [c["nome"] for c in cliente.get("/api/categorias").json()]
    assert nomes == ["Empório", "Hortifrúti", "Laticínios"]


def test_busca_ignora_maiusculas(cliente):
    """Regressão do bug #2: a busca diferenciava maiúsculas de minúsculas."""
    produtos = cliente.get("/api/produtos?busca=tomate").json()
    assert [p["nome"] for p in produtos] == ["Tomate orgânico"]
