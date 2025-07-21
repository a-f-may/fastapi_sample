from sqlalchemy import create_engine
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
engine = create_engine("mariadb://root:your_password@localhost:3306/sample",echo=True)


def print_engine():
    print(engine)

def user_insert():
    user_1 = SampleTable(email="sample@ex.com",password="password")
    with Session(engine) as session:
        session.add(user_1)
        session.commit()
        session.refresh(user_1)
        return user_1

def user_select():
    return

def user_delete():
    return

def user_update():
    return
        
        
class SampleTable(SQLModel, table=True):
    __tablename__ = 'sample_table'
    id: int = Field(primary_key=True)
    name: str
    age: int
    email: str
    password: str