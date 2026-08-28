from database.database import engine
from models.models import Cliente , Pedido
from sqlalchemy.orm import sessionmaker 

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# cliente_generico = Cliente(nome="ana" , local_entrega="campinas do sul")
# session.add(cliente_generico)
# session.commit()

pedido_generico = Pedido(cliente_id=1 , preco=10.50)
session.add(pedido_generico)
session.commit()

pedido = session.query(Pedido).first()


print(pedido.id , pedido.preco , pedido.cliente.nome ,pedido.cliente.pedidos)