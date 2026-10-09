// Página de acompanhamento de pedido pelo código.

const ETAPAS = ["Recebido", "Em preparação", "Saiu para entrega", "Entregue"];

function renderizarPedido(pedido) {
    const indiceAtual = ETAPAS.indexOf(pedido.estado);
    const linhaDoTempo =
        pedido.estado === "Cancelado"
            ? `<p class="estado-cancelado">Este pedido foi cancelado.</p>`
            : `<ol class="linha-tempo">${ETAPAS.map(
                  (etapa, i) =>
                      `<li class="${i < indiceAtual ? "feito" : i === indiceAtual ? "atual" : ""}">${etapa}</li>`
              ).join("")}</ol>`;

    document.getElementById("resultado").innerHTML = `
        <article class="cartao-pedido">
            <header>
                <h2>${escaparHtml(pedido.codigo)}</h2>
                <span>${formatarData(pedido.criado_em)}</span>
            </header>
            ${linhaDoTempo}
            <ul class="lista-itens">
                ${pedido.itens
                    .map(
                        (i) => `<li><span>${i.quantidade}× ${escaparHtml(i.produto)}</span>
                                <span>${formatarMoeda(i.subtotal)}</span></li>`
                    )
                    .join("")}
            </ul>
            <dl class="resumo">
                <div><dt>Subtotal</dt><dd>${formatarMoeda(pedido.subtotal)}</dd></div>
                <div><dt>Frete</dt><dd>${pedido.frete === 0 ? "Grátis" : formatarMoeda(pedido.frete)}</dd></div>
                <div class="resumo-total"><dt>Total</dt><dd>${formatarMoeda(pedido.total)}</dd></div>
            </dl>
            <p class="entrega">Entrega: ${escaparHtml(pedido.endereco)}, ${escaparHtml(pedido.cidade)} · ${escaparHtml(pedido.cep)}</p>
        </article>`;
}

async function consultar(codigo) {
    const erro = document.getElementById("erro-acompanhar");
    erro.textContent = "";
    document.getElementById("resultado").innerHTML = "";
    try {
        renderizarPedido(await api(`/api/pedidos/${encodeURIComponent(codigo)}`));
    } catch (e) {
        erro.textContent = e.message;
    }
}

document.getElementById("form-acompanhar").addEventListener("submit", (e) => {
    e.preventDefault();
    const codigo = document.getElementById("codigo").value.trim();
    if (codigo) consultar(codigo);
});

const codigoNaUrl = new URLSearchParams(location.search).get("codigo");
if (codigoNaUrl) {
    document.getElementById("codigo").value = codigoNaUrl;
    consultar(codigoNaUrl);
}
