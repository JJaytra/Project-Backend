import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.error import InputError, AccessError
from src.auth import auth_register_v1

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
def channel_by_first_user(first_user):
    channel = requests.post(config.url + 'channels/create/v2', json={'token': first_user['token'],'name': "first users channel",'is_public': True})
    response_data = channel.json()
    return response_data['channel_id']

@pytest.fixture
def channel_by_second_user(second_user):
    channel = requests.post(config.url + 'channels/create/v2', json={'token': second_user['token'],'name': "second users channel",'is_public': True})
    response_data = channel.json()
    return response_data['channel_id']

@pytest.fixture
def dm_by_first_user_with_second(first_user,second_user):
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': first_user['token'], 'u_ids': [second_user['auth_user_id']]})
    dm_id = dm_id.json()
    return dm_id['dm_id']
    #note this makes notification[0] for second be about adding user to dm

def test_notifications_tagged(clear, first_user, second_user, channel_by_first_user, dm_by_first_user_with_second):
    #in channel
    requests.post(config.url + 'channel/join/v2', json={'token': second_user['token'], 'channel_id': channel_by_first_user})
    requests.post(config.url + 'message/send/v1', json={'token': first_user['token'], 'channel_id': channel_by_first_user, 'message': "notice me @dustinbordon senpai"})
    requests.post(config.url + 'message/send/v1', json={'token': first_user['token'], 'channel_id': channel_by_first_user, 'message': "notice me @fake tag"})
    notification = requests.get(config.url + 'notifications/get/v1', params={'token': second_user['token']})
    notification = notification.json()
#    assert notification == "hmm"
    assert notification['notifications'][0]['channel_id'] == channel_by_first_user
    assert notification['notifications'][0]['notification_message'] == "justingordon tagged you in first users channel: notice me @dustinbor"

    #in dm
    requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "@dustinbordon dm me for free money"})
    notification = requests.get(config.url + 'notifications/get/v1', params={'token': second_user['token']})
    notification = notification.json()
#    assert notification == "wtf"
    assert notification['notifications'][0]['dm_id'] == dm_by_first_user_with_second
    assert notification['notifications'][0]['notification_message'] == "justingordon tagged you in dustinbordon, justingordon: @dustinbordon dm me "

def test_notifications_reacted(clear, first_user, second_user, channel_by_first_user, dm_by_first_user_with_second):
    #for channels
    requests.post(config.url + 'channel/join/v2', json={'token': second_user['token'], 'channel_id': channel_by_first_user})
    msg_id = requests.post(config.url + 'message/send/v1', json={'token': first_user['token'], 'channel_id': channel_by_first_user, 'message': "scooby dooby doo"})
    msg_id =  msg_id.json()
    requests.post(config.url + 'message/react/v1', json={'token': second_user['token'], 'message_id': msg_id['message_id'], 'react_id': 1})
    notification = requests.get(config.url + 'notifications/get/v1', params={'token': first_user['token']})
    notification = notification.json()
#    assert notification == "wtf"
    assert notification['notifications'][0]['notification_message'] == f"dustinbordon reacted to your message in first users channel"
    
    #for dms
    message_id = requests.post(config.url + 'message/senddm/v1', json={'token': first_user['token'],'dm_id': dm_by_first_user_with_second, 'message': "react if you think comp1531 is hard"})
    message_id =  message_id.json()
#    assert message_id['message_id'] == "hmm"
    requests.post(config.url + 'message/react/v1', json={'token': second_user['token'], 'message_id': message_id['message_id'], 'react_id': 1})
    notification = requests.get(config.url + 'notifications/get/v1', params={'token': first_user['token']})
    notification = notification.json()
    assert notification['notifications'][0]['channel_id'] == -1
    assert notification['notifications'][0]['notification_message'] == f"dustinbordon reacted to your message in dustinbordon, justingordon"

def test_notifications_added_to_channel_dm(clear, first_user, second_user, channel_by_first_user, dm_by_first_user_with_second):
    #for channels
    requests.post(config.url + 'channel/invite/v2', json={'token': first_user['token'], 'channel_id': channel_by_first_user, 'u_id': second_user['auth_user_id']})
    notification = requests.get(config.url + 'notifications/get/v1', params={'token': second_user['token']})
    notification = notification.json()
    assert notification['notifications'][0]['channel_id'] == channel_by_first_user
    assert notification['notifications'][0]['notification_message'] == "justingordon added you to first users channel"
    
    #for dm
    notification = requests.get(config.url + 'notifications/get/v1', params={'token': second_user['token']})
    notification = notification.json()
    assert notification['notifications'][0]['dm_id'] == dm_by_first_user_with_second
    assert notification['notifications'][0]['notification_message'] == "justingordon added you to dustinbordon, justingordon"
