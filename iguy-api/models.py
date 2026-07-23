from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.sql import func
import uuid
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    # Usamos uuid4() para gerar aquele ID longo e seguro
    id_usuario = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome_completo = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    telefone = Column(String(20), nullable=False)
    tipo_perfil = Column(Enum('CLIENTE', 'ACOMPANHANTE'), nullable=False)
    data_criacao = Column(DateTime, default=func.now())