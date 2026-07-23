import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

def get_password_hash(password: str) -> str:
    """Recebe a senha em texto puro e retorna o hash criptografado"""
    # O bcrypt exige que a senha seja convertida para formato de bytes ('utf-8')
    senha_bytes = password.encode('utf-8')
    
    # Gera o salt aleatório e cria o hash
    salt = bcrypt.gensalt()
    hash_criptografado = bcrypt.hashpw(senha_bytes, salt)
    
    # Converte o resultado de volta para string para o MySQL conseguir salvar
    return hash_criptografado.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha digitada bate com o hash salvo no banco"""
    senha_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(senha_bytes, hash_bytes)

# --- CONFIGURAÇÕES DO TOKEN DO IGUY ---
SECRET_KEY = "chave_secreta_super_segura_iguy_2026"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # O token expira em 1 hora

# ... (MANTENHA AQUI SUAS FUNÇÕES get_password_hash E verify_password) ...

def criar_token_acesso(data: dict):
    """Gera o token JWT com um tempo de expiração"""
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt