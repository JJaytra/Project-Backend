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

def send_message(token, channel_id):
    send_response = requests.post(config.url + 'message/send/v1', json={'token': token, 'channel_id': channel_id, "message": "Lightning Mcqueen goes kachow"})
    response_data = send_response.json()
    return response_data['message_id']

def create_another_token(email):
    register_response = requests.post(config.url + 'auth/register/v2', json={'email': email,'password': 'riddles','name_first': 'Bob','name_last': 'thebuilder'})
    register_response_data = register_response.json()
    return register_response_data['token']
#------------------------------------------------


def test_invalid_msg_id(clear):
    token = create_valid_token()
    response = requests.post(config.url + 'message/pin/v1', json={'token': token, 'message_id': -1})
    assert response.status_code == 400

def test_already_pinned(clear):
    token = create_valid_token()
    channel_id = create_valid_channel_id(token)
    msg_id = send_message(token, channel_id)

    requests.post(config.url + 'message/pin/v1', json={'token': token, 'message_id': msg_id})
    response = requests.post(config.url + 'message/pin/v1', json={'token': token, 'message_id': msg_id})
    assert response.status_code == 400


def test_no_owner_permission(clear):
    token = create_valid_token()
    channel_id = create_valid_channel_id(token)
    msg_id = send_message(token, channel_id)

    token2 = create_another_token("bob@gmail.com")
    requests.post(config.url + 'channel/join/v2', json={'token': token2, 'channel_id': channel_id})

    response = requests.post(config.url + 'message/pin/v1', json={'token': token2, 'message_id': msg_id})
    assert response.status_code == 403


def test_message_pin_success(clear):
    token = create_valid_token()
    channel_id = create_valid_channel_id(token)
    msg_id = send_message(token, channel_id)

    response = requests.post(config.url + 'message/pin/v1', json={'token': token, 'message_id': msg_id})
    assert response.status_code == 200