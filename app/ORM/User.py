from sqlalchemy import create_engine
from sqlmodel import Field, Session, SQLModel, create_engine, select, update
from typing import Optional
engine = create_engine("mariadb://root:your_password@localhost:3306/sample",echo=True)

class SampleTable(SQLModel, table=True):
    __tablename__ = 'sample_table'
    id: int = Field(primary_key=True)
    name: str
    age: int
    email: str
    password: str

def print_engine():
    with Session(engine) as session:
        statement = select(SampleTable).where(SampleTable.name =='sample')
        selected = session.exec(statement).first()
        print(selected)

def user_insert(user_info: SampleTable):
    with Session(engine) as session:
        session.add(user_info)
        session.commit()
        session.refresh(user_info)
        return 

def user_select(username):
    with Session(engine) as session:
        statement = select(SampleTable).where(SampleTable.name == username)
        user_info = session.exec(statement).first()
        print("-------userInfo--------")
        print(user_info)

    return user_info

def user_delete():
    return

def user_update(username,i_email,i_age):
    with Session(engine) as session:
        statement = update(SampleTable) \
            .where(SampleTable.name == username).values(
            email = i_email,
            age = i_age
        )
        session.exec(statement)
        session.commit()
        return 
        
