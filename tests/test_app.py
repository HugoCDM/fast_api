from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_api.app import app


def test_root_deve_retornar_ola_mundo():
    """
    Teste com 3 etapas (AAA):
    - Arrange (arranjo)
    - Act (executar a coisa / agir)
    - Assert (garantir que a coisa é a coisa e não diferente)
    """

    client = TestClient(app)  # Arrange
    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'message': 'Olá Mundo!'}  # Assert


def teste_bem_vindo_deve_retornar_ola_mundo():
    client = TestClient(app)
    response = client.get('/bem-vindo')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}
