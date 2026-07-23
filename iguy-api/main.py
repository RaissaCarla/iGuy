from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import database
import models
import schemas
import security

app = FastAPI(
    title="iGuy API",
    description="API para o ecossistema de acompanhantes iGuy",
    version="1.0.0"
)

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

# --- NOVA ROTA DE CADASTRO ---
@app.post("/usuarios/", response_model=schemas.UsuarioResponse)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(database.get_db)):
    # 1. Verifica se o email já está cadastrado
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    # 2. Cria o novo usuário com a senha criptografada
    novo_usuario = models.Usuario(
        nome_completo=usuario.nome_completo,
        email=usuario.email,
        # A mágica acontece na linha abaixo:
        senha_hash=security.get_password_hash(usuario.senha), 
        cpf=usuario.cpf,
        telefone=usuario.telefone,
        tipo_perfil=usuario.tipo_perfil
    )
    
    # 3. Salva no banco de dados
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    return novo_usuario

@app.post("/login/")
def login(usuario_login: schemas.UsuarioLogin, db: Session = Depends(database.get_db)):
    # 1. Busca o usuário no banco
    usuario = db.query(models.Usuario).filter(models.Usuario.email == usuario_login.email).first()
    
    # 2. Se não achar o email, ou se a senha do bcrypt não bater, bloqueia
    if not usuario or not security.verify_password(usuario_login.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Email ou senha incorretos"
        )
        
    # 3. Sucesso! Gera o token guardando o ID e o Perfil (Cliente ou Acompanhante)
    token = security.criar_token_acesso(
        data={"sub": str(usuario.id_usuario), "perfil": usuario.tipo_perfil}
    )
    
    return {"access_token": token, "token_type": "bearer"}