from fastapi import HTTPException
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session, create_engine, select, Field, Table
from contextlib import asynccontextmanager
from fastapi_todoapp import settings
from typing import Optional, Union, Annotated
import uvicorn


class Todo(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    content: str = Field(index=True, max_length=255)
    is_completed: bool = Field(default=False)


connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

engine = create_engine(connection_string, connect_args={
                       "sslmode": "require"}, pool_recycle=300, pool_size=10, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    print("Tables Created")
    yield

app = FastAPI(lifespan=lifespan, title="Todo App API",
              version="1.0.0")


def get_session():
    with Session(engine) as session:
        yield session


@app.get('/')
def home():
    return {'message': 'Simple todo Application'}


@app.post('/create_todos/', response_model=Todo)
async def create_todoapp(todo: Todo, session: Annotated[Session, Depends(get_session)]):
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@app.get('/get_todos/', response_model=list[Todo])
async def get_todoapp(session: Annotated[Session, Depends(get_session)]):
    todo = session.exec(select(Todo)).all()
    if todo:
        return todo
    else:
        raise HTTPException(status_code=404, detail="No Task found")


@app.get('/get_todos/{todo_id}', response_model=Todo)
async def get_todo_by_id(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.put('/update_todos/{todo_id}', response_model=Todo)
async def update_todo(todo_id: int, updated_todo: Todo, session: Session = Depends(get_session)):
    existing_todo = session.get(Todo, todo_id)
    if existing_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    existing_todo.content = updated_todo.content
    session.commit()
    session.refresh(existing_todo)
    return existing_todo


@app.delete('/delete_todos/{todo_id}')
async def delete_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()
    return {"message": "Todo deleted successfully"}


# if __name__ == '__main__':
#     uvicorn.run('fastapi_todoapp.main:app',
#                 host='127.0.0.1', port=8000, reload=True)
