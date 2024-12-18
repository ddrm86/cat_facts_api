import uuid
from typing import Annotated, Type, Sequence
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

def generate_uuid():
    return str(uuid.uuid4())

class CatFact(SQLModel, table=True):
    id: str | None = Field(default_factory=generate_uuid, primary_key=True)
    description: str = Field(index=True)

sqlite_file_name = 'cat_facts.db'
sqlite_url = f'sqlite:///{sqlite_file_name}'

connect_args = {'check_same_thread': False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.on_event('startup')
def on_startup():
    create_db_and_tables()

@app.post('/cat_facts/')
def create_cat_fact(cat_fact: CatFact, session: SessionDep) -> CatFact:
    session.add(cat_fact)
    session.commit()
    session.refresh(cat_fact)
    return cat_fact

@app.get('/cat_facts/')
def read_cat_facts(session: SessionDep) -> Sequence[CatFact]:
    cat_facts = session.exec(select(CatFact)).all()
    return cat_facts

@app.get('/cat_facts/{cat_fact_id}')
def read_cat_fact(cat_fact_id: str, session: SessionDep) -> CatFact:
    cat_fact = session.get(CatFact, cat_fact_id)
    if not cat_fact:
        raise HTTPException(status_code=404, detail='Cat fact not found')
    return cat_fact

@app.delete('/cat_facts/{cat_fact_id}')
def delete_cat_fact(cat_fact_id: str, session: SessionDep):
    cat_fact = session.get(CatFact, cat_fact_id)
    if not cat_fact:
        raise HTTPException(status_code=404, detail='Cat fact not found')
    session.delete(cat_fact)
    session.commit()
    return {'ok': True}
