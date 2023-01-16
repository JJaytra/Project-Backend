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


#------------------Channels Listall-----------------------------------------------------------------

def test_channels_listall_success_no_channels(clear):
    token = create_valid_token()
    response = requests.get(config.url + 'channels/listall/v2?token='+token)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['channels'] == []


def test_channels_listall_success_one_channel(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)

    response = requests.get(config.url + 'channels/listall/v2?token='+token)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['channels'] == [{'channel_id': c_id, 'name': 'potatotime'}]


def test_channels_listall_success_multiple_public_channels(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    token2 = create_another_token("brucewayne@gmail.com")

    c_id2 = create_valid_channel_custom(token2, "PizzaParty", True)
    c_id3 = create_valid_channel_custom(token2, "Disneyland", True)
    
    response = requests.get(config.url + 'channels/listall/v2?token='+token)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['channels'] == [{'channel_id': c_id, 'name': 'potatotime'}, {'channel_id': c_id2, 'name': 'PizzaParty'}, {'channel_id': c_id3, 'name': 'Disneyland'}]

