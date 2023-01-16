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
def dm_by_first_user(first_user,second_user):
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id = dm_id.json()
    return dm_id['dm_id']

def test_details_succesful(first_user,second_user,dm_by_first_user):
    dm_details = requests.get(config.url + 'dm/details/v1', params = {'token': first_user['token'], 'dm_id': dm_by_first_user})
    response_data = dm_details.json()
    member_with_user_id = False
    if (response_data['members'][0]['email'] == "grapesmango2@gmail.com" or response_data['members'][1]['email'] == "grapesmango2@gmail.com"):
        member_with_user_id = True
    assert member_with_user_id == True
    
def test_details_invalid_dm(first_user,second_user,dm_by_first_user):
    dm_details = requests.get(config.url + 'dm/details/v1', params = {'token': first_user['token'], 'dm_id': "fake news"})
    assert dm_details.status_code == 400
    
def test_details_not_dm_member(first_user,second_user,dm_by_first_user):
    third_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango3@gmail.com','password': 'sunnyday','name_first': 'Lustin','name_last': 'Hordon'})
    third_user = third_user.json()
    dm_details = requests.get(config.url + 'dm/details/v1', params = {'token': third_user['token'], 'dm_id': dm_by_first_user})
    assert dm_details.status_code == 403
