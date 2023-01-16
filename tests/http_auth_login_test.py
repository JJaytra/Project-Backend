import requests
from src import config
import json
import pytest


@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return

def test_auth_login_success(clear):
    
    requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    
    login_response = requests.post(config.url + 'auth/login/v2', json={'email': 'grapesmango1@gmail.com', 'password': 'sunnyday'})
    assert login_response.status_code == 200

    
def test_auth_login_invalid_email(clear):
    requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    
    response = requests.post(config.url + 'auth/login/v2', json={'email': 'grapesmango1', 'password': 'sunnyday'})
    assert response.status_code == 400

def test_auth_login_no_account(clear):
    login_response = requests.post(config.url + 'auth/login/v2', json={'email': 'grapesmango1@gmail.com', 'password': 'sunnyday'})
    assert login_response.status_code == 400

def test_auth_login_wrong_password(clear):
    requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})

    login_response = requests.post(config.url + 'auth/login/v2', json={'email': 'grapesmango1@gmail.com', 'password': 'rainyday'})
    assert login_response.status_code == 400