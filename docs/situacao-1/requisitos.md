# Requisitos

## Requisitos funcionais

| ID | Requisito | Ator |
|---|---|---|
| RF01 | Listar os produtos ativos com nome, produtor, preço, unidade e estoque | Cliente |
| RF02 | Buscar produtos pelo nome | Cliente |
| RF03 | Filtrar produtos por categoria | Cliente |
| RF04 | Adicionar, aumentar, diminuir e remover produtos da cesta | Cliente |
| RF05 | Exibir subtotal, frete e total da cesta em tempo real | Cliente |
| RF06 | Finalizar o pedido informando nome, e-mail, telefone, endereço, cidade e CEP | Cliente |
| RF07 | Gerar um código único para cada pedido | Sistema |
| RF08 | Consultar o pedido e seu estado pelo código | Cliente |
| RF09 | Autenticar o administrador com e-mail e senha | Administrador |
| RF10 | Listar os pedidos, do mais recente para o mais antigo, com filtro por estado | Administrador |
| RF11 | Avançar ou cancelar um pedido seguindo o fluxo de estados | Administrador |

## Requisitos não funcionais

| ID | Requisito | Categoria |
|---|---|---|
| RNF01 | Interface responsiva, utilizável em telas a partir de 360 px de largura | Usabilidade |
| RNF02 | Mensagens de erro claras, em português, indicando o campo com problema | Usabilidade |
| RNF03 | Senhas armazenadas apenas como hash com sal (PBKDF2-SHA256) | Segurança |
| RNF04 | Rotas administrativas acessíveis somente com sessão autenticada | Segurança |
| RNF05 | Preços e totais calculados no servidor, nunca aceitos do navegador | Segurança/Integridade |
| RNF06 | Valores monetários armazenados como `NUMERIC(10,2)`, sem ponto flutuante | Integridade |
| RNF07 | Código organizado em MVC, com regras de negócio isoladas em *services* | Manutenibilidade |
| RNF08 | Testes automatizados executáveis com um único comando (`pytest`) | Manutenibilidade |
| RNF09 | Listagem de produtos respondida em menos de 500 ms com até 1.000 produtos | Desempenho |
| RNF10 | Elementos interativos acessíveis por teclado e com rótulos para leitores de tela | Acessibilidade |

## Regras de negócio

| ID | Regra |
|---|---|
| RN01 | O frete custa R$ 12,00 e é **grátis para pedidos a partir de R$ 150,00** (subtotal). |
| RN02 | Não é possível pedir quantidade maior que o estoque disponível do produto. |
| RN03 | Ao confirmar o pedido, o estoque de cada produto é reduzido na quantidade vendida. |
| RN04 | Cada item do pedido deve ter quantidade entre 1 e 50. |
| RN05 | O preço unitário gravado no item é o preço do produto no momento da compra. |
| RN06 | Clientes são identificados pelo e-mail; um novo pedido com o mesmo e-mail atualiza nome e telefone. |
| RN07 | Fluxo de estados: `Recebido → Em preparação → Saiu para entrega → Entregue`. Um pedido pode ser cancelado enquanto estiver *Recebido* ou *Em preparação*. *Entregue* e *Cancelado* são finais. |
| RN08 | O telefone deve conter DDD e número (10 ou 11 dígitos); o CEP deve ter 8 dígitos. |
