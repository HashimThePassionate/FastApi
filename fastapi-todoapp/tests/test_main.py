from fastapi.testclient import TestClient
from fastapi_todoapp.main import app, Todo, get_session
from sqlmodel import Session, SQLModel, create_engine
from fastapi import FastAPI
from fastapi_todoapp import settings
import pytest


connection_string = str(settings.TEST_DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)
engine = create_engine(connection_string, connect_args={
                       "sslmode": "require"}, pool_recycle=300, pool_size=10, echo=True)


@pytest.fixture(scope="module", autouse=True)
def get_db_session():
    SQLModel.metadata.create_all(engine)
    yield Session(engine)


@pytest.fixture(scope='function')
def test_app(get_db_session):
    def test_session():
        yield get_db_session
    app.dependency_overrides[get_session] = test_session
    with TestClient(app=app) as client:
        yield client


def test_home():
    client = TestClient(app=app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'message': 'Simple todo Application'}


def test_create_todoapp(test_app):
    # SQLModel.metadata.create_all(engine)
    # with Session(engine) as session:
    #     def get_session_override():
    #         return session
    #     app.dependency_overrides[get_session] = get_session_override
    #     client = TestClient(app=app)
    todo_content = "pytest"
    response = test_app.post("/create_todos/",
                             json={"content": todo_content}
                             )
    data = response.json()
    assert response.status_code == 200
    assert data["content"] == todo_content


def test_get_todoapp(test_app):
    # SQLModel.metadata.create_all(engine)
    # with Session(engine) as session:
    #     def get_session_override():
    #         return session
    #     app.dependency_overrides[get_session] = get_session_override
    #     client = TestClient(app=app)
    test_todo = {"content": "get_todo"}
    response = test_app.post("/create_todos/",
                             json=test_todo
                             )
    response = test_app.get("/get_todos/")
    new_todo = response.json()[-1]
    assert response.status_code == 200
    assert test_todo['content'] == new_todo['content']


def test_get_todo_by_id(test_app):
    # SQLModel.metadata.create_all(engine)
    # with Session(engine) as session:
    #     def get_session_override():
    #         return session
    #     app.dependency_overrides[get_session] = get_session_override
    #     client = TestClient(app=app)
    todo_data = {"content": "get todo by id"}
    response = test_app.post("/create_todos/", json=todo_data)
    todo_id = response.json()["id"]

    response = test_app.get(f"/get_todos/{todo_id}")
    data = response.json()
    assert response.status_code == 200
    assert data['content'] == todo_data['content']


def test_update_todo(test_app):
    # SQLModel.metadata.create_all(engine)
    # with Session(engine) as session:
    #     def get_session_override():
    #         return session
    #     app.dependency_overrides[get_session] = get_session_override
    # client = TestClient(app=app)
    todo_data = {"content": "Edit todo Todo"}
    response = test_app.post("/create_todos/", json=todo_data)
    todo_id = response.json()["id"]

    updated_data = {"content": "Updated Todo"}
    response = test_app.put(f"/update_todos/{todo_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["content"] == updated_data['content']


def test_delete_todo(test_app):
    # SQLModel.metadata.create_all(engine)
    # with Session(engine) as session:
    #     def get_session_override():
    #         return session
    #     app.dependency_overrides[get_session] = get_session_override
    #     client = TestClient(app=app)
    todo_data = {"content": "Delete Todo"}
    response = test_app.post("/create_todos/", json=todo_data)
    todo_id = response.json()["id"]

    response = test_app.delete(f"/delete_todos/{todo_id}")
    data = response.json()
    assert response.status_code == 200
    assert data["message"] == "Todo deleted successfully"
