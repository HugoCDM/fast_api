from http import HTTPStatus


def test_root_deve_retornar_ola_mundo(client):
    """
    Teste com 3 etapas (AAA):
    - Arrange (arranjo)
    - Act (executar a coisa / agir)
    - Assert (garantir que a coisa é a coisa e não diferente)
    """

    # Arrange
    response = client.get('/')  # Act

    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'message': 'Olá Mundo!'}  # Assert
