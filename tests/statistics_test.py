import requests
import pytest
import json
from src import config
from src.tokens import decode_jwt, get_userid_from_token
from src.helper_functions import return_user_by_id
from src.error import InputError, AccessError

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return
    
def create_valid_token():
    registered_user = requests.post(config.url + 'auth/register/v2', json={'email': 'student@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    registered_data = registered_user.json()
    return registered_data['token']

#--------------TESTS------------------#

# invalid token
#def test_invalid_token(clear):
    
 #   output = requests.get(config.url + 'user/stats/v1', params={'token': 'abcgedfhsd'})
  #  assert output.status_code == 403


# testing initial state for user - everything 0
def test_initial_data(clear):
    
    user = create_valid_token()
    
    output = requests.get(config.url + 'user/stats/v1', params={'token': user})
    output.status_code == 200
    
    data = output.json()
    assert data == {'user_stats': {'channels_joined': [{'num_channels_joined': 0, 'time_stamp': data['user_stats']['channels_joined'][0]['time_stamp']}],
                                    'dms_joined': [{'num_dms_joined': 0, 'time_stamp': data['user_stats']['dms_joined'][0]['time_stamp']}],
                                    'messages_sent': [{'num_messages_sent': 0, 'time_stamp': data['user_stats']['messages_sent'][0]['time_stamp']}],
                                    'involvement_rate': 0
                                   }}
 
 # testing initia state for workspace                                  
def test_initial_state_for_workspace(clear):
    user = create_valid_token()
    
    output = requests.get(config.url + 'users/stats/v1', params={'token': user})
    output.status_code == 200
    
    data = output.json()
    assert data == {'workspace_stats': {'channels_exist': [{'num_channels_exist': 0, 'time_stamp': data['workspace_stats']['channels_exist'][0]['time_stamp']}],
                                    'dms_exist': [{'num_dms_exist': 0, 'time_stamp': data['workspace_stats']['dms_exist'][0]['time_stamp']}],
                                    'messages_exist': [{'num_messages_exist': 0, 'time_stamp': data['workspace_stats']['messages_exist'][0]['time_stamp']}],
                                    'utilization_rate': 0
                                   }}
    
