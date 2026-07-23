from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Text, Numeric, SmallInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
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

class CategoriaServico(Base):
    __tablename__ = "categorias_servico"
    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)
    preco_base_hora = Column(Numeric(10, 2), nullable=False)
    
class Solicitacao(Base):
    __tablename__ = "solicitacoes"

    id_solicitacao = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    id_cliente = Column(String(36), ForeignKey("usuarios.id_usuario"), nullable=False)
    id_acompanhante = Column(String(36), ForeignKey("usuarios.id_usuario"), nullable=True)
    id_categoria = Column(Integer, ForeignKey("categorias_servico.id_categoria"), nullable=False)
    status = Column(String(30), default="BUSCANDO") # BUSCANDO, ACEITO, EM_ANDAMENTO, CONCLUIDO, CANCELADO
    data_hora_agendada = Column(DateTime, nullable=False)
    endereco_origem = Column(String(255), nullable=False)
    endereco_destino = Column(String(255), nullable=True)
    codigo_seguranca_pin = Column(SmallInteger, nullable=True)
    valor_total = Column(Numeric(10, 2), nullable=True)
    data_criacao = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    cliente = relationship("Usuario", foreign_keys=[id_cliente])
    acompanhante = relationship("Usuario", foreign_keys=[id_acompanhante])