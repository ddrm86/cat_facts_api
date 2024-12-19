from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
import pytest

from main import app, get_session


@pytest.fixture(name='session')
def session_fixture():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name='client')
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_cat_fact(client: TestClient):
    response = client.post('/cat_facts/', json={'description': 'Cats are great!'})
    assert response.status_code == 200
    data = response.json()
    assert data['description'] == 'Cats are great!'
    assert 'id' in data


def test_read_cat_facts(client: TestClient):
    # Crear dos hechos sobre gatos
    client.post('/cat_facts/', json={'description': 'Cats are great!'})
    client.post('/cat_facts/', json={'description': 'Cats are awesome!'})

    # Leer todos los hechos sobre gatos
    response = client.get('/cat_facts/')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['description'] == 'Cats are great!'
    assert data[1]['description'] == 'Cats are awesome!'


def test_read_cat_fact(client: TestClient):
    # Primero, crear un hecho sobre gatos
    response = client.post('/cat_facts/', json={'description': 'Cats are great!'})
    cat_fact_id = response.json()['id']

    # Luego, leer el hecho sobre gatos creado
    response = client.get(f'/cat_facts/{cat_fact_id}')
    assert response.status_code == 200
    data = response.json()
    assert data['description'] == 'Cats are great!'
    assert data['id'] == cat_fact_id


def test_read_nonexistent_cat_fact(client: TestClient):
    # Intentar leer un hecho sobre gatos con un ID que no existe
    response = client.get('/cat_facts/nonexistent_id')
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == 'Cat fact not found'


def test_update_cat_fact(client: TestClient):
    # Primero, crear un hecho sobre gatos
    response = client.post('/cat_facts/', json={'description': 'Cats are great!'})
    cat_fact_id = response.json()['id']

    # Luego, actualizar el hecho sobre gatos creado
    response = client.patch(f'/cat_facts/{cat_fact_id}', json={'description': 'Cats are awesome!'})
    assert response.status_code == 200
    data = response.json()
    assert data['description'] == 'Cats are awesome!'
    assert data['id'] == cat_fact_id


def test_delete_cat_fact(client: TestClient):
    # Primero, crear un hecho sobre gatos
    response = client.post('/cat_facts/', json={'description': 'Cats are great!'})
    cat_fact_id = response.json()['id']

    # Luego, eliminar el hecho sobre gatos creado
    response = client.delete(f'/cat_facts/{cat_fact_id}')
    assert response.status_code == 200
    data = response.json()
    assert data == {'ok': True}

    # Finalmente, intentar leer el hecho sobre gatos eliminado
    response = client.get(f'/cat_facts/{cat_fact_id}')
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == 'Cat fact not found'


def test_update_nonexistent_cat_fact(client: TestClient):
    # Intentar actualizar un hecho sobre gatos con un ID que no existe
    response = client.patch('/cat_facts/nonexistent_id', json={'description': 'Cats are awesome!'})
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == 'Cat fact not found'


def test_delete_nonexistent_cat_fact(client: TestClient):
    # Intentar eliminar un hecho sobre gatos con un ID que no existe
    response = client.delete('/cat_facts/nonexistent_id')
    assert response.status_code == 404
    data = response.json()
    assert data['detail'] == 'Cat fact not found'
