import requests
import pytest
import json
from src import config
from src.tokens import decode_jwt, get_userid_from_token
from src.helper_functions import return_user_by_id, get_user_from_token
from src.user import user_profile_v1

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return

def create_valid_token():
    register_response = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    register_response_data = register_response.json()
    return register_response_data

# user_id is not valid 
def test_invalid_user_id(clear): 
    
    token = create_valid_token()
    output = requests.get(config.url + 'user/profile/v1', json={'token': token['token'], 'u_id': -50})
    
    output.status_code == 403
    
    
# successful_case        
def test_successful_case(clear):
 
    token = create_valid_token()
    
    response = requests.get(config.url + 'user/profile/v1', params={'token': token['token'], 'u_id': token['auth_user_id']})
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {'user': {'u_id': 1, 'email': 'grapesmango1@gmail.com', 'name_first': 'Justin', 'name_last': 'Gordon', 'handle_str': 'justingordon', 'profile_img_url': config.url + 'static/dbrc.jpg'}}

