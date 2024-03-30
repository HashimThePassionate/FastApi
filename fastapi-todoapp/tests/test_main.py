from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
import pytest
from main import app, Todo, get_session
from settings import DATABASE_URL, TEST_DATABASE_URL

# Test cases
client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"title": "Hello World"}

def test_create_todo():
    connection_string = str(TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg")
    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def get_session_override():
            return session
        app.dependency_overrides[get_session] = get_session_override
        client = TestClient(app)
        todo_content = "buy bread"
        response = client.post("/create_todos/",
                               json={"content": todo_content}
                               )
        data = response.json()
        assert response.status_code == 200
        assert data["content"] == todo_content

def test_get_todo():
    connection_string = str(TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg")
    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def get_session_override():
            return session
        app.dependency_overrides[get_session] = get_session_override
        client = TestClient(app)
        response = client.get("/get_todos/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

def test_get_todo_by_id():
    connection_string = str(TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg")
    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def get_session_override():
            return session
        app.dependency_overrides[get_session] = get_session_override
        client = TestClient(app)
        todo_data = {"content": "Test Todo"}
        response = client.post("/create_todos/", json=todo_data)
        todo_id = response.json()["id"]
        response = client.get(f"/get_todos/{todo_id}")
        assert response.status_code == 200
        assert response.json()["id"] == todo_id

def test_update_todo():
    connection_string = str(TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg")
    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def get_session_override():
            return session
        app.dependency_overrides[get_session] = get_session_override
        client = TestClient(app)
        todo_data = {"content": "Test Todo"}
        response = client.post("/create_todos/", json=todo_data)
        todo_id = response.json()["id"]
        updated_data = {"content": "Updated Todo"}
        response = client.put(f"/update_todos/{todo_id}", json=updated_data)
        assert response.status_code == 200
        assert response.json()["content"] == "Updated Todo"

def test_delete_todo():
    connection_string = str(TEST_DATABASE_URL).replace(
        "postgresql", "postgresql+psycopg")
    engine = create_engine(
        connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        def get_session_override():
            return session
        app.dependency_overrides[get_session] = get_session_override
        client = TestClient(app)
        todo_data = {"content": "Test Todo"}
        response = client.post("/create_todos/", json=todo_data)
        todo_id = response.json()["id"]
        response = client.delete(f"/delete_todos/{todo_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Todo deleted successfully"
