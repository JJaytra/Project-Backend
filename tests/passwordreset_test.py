import pytest
import requests
import json
from src import config
from src.auth import auth_register_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.tokens import get_userid_from_token

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return

@pytest.fixture
def user():
    user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    response_data = user.json()
    return response_data

    # Reset code is invalid
def test_passwordreset_reset_error1(clear,user):
    response = requests.post(config.url + '/auth/passwordreset/reset/v1', json={'reset_code': 'aaaaa', 'new_password': '123abcd'})        
    assert response.status_code == 400   
    
    # New password entered is less than six characters
def test_passwordreset_reset_error2(clear, user):
    response = requests.post(config.url + '/auth/passwordreset/reset/v1', json={'reset_code': 'aaaaaa', 'new_password': '123ab'})            
    assert response.status_code == 400 

    
