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

def test_leave_not_owner_successful(first_user, second_user, dm_by_first_user_with_second):
    requests.post(config.url + 'dm/leave/v1', json={'token': second_user['token'], 'dm_id': dm_by_first_user_with_second})
    dm_list = requests.get(config.url + 'dm/list/v1', params={'token': second_user['token']})
    response_data = dm_list.json()
    assert response_data['dms'] == []
    
def test_leave_is_owner_successful(first_user, second_user, dm_by_first_user_with_second):
    requests.post(config.url + 'dm/leave/v1', json={'token': first_user['token'], 'dm_id': dm_by_first_user_with_second})
    dm_list = requests.get(config.url + 'dm/list/v1', params={'token': first_user['token']})
    response_data = dm_list.json()
    assert response_data['dms'] == []

def test_mass_leaving_successful(first_user, second_user, dm_by_first_user_with_second):
    requests.post(config.url + 'dm/leave/v1', json={'token': second_user['token'], 'dm_id': dm_by_first_user_with_second})
    requests.post(config.url + 'dm/leave/v1', json={'token': first_user['token'], 'dm_id': dm_by_first_user_with_second})    
    dm_list = requests.get(config.url + 'dm/list/v1', params={'token': first_user['token']})
    response_data = dm_list.json()
    assert response_data['dms'] == []
    
def test_leave_invalid_dm(first_user, second_user):
    response = requests.post(config.url + 'dm/leave/v1', json={'token': first_user['token'], 'dm_id': "69420"})
    assert response.status_code == 400

def test_leave_not_member(first_user, second_user, dm_by_first_user_with_second):
    third_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango3@gmail.com','password': 'sunnyday','name_first': 'Lustin','name_last': 'Hordon'})
    third_user = third_user.json()
    response = requests.post(config.url + 'dm/leave/v1', json={'token': third_user['token'], 'dm_id': dm_by_first_user_with_second})
    assert response.status_code == 403
