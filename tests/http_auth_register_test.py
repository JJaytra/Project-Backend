import requests
from src import config
import json
import pytest

from src.tokens import generate_jwt
from src.data_store import data_store

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return

def test_auth_register_success(clear):
    response = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    assert response.status_code == 200



def test_auth_register_invalid_email(clear):
    response = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango', 'password': 'pizzacrust', 'name_first': 'Justin', 'name_last': 'Gordon'})
    assert response.status_code == 400

    
def test_auth_used_email(clear):
    requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango@gmail.com', 'password': 'pizzacrust', 'name_first': 'Justin', 'name_last': 'Gordon'})
    response = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango@gmail.com', 'password': 'pizzacrust', 'name_first': 'Justin', 'name_last': 'Gordon'})
    assert response.status_code == 400

def test_auth_register_short_password(clear):
    response = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango@gmail.com', 'password': 'five1', 'name_first': 'Justin', 'name_last': 'Gordon'})
    assert response.status_code == 400

def test_auth_register_invalid_name_first(clear):
    response = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango@gmail.com', 'password': 'pizzacruist', 'name_first': '', 'name_last': 'Gordon'})
    assert response.status_code == 400

def test_auth_register_invalid_name_last(clear):
    response = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango@gmail.com', 'password': 'five1', 'name_first': 'Justin', 'name_last': ''})
    assert response.status_code == 400







