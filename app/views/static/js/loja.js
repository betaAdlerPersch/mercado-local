// Página da loja: catálogo, filtros, cesta e finalização do pedido.

const estado = {
    produtos: [],
    categoriaSelecionada: null,
    cesta: carregarCesta(), // { [produtoId]: quantidade }
};

// ---------- Persistência da cesta ----------

function carregarCesta() {
    try {
        return JSON.parse(localStorage.getItem("cesta")) || {};
    } catch {
        return {};
    }
}

function salvarCesta() {
    try {
        localStorage.setItem("cesta", JSON.stringify(estado.cesta));
    } catch {
        // navegação privada: a cesta só não é lembrada
    }
}

// ---------- Catálogo ----------

async function carregarCategorias() {
    const categorias = await api("/api/categorias");
    const filtros = document.getElementById("filtros");
    const botoes = [{ id: null, nome: "Todos" }, ...categorias].map((categoria) => {
        const botao = document.createElement("button");
        botao.type = "button";
        botao.className = "filtro";
        botao.textContent = categoria.nome;
        botao.setAttribute("aria-pressed", categoria.id === estado.categoriaSelecionada);
        botao.addEventListener("click", () => {
            estado.categoriaSelecionada = categoria.id;
            filtros.querySelectorAll(".filtro").forEach((b) => b.setAttribute("aria-pressed", "false"));
            botao.setAttribute("aria-pressed", "true");
            carregarProdutos();
        });
        return botao;
    });
    filtros.replaceChildren(...botoes);
}

async function carregarProdutos() {
    const parametros = new URLSearchParams();
    const busca = document.getElementById("busca").value.trim();
    if (busca) parametros.set("busca", busca);
    if (estado.categoriaSelecionada) parametros.set("categoria_id", estado.categoriaSelecionada);

    const container = document.getElementById("produtos");
    try {
        estado.produtos = await api(`/api/produtos?${parametros}`);
        renderizarProdutos();
        renderizarCesta();
    } catch (erro) {
        container.innerHTML = `<p class="erro">Não foi possível carregar os produtos. ${escaparHtml(erro.message)}</p>`;
    }
}

function renderizarProdutos() {
    const container = document.getElementById("produtos");
    if (estado.produtos.length === 0) {
        container.innerHTML = `<p class="vazio">Nenhum produto encontrado.</p>`;
        return;
    }
    container.innerHTML = estado.produtos
        .map((p) => {
            const esgotado = p.estoque === 0;
            return `
            <article class="card-produto">
                <div class="card-icone" aria-hidden="true">${p.icone}</div>
                <div class="card-corpo">
                    <span class="etiqueta">${escaparHtml(p.categoria)}</span>
                    <h3>${escaparHtml(p.nome)}</h3>
                    <p class="produtor">${escaparHtml(p.produtor)}</p>
                    <p class="descricao">${escaparHtml(p.descricao)}</p>
                </div>
                <div class="card-rodape">
                    <div>
                        <strong class="preco">${formatarMoeda(p.preco)}</strong>
                        <span class="unidade">/ ${escaparHtml(p.unidade)}</span>
                        <span class="estoque">${esgotado ? "Esgotado" : `${p.estoque} disponíveis`}</span>
                    </div>
                    <button type="button" class="botao-adicionar" data-id="${p.id}" ${esgotado ? "disabled" : ""}>
                        Adicionar
                    </button>
                </div>
            </article>`;
        })
        .join("");

    container.querySelectorAll(".botao-adicionar").forEach((botao) => {
        botao.addEventListener("click", () => adicionarNaCesta(Number(botao.dataset.id)));
    });
}

// ---------- Cesta ----------

function buscarProduto(id) {
    return estado.produtos.find((p) => p.id === id) || estado.cacheProdutos?.[id];
}

function adicionarNaCesta(id) {
    const produto = buscarProduto(id);
    const atual = estado.cesta[id] || 0;
    if (produto && atual >= produto.estoque) {
        avisar(`Só temos ${produto.estoque} unidade(s) de ${produto.nome}.`);
        return;
    }
    estado.cesta[id] = atual + 1;
    salvarCesta();
    renderizarCesta();
    if (produto) avisar(`${produto.nome} adicionado à cesta.`);
}

function aumentar(id) {
    adicionarNaCesta(id);
}

function diminuir(id) {
    const novaQuantidade = (estado.cesta[id] || 0) - 1;
    if (novaQuantidade <= 0) {
        delete estado.cesta[id];
    } else {
        estado.cesta[id] = novaQuantidade;
    }
    salvarCesta();
    renderizarCesta();
}

function remover(id) {
    delete estado.cesta[id];
    salvarCesta();
    renderizarCesta();
}

