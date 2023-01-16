import pytest
import requests
from src import config
import json

from src.data_store import data_store

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

def create_valid_channel_custom(token, name, ispublic):
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': name, 'is_public': ispublic})
    channel_data = channel_response.json()
    return channel_data['channel_id']

def send_another_message(token, channel_id):
    send_response = requests.post(config.url + 'message/send/v1', json={'token': token, 'channel_id': channel_id, "message": "Sheep goes baaaa"})
    response_data = send_response.json()
    return response_data['message_id']

#--------------------------------------------------------------------------------

def test_message_edit_long_message(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    msg_id = send_message(token, c_id)

    response = requests.put(config.url + 'message/edit/v1', json={'token': token, 'message_id': msg_id, 'message': """
    BeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
    BeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
    BeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
    BeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
    BeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
    BeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
    BeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
    """})

    assert response.status_code == 400

# message_id does not refer to a valid message within a channel/DM that the authorised user has joined
def test_message_edit_not_found(clear):
    token = create_valid_token()
    create_valid_channel_id(token)

    token2 = create_another_token("ihatebeans@gmail.com")
    c_id2 = create_valid_channel_custom(token2, "partytime", True)
    msg_id2 = send_another_message(token2, c_id2)

    response = requests.put(config.url + 'message/edit/v1', json={'token': token, 'message_id': msg_id2, 'message': "bababa"})
    assert response.status_code == 400

# the message was not sent by the authorised user making this request
def test_message_edit_not_sendee(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    msg_id = send_message(token, c_id)

    token2 = create_another_token("ihatebeans@gmail.com")
    requests.post(config.url + 'channel/join/v2', json={'token': token2, 'channel_id': c_id})

    response = requests.put(config.url + 'message/edit/v1', json={'token': token2, 'message_id': msg_id, 'message': "Hello there"})
    assert response.status_code == 403

#make one for dms

# sendee edits their own message
def test_message_edit_success_is_sendee(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    msg_id = send_message(token, c_id)

    response = requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0})
    response_data = response.json()
    assert response_data['messages'][0]['message'] == 'Lightning Mcqueen goes kachow'

    response = requests.put(config.url + 'message/edit/v1', json={'token': token, 'message_id': msg_id, 'message': "Hello there"})
    assert response.status_code == 200

    response = requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': c_id, 'start': 0})
    response_data = response.json()
    assert response_data['messages'][0]['message'] == 'Hello there'



# channel owner edits message
def test_message_edit_success_has_owner_perms(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    send_message(token, c_id)

    token2 = create_another_token("ihatebeans@gmail.com")
    requests.post(config.url + 'channel/join/v2', json={'token': token2, 'channel_id': c_id})
    msg_id2 = send_another_message(token2, c_id)

    response = requests.put(config.url + 'message/edit/v1', json={'token': token, 'message_id': msg_id2, 'message': "Hello there"})
    assert response.status_code == 200

# #make one for dms

def test_message_edit_success_delete(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    msg_id = send_message(token, c_id)

    response = requests.put(config.url + 'message/edit/v1', json={'token': token, 'message_id': msg_id, 'message': ""})
    assert response.status_code == 200

    
    

