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
   
def test_dm_create_invalid_token(clear, first_user, second_user):
    response = requests.post(config.url + 'dm/create/v1', json={'token': "The limit does not exist!", 'u_ids': [second_user['auth_user_id']]})
    assert response.status_code == 500

def test_dm_create_one_uid(clear, first_user, second_user):
    response = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    response = response.json()
    details = requests.get(config.url + 'dm/details/v1', params= {'token': first_user['token'], 'dm_id': response['dm_id']})
    response_data = details.json() 
    member_with_user_id = False
    if (response_data['members'][1]['u_id'] == second_user['auth_user_id'] or response_data['members'][0]['u_id'] == second_user['auth_user_id']):
        member_with_user_id = True
    assert member_with_user_id == True
    

def test_dm_create_multiple_uid(clear, first_user, second_user):
    third_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango3@gmail.com','password': 'sunnyday','name_first': 'Third','name_last': 'User'})
    third_user = third_user.json()
    response = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id'], third_user['auth_user_id']]})
    dm_id = response.json()
    details = requests.get(config.url + 'dm/details/v1', params= {'token': first_user['token'], 'dm_id': dm_id['dm_id']})
    response_data = details.json()
    member_with_user_id = False
    if (response_data['members'][1]['u_id'] == second_user['auth_user_id'] or response_data['members'][0]['u_id'] == second_user['auth_user_id']):
        member_with_user_id = True
    assert member_with_user_id == True
    
def test_dm_create_uid_invalid_user(clear, first_user, second_user):
    response = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [(second_user['auth_user_id']+first_user['auth_user_id'])]})
    assert response.status_code == 400

def test_dm_create_uid_dupe_user(clear, first_user, second_user):
    response = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id'], second_user['auth_user_id']]})
    assert response.status_code == 400
