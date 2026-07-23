from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Substitua 'root' e 'suasenha' pelos dados de acesso do seu MySQL local
# Altere "suasenha" para a senha real que você configurou no banco
URL_BANCO_DADOS = "mysql+pymysql://root@localhost:3306/db_iGuy"

engine = create_engine(URL_BANCO_DADOS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Função que gerencia a sessão com o banco para cada requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()