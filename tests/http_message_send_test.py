import pytest
import requests
from src import config
import json
from datetime import datetime

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

#--------------------------------------------------------------------------------

def test_message_send_invalid_channel(clear):
    token = create_valid_token()
    response = requests.post(config.url + 'message/send/v1', json={'token': token, 'channel_id': "1", "message": "typing here"})
    assert response.status_code == 400

def test_message_send_bad_length(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    response = requests.post(config.url + 'message/send/v1', json={'token': token, 'channel_id': c_id, "message": ""})
    assert response.status_code == 400

def test_message_send_not_member(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)

    register_response = requests.post(config.url + 'auth/register/v2', json={'email': 'potato@gmail.com','password': 'secrets','name_first': 'Bob','name_last': 'Bob'})
    register_response_data = register_response.json()
    token2 = register_response_data['token']

    response = requests.post(config.url + 'message/send/v1', json={'token': token2, 'channel_id': c_id, "message": "hello there"})
    assert response.status_code == 403

def test_message_send_success(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)

    response = requests.post(config.url + 'message/send/v1', json={'token': token, 'channel_id': c_id, "message": "hello there"})
    # current_time = datetime.now()
    assert response.status_code == 200
    
    response = requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['messages'][0]['message'] == 'hello there'

    

def test_message_send_success_multiple_messages(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)

    response = requests.post(config.url + 'message/send/v1', json={'token': token, 'channel_id': c_id, "message": "one"})

    response = requests.post(config.url + 'message/send/v1', json={'token': token, 'channel_id': c_id, "message": "two"})

    response = requests.post(config.url + 'message/send/v1', json={'token': token, 'channel_id': c_id, "message": "three"})

    
    
    response = requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['messages'][0]['message_id'] == 3
    assert response_data['messages'][0]['message'] == 'three'
    assert response_data['messages'][1]['message_id'] == 2
    assert response_data['messages'][1]['message'] == 'two'
    assert response_data['messages'][2]['message_id'] == 1
    assert response_data['messages'][2]['message'] == 'one'

    

    
    
 

   
