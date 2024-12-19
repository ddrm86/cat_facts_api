import uuid
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select


def generate_uuid():
    return str(uuid.uuid4())

class CatFactBase(SQLModel):
    description: str = Field(index=True)

class CatFact(CatFactBase, table=True):
    id: str | None = Field(default_factory=generate_uuid, primary_key=True)

class CatFactPublic(CatFactBase):
    id: str

class CatFactCreate(CatFactBase):
    pass

class CatFactUpdate(CatFactBase):
    description: str | None = None

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

CAT_FACT_NOT_FOUND_MSG: str = 'Cat fact not found'

@app.on_event('startup')
def on_startup():
    create_db_and_tables()

@app.post('/cat_facts/', response_model=CatFactPublic)
def create_cat_fact(cat_fact: CatFactCreate, session: SessionDep) -> CatFact:
    db_fact = CatFact.model_validate(cat_fact)
    session.add(db_fact)
    session.commit()
    session.refresh(db_fact)
    return db_fact

@app.get('/cat_facts/', response_model=list[CatFactPublic])
def read_cat_facts(session: SessionDep):
    cat_facts = session.exec(select(CatFact)).all()
    return cat_facts

@app.get('/cat_facts/{cat_fact_id}', response_model=CatFactPublic)
def read_cat_fact(cat_fact_id: str, session: SessionDep):
    cat_fact = session.get(CatFact, cat_fact_id)
    if not cat_fact:
        raise HTTPException(status_code=404, detail=CAT_FACT_NOT_FOUND_MSG)
    return cat_fact

@app.patch('/cat_facts/{cat_fact_id}', response_model=CatFactPublic)
def update_cat_fact(cat_fact_id: str, cat_fact: CatFactUpdate, session: SessionDep):
    db_fact = session.get(CatFact, cat_fact_id)
    if not db_fact:
        raise HTTPException(status_code=404, detail=CAT_FACT_NOT_FOUND_MSG)
    cat_fact_data = cat_fact.model_dump(exclude_unset=True)
    db_fact.sqlmodel_update(cat_fact_data)
    session.add(db_fact)
    session.commit()
    session.refresh(db_fact)
    return db_fact

@app.delete('/cat_facts/{cat_fact_id}')
def delete_cat_fact(cat_fact_id: str, session: SessionDep):
    cat_fact = session.get(CatFact, cat_fact_id)
    if not cat_fact:
        raise HTTPException(status_code=404, detail=CAT_FACT_NOT_FOUND_MSG)
    session.delete(cat_fact)
    session.commit()
    return {'ok': True}