function calcularFrete(subtotal) {
    if (subtotal === 0) return 0;
    return subtotal >= window.CONFIG_FRETE.gratisAPartirDe ? 0 : window.CONFIG_FRETE.valor;
}

function renderizarCesta() {
    // Guarda os produtos já vistos para a cesta continuar funcionando com filtros ativos
    estado.cacheProdutos = estado.cacheProdutos || {};
    estado.produtos.forEach((p) => (estado.cacheProdutos[p.id] = p));

    const lista = document.getElementById("itens-carrinho");
    const ids = Object.keys(estado.cesta).map(Number);
    let subtotal = 0;

    lista.innerHTML = ids
        .map((id) => {
            const produto = buscarProduto(id);
            if (!produto) return "";
            const quantidade = estado.cesta[id];
            subtotal += produto.preco * quantidade;
            return `
            <li class="item-carrinho">
                <span class="item-icone" aria-hidden="true">${produto.icone}</span>
                <div class="item-info">
                    <strong>${escaparHtml(produto.nome)}</strong>
                    <span>${formatarMoeda(produto.preco)} / ${escaparHtml(produto.unidade)}</span>
                </div>
                <div class="quantidade" role="group" aria-label="Quantidade de ${escaparHtml(produto.nome)}">
                    <button type="button" onclick="diminuir(${id})" aria-label="Diminuir">−</button>
                    <span>${quantidade}</span>
                    <button type="button" onclick="aumentar(${id})" aria-label="Aumentar">+</button>
                </div>
                <button type="button" class="remover" onclick="remover(${id})" aria-label="Remover ${escaparHtml(produto.nome)}">✕</button>
            </li>`;
        })
        .join("");

    const frete = calcularFrete(subtotal);
    document.getElementById("carrinho-vazio").hidden = ids.length > 0;
    document.getElementById("subtotal").textContent = formatarMoeda(subtotal);
    document.getElementById("frete").textContent =
        subtotal === 0 ? "—" : frete === 0 ? "Grátis" : formatarMoeda(frete);
    document.getElementById("total").textContent = formatarMoeda(subtotal + frete);
}

// ---------- Finalização ----------

async function finalizarPedido(evento) {
    evento.preventDefault();
    const formulario = evento.target;
    const erro = document.getElementById("erro-pedido");
    const botao = document.getElementById("botao-finalizar");
    erro.textContent = "";

    const itens = Object.entries(estado.cesta).map(([id, quantidade]) => ({
        produto_id: Number(id),
        quantidade,
    }));
    if (itens.length === 0) {
        erro.textContent = "Adicione pelo menos um produto à cesta.";
        return;
    }
    if (!formulario.checkValidity()) {
        formulario.reportValidity();
        return;
    }

    const dados = Object.fromEntries(new FormData(formulario));
    const corpo = {
        cliente: { nome: dados.nome.trim(), email: dados.email.trim(), telefone: dados.telefone.trim() },
        endereco: dados.endereco.trim(),
        cidade: dados.cidade.trim(),
        cep: dados.cep.trim(),
        itens,
    };

    botao.disabled = true;
    botao.textContent = "Enviando…";
    try {
        const pedido = await api("/api/pedidos", { method: "POST", body: JSON.stringify(corpo) });
        estado.cesta = {};
        salvarCesta();
        formulario.reset();
        await carregarProdutos();
        mostrarConfirmacao(pedido);
    } catch (e) {
        erro.textContent = e.message;
    } finally {
        botao.disabled = false;
        botao.textContent = "Finalizar pedido";
    }
}

function mostrarConfirmacao(pedido) {
    document.getElementById("codigo-pedido").textContent = pedido.codigo;
    document.getElementById("resumo-confirmacao").textContent =
        `Total: ${formatarMoeda(pedido.total)} (frete ${pedido.frete === 0 ? "grátis" : formatarMoeda(pedido.frete)})`;
    document.getElementById("link-acompanhar").href = `/acompanhar?codigo=${encodeURIComponent(pedido.codigo)}`;
    document.getElementById("confirmacao").showModal();
}

// Máscara simples de CEP: 00000-000
document.querySelector("input[name=cep]").addEventListener("input", (e) => {
    const digitos = e.target.value.replace(/\D/g, "").slice(0, 8);
    e.target.value = digitos.length > 5 ? `${digitos.slice(0, 5)}-${digitos.slice(5)}` : digitos;
});

let temporizadorBusca;
document.getElementById("busca").addEventListener("input", () => {
    clearTimeout(temporizadorBusca);
    temporizadorBusca = setTimeout(carregarProdutos, 300);
});

document.getElementById("form-pedido").addEventListener("submit", finalizarPedido);

carregarCategorias();
carregarProdutos();
