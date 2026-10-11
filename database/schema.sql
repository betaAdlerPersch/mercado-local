-- Mercado Local - esquema físico do banco (PostgreSQL)
-- Arquivo gerado por scripts/gerar_schema_sql.py. Não edite à mão.

CREATE TYPE estado_pedido AS ENUM ('Recebido', 'Em preparação', 'Saiu para entrega', 'Entregue', 'Cancelado');

CREATE TABLE administradores (
	id SERIAL NOT NULL, 
	email VARCHAR(160) NOT NULL, 
	senha_hash VARCHAR(200) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);

CREATE TABLE categorias (
	id SERIAL NOT NULL, 
	nome VARCHAR(60) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
);

CREATE TABLE clientes (
	id SERIAL NOT NULL, 
	nome VARCHAR(120) NOT NULL, 
	email VARCHAR(160) NOT NULL, 
	telefone VARCHAR(30) NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_clientes_email ON clientes (email);

CREATE TABLE pedidos (
	id SERIAL NOT NULL, 
	codigo VARCHAR(12) NOT NULL, 
	cliente_id INTEGER NOT NULL, 
	criado_em TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	estado estado_pedido NOT NULL, 
	endereco VARCHAR(200) NOT NULL, 
	cidade VARCHAR(80) NOT NULL, 
	cep VARCHAR(9) NOT NULL, 
	subtotal NUMERIC(10, 2) NOT NULL, 
	frete NUMERIC(10, 2) NOT NULL, 
	total NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(cliente_id) REFERENCES clientes (id)
);

CREATE UNIQUE INDEX ix_pedidos_codigo ON pedidos (codigo);

CREATE TABLE produtos (
	id SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	descricao TEXT NOT NULL, 
	produtor VARCHAR(100) NOT NULL, 
	unidade VARCHAR(20) NOT NULL, 
	preco NUMERIC(10, 2) NOT NULL, 
	estoque INTEGER NOT NULL, 
	icone VARCHAR(10) NOT NULL, 
	ativo BOOLEAN NOT NULL, 
	categoria_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_produtos_preco_positivo CHECK (preco > 0), 
	CONSTRAINT ck_produtos_estoque_nao_negativo CHECK (estoque >= 0), 
	FOREIGN KEY(categoria_id) REFERENCES categorias (id)
);

CREATE TABLE itens_pedido (
	id SERIAL NOT NULL, 
	pedido_id INTEGER NOT NULL, 
	produto_id INTEGER NOT NULL, 
	quantidade INTEGER NOT NULL, 
	preco_unitario NUMERIC(10, 2) NOT NULL, 
	subtotal NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(pedido_id) REFERENCES pedidos (id) ON DELETE CASCADE, 
	FOREIGN KEY(produto_id) REFERENCES produtos (id)
);
