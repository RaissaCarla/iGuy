from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# O que a API exige receber para criar um usuário
class UsuarioCreate(BaseModel):
    nome_completo: str
    email: str
    senha: str
    cpf: str
    telefone: str
    tipo_perfil: str # 'CLIENTE' ou 'ACOMPANHANTE'

# O que a API devolve como resposta (sem a senha)
class UsuarioResponse(BaseModel):
    id_usuario: str
    nome_completo: str
    email: str
    tipo_perfil: str

    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    email: str
    senha: str

# O que o Cliente preenche ao pedir um acompanhante
class SolicitacaoCreate(BaseModel):
    id_categoria: int
    data_hora_agendada: datetime
    endereco_origem: str
    endereco_destino: Optional[str] = None
    valor_total: Optional[float] = None

# O que a API devolve ao mostrar os detalhes do serviço
class SolicitacaoResponse(BaseModel):
    id_solicitacao: str
    id_cliente: str
    id_acompanhante: Optional[str] = None
    id_categoria: int
    status: str
    data_hora_agendada: datetime
    endereco_origem: str
    endereco_destino: Optional[str] = None
    codigo_seguranca_pin: Optional[int] = None
    valor_total: Optional[float] = None

    class Config:
        from_attributes = True