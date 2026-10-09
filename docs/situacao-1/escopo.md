# Escopo

## Problema

Pequenos produtores rurais vendem principalmente em feiras de rua, o que limita o alcance a quem passa no local no dia e hora da feira. Do outro lado, muitos consumidores querem comprar produtos frescos e artesanais da região, mas não têm tempo de ir à feira.

## Objetivo

Oferecer uma loja online simples na qual o consumidor monta uma cesta com produtos de vários produtores e recebe tudo em casa, e o produtor acompanha e atualiza os pedidos.

## Público-alvo

- **Cliente:** consumidor urbano, de 25 a 60 anos, que valoriza alimentos frescos e compra pelo celular.
- **Produtor/administrador:** responsável pela cooperativa de produtores, que separa e despacha os pedidos.

## Dentro do escopo (versão 1.0)

- Catálogo com busca e filtro por categoria
- Cesta de compras com controle de estoque
- Checkout sem cadastro (identificação do cliente pelo e-mail)
- Cálculo de frete com regra de frete grátis
- Acompanhamento do pedido por código
- Área restrita com login para gerenciar pedidos e avançar seus estados

## Fora do escopo (evoluções futuras)

- Pagamento online (nesta versão o pagamento é feito na entrega)
- Cadastro de produtos pela interface (feito via script/banco)
- Conta do cliente com histórico de pedidos
- Cálculo de frete por distância/CEP
- Notificações por e-mail ou WhatsApp

## Premissas e restrições

- Atendimento a uma única região, com frete de valor fixo.
- Um único perfil de administrador (a cooperativa).
- Banco de dados relacional popular e de fácil manutenção: **PostgreSQL**.
- Código e documentação mantidos num único repositório Git.
