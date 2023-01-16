from src.data_store import data_store
from src.error import InputError, AccessError
from datetime import timezone
import datetime
from src.message import message_send_v1
from src.helper_functions import channel_lookup, is_user_in_channel
from src.tokens import check_token_valid, decode_jwt, get_userid_from_token
import threading
import time

def standup_start_v1(token, channel_id, length):
    data = data_store.get()
    token_user = get_user_from_token(token)

    if channel_lookup(channel_id) == False:
        raise InputError("channel id does not exist")
    if is_user_in_channel(token_user['u_id'], channel_id) == False:
        raise AccessError("user is not a member of channel")
    if length < 0:
        raise InputError("time length cannot be negative")
    for standup in data['standups']:
        if standup['channel_id'] == channel_id:
            raise InputError("an active standup is already currently running in this channel")
    
    time_with_date = datetime.datetime.now(timezone.utc)
    utc_time = time_with_date.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    init_standup_dict = {'channel_id':channel_id, 'token':token, 'message':"",'time_finish': int(utc_timestamp + length)}
    data['standups'].append(init_standup_dict)
    standup_begin = threading.Timer(length, standup_finish, args =[channel_id])
    standup_begin.start()

    return {'time_finish': int(utc_timestamp + length)}
    
def standup_finish(channel_id):
    data = data_store.get()
    for standup in data['standups']:
        if channel_id == standup['channel_id']:
            if standup['message'] == "":
                data['standups'].remove(standup)
                return()
            token = standup['token']
            channel_id = standup['channel_id']
            message =  standup['message']
            message = message.strip() #remove trailing new lines
            message_send_v1(token, channel_id, message)
            data['standups'].remove(standup)
            return()
    return()

def standup_send_v1(token, channel_id, message):
    data = data_store.get()
    token_user = get_user_from_token(token)
    if channel_lookup(channel_id) == False:
        raise InputError("channel id does not exist")
    if is_user_in_channel(token_user['u_id'], channel_id) == False:
        raise AccessError("user is not a member of channel")
    if len(message) > 1000:
        raise InputError("length of message is too long (over 1000 char)")
    standup_found = False
    for standup in data['standups']:
        if standup['channel_id'] == channel_id:
            standup_found = True
    if standup_found == False:
        raise InputError("no standup currently exists in this channel")

    token_user_handle = token_user['handle_str']
    message_to_append = f"{token_user_handle}: {message}\n"
    for standup in data['standups']:
        if channel_id == standup['channel_id']:
            standup['message'] += (message_to_append)
            return{}
            
def standup_active_v1(token, channel_id):
    data = data_store.get()
    token_user = get_user_from_token(token)
    if channel_lookup(channel_id) == False:
        raise InputError("channel id does not exist")    
    if is_user_in_channel(token_user['u_id'], channel_id) == False:
        raise AccessError("user is not a member of channel")
    for standup in data['standups']:
        if standup['channel_id'] == channel_id:
            return {'is_active': True, 'time_finish': standup['time_finish']}
    return {'is_active': False, 'time_finish': None}

def get_user_from_token(token):
    token_user = decode_jwt(token)
    data = data_store.get()
    for user in data['users']:
        if token_user['u_id'] == user['u_id']:
            return user
