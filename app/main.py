"""Ponto de entrada da aplicação Mercado Local."""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.controllers import admin_controller, pagina_controller, pedido_controller, produto_controller

app = FastAPI(
    title="Mercado Local",
    description="Loja online de produtos de pequenos produtores rurais.",
    version="1.0.0",
)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax", max_age=8 * 3600)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent / "views" / "static"),
    name="static",
)

app.include_router(pagina_controller.router)
app.include_router(produto_controller.router)
app.include_router(pedido_controller.router)
app.include_router(admin_controller.router)


MENSAGENS_VALIDACAO = {
    "missing": "campo obrigatório",
    "string_too_short": "muito curto (mínimo {min_length} caracteres)",
    "string_too_long": "muito longo (máximo {max_length} caracteres)",
    "too_short": "deve ter pelo menos {min_length} item",
    "greater_than_equal": "deve ser no mínimo {ge}",
    "less_than_equal": "deve ser no máximo {le}",
    "int_parsing": "deve ser um número inteiro",
    "enum": "valor inválido",
}


@app.exception_handler(RequestValidationError)
async def erro_de_validacao(request: Request, exc: RequestValidationError):
    """Devolve os erros de validação em português, mantendo o formato padrão do FastAPI."""
    erros = []
    for erro in exc.errors():
        tipo = erro["type"]
        contexto = erro.get("ctx") or {}
        if tipo == "value_error":
            campo = erro["loc"][-1]
            mensagem = "e-mail inválido" if campo == "email" else str(contexto.get("error", erro["msg"]))
        else:
            modelo = MENSAGENS_VALIDACAO.get(tipo)
            mensagem = modelo.format(**contexto) if modelo else erro["msg"]
        erros.append({"loc": list(erro["loc"]), "msg": mensagem, "type": tipo})
    return JSONResponse(status_code=422, content={"detail": erros})


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}
