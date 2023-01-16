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

#------------------Channel Join-----------------------------------------------------------------
def test_channel_join_channel_invalid(clear):
    token = create_valid_token()
    response = requests.post(config.url + 'channel/join/v2', json={'token': token, 'channel_id': 1})
    assert response.status_code == 400

def test_channel_join_already_member(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)

    token2 = create_another_token("banana@gmail.com")

    requests.post(config.url + 'channel/join/v2', json={'token': token2, 'channel_id': c_id})
    response = requests.post(config.url + 'channel/join/v2', json={'token': token2, 'channel_id': c_id})
    assert response.status_code == 400


def test_channel_join_private_channel(clear):
    token = create_valid_token()
    c_id = create_valid_channel_custom(token, "Hellomsgs", "False")
    token2 = create_another_token("apples@gmail.com")
    response = requests.post(config.url + 'channel/join/v2', json={'token': token2, 'channel_id': c_id})
    assert response.status_code == 403

def test_channel_join_success(clear):
    token = create_valid_token()
    c_id = create_valid_channel_id(token)

    u_id = get_userid_from_token(token)

    token2 = create_another_token("pingu@gmail.com")
    u_id2 = get_userid_from_token(token2)

    response = requests.post(config.url + 'channel/join/v2', json={'token': token2, 'channel_id': c_id})
    assert response.status_code == 200

    response = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': c_id})
    response_data = response.json()

    assert response_data == {'name': 'potatotime', 'is_public': True,     
    'owner_members': [{'u_id': u_id, 'email': 'grapesmango1@gmail.com', 'name_first': 'Justin', 'name_last': 'Gordon', 'handle_str': 'justingordon'}],
    'all_members': [{'u_id': u_id, 'email': 'grapesmango1@gmail.com', 'name_first': 'Justin', 'name_last': 'Gordon', 'handle_str': 'justingordon'}, {'u_id': u_id2, 'email': 'pingu@gmail.com', 'name_first': 'Bob', 'name_last': 'thebuilder', 'handle_str': 'bobthebuilder', 'time_stamp': response_data['all_members'][1]['time_stamp']}]}

