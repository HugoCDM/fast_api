from http import HTTPStatus

from fastapi import FastAPI

from fast_api.routers import auth, todos, users
from fast_api.schemas import Message

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
async def read_root():
    return {'message': 'Olá Mundo!'}


# @app.get('/bem-vindo', status_code=HTTPStatus.OK, response_model=Message)
# def welcome_roater():
#     return {'message': 'Olá Mundo!'}
