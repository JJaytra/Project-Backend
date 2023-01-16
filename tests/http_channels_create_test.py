import requests
from src import config
import json
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


#------------------Channels Create-----------------------------------------------------------------
def test_channels_create_success(clear):
    
    token = create_valid_token()
    response = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'pizzatime', 'is_public': "True"})
    assert response.status_code == 200
    response_data = response.json()

    c_id = response_data['channel_id']

    response = requests.get(config.url + 'channels/list/v2?token='+token)
    response_data = response.json()
    assert response_data['channels'] == [{'channel_id': c_id, 'name': 'pizzatime'}]


def test_second_channels_create_success(clear):
   
    token = create_valid_token()
    response = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'pizzatime', 'is_public': True})
    response_data = response.json()
    c_id1 = response_data['channel_id']

    response = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'potatotime', 'is_public': True})
    assert response.status_code == 200
    response_data = response.json()
    c_id2 = response_data['channel_id']
    
    response = requests.get(config.url + 'channels/list/v2?token='+token)
    response_data = response.json()
    assert response_data['channels'] == [{'channel_id': c_id1, 'name': 'pizzatime'}, {'channel_id': c_id2, 'name': 'potatotime'}]


def test_channels_create_long_name(clear):
    token = create_valid_token()
    response = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'Ademonstrationofsuperiorjudgment', 'is_public': True})
    assert response.status_code == 400

