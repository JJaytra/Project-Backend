import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.error import InputError, AccessError
from src.auth import auth_register_v1

@pytest.fixture
def first_user():
    requests.delete(config.url + 'clear/v1', json={})
    first_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    response_data = first_user.json()
    return response_data

@pytest.fixture
def second_user():
    second_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango2@gmail.com','password': 'sunnyday','name_first': 'Dustin','name_last': 'Bordon'})
    response_data = second_user.json()
    return response_data
    
@pytest.fixture
def dm_by_first_user_with_second(first_user,second_user):
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id = dm_id.json()
    return dm_id['dm_id']
    
def test_messages_senddm_one_message(first_user,second_user,dm_by_first_user_with_second):
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "scooby dooby doo"})
    message_id = message_id.json()
    dm_messages = requests.get(config.url + 'dm/messages/v1', params = {'token': first_user['token'], 'dm_id': dm_by_first_user_with_second, 'start': 0})
    response_data = dm_messages.json()
    assert response_data['messages'][0]['message_id'] == message_id['message_id']
    assert response_data['messages'][0]['message'] == "scooby dooby doo"
    assert response_data['start'] == 0
    assert response_data['end'] == -1

def test_messages_senddm_one_message_multiple_dms_check_unique_msg_id(first_user,second_user,dm_by_first_user_with_second):
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id2 = dm_id.json()
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id3 = dm_id.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "same message"})
    message_id1 = message_id.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_id2['dm_id'], 'message': "same message"})
    message_id2 = message_id.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_id3['dm_id'], 'message': "same message"})
    message_id3 = message_id.json()
    assert message_id1['message_id'] != message_id2['message_id']
    assert message_id1['message_id'] != message_id3['message_id']
    assert message_id2['message_id'] != message_id3['message_id']
    
def test_messages_senddm_invalid_dm(first_user):
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': 69420, 'message': "one"})
    assert message_id.status_code == 400

def test_messages_senddm_invalid_message_length(first_user,second_user,dm_by_first_user_with_second):
    short_msg = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': ""})
    assert short_msg.status_code == 400
    long_msg = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "helloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo"})
    assert long_msg.status_code == 400

def test_messages_senddm_not_dm_member(first_user, second_user, dm_by_first_user_with_second):
    third_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango3@gmail.com','password': 'sunnyday','name_first': 'Lustin','name_last': 'Hordon'})
    third_user = third_user.json()
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': third_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "scooby dooby doo"})
    assert message_id.status_code == 403
