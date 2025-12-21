from http import HTTPStatus

import factory
import factory.fuzzy
import pytest

from fast_api.models import Todo, TodoState
from fast_api.schemas import TodoPublic


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


@pytest.mark.asyncio
async def test_create_todo(client, token, mock_db_time, user):

    with mock_db_time(model=Todo) as time:
        new_todo = TodoFactory(user_id=user.id)
        response = client.post(
            '/todos/',
            json={
                'title': new_todo.title,
                'description': new_todo.description,
                'state': new_todo.state.value,
            },
            headers={'Authorization': f'Bearer {token}'},
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'title': new_todo.title,
        'description': new_todo.description,
        'state': new_todo.state.value,
        'id': 1,
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


@pytest.mark.asyncio
async def test_list_todos_should_return_all_fields(
    session, client, user, token
):
    # arrange
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.get(
        '/todos', headers={'Authorization': f'Bearer {token}'}
    )

    todo = TodoPublic.model_validate(todo).model_dump(mode='json')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'todos': [todo]}


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(session, client, user, token):
    # arrange
    expected_todos = 5

    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    session, user, client, token
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, title='wheresss')
    )
    await session.commit()

    response = client.get(
        '/todos/?title=whe',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_todos(
    client, session, user, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5, user_id=user.id, description='no description'
        )
    )
    await session.commit()

    response = client.get(
        '/todos/?description=desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_todos(
    client, session, user, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft)
    )
    await session.commit()

    response = client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_delete_todo(client, token, session, user):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted successfully'}


def test_delete_todo_not_found_error(client, token):
    response = client.delete(
        '/todos/10', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_delete_other_user_todo(client, token, other_user, session):
    """tenho que criar outro todo, que recebe o other_user.id
    como o token está para o user.id, ele dá conflito, pois o
    'other_todo.id é do other_user e não do user"""

    other_todo = TodoFactory(user_id=other_user.id)
    session.add(other_todo)
    await session.commit()

    response = client.delete(
        f'/todos/{other_todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_update_todo(client, session, token, user, mock_db_time):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory(user_id=user.id)
        session.add(todo)
        await session.commit()

        response = client.patch(
            f'/todos/{todo.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={'title': 'titulo teste'},
        )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data['title'] == todo.title
    assert data['description'] == todo.description
    assert data['state'] == todo.state.value
    assert data['id'] == todo.id
    assert data['created_at'] == time.isoformat()
    assert 'updated_at' in data


def test_update_todo_error_not_found(client, token):
    response = client.patch(
        '/todos/5', headers={'Authorization': f'Bearer {token}'}, json={}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}
