# API REST

A documentação interativa (Swagger) fica disponível em `http://localhost:8000/docs` com a aplicação rodando.

## Públicas

### `GET /api/produtos`

Lista os produtos ativos em ordem alfabética.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `busca` | texto (opcional) | Parte do nome do produto |
| `categoria_id` | inteiro (opcional) | Filtra pela categoria |

```json
[
  {
    "id": 1, "nome": "Tomate orgânico", "descricao": "Tomate italiano…",
    "produtor": "Sítio Boa Vista", "unidade": "kg", "preco": 9.9,
    "estoque": 40, "icone": "🍅", "categoria": "Hortifrúti"
  }
]
```

### `GET /api/categorias`

```json
[{ "id": 3, "nome": "Empório" }, { "id": 1, "nome": "Hortifrúti" }]
```

### `POST /api/pedidos`

```json
{
  "cliente": { "nome": "Maria Silva", "email": "maria@exemplo.com", "telefone": "(11) 91234-5678" },
  "endereco": "Rua das Palmeiras, 100",
  "cidade": "São Paulo",
  "cep": "01310-100",
  "itens": [{ "produto_id": 1, "quantidade": 2 }]
}
```

| Status | Quando |
|---|---|
| 201 | Pedido criado; devolve o pedido completo com `codigo` |
| 400 | Estoque insuficiente |
| 404 | Produto não encontrado |
| 422 | Dados inválidos (e-mail, CEP, cesta vazia, campos curtos) |

### `GET /api/pedidos/{codigo}`

Devolve o pedido (aceita o código em maiúsculas ou minúsculas). `404` se não existir.

```json
{
  "codigo": "ML-4F2A9C", "estado": "Recebido", "criado_em": "2026-10-09T21:38:37+02:00",
  "cliente": "Maria Silva", "endereco": "Rua das Palmeiras, 100", "cidade": "São Paulo", "cep": "01310-100",
  "itens": [{ "produto": "Tomate orgânico", "quantidade": 2, "preco_unitario": 9.9, "subtotal": 19.8 }],
  "subtotal": 19.8, "frete": 12.0, "total": 31.8
}
```

## Administrativas (exigem login)

| Método e rota | Descrição | Respostas |
|---|---|---|
| `POST /api/admin/login` | Corpo `{ "email", "senha" }`; cria a sessão | 200, 401 |
| `POST /api/admin/logout` | Encerra a sessão | 200 |
| `GET /api/admin/pedidos?estado=Recebido` | Lista pedidos, mais recentes primeiro; filtro opcional | 200, 401 |
| `PATCH /api/admin/pedidos/{codigo}/estado` | Corpo `{ "estado": "Em preparação" }` | 200, 400 (transição proibida), 401, 404, 422 |
