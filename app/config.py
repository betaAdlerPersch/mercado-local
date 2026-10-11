"""Configurações da aplicação, lidas de variáveis de ambiente ou do arquivo .env."""
from decimal import Decimal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://mercado:mercado@localhost:5432/mercado_local"

    @field_validator("database_url")
    @classmethod
    def usar_driver_psycopg(cls, url: str) -> str:
        """Serviços como o Render fornecem 'postgres://' ou 'postgresql://';
        o SQLAlchemy precisa do driver explícito 'postgresql+psycopg://'."""
        for prefixo in ("postgres://", "postgresql://"):
            if url.startswith(prefixo):
                return "postgresql+psycopg://" + url[len(prefixo):]
        return url
    secret_key: str = "troque-esta-chave-em-producao"

    admin_email: str = "admin@mercadolocal.com"
    admin_password: str = "admin123"

    # Regras de negócio do frete (valores em reais)
    valor_frete: Decimal = Decimal("12.00")
    frete_gratis_a_partir_de: Decimal = Decimal("150.00")


settings = Settings()
