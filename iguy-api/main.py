from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import database
import models
import schemas
import security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import random

app = FastAPI(
    title="iGuy API",
    description="API para o ecossistema de acompanhantes iGuy",
    version="1.0.0"
)

# =====================================================================
# CONFIGURAÇÕES DE SEGURANÇA (A CATRACA)
# =====================================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/")

def obter_usuario_logado(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """A Catraca: Lê o token e barra quem não estiver autenticado"""
    try:
        # Tenta abrir o token usando a mesma chave secreta
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        id_usuario: str = payload.get("sub")
        
        if id_usuario is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
            
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado ou inválido")
        
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
        
    return usuario


# =====================================================================
# ROTAS DO SISTEMA
# =====================================================================

@app.get("/")
def read_root():
    return {"mensagem": "Bem-vindo à API do iGuy!"}

@app.get("/teste-banco")
def testar_conexao(db: Session = Depends(database.get_db)):
    try:
        resultado = db.execute(text("SELECT DATABASE()")).fetchone()
        return {"status": "sucesso", "banco_conectado": resultado[0]}
    except Exception as e:
        return {"status": "erro", "detalhes": str(e)}

# --- ROTAS DE USUÁRIOS E LOGIN ---

@app.post("/usuarios/", response_model=schemas.UsuarioResponse)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(database.get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    novo_usuario = models.Usuario(
        nome_completo=usuario.nome_completo,
        email=usuario.email,
        senha_hash=security.get_password_hash(usuario.senha), 
        cpf=usuario.cpf,
        telefone=usuario.telefone,
        tipo_perfil=usuario.tipo_perfil
    )
    
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

@app.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == form_data.username).first()
    
    if not usuario or not security.verify_password(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Email ou senha incorretos"
        )
        
    token = security.criar_token_acesso(
        data={"sub": str(usuario.id_usuario), "perfil": usuario.tipo_perfil}
    )
    return {"access_token": token, "token_type": "bearer"}

@app.get("/meu-perfil/", response_model=schemas.UsuarioResponse)
def ler_perfil(usuario_atual: models.Usuario = Depends(obter_usuario_logado)):
    return usuario_atual


# --- ROTAS DE SOLICITAÇÕES (PEDIDOS) ---

@app.post("/solicitacoes/", response_model=schemas.SolicitacaoResponse)
def criar_solicitacao(
    solicitacao: schemas.SolicitacaoCreate,
    db: Session = Depends(database.get_db),
    usuario_atual: models.Usuario = Depends(obter_usuario_logado)
):
    pin_seguranca = random.randint(1000, 9999)

    nova_solicitacao = models.Solicitacao(
        id_cliente=usuario_atual.id_usuario,
        id_categoria=solicitacao.id_categoria,
        data_hora_agendada=solicitacao.data_hora_agendada,
        endereco_origem=solicitacao.endereco_origem,
        endereco_destino=solicitacao.endereco_destino,
        valor_total=solicitacao.valor_total,
        codigo_seguranca_pin=pin_seguranca,
        status="BUSCANDO"
    )

    db.add(nova_solicitacao)
    db.commit()
    db.refresh(nova_solicitacao)
    return nova_solicitacao

@app.get("/solicitacoes/disponiveis", response_model=list[schemas.SolicitacaoResponse])
def listar_solicitacoes_disponiveis(
    db: Session = Depends(database.get_db),
    usuario_atual: models.Usuario = Depends(obter_usuario_logado)
):
    if usuario_atual.tipo_perfil != "ACOMPANHANTE":
        raise HTTPException(status_code=403, detail="Apenas acompanhantes podem ver essa lista")

    return db.query(models.Solicitacao).filter(models.Solicitacao.status == "BUSCANDO").all()

@app.put("/solicitacoes/{id_solicitacao}/aceitar", response_model=schemas.SolicitacaoResponse)
def aceitar_solicitacao(
    id_solicitacao: str,
    db: Session = Depends(database.get_db),
    usuario_atual: models.Usuario = Depends(obter_usuario_logado)
):
    if usuario_atual.tipo_perfil != "ACOMPANHANTE":
        raise HTTPException(status_code=403, detail="Apenas acompanhantes podem aceitar solicitações")

    solicitacao = db.query(models.Solicitacao).filter(
        models.Solicitacao.id_solicitacao == id_solicitacao
    ).first()

    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if solicitacao.status != "BUSCANDO":
        raise HTTPException(status_code=400, detail="Essa solicitação já foi aceita ou cancelada")

    solicitacao.id_acompanhante = usuario_atual.id_usuario
    solicitacao.status = "ACEITO"

    db.commit()
    db.refresh(solicitacao)
    return solicitacao