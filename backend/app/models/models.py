from database.database import engine
from sqlalchemy import Column, Integer, String , ForeignKey , Numeric , DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base


class Cliente(Base):
    __tablename__= "clientes"
    
    id = Column( Integer ,primary_key=True)
    nome = Column(String(100) , nullable=False)
    local_entrega = Column(String(250) , nullable=False)
    pedidos = relationship("Pedido", back_populates="cliente")
    
class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column( Integer ,primary_key=True)
    cliente_id = Column(ForeignKey("clientes.id") , nullable=False)
    preco = Column(Numeric(10 , 2) , nullable=False)
    status = Column(String(20) , server_default="pendente")
    criado_em = Column(DateTime, server_default=func.now())
    cliente = relationship("Cliente", back_populates="pedidos")  
    
class itensPedido(Base):
    pass

class Produto(Base):
    pass  
    
if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tabelas criadas com sucesso!")
    