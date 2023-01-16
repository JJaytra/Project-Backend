import requests
from src import config
import json
import pytest
from src.data_store import data_store
from src.tokens import get_userid_from_token

#---------------------------------------------

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return

@pytest.fixture
def first_user():
    register_response = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    register_response_data = register_response.json()
    return register_response_data['token']

def create_valid_channel_id(token):
    channel_response = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'potatotime', 'is_public': True})
    channel_data = channel_response.json()
    return channel_data['channel_id']

def create_valid_dm(token, second_user):
    dm_response = requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': [second_user]})
    dm_id = dm_response.json()
    return dm_id['dm_id']

def send_message(token, channel_id):
    send_response = requests.post(config.url + 'message/send/v1', json={'token': token, 'channel_id': channel_id, "message": "Lightning Mcqueen goes kachow"})
    response_data = send_response.json()
    return response_data['message_id']

def create_another_token(email):
    register_response = requests.post(config.url + 'auth/register/v2', json={'email': email,'password': 'riddles','name_first': 'Bob','name_last': 'thebuilder'})
    register_response_data = register_response.json()
    return register_response_data['auth_user_id']
#------------------------------------------------

def test_invalid_channel_and_dm(clear, first_user):
    channel_id = create_valid_channel_id(first_user)
    message_id = send_message(first_user, channel_id)
    
    response = requests.post(config.url + 'message/share/v1', json={'token': first_user, 'og_message_id': message_id, 'message': "Cool message!", 'channel_id': 5, 'dm_id': -1})
    assert response.status_code == 400

def test_invalid_channel_and_dm_two(clear, first_user):
    channel_id = create_valid_channel_id(first_user)
    message_id = send_message(first_user, channel_id)
    
    response = requests.post(config.url + 'message/share/v1', json={'token': first_user, 'og_message_id': message_id, 'message': "Cool message!", 'channel_id': -1, 'dm_id': 5})
    assert response.status_code == 400

    

def test_no_invalid_channel_and_dm(clear, first_user):
    channel_id = create_valid_channel_id(first_user)
    message_id = send_message(first_user, channel_id)
    second_user = create_another_token("haha@gmail.com")
    dm_id = create_valid_dm(first_user, second_user)
    
    response = requests.post(config.url + 'message/share/v1', json={'token': first_user, 'og_message_id': message_id, 'message': "Cool message!", 'channel_id': channel_id, 'dm_id': dm_id})
    assert response.status_code == 400

def test_og_message_not_in_user_channels_or_dm(clear, first_user):
    channel_id = create_valid_channel_id(first_user)


    response = requests.post(config.url + 'message/share/v1', json={'token': first_user, 'og_message_id': 5, 'message': "Cool message!", 'channel_id': channel_id, 'dm_id': -1})
    assert response.status_code == 400

def test_long_message(clear, first_user):
    channel_id = create_valid_channel_id(first_user)
    message_id = send_message(first_user, channel_id)

    response = requests.post(config.url + 'message/share/v1', json={'token': first_user, 'og_message_id': message_id, 'message': """BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
                                                                                                            BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
                                                                                                            BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
                                                                                                            BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
                                                                                                            BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
                                                                                                            BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
                                                                                                            BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
                                                                                                            BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
                                                                                                            BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
                                                                                                            BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
                                                                                                            BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans""",
                                                                                                            'channel_id': channel_id, 'dm_id': -1})
    assert response.status_code == 400


def test_user_not_in_specified_channel_or_dm(clear, first_user):
    channel_id = create_valid_channel_id(first_user)
    message_id = send_message(first_user, channel_id)

    register_response = requests.post(config.url + 'auth/register/v2', json={'email': "ba@gmail.com",'password': 'riddles','name_first': 'Bob','name_last': 'thebuilder'})
    register_response_data = register_response.json()
    second_user = register_response_data['token']

    response = requests.post(config.url + 'message/share/v1', json={'token': second_user, 'og_message_id': message_id, 'message': "Cool message!", 'channel_id': channel_id, 'dm_id': -1})
    assert response.status_code == 400


def test_message_share_channel_success(clear, first_user):
    channel_id = create_valid_channel_id(first_user)
    message_id = send_message(first_user, channel_id)

    response = requests.post(config.url + 'message/share/v1', json={'token': first_user, 'og_message_id': message_id, 'message': "Cool message!", 'channel_id': channel_id, 'dm_id': -1})
    assert response.status_code == 200

    response = requests.get(config.url + 'channel/messages/v2', params={'token': first_user, 'channel_id': channel_id, 'start': 0})


def test_message_share_dm_success(clear, first_user):
    second_user = create_another_token("bob@gmail.com")
    dm_id = create_valid_dm(first_user, second_user)
    channel_id = create_valid_channel_id(first_user)
    message_id = send_message(first_user, channel_id)

    response = requests.post(config.url + 'message/share/v1', json={'token': first_user, 'og_message_id': message_id, 'message': "Cool message!", 'channel_id': -1, 'dm_id': dm_id})
    assert response.status_code == 200