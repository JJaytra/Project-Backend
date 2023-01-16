import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.error import InputError, AccessError
from src.auth import auth_register_v1

@pytest.fixture
def first_user():
    first_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    response_data = first_user.json()
    return response_data

@pytest.fixture
def second_user():
    second_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango2@gmail.com','password': 'sunnyday','name_first': 'Dustin','name_last': 'Bordon'})
    response_data = second_user.json()
    return response_data

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return

def test_remove_succesful(clear,first_user,second_user):
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    requests.delete(config.url + 'dm/remove/v1', json = {'token': first_user['token'], 'dm_id': dm_id})
    dm_list = requests.get(config.url + 'dm/list/v1', params = {'token': first_user['token']})
    response_data = dm_list.json()
    assert response_data['dms'] == []
    
def test_remove_dm_then_create_dm_then_remove(clear,first_user,second_user):
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id1 = dm_id.json()
    dm_id1 = dm_id1['dm_id']
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id2 = dm_id.json()
    dm_id2 = dm_id2['dm_id']
    requests.delete(config.url + 'dm/remove/v1', json = {'token': first_user['token'], 'dm_id': dm_id2})
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id3 = dm_id.json()
    dm_id3 = dm_id3['dm_id']    
    requests.delete(config.url + 'dm/remove/v1', json = {'token': first_user['token'], 'dm_id': dm_id1})
    requests.delete(config.url + 'dm/remove/v1', json = {'token': first_user['token'], 'dm_id': dm_id3})    
    dm_list = requests.get(config.url + 'dm/list/v1', params = {'token': first_user['token']})
    response_data = dm_list.json()
    assert response_data['dms'] == []

def test_remove_invalid_dm(clear,first_user,second_user):
    response = requests.delete(config.url + 'dm/remove/v1', json = {'token': first_user['token'], 'dm_id': "fake news"})
    assert response.status_code == 400
    
def test_remove_not_creator(clear,first_user,second_user):
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    response = requests.delete(config.url + 'dm/remove/v1', json = {'token': second_user['token'], 'dm_id': dm_id})
    assert response.status_code == 403

def test_remove_not_in_dm(clear,first_user,second_user):
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    response = requests.post(config.url + 'dm/leave/v1', json={'token': first_user['token'], 'dm_id': dm_id})
    response = requests.delete(config.url + 'dm/remove/v1', json = {'token': first_user['token'], 'dm_id': dm_id})
    assert response.status_code == 403
