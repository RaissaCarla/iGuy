from pydantic import BaseModel

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