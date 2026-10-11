# 🧺 Mercado Local

[![Testes](../../actions/workflows/testes.yml/badge.svg)](../../actions/workflows/testes.yml)

**🌐 Aplicação online:** *adicionar aqui o link do Render*

Loja online que conecta pequenos produtores rurais a consumidores da região. O cliente monta uma cesta de produtos frescos (hortifrúti, laticínios e empório), informa o endereço e acompanha a entrega por um código. O produtor gerencia os pedidos numa área restrita.

> Projeto Integrador Transdisciplinar em Engenharia de Software II — Cruzeiro do Sul Virtual.

## Funcionalidades

**Cliente**
- Catálogo com busca por nome e filtro por categoria
- Cesta com controle de quantidade, respeitando o estoque
- Cálculo de frete (grátis a partir de R$ 150,00)
- Finalização do pedido com validação de dados (e-mail, CEP)
- Acompanhamento do pedido pelo código (ex.: `ML-4F2A9C`)

**Produtor (administrador)**
- Login com senha protegida por hash (PBKDF2)
- Lista de pedidos com filtro por estado
- Avanço do pedido pelo fluxo `Recebido → Em preparação → Saiu para entrega → Entregue` (ou `Cancelado`), sem permitir pular etapas

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3.12+, FastAPI, SQLAlchemy 2 |
| Banco de dados | PostgreSQL 16 |
| Front-end | HTML, CSS e JavaScript puro, templates Jinja2 |
| Testes | pytest + TestClient do FastAPI |
| Infra local | Docker Compose |

## Arquitetura (MVC)

```
app/
├── models/        → MODEL: entidades e mapeamento do banco (SQLAlchemy)
├── views/         → VIEW: templates HTML, CSS e JavaScript
├── controllers/   → CONTROLLER: rotas HTTP, recebem a requisição e chamam os services
├── services/      → regras de negócio (frete, estoque, transições de estado, autenticação)
├── schemas/       → validação de entrada e formato de saída (Pydantic)
├── config.py      → configurações via variáveis de ambiente
└── main.py        → montagem da aplicação
```

Detalhes em [docs/situacao-2/arquitetura.md](docs/situacao-2/arquitetura.md).

## Como executar

Pré-requisitos: Python 3.12+ e Docker.

```bash
# 1. Suba o PostgreSQL (cria também o banco de testes)
docker compose up -d

# 2. Crie o ambiente virtual e instale as dependências
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure as variáveis de ambiente
cp .env.example .env             # Windows: copy .env.example .env

# 4. Crie as tabelas e os dados iniciais
python -m scripts.init_db

# 5. Rode a aplicação
uvicorn app.main:app --reload
```

| Endereço | O que é |
|---|---|
| http://localhost:8000 | Loja |
| http://localhost:8000/acompanhar | Acompanhar pedido |
| http://localhost:8000/admin | Área do produtor (`admin@mercadolocal.com` / `admin123`) |
| http://localhost:8000/docs | Documentação interativa da API (Swagger) |

Para recomeçar com o banco zerado: `python -m scripts.init_db --reset`.

## Testes

```bash
pytest
```

Os testes usam o banco `mercado_local_test` (criado pelo Docker Compose) e cobrem catálogo, criação de pedidos, cálculo de valores, validações, autenticação e fluxo de estados. Plano completo em [docs/situacao-3/plano-de-testes.md](docs/situacao-3/plano-de-testes.md).

A cada `push` no GitHub, os testes rodam automaticamente no **GitHub Actions** com um PostgreSQL real (aba *Actions* do repositório).

## Deploy (Render)

O arquivo [`render.yaml`](render.yaml) descreve a infraestrutura: um serviço web Python e um banco PostgreSQL, ambos no plano gratuito.

1. Crie uma conta em [render.com](https://render.com) entrando com o GitHub.
2. No painel, clique em **New → Blueprint** e escolha este repositório.
3. Informe a senha do administrador (`ADMIN_PASSWORD`) quando o Render pedir.
4. Clique em **Apply**. O Render cria o banco, instala as dependências, cria as tabelas e publica o site.

Cada novo `push` na branch `main` gera um novo deploy automaticamente.

> No plano gratuito, o serviço "dorme" depois de alguns minutos sem acesso; o primeiro acesso seguinte demora cerca de um minuto para acordar.

## Documentação do projeto

| Situação | Conteúdo |
|---|---|
| [Situação 1 — Planejamento](docs/situacao-1/) | Escopo, requisitos, UML, IHC, projeto do banco e dicionário de dados |
| [Situação 2 — Desenvolvimento](docs/situacao-2/) | Arquitetura, API e manual de uso |
| [Situação 3 — Testes e validação](docs/situacao-3/) | Plano de testes, template de laudo, laudos dos testadores e relatório de correções |

O esquema físico do banco está em [database/schema.sql](database/schema.sql), gerado a partir dos models com `python -m scripts.gerar_schema_sql`.

## Autor

William — [github.com/WilliamLoey](https://github.com/WilliamLoey)
