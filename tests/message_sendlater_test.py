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

def create_another_token(email):
    register_response = requests.post(config.url + 'auth/register/v2', json={'email': email,'password': 'riddles','name_first': 'Bob','name_last': 'thebuilder'})
    register_response_data = register_response.json()
    return register_response_data['token']

#----------------------------------------------------------------

def test_invalid_channel_id(clear):
    token = create_valid_token()
    response = requests.post(config.url+'message/sendlater/v1', json={'token': token, 'channel_id': -1, 'message': "hello", 'time_sent': datetime.timestamp(datetime.now())+2})
    assert response.status_code == 400

def test_short_message(clear):
    token = create_valid_token()
    channel_id = create_valid_channel_id(token)
    response = requests.post(config.url+'message/sendlater/v1', json={'token': token, 'channel_id': channel_id, 'message': "", 'time_sent': datetime.timestamp(datetime.now())+2})
    assert response.status_code == 400

def test_long_message(clear):
    token = create_valid_token()
    channel_id = create_valid_channel_id(token)
    response = requests.post(config.url+'message/sendlater/v1', json={'token': token, 'channel_id': channel_id, 'message': """BeansBeansBeansBeansBeansBeansBeansBeansBeansBeans
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
                                                                                                                         'time_sent': datetime.timestamp(datetime.now())+2})
    assert response.status_code == 400


def test_time_sent_is_past(clear):
    token = create_valid_token()
    channel_id = create_valid_channel_id(token)
    response = requests.post(config.url+'message/sendlater/v1', json={'token': token, 'channel_id': channel_id, 'message': "Hello", 'time_sent': datetime.timestamp(datetime.now())-2})
    assert response.status_code == 400

    

def test_not_channel_members(clear):
    token = create_valid_token()
    channel_id = create_valid_channel_id(token)
    another_token = create_another_token("happy@gmail.com")
    response = requests.post(config.url+'message/sendlater/v1', json={'token': another_token, 'channel_id': channel_id, 'message': "Hello", 'time_sent': datetime.timestamp(datetime.now())+2})
    assert response.status_code == 403


def test_message_sendlater_success(clear):
    token = create_valid_token()
    channel_id = create_valid_channel_id(token)
    send_time = time.time()+2
    sendlater_response = requests.post(config.url+'message/sendlater/v1', json={'token': token, 'channel_id': channel_id, 'message': "Hello", 'time_sent': send_time})
    assert sendlater_response.status_code == 200
    sendlater_response = sendlater_response.json()
    response = requests.put(config.url + 'message/edit/v1', json={'token': token, 'message_id': sendlater_response['message_id'], 'message': "shouldn't work"})
#    assert sendlater_response['message_id'] == "wtf"
    assert response.status_code == 400    

    response = requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': channel_id, 'start': 0})
    response_data = response.json()
    assert len(response_data['messages']) == 0
    time.sleep(2.0)
    response = requests.get(config.url + 'channel/messages/v2', params={'token': token, 'channel_id': channel_id, 'start': 0})
    response_data = response.json()
    assert len(response_data['messages']) == 1
    response = requests.put(config.url + 'message/edit/v1', json={'token': token, 'message_id': sendlater_response['message_id'], 'message': "should now work"})
    assert response.status_code == 200

