import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.error import InputError, AccessError
from src.auth import auth_register_v1
from datetime import timezone
import datetime
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
    channel = requests.post(config.url + 'channels/create/v2', json={'token': first_user['token'],'name': "first users channel",'is_public': 'True'})
    response_data = channel.json()
    return response_data['channel_id']

@pytest.fixture
def channel_by_second_user(second_user):
    channel = requests.post(config.url + 'channels/create/v2', json={'token': second_user['token'],'name': "second users channel",'is_public': 'True'})
    response_data = channel.json()
    return response_data['channel_id']

def test_standup_start_one_standup_success(clear,first_user, channel_by_first_user):
    time_before_startup = get_time()
    standup_start = requests.post(config.url + 'standup/start/v1', json={'token': first_user['token'],'channel_id': channel_by_first_user,'length': 5})
    standup_start_finish = standup_start.json()
    expected_time_after_startup = time_before_startup + 5
    assert standup_start_finish['time_finish'] == int(expected_time_after_startup)

def test_standup_start_two_standup_success(clear,first_user,second_user, channel_by_first_user,channel_by_second_user):
    
    time_before_startup = get_time()
    standup_start = requests.post(config.url + 'standup/start/v1', json={'token': first_user['token'],'channel_id': channel_by_first_user,'length': 5})
    standup_start_finish = standup_start.json()
    expected_time_after_startup = time_before_startup + 5
    assert standup_start_finish['time_finish'] == int(expected_time_after_startup)

    time_before_startup = get_time()
    standup_start = requests.post(config.url + 'standup/start/v1', json={'token': second_user['token'],'channel_id': channel_by_second_user,'length': 6})
    standup_start_finish = standup_start.json()
    expected_time_after_startup = time_before_startup + 6
    assert standup_start_finish['time_finish'] == int(expected_time_after_startup)

def test_standup_start_invalid_channel(clear, first_user):
    standup_start = requests.post(config.url + 'standup/start/v1', json={'token': first_user['token'],'channel_id': 69420,'length': 5})
    assert standup_start.status_code == 400

def test_standup_start_invalid_length(clear, first_user, channel_by_first_user):
    standup_start = requests.post(config.url + 'standup/start/v1', json={'token': first_user['token'],'channel_id': channel_by_first_user,'length': -10})
    assert standup_start.status_code == 400

def test_standup_start_standup_already_exists(clear,first_user,channel_by_first_user):
    requests.post(config.url + 'standup/start/v1', json={'token': first_user['token'],'channel_id': channel_by_first_user,'length': 10})
    standup_start = requests.post(config.url + 'standup/start/v1', json={'token': first_user['token'],'channel_id': channel_by_first_user,'length': 5})
    assert standup_start.status_code == 400

def test_standup_start_not_in_channel(clear, first_user, second_user, channel_by_first_user):
    requests.post(config.url + 'standup/start/v1', json={'token': second_user['token'],'channel_id': channel_by_first_user,'length': 10})

def get_time():
    curr_time = datetime.datetime.now(timezone.utc)
    utc_time = curr_time.replace(tzinfo=timezone.utc)
    unix_timestamp = utc_time.timestamp()
    return unix_timestamp
