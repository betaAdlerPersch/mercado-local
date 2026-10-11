# Modelagem UML

Os diagramas estão em [Mermaid](https://mermaid.js.org/), renderizados automaticamente pelo GitHub.

## Diagrama de casos de uso

```mermaid
flowchart LR
    cliente([👤 Cliente])
    admin([👤 Administrador])

    subgraph Sistema Mercado Local
        uc1((Consultar catálogo))
        uc2((Buscar / filtrar produtos))
        uc3((Gerenciar cesta))
        uc4((Finalizar pedido))
        uc5((Calcular frete))
        uc6((Acompanhar pedido))
        uc7((Fazer login))
        uc8((Listar pedidos))
        uc9((Atualizar estado do pedido))
    end

    cliente --- uc1
    cliente --- uc2
    cliente --- uc3
    cliente --- uc4
    cliente --- uc6
    uc2 -. extend .-> uc1
    uc4 -. include .-> uc5

    admin --- uc7
    admin --- uc8
    admin --- uc9
    uc8 -. include .-> uc7
    uc9 -. include .-> uc7
```

### Especificação do caso de uso principal — UC4 Finalizar pedido

| Item | Descrição |
|---|---|
| Ator | Cliente |
| Pré-condição | A cesta tem pelo menos um produto |
| Fluxo principal | 1. Cliente preenche nome, e-mail, telefone, endereço, cidade e CEP. 2. Cliente clica em *Finalizar pedido*. 3. Sistema valida os dados. 4. Sistema confere o estoque de cada item. 5. Sistema calcula subtotal, frete (UC5) e total com os preços do banco. 6. Sistema grava o pedido, desconta o estoque e gera o código. 7. Sistema exibe o código e o total. |
| Fluxo alternativo 3a | Dado inválido: sistema exibe a mensagem indicando o campo e mantém o formulário preenchido. |
| Fluxo alternativo 4a | Estoque insuficiente: sistema informa o produto e a quantidade disponível. |
| Pós-condição | Pedido gravado com estado *Recebido*; cesta esvaziada. |

## Diagrama de classes (persistência)

```mermaid
classDiagram
    direction LR
    class Categoria {
        +int id
        +str nome
    }
    class Produto {
        +int id
        +str nome
        +str descricao
        +str produtor
        +str unidade
        +Decimal preco
        +int estoque
        +str icone
        +bool ativo
    }
    class Cliente {
        +int id
        +str nome
        +str email
        +str telefone
    }
    class Pedido {
        +int id
        +str codigo
        +datetime criado_em
        +EstadoPedido estado
        +str endereco
        +str cidade
        +str cep
        +Decimal subtotal
        +Decimal frete
        +Decimal total
    }
    class ItemPedido {
        +int id
        +int quantidade
        +Decimal preco_unitario
        +Decimal subtotal
    }
    class EstadoPedido {
        <<enumeration>>
        RECEBIDO
        EM_PREPARACAO
        SAIU_PARA_ENTREGA
        ENTREGUE
        CANCELADO
    }
    class Administrador {
        +int id
        +str email
        +str senha_hash
    }

    Categoria "1" --> "0..*" Produto
    Cliente "1" --> "0..*" Pedido
    Pedido "1" *-- "1..*" ItemPedido
    ItemPedido "0..*" --> "1" Produto
    Pedido ..> EstadoPedido
```

## Diagrama de sequência — Finalizar pedido

```mermaid
sequenceDiagram
    actor C as Cliente
    participant V as View (loja.js)
    participant Ctl as PedidoController
    participant S as PedidoService
    participant DB as PostgreSQL

    C->>V: clica em "Finalizar pedido"
    V->>V: valida campos do formulário
    V->>Ctl: POST /api/pedidos (cliente, endereço, itens)
    Ctl->>Ctl: valida o JSON (schema Pydantic)
    alt dados inválidos
        Ctl-->>V: 422 + lista de erros
        V-->>C: mostra mensagem por campo
    else dados válidos
        Ctl->>S: criar_pedido(entrada)
        S->>DB: SELECT produtos dos itens
        DB-->>S: produtos com preço e estoque
        alt estoque insuficiente
            S-->>Ctl: ErroDeNegocio
            Ctl-->>V: 400 "Estoque insuficiente…"
            V-->>C: mostra o erro
        else estoque ok
            S->>S: calcula subtotal e frete
            S->>DB: INSERT cliente/pedido/itens, UPDATE estoque
            DB-->>S: pedido gravado
            S-->>Ctl: pedido
            Ctl-->>V: 201 + código e totais
            V-->>C: exibe o código do pedido
        end
    end
```

## Diagrama de atividades — Ciclo de vida do pedido

```mermaid
stateDiagram-v2
    [*] --> Recebido: cliente finaliza
    Recebido --> EmPreparacao: produtor aceita
    Recebido --> Cancelado: produtor cancela
    EmPreparacao --> SaiuParaEntrega: cesta despachada
    EmPreparacao --> Cancelado: produtor cancela
    SaiuParaEntrega --> Entregue: cliente recebe
    Entregue --> [*]
    Cancelado --> [*]

    EmPreparacao: Em preparação
    SaiuParaEntrega: Saiu para entrega
```
