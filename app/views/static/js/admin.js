// Área do produtor: login, listagem de pedidos e mudança de estado.

const PROXIMOS_ESTADOS = {
    "Recebido": ["Em preparação", "Cancelado"],
    "Em preparação": ["Saiu para entrega", "Cancelado"],
    "Saiu para entrega": ["Entregue"],
    "Entregue": [],
    "Cancelado": [],
};

function mostrarPainel(logado) {
    document.getElementById("area-login").hidden = logado;
    document.getElementById("painel").hidden = !logado;
    if (logado) carregarPedidos();
}

async function entrar(evento) {
    evento.preventDefault();
    const erro = document.getElementById("erro-login");
    erro.textContent = "";
    const dados = Object.fromEntries(new FormData(evento.target));
    try {
        await api("/api/admin/login", { method: "POST", body: JSON.stringify(dados) });
        evento.target.reset();
        mostrarPainel(true);
    } catch (e) {
        erro.textContent = e.message;
    }
}

async function sair() {
    await api("/api/admin/logout", { method: "POST" });
    mostrarPainel(false);
}

async function carregarPedidos() {
    const filtro = document.getElementById("filtro-estado").value;
    const url = filtro ? `/api/admin/pedidos?estado=${encodeURIComponent(filtro)}` : "/api/admin/pedidos";
    try {
        const pedidos = await api(url);
        renderizarPedidos(pedidos);
    } catch (e) {
        if (e.message.includes("login")) {
            mostrarPainel(false);
        } else {
            avisar(e.message);
        }
    }
}

function renderizarPedidos(pedidos) {
    document.getElementById("sem-pedidos").hidden = pedidos.length > 0;
    document.getElementById("tabela-pedidos").innerHTML = pedidos
        .map((p) => {
            const proximos = PROXIMOS_ESTADOS[p.estado];
            const seletor = proximos.length
                ? `<select data-codigo="${escaparHtml(p.codigo)}" aria-label="Mudar estado do pedido ${escaparHtml(p.codigo)}">
                       <option value="">${escaparHtml(p.estado)}</option>
                       ${proximos.map((e) => `<option value="${e}">→ ${e}</option>`).join("")}
                   </select>`
                : `<span class="estado estado-${p.estado === "Entregue" ? "ok" : "cancelado"}">${escaparHtml(p.estado)}</span>`;
            return `
            <tr>
                <td><strong>${escaparHtml(p.codigo)}</strong></td>
                <td>${formatarData(p.criado_em)}</td>
                <td>${escaparHtml(p.cliente)}</td>
                <td>${p.itens.map((i) => `${i.quantidade}× ${escaparHtml(i.produto)}`).join("<br>")}</td>
                <td>${escaparHtml(p.endereco)}<br><small>${escaparHtml(p.cidade)} · ${escaparHtml(p.cep)}</small></td>
                <td class="num">${formatarMoeda(p.total)}</td>
                <td>${seletor}</td>
            </tr>`;
        })
        .join("");

    document.querySelectorAll("#tabela-pedidos select").forEach((select) => {
        select.addEventListener("change", () => mudarEstado(select.dataset.codigo, select.value));
    });
}

async function mudarEstado(codigo, novoEstado) {
    if (!novoEstado) return;
    try {
        await api(`/api/admin/pedidos/${encodeURIComponent(codigo)}/estado`, {
            method: "PATCH",
            body: JSON.stringify({ estado: novoEstado }),
        });
        avisar(`Pedido ${codigo}: ${novoEstado}`);
    } catch (e) {
        avisar(e.message);
    }
    carregarPedidos();
}

document.getElementById("form-login").addEventListener("submit", entrar);
document.getElementById("botao-sair").addEventListener("click", sair);
document.getElementById("filtro-estado").addEventListener("change", carregarPedidos);

if (!document.getElementById("painel").hidden) carregarPedidos();
