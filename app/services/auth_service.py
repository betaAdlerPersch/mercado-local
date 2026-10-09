"""Autenticação do administrador com hash PBKDF2 (biblioteca padrão do Python)."""
import hashlib
import hmac
import secrets

from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Administrador

ITERACOES = 260_000


def gerar_hash(senha: str) -> str:
    sal = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal.encode(), ITERACOES).hex()
    return f"pbkdf2_sha256${ITERACOES}${sal}${digest}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        _, iteracoes, sal, digest = senha_hash.split("$")
    except ValueError:
        return False
    calculado = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal.encode(), int(iteracoes)).hex()
    return hmac.compare_digest(calculado, digest)


def autenticar(db: Session, email: str, senha: str) -> Administrador | None:
    admin = db.scalar(select(Administrador).where(Administrador.email == email.strip().lower()))
    if admin and verificar_senha(senha, admin.senha_hash):
        return admin
    return None


def exigir_admin(request: Request) -> int:
    """Dependência que bloqueia rotas administrativas sem login."""
    admin_id = request.session.get("admin_id")
    if not admin_id:
        raise HTTPException(status_code=401, detail="Faça login como administrador.")
    return admin_id
