import requests
import pytest
import json
from src import config
from src.tokens import decode_jwt
from src.helper_functions import return_user_by_id, get_user_from_token

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
    
# the first name is either too short or too long, while the last name is valid
def test_invalid_firstname(clear):
    person = create_valid_token()
    
    output = requests.get(config.url + 'user/profile/v1', json={'token': person['token'], 'name_first': ' ', 'name_last': 'Barisic'})
    output.status_code == 400

# the last name is short     
def test_invalid_lastname(clear):
    person = create_valid_token()
  
    output = requests.get(config.url + 'user/profile/v1', json={'token': person['token'], 'name_first': 'Sasha', 'name_last': ' '})
    output.status_code == 400
    
# both names don't satisfy the length condition    
def test_both_names_invalid(clear):
    person = create_valid_token()
  
    output = requests.get(config.url + 'user/profile/v1', json={'token': person['token'], 'name_first': ' ', 'name_last': ' '})
    output.status_code == 400
    
# successful case - both names within length boundaries
def test_valid_inputs(clear):
    person = create_valid_token()
   
    output = requests.put(config.url + 'user/profile/setname/v1', json={
        'token': person['token'],
        'name_first': 'Sasha',
        'name_last': 'Barisic'
    })
    assert output.status_code == 200
    
    response = requests.get(config.url + 'user/profile/v1', params={'token': person['token'], 'u_id': person['auth_user_id']})
    assert response.status_code == 200
    
    changed_data = response.json()
    assert changed_data == {'user': {'u_id': 1, 'email': 'student@gmail.com', 'name_first': 'Sasha', 'name_last': 'Barisic', 'handle_str': 'justingordon', 'profile_img_url': config.url + 'static/dbrc.jpg'}}
