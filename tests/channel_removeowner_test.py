import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from src.channel import channel_addowner_v1, channel_invite_v1, channel_removeowner_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.data_store import data_store

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return
    
@pytest.fixture
def first_user():
    first_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango1@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    response_data = first_user.json()
    return response_data

@pytest.fixture
def second_user():
    second_user = requests.post(config.url + 'auth/register/v2', json={'email': 'grapesmango2@gmail.com','password': 'sunnyday','name_first': 'Dustin','name_last': 'Bordon'})
    response_data = second_user.json() 
    return response_data
    
@pytest.fixture
def first_user_create_channel(first_user):
    channel_id = requests.post(config.url + 'channels/create/v2', json={'token': first_user['token'], 'name': 'Justin', 'is_public' : True})
    response_data = channel_id.json() 
    return response_data 
    
    # Valid input and normal function
def test_removeowner_success(clear, first_user, second_user, first_user_create_channel):
    requests.post(config.url + 'channel/invite/v2', json={'token': first_user['token'], 'channel_id': first_user_create_channel['channel_id'], 'u_id': second_user['auth_user_id']})
    requests.post(config.url + 'channel/addowner/v1', json={'token': first_user['token'], 'channel_id': first_user_create_channel['channel_id'], 'u_id': second_user['auth_user_id']}) 
    response = requests.post(config.url + 'channel/removeowner/v1', json={'token': first_user['token'], 'channel_id': first_user_create_channel['channel_id'], 'u_id': second_user['auth_user_id']})
    response_data = response.json()
    assert response_data == {}
    
    # Does not refer to a valid channel_id
def test_removeowner_error1(clear, first_user, second_user):
    response = requests.post(config.url + 'channel/removeowner/v1', json={'token': first_user['token'], 'channel_id': -1, 'u_id': second_user['auth_user_id']})         
    assert response.status_code == 400

    # U_id does not refer to a valid user
def test_removeowner_error2(clear, first_user, second_user, first_user_create_channel):
    response = requests.post(config.url + 'channel/removeowner/v1', json={'token': first_user['token'], 'channel_id': first_user_create_channel['channel_id'], 'u_id': -1})         
    assert response.status_code == 400 

    # U_id refers to a user who is not an owner
def test_removeowner_error3(clear, first_user, second_user, first_user_create_channel):
    requests.post(config.url + 'channel/invite/v2', json={'token': first_user['token'], 'channel_id': first_user_create_channel['channel_id'], 'u_id': second_user['auth_user_id']}) 
    response = requests.post(config.url + 'channel/removeowner/v1', json={'token': first_user['token'], 'channel_id': first_user_create_channel['channel_id'], 'u_id': second_user['auth_user_id']})         
    assert response.status_code == 400 

    #U_id refers to the ONLY owner of the channel
def test_removeowner_error4(clear, first_user, second_user, first_user_create_channel):
    response = requests.post(config.url + 'channel/removeowner/v1', json={'token': first_user['token'], 'channel_id': first_user_create_channel['channel_id'], 'u_id': first_user['auth_user_id']})         
    assert response.status_code == 400 
    
    #Authorised user does not have channel permissions
def test_removeowner_error5(clear, first_user, second_user, first_user_create_channel):
    requests.post(config.url + 'channel/invite/v2', json={'token': first_user['token'], 'channel_id': first_user_create_channel['channel_id'], 'u_id': second_user['auth_user_id']})  
    response = requests.post(config.url + 'channel/addowner/v1', json={'token': second_user['token'], 'channel_id': first_user_create_channel['channel_id'], 'u_id': second_user['auth_user_id']})        
    assert response.status_code == 403

   
