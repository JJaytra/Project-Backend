import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from src.dm import dm_create_v1

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return

#first user is owner
@pytest.fixture
def first_user():
    first_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    response_data = first_user.json()
    return response_data

#second user is not owner
@pytest.fixture
def second_user():
    second_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango2@gmail.com','password': 'sunnyday','name_first': 'Dustin','name_last': 'Bordon'})
    response_data = second_user.json()
    return response_data

@pytest.fixture
def first_users_channel(first_user,second_user):
    first_users_channel = requests.post(config.url + 'channels/create/v2', json = {'token': first_user['token'], 'name': "test_name", 'is_public': "True"})
    first_users_channel = (first_users_channel.json())['channel_id']
    requests.post(config.url + 'channel/join/v2', json = {'token': second_user['token'], 'channel_id': first_users_channel})
    return first_users_channel

@pytest.fixture
def first_users_dm(first_user,second_user):
    first_users_dm = requests.post(config.url + 'dm/create/v1', json = {'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    first_users_dm = (first_users_dm.json())['dm_id']
    return first_users_dm
    

def test_admin_remove_channel_and_dm_successful(clear, first_user,second_user,first_users_channel,first_users_dm):
    requests.post(config.url + 'message/senddm/v1', json={'token': second_user['token'],'dm_id': first_users_dm, 'message': "second users message not removed"})
    requests.delete(config.url + 'admin/user/remove/v1', json = {'token': first_user['token'], 'u_id': second_user['auth_user_id']})
    dm_messages = requests.get(config.url + 'dm/messages/v1', params = {'token': first_user['token'], 'dm_id': first_users_dm, 'start': 0})
    messages_data = dm_messages.json()
    assert messages_data['messages'][0]['message'] == "Removed user"
    user_profile = requests.get(config.url + 'user/profile/v1', params = {'token': first_user['token'], 'u_id': second_user['auth_user_id']})
    user_data = user_profile.json()
    assert user_data['user']['name_first'] == "Removed"
    assert user_data['user']['name_last'] == "user"
    
    #check if email & handle still reuseable
    second_user_same_email = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango2@gmail.com','password': 'sunnyday','name_first': 'Dustin','name_last': 'Bordon'})
    second_user_same_email = second_user_same_email.json()
    user_profile = requests.get(config.url + 'user/profile/v1', params = {'token': second_user_same_email['token'], 'u_id': second_user_same_email['auth_user_id']})
    user_data = user_profile.json()
    assert user_data['user']['name_first'] == "Dustin"
    assert user_data['user']['name_last'] == "Bordon"
    assert user_data['user']['email'] == "grapesmango2@gmail.com"
    
#using change permissions to make second user remove first user instead
def test_admin_remove_channel_and_dm_owners_successful(clear, first_user,second_user,first_users_channel,first_users_dm):
    requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango3@gmail.com','password': 'sunnyday','name_first': 'Lustin','name_last': 'Hordon'})
    requests.post(config.url + 'admin/userpermission/change/v1', json={'token': first_user['token'], 'u_id': second_user['auth_user_id'], 'permission_id': 1})
    requests.post(config.url + 'message/senddm/v1', json={'token': second_user['token'],'dm_id': first_users_dm, 'message': "second users message not removed"})
    requests.delete(config.url + 'admin/user/remove/v1', json = {'token': second_user['token'], 'u_id': first_user['auth_user_id']})
    user_profile = requests.get(config.url + 'user/profile/v1', params = {'token': second_user['token'], 'u_id': first_user['auth_user_id']})
    user_data = user_profile.json()
    assert user_data['user']['name_first'] == "Removed"
    assert user_data['user']['name_last'] == "user"

def test_admin_remove_invalid_uid(clear, first_user):
    response = requests.delete(config.url + 'admin/user/remove/v1', json = {'token': first_user['token'], 'u_id': "spongebob squarepants"})
    assert response.status_code == 400

def test_admin_remove_global_owner_removing_only_global_owner(clear, first_user):
    response = requests.delete(config.url + 'admin/user/remove/v1', json = {'token': first_user['token'], 'u_id': first_user['auth_user_id']})
    assert response.status_code == 400

def test_admin_remove_not_a_global_owner(clear, first_user, second_user):
    response = requests.delete(config.url + 'admin/user/remove/v1', json= {'token': second_user['token'], 'u_id': first_user['auth_user_id']})
    assert response.status_code == 403

