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
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'potatotime', 'is_public': "True"})
    channel_data = channel_response.json()
    return channel_data['channel_id']

def send_message(token, channel_id):
    send_response = requests.post(config.url + 'message/send/v1', json={'token': token, 'channel_id': channel_id, "message": "Lightning Mcqueen goes kachow"})
    response_data = send_response.json()
    return response_data['message_id']
#------------------------------------------------

# Input Error: MessageID not part of a valid channel/dm user is part of
def test_invalid_msg_id(clear):
    token = create_valid_token()
    response = requests.post(config.url + 'message/react/v1', json={'token': token, 'message_id': 2, 'react_id': 1})
    assert response.status_code == 400

# Input Error: React_ID is invalid (not 1)
def test_invalid_react_id(clear):
    token = create_valid_token()
    channel_id = create_valid_channel_id(token)
    message_id = send_message(token, channel_id)

    response = requests.post(config.url + 'message/react/v1', json={'token': token, 'message_id': message_id, 'react_id': -2})
    assert response.status_code == 400


# Input Error: Message already contains a react with ID react_id from the auth user
def test_already_reacted(clear):
    token = create_valid_token()
    channel_id = create_valid_channel_id(token)
    message_id = send_message(token, channel_id)

    response = requests.post(config.url + 'message/react/v1', json={'token': token, 'message_id': message_id, 'react_id': 1})
    assert response.status_code == 200

    response = requests.post(config.url + 'message/react/v1', json={'token': token, 'message_id': message_id, 'react_id': 1})
    assert response.status_code == 400

# Success: Message_react is successful for msg in channel
def test_successful_react_channel(clear):
    token = create_valid_token()
    channel_id = create_valid_channel_id(token)
    message_id = send_message(token, channel_id)

    response = requests.post(config.url + 'message/react/v1', json={'token': token, 'message_id': message_id, 'react_id': 1})
    assert response.status_code == 200

    # data = data_store.get()
    # messages = data['messages']
    # message = messages[message_id-1]
    # reacts = message['reacts']

    # u_id = get_userid_from_token(token)
    # assert u_id in reacts['u_ids']


# # Success: Message_react is successful for msg in dm
# def test_successful_react_dm(clear):