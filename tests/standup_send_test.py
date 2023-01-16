import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
import time

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
    channel = requests.post(config.url + 'channels/create/v2', json={'token': second_user['token'],'name': "second users channel",'is_public': 'True'})
    response_data = channel.json()
    return response_data['channel_id']

def test_standup_send_one_message(clear,first_user, channel_by_first_user):
    requests.post(config.url + 'standup/start/v1', json={'token': first_user['token'],'channel_id': channel_by_first_user,'length': 3})
    requests.post(config.url + 'standup/send/v1', json={'token': first_user['token'],'channel_id': channel_by_first_user,'message': "test message"})

    #testing that the message is not sent instantly
    messages_in_channel = requests.get(config.url + 'channel/messages/v2', params={'token': first_user['token'], 'channel_id': channel_by_first_user, 'start': 0})
    messages_in_channel = messages_in_channel.json()
    assert messages_in_channel['messages'] == []
    
    #testing that the message has been sent after time length
    time.sleep(3)
    messages_in_channel = requests.get(config.url + 'channel/messages/v2', params={'token': first_user['token'], 'channel_id': channel_by_first_user, 'start': 0})
    messages_in_channel = messages_in_channel.json()
    assert messages_in_channel['messages'][0]['message'] == "justingordon: test message"

def test_standup_send_multiple_message_alongside_non_standup_messages(clear, first_user, second_user, channel_by_first_user):
    requests.post(config.url + 'channel/join/v2', json={'token': second_user['token'], 'channel_id': channel_by_first_user})
    requests.post(config.url + 'standup/start/v1', json={'token': first_user['token'],'channel_id': channel_by_first_user,'length': 5})
    requests.post(config.url + 'message/send/v1', json={'token': first_user['token'], 'channel_id': channel_by_first_user, 'message': "first non-standup message"})
    requests.post(config.url + 'standup/send/v1', json={'token': first_user['token'],'channel_id': channel_by_first_user,'message': "standup message"})
    requests.post(config.url + 'standup/send/v1', json={'token': second_user['token'],'channel_id': channel_by_first_user,'message': "second standup message"})
    requests.post(config.url + 'message/send/v1', json={'token': first_user['token'], 'channel_id': channel_by_first_user, 'message': "second non-standup message"})
    requests.post(config.url + 'message/send/v1', json={'token': first_user['token'], 'channel_id': channel_by_first_user, 'message': "third non-standup message"})

    time.sleep(5)
    messages_in_channel = requests.get(config.url + 'channel/messages/v2', params={'token': first_user['token'], 'channel_id': channel_by_first_user, 'start': 0})
    messages_in_channel = messages_in_channel.json()
    assert messages_in_channel['messages'][0]['message'] ==   "justingordon: standup message\ndustinbordon: second standup message"

def test_standup_send_invalid_channel(clear,first_user):
    standup_msg = requests.post(config.url + 'standup/send/v1', json={'token': first_user['token'],'channel_id': 69420,'message': "test message"})
    assert standup_msg.status_code == 400
    
def test_standup_send_invalid_length(clear, first_user, channel_by_first_user):
    standup_msg = requests.post(config.url + 'standup/send/v1', json={'token': first_user['token'],'channel_id': channel_by_first_user,'message': "scooby dooby doooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo"})
    assert standup_msg.status_code == 400

def test_standup_send_standup_not_active(clear,first_user, channel_by_first_user):
    standup_msg = requests.post(config.url + 'standup/send/v1', json={'token': first_user['token'],'channel_id': channel_by_first_user,'message': "test message"})
    assert standup_msg.status_code == 400

def test_standup_send_not_in_channel(clear, first_user, second_user, channel_by_first_user):
    standup_msg = requests.post(config.url + 'standup/send/v1', json={'token': second_user['token'],'channel_id': channel_by_first_user, 'message': "test message"})
    assert standup_msg.status_code == 403

