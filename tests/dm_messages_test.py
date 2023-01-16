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
    
def test_dm_messages_one_message(first_user,second_user,dm_by_first_user_with_second):
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "scooby dooby doo"})
    message_id = message_id.json()
    dm_messages = requests.get(config.url + 'dm/messages/v1', params = {'token': first_user['token'], 'dm_id': dm_by_first_user_with_second, 'start': 0})
    response_data = dm_messages.json()
    assert response_data['messages'][0]['message_id'] == message_id['message_id']
    assert response_data['messages'][0]['message'] == "scooby dooby doo"
    assert response_data['start'] == 0
    assert response_data['end'] == -1

def test_dm_messages_25_messages(first_user,second_user,dm_by_first_user_with_second):
    for i in range(1,24):
        message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "scooby dooby doo"})
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "twenty five scooby dooby doos :)"})
    message_id = message_id.json()
    dm_messages = requests.get(config.url + 'dm/messages/v1', params = {'token': first_user['token'], 'dm_id': dm_by_first_user_with_second, 'start': 0})
    response_data = dm_messages.json()
    for i in range(1,24):
        assert response_data['messages'][i]['message'] == "scooby dooby doo"
    assert response_data['messages'][0]['message_id'] == message_id['message_id']
    assert response_data['messages'][0]['message'] == "twenty five scooby dooby doos :)"
    assert response_data['start'] == 0
    assert response_data['end'] == -1

def test_dm_messages_50_messages(first_user,second_user,dm_by_first_user_with_second):
    for i in range(1,49):
        message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "scooby dooby doo"})
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "fifty scooby dooby doos :)"})
    message_id = message_id.json()
    dm_messages = requests.get(config.url + 'dm/messages/v1', params = {'token': first_user['token'], 'dm_id': dm_by_first_user_with_second, 'start': 0})
    response_data = dm_messages.json()
    for i in range(1,49):
        assert response_data['messages'][i]['message'] == "scooby dooby doo"
    assert response_data['messages'][0]['message_id'] == message_id['message_id']
    assert response_data['messages'][0]['message'] == "fifty scooby dooby doos :)"
    assert response_data['start'] == 0
    assert response_data['end'] == -1

def test_dm_messages_100_messages(first_user,second_user,dm_by_first_user_with_second):
    for i in range(1,100):
        requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "scooby dooby doo"})
    dm_messages = requests.get(config.url + 'dm/messages/v1', params = {'token': first_user['token'], 'dm_id': dm_by_first_user_with_second, 'start': 0})
    response_data = dm_messages.json()
    for i in range(0,49):
        assert response_data['messages'][i]['message'] == "scooby dooby doo"
    assert response_data['start'] == 0
    assert response_data['end'] == 50

def test_dm_messages_starting_middle_multiple_users(first_user,second_user,dm_by_first_user_with_second):
    first_message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "one"})
    first_message_id = first_message_id.json()
    second_message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "two"})
    second_message_id = second_message_id.json()
    third_message_id = requests.post(config.url + 'message/senddm/v1', json={'token': second_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "three"})
    third_message_id = third_message_id.json()
    dm_messages = requests.get(config.url + 'dm/messages/v1', params = {'token': first_user['token'], 'dm_id': dm_by_first_user_with_second, 'start': 1})
    response_data = dm_messages.json()
    assert response_data['start'] == 1
    assert response_data['end'] == -1
    assert response_data['messages'][0]['message_id'] == second_message_id['message_id']
    assert response_data['messages'][0]['message'] == "two"    
    assert response_data['messages'][1]['message_id'] == first_message_id['message_id']
    assert response_data['messages'][1]['message'] == "one"

def test_dm_messages_invalid_dm(first_user):
    dm_messages = requests.get(config.url + 'dm/messages/v1', params = {'token': first_user['token'], 'dm_id': 69420, 'start': 1})
    assert dm_messages.status_code == 400

def test_dm_messages_invalid_start(first_user, second_user, dm_by_first_user_with_second):
    requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "scooby dooby doo"})
    dm_messages = requests.get(config.url + 'dm/messages/v1', params = {'token': first_user['token'], 'dm_id': dm_by_first_user_with_second, 'start': 2})
    assert dm_messages.status_code == 400

def test_dm_messages_not_dm_member(first_user, second_user, dm_by_first_user_with_second):
    third_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango3@gmail.com','password': 'sunnyday','name_first': 'Lustin','name_last': 'Hordon'})
    third_user = third_user.json()
    requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "scooby dooby doo"})
    dm_messages = requests.get(config.url + 'dm/messages/v1', params = {'token': third_user['token'], 'dm_id': dm_by_first_user_with_second, 'start': 0})
    assert dm_messages.status_code == 403
