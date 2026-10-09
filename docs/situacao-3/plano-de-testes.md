# Plano de testes

## Estratégia

| Tipo | Objetivo | Como |
|---|---|---|
| **Unitário** (verificação) | Regras de negócio isoladas: frete, hash de senha | `tests/test_servicos.py` |
| **Integração** (verificação) | API + banco PostgreSQL real, do request à gravação | `tests/test_produtos.py`, `test_pedidos.py`, `test_admin.py`, `test_paginas.py` |
| **Aceitação com usuários** (validação) | Confirmar que o sistema atende quem vai usar | 5 testadores seguindo o roteiro abaixo e preenchendo o laudo |
| **Regressão** | Garantir que bugs corrigidos não voltem | Um teste novo para cada bug corrigido |

## Ambiente

- Banco de testes separado: `mercado_local_test` (criado pelo Docker Compose).
- Antes de cada teste o banco é limpo e repopulado (fixture `banco_limpo` em `tests/conftest.py`), então os testes são independentes entre si.
- Execução: `pytest` na raiz do projeto.

## Casos de teste automatizados

| ID | Caso | Requisito | Arquivo |
|---|---|---|---|
| CT01 | Lista os 12 produtos ativos com os campos esperados | RF01 | test_produtos |
| CT02 | Produtos em ordem alfabética | RF01 | test_produtos |
| CT03 | Filtro por categoria | RF03 | test_produtos |
| CT04 | Busca por nome / busca sem resultado | RF02 | test_produtos |
| CT05 | Pedido calcula subtotal, frete e total | RF06, RN01 | test_pedidos |
| CT06 | Preço enviado pelo navegador é ignorado | RNF05 | test_pedidos |
| CT07 | Frete grátis em pedido grande | RN01 | test_pedidos |
| CT08 | Itens repetidos são agrupados | RF04 | test_pedidos |
| CT09 | Recusa quantidade acima do estoque | RN02 | test_pedidos |
| CT10 | Recusa produto inexistente, cesta vazia, CEP, e-mail e endereço inválidos | RF06, RN08 | test_pedidos |
| CT11 | Cliente reaproveitado pelo e-mail | RN06 | test_pedidos |
| CT12 | Acompanhar pedido pelo código / código inexistente | RF08 | test_pedidos |
| CT13 | Rotas admin exigem login; senha errada; logout | RF09, RNF04 | test_admin |
| CT14 | Avançar estado, não pular etapas, cancelado é final, estado inválido | RF11, RN07 | test_admin |
| CT15 | Filtro de pedidos por estado | RF10 | test_admin |
| CT16 | Hash de senha confere, é único e resiste a hash malformado | RNF03 | test_servicos |
| CT17 | Páginas e arquivos estáticos carregam | RNF01 | test_paginas |

Resultado da última execução: *colar aqui a saída do `pytest` (ex.: `39 passed`)*.

## Roteiro para os testadores (validação)

Entregue o endereço do sistema e este roteiro a cada testador. Peça que testem **como usuários reais** e anotem tudo no [laudo](template-laudo-de-teste.md), com prints dos erros.

**Como cliente**
1. Procure produtos usando a busca e os filtros de categoria.
2. Monte uma cesta com produtos de categorias diferentes; use +, − e ✕.
3. Observe o frete: monte uma cesta abaixo e outra acima de R$ 150,00.
4. Finalize um pedido com dados válidos e anote o código.
5. Tente finalizar com dados inválidos (e-mail sem @, CEP curto, telefone estranho, cesta vazia).
6. Compre todas as unidades de um produto e veja o que acontece com o estoque.
7. Acompanhe o pedido pelo código.

**Como produtor** (passe o login de teste)
8. Entre na área do produtor e encontre o seu pedido.
9. Avance o pedido até *Entregue*; tente também cancelar outro pedido.
10. Use o filtro por estado.
11. Saia e confira se a área volta a pedir login.

**Livre**
12. Use no celular. Tente "quebrar" o sistema de qualquer forma que imaginar.
