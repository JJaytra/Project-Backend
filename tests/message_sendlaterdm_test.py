import requests
from src import config
import json
import pytest
from src.data_store import data_store
from src.tokens import get_userid_from_token
import time
from datetime import datetime



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

def create_another_uid(email):
    register_response = requests.post(config.url + 'auth/register/v2', json={'email': email,'password': 'riddles','name_first': 'Bob','name_last': 'thebuilder'})
    register_response_data = register_response.json()
    return register_response_data['auth_user_id']

def create_valid_dm(token, second_user):
    dm_response = requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': [second_user]})
    dm_id = dm_response.json()
    return dm_id['dm_id']

def create_another_token(email):
    register_response = requests.post(config.url + 'auth/register/v2', json={'email': email,'password': 'riddles','name_first': 'Bob','name_last': 'thebuilder'})
    register_response_data = register_response.json()
    return register_response_data['token']

#----------------------------------------------------------------

def test_invalid_dm(clear):
    token = create_valid_token()
    response = requests.post(config.url + 'message/sendlaterdm/v1', json={'token': token, 'dm_id': -1, 'message': "Hello", 'time_sent': time.time()+2})
    assert response.status_code == 400


def test_short_message(clear):
    token = create_valid_token()
    second_user_id = create_another_uid("mario@gmail.com")
    dm_id = create_valid_dm(token, second_user_id)

    response = requests.post(config.url + 'message/sendlaterdm/v1', json={'token': token, 'dm_id': dm_id, 'message': "", 'time_sent': time.time()+2})
    assert response.status_code == 400


def test_long_message(clear):
    token = create_valid_token()
    second_user_id = create_another_uid("mario@gmail.com")
    dm_id = create_valid_dm(token, second_user_id)

    response = requests.post(config.url + 'message/sendlaterdm/v1', json={'token': token, 'dm_id': dm_id, 'message': """BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
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
                                                                                                            'time_sent': time.time()+2})
    assert response.status_code == 400

def test_past_time(clear):
    token = create_valid_token()
    second_user_id = create_another_uid("mario@gmail.com")
    dm_id = create_valid_dm(token, second_user_id)

    response = requests.post(config.url + 'message/sendlaterdm/v1', json={'token': token, 'dm_id': dm_id, 'message': "Hello", 'time_sent': time.time()-2})
    assert response.status_code == 400

def test_user_not_in_dm(clear):
    token = create_valid_token()
    second_user_id = create_another_uid("mario@gmail.com")
    dm_id = create_valid_dm(token, second_user_id)

    excluded_user = create_another_token("batman@gmail.com")
    response = requests.post(config.url + 'message/sendlaterdm/v1', json={'token': excluded_user, 'dm_id': dm_id, 'message': "Hello", 'time_sent': time.time()+2})
    assert response.status_code == 403


def test_message_sendlaterdm_success(clear):
    token = create_valid_token()
    second_user_id = create_another_uid("mario@gmail.com")
    dm_id = create_valid_dm(token, second_user_id)

    response = requests.post(config.url + 'message/sendlaterdm/v1', json={'token': token, 'dm_id': dm_id, 'message': "Hello", 'time_sent': time.time()+2})
    assert response.status_code == 200

    response = requests.get(config.url + 'dm/messages/v1', params = {'token': token, 'dm_id': dm_id, 'start': 0})
    response_data = response.json()
    assert len(response_data['messages']) == 0
    
    time.sleep(2.0)
    response = requests.get(config.url + 'dm/messages/v1', params = {'token': token, 'dm_id': dm_id, 'start': 0})
    response_data = response.json()
    assert len(response_data['messages']) == 1
