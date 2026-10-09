from pydantic import BaseModel, ConfigDict


class ProdutoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str
    produtor: str
    unidade: str
    preco: float
    estoque: int
    icone: str
    categoria: str


class CategoriaSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
