import requests
from src import config
import json
import pytest
from src.data_store import data_store
from src.tokens import get_userid_from_token

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

#-------------Channel messages---------------------------

def test_channel_messages_invalid_channel(clear):
    token = create_valid_token()
    response = requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': 5, 'start': 0})
    assert response.status_code == 400


def test_channel_messages_invalid_start(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    response = requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 15})
    assert response.status_code == 400

def test_channel_messages_not_member(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    token2 = create_another_token("apples@gmail.com")

    response = requests.get(config.url + 'channel/messages/v2', params={'token': token2, 'channel_id': c_id, 'start': 0})
    assert response.status_code == 403


def test_channel_messages_success_no_messages(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    response = requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['messages'] == []
    assert response_data['start'] == 0
    assert response_data['end'] == -1

def send_messages_helper(token, c_id, message):
    requests.post(config.url + 'message/send/v1', json={'token': token, 'channel_id': c_id, "message": message})


def test_channel_messages_success_many_messages(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    i = 0
    while i < 52:
        send_messages_helper(token, c_id, "Hello")
        i+=1
    
    response = requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0})
    assert response.status_code == 200
    response_data = response.json()

    assert response_data['start'] == 0
    assert response_data['end'] == 50