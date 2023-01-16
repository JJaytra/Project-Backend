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

def test_user_owner_dm(clear, first_user, second_user):
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id = dm_id.json()
    dm_list = requests.get(config.url + 'dm/list/v1', params = {'token': first_user['token']})
    response_data = dm_list.json()
    assert response_data['dms'][0]['dm_id'] == dm_id['dm_id']
    
def test_user_not_owner_dm(clear, first_user,second_user):
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id = dm_id.json()
    dm_list = requests.get(config.url + 'dm/list/v1', params = {'token': second_user['token']})
    response_data = dm_list.json()
    assert response_data['dms'][0]['dm_id'] == dm_id['dm_id']
    
