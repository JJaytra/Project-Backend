import requests
import pytest
import json
from src import config
from src.tokens import decode_jwt
from src.helper_functions import return_user_by_id
from src.error import InputError, AccessError
from src.auth import auth_register_v1
from src.user import user_profile_v1, users_all_v1

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return
    
def create_valid_token():
    register_response = requests.post(config.url + 'auth/register/v2', json={'email': 'student@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    register_response_data = register_response.json()
    return register_response_data['token']

def create_valid_token2():
    output = requests.post(config.url + 'auth/register/v2', json={'email': 'sasha@gmail.com','password': 'hello sunshine','name_first': 'Sasha','name_last': 'Barisic'})
    output_data = output.json()
    return output_data['token']
  

# passing in an invalid token
def test_invalid_token(clear):    
    create_valid_token()

    output = requests.put(config.url + 'user/profile/setname/v1', json={'token': "abcdef", 'name_first': 'Sasha', 'name_last': 'Barisic'})
    
    output.status_code == 403
  

# test valid input

def test_two_users(clear):
    token1 = create_valid_token()
    create_valid_token2()
   
    response = requests.get(config.url + 'users/all/v1', params={'token': token1})
    assert response.status_code == 200
   
    listed_data = response.json()
    assert listed_data == {'users' : [{'u_id': 1, 'email': 'student@gmail.com', 'name_first': 'Justin','name_last': 'Gordon', 'handle_str': 'justingordon', 'profile_img_url': config.url + 'static/dbrc.jpg'}, 
                                     {'u_id': 2, 'email': 'sasha@gmail.com', 'name_first': 'Sasha','name_last': 'Barisic', 'handle_str': 'sashabarisic', 'profile_img_url': config.url + 'static/dbrc.jpg'}]}

