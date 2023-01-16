import requests
from src import config
import json
import pytest

from src.tokens import generate_jwt



@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return


def test_auth_logout_success(clear):
    register_response = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    register_data = register_response.json()
    token = register_data['token']

    logout_response = requests.post(config.url + 'auth/logout/v1', json={'token': token})
    assert logout_response.status_code == 200

    another_logout = requests.post(config.url + 'auth/logout/v1', json={'token': token})
    assert another_logout.status_code == 403

def test_auth_logout_invalid_token(clear):

    response = requests.post(config.url + 'auth/logout/v1', json={'token': generate_jwt(1, 1)})
    assert response.status_code == 403