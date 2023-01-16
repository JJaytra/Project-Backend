import requests
import pytest
import json
from src import config
from src.tokens import decode_jwt
from src.helper_functions import return_user_by_id
from src.error import InputError, AccessError

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return
    
def create_valid_token():
    register_response = requests.post(config.url + 'auth/register/v2', json={'email': 'student@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    register_response_data = register_response.json()
    return register_response_data
 

# passing in an invalid token
def test_invalid_token(clear):
    create_valid_token()
    
    output = requests.put(config.url + 'user/profile/setname/v1', json={'token': "abcdef", 'name_first': 'Sasha', 'name_last': 'Barisic'})
    
    output.status_code == 403
  

# invalid length of handle 
def test_invalid_length(clear):
    token = create_valid_token()
    
    output = requests.put(config.url + 'user/profile/sethandle/v1', json={'token': token['token'], 'handle_str': 'justingordonjustingordon123'})
    output.status_code == 400

   
# handle contains chars that aren't alphanumeric
def test_invalid_chars(clear):
    token = create_valid_token()
    
    output = requests.put(config.url + 'user/profile/sethandle/v1', json={'token': token['token'], 'handle_str': 'justin**/**||**/**gordon'})
    output.status_code == 400   

# handle is used by another user when changing
def test_handle_used_already(clear):
    token = create_valid_token()

    output = requests.put(config.url + 'user/profile/sethandle/v1', json={'token': token['token'], 'handle_str': 'justingordon'})
    output.status_code == 400
    
# successful case
def test_good_handle(clear):
    token = create_valid_token()

    output = requests.put(config.url + 'user/profile/sethandle/v1', json={'token': token['token'], 'handle_str': 'sashabarisic1'})
    assert output.status_code == 200
    
    response = requests.get(config.url + 'user/profile/v1', params={'token': token['token'], 'u_id': token['auth_user_id']})
    assert response.status_code == 200
    
    changed_data = response.json()
    assert changed_data == {'user': {'u_id': 1, 'email': 'student@gmail.com', 'name_first': 'Justin', 'name_last': 'Gordon', 'handle_str': 'sashabarisic1', 'profile_img_url': config.url + 'static/dbrc.jpg'}}
