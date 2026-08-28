from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

url_conexao = "postgresql://fael:senha123@localhost:5432/estudo_db"

engine = create_engine(url_conexao)
Base = declarative_base()



