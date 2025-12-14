from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_api.database import get_session
from fast_api.models import Todo, User
from fast_api.schemas import (
    FilterTodo,
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
)
from fast_api.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

# O usuário tem que estar conectado, ou seja, tem que te ro current_user


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TodoPublic)
async def create_todo(
    user: CurrentUser,
    session: Session,
    todo: TodoSchema,
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', status_code=HTTPStatus.OK, response_model=TodoList)
async def list_todos(
    user: CurrentUser,
    session: Session,
    todo_filter: Annotated[FilterTodo, Query()],
):
    query = select(Todo).where(user.id == Todo.user_id)

    if todo_filter.title:
        query = query.filter(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.filter(
            Todo.description.contains(todo_filter.description)
        )

    if todo_filter.state:
        query = query.filter(Todo.state == todo_filter.state)

    todos = await session.scalars(
        query.offset(todo_filter.offset).limit(todo_filter.limit)
    )

    return {'todos': todos.all()}


@router.delete('/{todo_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_todos(todo_id: int, session: Session, user: CurrentUser):
    todo = await session.scalar(
        select(Todo).where(todo_id == Todo.id, user.id == Todo.user_id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found'
        )

    await session.delete(todo)
    await session.commit()

    return {'message': 'Task has been deleted successfully'}
