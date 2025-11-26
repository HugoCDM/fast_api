from http import HTTPStatus

from fastapi import FastAPI

from fast_api.schemas import Message

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá Mundo!'}


@app.get('/bem-vindo', status_code=HTTPStatus.OK, response_model=Message)
def welcome_roater():
    return {'message': 'Olá Mundo!'}
