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

#------------------Channel Invite-----------------------------------------------------------------
def test_channel_invite_invalid_channel(clear):
    token = create_valid_token()
    token2 = create_another_token("meeee@gmail.com")
    u_id2 = get_userid_from_token(token2)
    response = requests.post(config.url + 'channel/invite/v2', json={'token': token, 'channel_id': 1, 'u_id': u_id2})
    assert response.status_code == 400

def test_channel_invite_invalid_user(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    response = requests.post(config.url + 'channel/invite/v2', json={'token': token, 'channel_id': c_id, 'u_id': 4})
    assert response.status_code == 400

def test_channel_invite_already_member(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    token2 = create_another_token("meeee@gmail.com")
    u_id2 = get_userid_from_token(token2)
    requests.post(config.url + 'channel/invite/v2', json={'token': token, 'channel_id': c_id, 'u_id': u_id2}) 


    response = requests.post(config.url + 'channel/invite/v2', json={'token': token, 'channel_id': c_id, 'u_id': u_id2})
    assert response.status_code == 400


def test_channel_invite_from_non_member(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    token2 = create_another_token("meeee@gmail.com")
    token3 = create_another_token("rob@gmail.com")
    u_id3 = get_userid_from_token(token3)

    response = requests.post(config.url + 'channel/invite/v2', json={'token': token2, 'channel_id': c_id, 'u_id': u_id3})
    assert response.status_code == 403


def test_channel_invite_success(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)
    token2 = create_another_token("apples@gmail.com")
    u_id2 = get_userid_from_token(token2)
    u_id1 = get_userid_from_token(token)

    response = requests.post(config.url + 'channel/invite/v2', json={'token': token, 'channel_id': c_id, 'u_id': u_id2})
    assert response.status_code == 200

    response = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': c_id})
    response_data = response.json()

    assert response_data == {'name': 'potatotime', 'is_public': True,     
    'owner_members': [{'u_id': u_id1, 'email': 'grapesmango1@gmail.com', 'name_first': 'Justin', 'name_last': 'Gordon', 'handle_str': 'justingordon'}],
    'all_members': [{'u_id': u_id1, 'email': 'grapesmango1@gmail.com', 'name_first': 'Justin', 'name_last': 'Gordon', 'handle_str': 'justingordon'}, {'u_id': u_id2, 'email': 'apples@gmail.com', 'name_first': 'Bob', 'name_last': 'thebuilder', 'handle_str': 'bobthebuilder'}]}
