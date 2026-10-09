// Funções compartilhadas por todas as páginas.

const moeda = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

function formatarMoeda(valor) {
    return moeda.format(valor);
}

function formatarData(iso) {
    return new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function escaparHtml(texto) {
    const div = document.createElement("div");
    div.textContent = String(texto);
    return div.innerHTML;
}

let temporizadorAviso;
function avisar(mensagem) {
    const aviso = document.getElementById("aviso");
    aviso.textContent = mensagem;
    aviso.classList.add("visivel");
    clearTimeout(temporizadorAviso);
    temporizadorAviso = setTimeout(() => aviso.classList.remove("visivel"), 2500);
}

// Faz uma requisição à API e transforma erros em mensagens legíveis.
async function api(url, opcoes = {}) {
    const resposta = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...opcoes,
    });
    let corpo = null;
    try {
        corpo = await resposta.json();
    } catch {
        corpo = null;
    }
    if (!resposta.ok) {
        throw new Error(extrairMensagemDeErro(corpo, resposta.status));
    }
    return corpo;
}

function extrairMensagemDeErro(corpo, status) {
    if (!corpo || !corpo.detail) {
        return `Erro inesperado (${status}). Tente novamente.`;
    }
    if (typeof corpo.detail === "string") {
        return corpo.detail;
    }
    // Erros de validação do FastAPI chegam como lista
    const nomesCampos = {
        nome: "Nome", email: "E-mail", telefone: "Telefone", endereco: "Endereço",
        cidade: "Cidade", cep: "CEP", itens: "Cesta", quantidade: "Quantidade",
    };
    return corpo.detail
        .map((erro) => {
            const campo = erro.loc[erro.loc.length - 1];
            const rotulo = nomesCampos[campo] || campo;
            return `${rotulo}: ${erro.msg}`;
        })
        .join(" · ");
}
