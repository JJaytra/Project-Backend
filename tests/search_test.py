import pytest
import json
import random
import string
import requests
from src import config
from src.tokens import decode_jwt
from src.helper_functions import return_user_by_id
from src.error import InputError, AccessError

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return
 
# create a user that will be the owner of the channel   
def create_owner():
    registered_user = requests.post(config.url + 'auth/register/v2', json={'email': 'teacher@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    registered_user = registered_user.json()
    return registered_user

# create an user
def create_user():
    registered_user = requests.post(config.url + 'auth/register/v2', json={'email': 'student@gmail.com','password': 'comp1531','name_first': 'Mark','name_last': 'Smith'})
    registered_user = registered_user.json()
    return registered_user

# create a channel
def create_channel(owner_token):
    channel = requests.post(config.url + 'channels/create/v2', json={'token': owner_token, 'name': 'project', 'is_public': "True"})
    channel_info = channel.json()
    return channel_info['channel_id']    



#---------------TESTS----------------------    


# the length of query_str is invalid: < 1 or > 1000 chars   
def test_invalid_query_length(clear):
    owner_token = create_owner()['token']
    
    output = requests.get(config.url + 'search/v1', params={'token': owner_token, 'query_str': ''})
    assert output.status_code == 400
    
    list_of_chrs = string.ascii_lowercase
    long_str = ''.join(random.choice(list_of_chrs) for i in range(1001)) 
    
    output = requests.get(config.url + 'search/v1', params={'token': owner_token, 'query_str': long_str})
    assert output.status_code == 400

# testing case-sensitive query_str, should return an empty dictionary   
def test_case_sensitive(clear):
    owner_token = create_owner()['token']
    
    channel_id = create_channel(owner_token)
    sent = requests.post(config.url + 'message/send/v1', json={'token': owner_token, 'channel_id': channel_id, "message": "Welcome to COMP1531!"})
    assert sent.status_code == 200
    
    search = requests.get(config.url + 'search/v1', params={'token': owner_token, 'query_str': 'comp1531'})
    assert search.status_code == 200
    
    search_output = search.json()

    assert search_output == {'messages': []}
    
# successful query_str searching
def test_found_query(clear):
    owner_token = create_owner()['token']
    
    channel_id = create_channel(owner_token)
    sent = requests.post(config.url + 'message/send/v1', json={'token': owner_token, 'channel_id': channel_id, "message": "Welcome to COMP1531!"})
    assert sent.status_code == 200
    
    chnl_msg = requests.get(config.url + 'channel/messages/v2', params={'token': owner_token, 'channel_id': channel_id, 'start': 0})
    assert chnl_msg.status_code == 200
    msg_data = chnl_msg.json()
    
    search = requests.get(config.url + 'search/v1', params={'token': owner_token, 'query_str': 'COMP1531'})
    assert search.status_code == 200
    search_output = search.json()
    
    assert search_output == {'messages': [{'is_pinned': False, 'message': 'Welcome to COMP1531!', 'message_id': 1, 'reacts': [], 'time_sent': msg_data['messages'][0]['time_sent'], 'u_id': 1}]}
    
        
