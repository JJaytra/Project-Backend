import requests
from src import config
import json
from src.other import clear_v1
import pytest

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return


def create_valid_token():
    register_response = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    register_response_data = register_response.json()
    return register_response_data['token']

def create_valid_channel_id(token):
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'potatotime', 'is_public': True})
    channel_data = channel_response.json()
    return channel_data['channel_id']

def create_another_token(email):
    register_response = requests.post(config.url + 'auth/register/v2', json={'email': email,'password': 'riddles','name_first': 'Bob','name_last': 'thebuilder'})
    register_response_data = register_response.json()
    return register_response_data['token']

def create_valid_channel_custom(token, name, ispublic):
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': name, 'is_public': ispublic})
    channel_data = channel_response.json()
    return channel_data['channel_id']

#------------------Channels List-----------------------------------------------------------------
def test_channels_list_success_one_channel(clear):
    token = create_valid_token()

    c_id = create_valid_channel_id(token)

    response = requests.get(config.url + 'channels/list/v2?token='+token)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['channels'] == [{'channel_id': c_id, 'name': 'potatotime'}]


def test_channels_list_success_multiple_channels(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)

    channel_response2 = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'pizzaparty', 'is_public': False})
    channel_data2 = channel_response2.json()
    c_id2 = channel_data2['channel_id']

    response = requests.get(config.url + 'channels/list/v2?token='+token)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['channels'] == [{'channel_id': c_id, 'name': 'potatotime'}, {'channel_id': c_id2, 'name': 'pizzaparty'}]


def test_channels_list_no_channels(clear):
    token = create_valid_token()

    response = requests.get(config.url + 'channels/list/v2?token='+token)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['channels'] == []

def test_channels_list_user_in(clear):
    token = create_valid_token()
    token2 = create_another_token("rob@gmail.com")

    c_id = create_valid_channel_id(token)
    create_valid_channel_custom(token2, "HelloWorlds", True)

    response = requests.get(config.url + 'channels/list/v2?token='+token)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['channels'] == [{'channel_id': c_id, 'name': 'potatotime'}]


    