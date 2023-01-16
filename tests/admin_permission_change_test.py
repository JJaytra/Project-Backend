import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.error import InputError, AccessError
from src.auth import auth_register_v1
from src.admin import admin_userpermission_change_v1

#first user is owner
@pytest.fixture
def first_user():
    requests.delete(config.url + 'clear/v1', json = {})
    first_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    response_data = first_user.json()
    return response_data

#second user is not owner
@pytest.fixture
def second_user():
    second_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango2@gmail.com','password': 'sunnyday','name_first': 'Dustin','name_last': 'Bordon'})
    response_data = second_user.json()
    return response_data

def test_admin_perms_change_to_owner_success(first_user, second_user):
    requests.post(config.url + 'admin/userpermission/change/v1', json={'token': first_user['token'], 'u_id': second_user['auth_user_id'], 'permission_id': 1})
    response = requests.delete(config.url + 'admin/user/remove/v1', json={'token': second_user['token'], 'u_id': first_user['auth_user_id']})
    assert response.status_code == 200

def test_admin_perms_change_to_member_success(first_user, second_user):
    requests.post(config.url + 'admin/userpermission/change/v1', json={'token': first_user['token'], 'u_id': second_user['auth_user_id'], 'permission_id': 1})
    requests.post(config.url + 'admin/userpermission/change/v1', json={'token': first_user['token'], 'u_id': second_user['auth_user_id'], 'permission_id': 2})
    response = requests.delete(config.url + 'admin/user/remove/v1', json={'token': second_user['token'], 'u_id': first_user['auth_user_id']})
    assert response.status_code == 403

def test_admin_permission_change_invalid_user(first_user):
    response = requests.post(config.url + 'admin/userpermission/change/v1', json = {'token': first_user['token'], 'u_id': "spongebob", 'permission_id': 1})
    assert response.status_code == 400

def test_admin_permission_change_sole_owner_demoting_himself(first_user):
    response = requests.post(config.url + 'admin/userpermission/change/v1', json = {'token': first_user['token'], 'u_id': first_user['auth_user_id'], 'permission_id': 2})
    assert response.status_code == 400

def test_admin_permission_change_invalid_permission_id(first_user, second_user):
    response = requests.post(config.url + 'admin/userpermission/change/v1', json = {'token': first_user['token'], 'u_id': second_user['auth_user_id'], 'permission_id': 69})
    assert response.status_code == 400

def test_admin_permission_change_changing_to_existing_permission(first_user, second_user):
    response = requests.post(config.url + 'admin/userpermission/change/v1', json = {'token': first_user['token'], 'u_id': second_user['auth_user_id'], 'permission_id': 2})
    assert response.status_code == 400
    
def test_admin_permission_change_not_owner(first_user, second_user):
    response = requests.post(config.url + 'admin/userpermission/change/v1', json = {'token': second_user['token'], 'u_id': second_user['auth_user_id'], 'permission_id': 1})
    assert response.status_code == 403
