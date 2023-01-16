from src.data_store import data_store
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from json import dumps
from flask import Flask, request, Response
from src.tokens import check_token_valid, decode_jwt, get_userid_from_token
from datetime import datetime
from src.helper_functions import is_user_valid

def dm_create_v1(token, u_ids):
    '''
    Creates a dm with the owner being the owner of the authorised token and the dm members being the u_ids parsed. The function then returns a dm_id which is an identifier for the specific dm created.

    Arguments:
        token (string)   - special string to identify user, can be decoded to give user id and session id
        u_ids (list of integers)    - list of user ids

    Exceptions:
        InputError  - Occurs when any u_id in u_ids does not refer to a valid user or there are duplicate 'u_id's in u_ids

    Return Value:
        Returns {dm_id} - dict containing 'dm_id' which has the dm id integer attached
    '''

    list_of_names = []
    list_of_ids = []
    list_of_users = []
    list_of_owners = []
    data = data_store.get()

    #making the dm_id
    new_id = 1
    for dm_id in data['dms']:
        if new_id == dm_id['dm_id']:
            new_id += 1

    for user_id in u_ids:
        found_user_with_u_id = False        
        for datastore_id in data['users']:
            if user_id == datastore_id['u_id']:
                list_of_names.append(datastore_id['handle_str'])
                list_of_ids.append(datastore_id['u_id'])
                list_of_users.append(datastore_id)            
                found_user_with_u_id = True
        if not found_user_with_u_id:            
            raise InputError("invalid u_id's given")

    owner_dict = get_user_from_token(token)
    for datastore_id in data['users']:
        if owner_dict['u_id'] == datastore_id['u_id']:
            list_of_names.append(datastore_id['handle_str'])
            list_of_users.append(datastore_id)
            list_of_owners.append(datastore_id)

    #check for dupe id's
    same_ids = 0
    for user_id in list_of_ids:
        for id_to_compare in list_of_ids:
            if user_id == id_to_compare:
                same_ids += 1
        if same_ids == 1:
            same_ids = 0
    if same_ids > 0:
        raise InputError("duplicated ids")

    sorted(list_of_names)
    list_of_names = str(list_of_names)[1:-1]
    list_of_names = list_of_names.replace("'","") #gets rid of quotations
    dm_dict = {
        'dm_id': new_id,
        'name': list_of_names,
        'members': list_of_users,
        'owner': list_of_owners,
        'messages': [],
        'time_stamp': datetime.timestamp(datetime.now())
    }
    data['dms'].append(dm_dict)
    #create notification
    for user in list_of_users:
        if user == owner_dict:
            continue
        notification_dict = {
            'channel_id': -1,
            'dm_id': new_id,
            'notification_message': f"{owner_dict['handle_str']} added you to {list_of_names}",
        }
        user['notifications'].append(notification_dict)
    return {'dm_id': new_id}

def dm_list_v1(token):
    '''
    Generates a list of DM's that the user from the token is part of and returns it.

    Arguments:
        token (string)   - special string to identify user, can be decoded to give user id and session id

    Exceptions:
        None

    Return Value:
        Returns {dms} - dict containing 'dms' which is a list of dms
    '''

    token_user = get_user_from_token(token)
    list_of_dms = []
    data = data_store.get()
    for dm in data['dms']:
        for member in dm['members']:
            if token_user == member:
                dm_to_add =  {
                    'dm_id': dm['dm_id'],
                    'name': dm['name'],
                }
                list_of_dms.append(dm_to_add)
    return {'dms': list_of_dms}

def dm_remove_v1(token, dm_id):
    '''
    Removes a dm based on the dm_id passed if the token is the original dm creator and in the dm.

    Arguments:
        token (string)   - special string to identify user, can be decoded to give user id and session id
        dm_id (integer)    - an id used to determine which specific dm the user wants to remove

    Exceptions:
        InputError  - When any dm_id does not refer to a valid dm
        AccessError - When the user is not in the valid dm        
        AccessError - When the user is not the original creator

    Return Value:
        Nothing
    '''

    token_user = get_user_from_token(token)
    data = data_store.get()
    if is_valid_dm(dm_id) == False:
        raise InputError ("Can't remove, not a valid dm_id")    
    if is_member_of_dm(token_user, dm_id) == False:
        raise AccessError ("Can't remove, not in dm")    
    for dm in data['dms']:
        if dm['dm_id'] == dm_id:
            for owner in dm['owner']:
                if owner['u_id'] == token_user['u_id']:
                    for member in dm['members']:
                        if member == token_user:
                            data['dms'].remove(dm)  
                            return {}
                else:
                    raise AccessError("Can't remove, not owner")

def dm_details_v1(token, dm_id):
    '''
    Provides basic details on dm given that the token user is a member

    Arguments:
        token (string)   - special string to identify user, can be decoded to give user id and session id
        dm_id (integer)    - an id used to determine which specific dm the user wants details

    Exceptions:
        InputError  - When any dm_id does not refer to a valid dm
        AccessError - When the user is not in the valid dm

    Return Value:
        {name, members} - dict containing 'name' which is the name of the dm and 'members' which is a list of users in the dm
    '''

    token_user = get_user_from_token(token)    
    if is_valid_dm(dm_id) == False:
        raise InputError ("Invalid dm given")
    if is_member_of_dm(token_user, dm_id) == False:
        raise AccessError ("Not member of dm")
    dm = get_dm_from_dm_id(dm_id)
    return {'name': dm['name'], 'members': dm['members']}
    
def dm_leave_v1(token, dm_id):
    '''
    Leaves a dm based on the dm_id passed if the token user is in the dm.

    Arguments:
        token (string)   - special string to identify user, can be decoded to give user id and session id
        dm_id (integer)    - an id used to determine which specific dm

    Exceptions:
        InputError  - When any dm_id does not refer to a valid dm
        AccessError - When the user is not in the valid dm        

    Return Value:
        Nothing
    '''

    token_user = get_user_from_token(token)    
    if is_valid_dm(dm_id) == False:
        raise InputError ("Invalid dm given")
    if is_member_of_dm(token_user, dm_id) == False:
        raise AccessError ("Not member of dm")
    dm = get_dm_from_dm_id(dm_id)
    for owner in dm['owner']:
        if owner['email'] == token_user['email']:
            dm['owner'].remove(owner)
    for member in dm['members']:
        if member['email'] == token_user['email']:
            dm['members'].remove(member)
            return
        
def dm_messages_v1(token, dm_id, start):
    '''
    Gets a list of up to 50 messages with their appropriate start/end indexes based on start(see below Arguments->start) and returns the messages alongside the start index and an 'end' integer which is start+50 if there are still messages to be read and is -1 if all messages have been read

    Arguments:
        token (string)   - special string to identify user, can be decoded to give user id and session id
        dm_id (integer)    - an id used to determine which specific dm
        start (integer)    - an integer used to determine the nth most recent message index to start fetching from e.g. 0 is most recent and 9 is 10th most recent. 

    Exceptions:
        InputError  - When any dm_id does not refer to a valid dm
        InputError  - Start is greater than the number of messages
        AccessError - When the user is not in the valid dm

    Return Value:
        {messages, start, end} - dict containing 'messages' which is a list of all the messages with their assosiated information, 'start' which is the same as the one passed, 'end' which is start+50 when there are still messages after to be read and is -1 when there are no more messages to be read/loaded.
    '''

    token_user = get_user_from_token(token)
    data = data_store.get()
    if is_valid_dm(dm_id) == False:
        raise InputError ("Invalid dm given")
    if is_member_of_dm(token_user, dm_id) == False:
        raise AccessError ("Not member of dm")
    dm = get_dm_from_dm_id(dm_id)
    list_of_messages = []
    messages_length = len(dm['messages'])
    most_recent_msg_index = messages_length-1
    messages_start = most_recent_msg_index - start
    if messages_length == 0 and start == 0:
        return {
            'messages' : list_of_messages,
            'start': start,
            'end': -1,
        }
    if messages_start < 0:
        raise InputError ("start is greater than number of messages")        
    end = start + 50
    for index in range(messages_start, messages_start-50, -1):
        if index < 0:
            end = -1
            return {
                'messages' : list_of_messages,
                'start': start,
                'end': end,
            }
        msg_id = dm['messages'][index]
        for message in data['messages']:
            if message['message_id'] == msg_id:
                list_of_messages.append(message)
    return {
        'messages' : list_of_messages,
        'start': start,
        'end': end,
    }

def message_senddm_v1(token, dm_id, message):
    '''
    Sends a message from the user assosiated with the passed token to the dm specified in dm_id. Returns a message id used to identify the specific message sent. Additional note: Messages are stored in the data store and are fetched by seeing which messages are from the specified dm in dm['messages'] which contains a list of message id.

    Arguments:
        token (string)   - special string to identify user, can be decoded to give user id and session id
        dm_id (integer)    - an id used to determine which specific dm
        message (string)    - content of the message that the user wishes to send.

    Exceptions:
        InputError  - When any dm_id does not refer to a valid dm
        InputError  - Length of message is less than 1 or over 1000 characters
        AccessError - When the user is not in the valid dm

    Return Value:
        {message_id} - dict containing 'message_id' which contains the message_id used to identify specific messages sent.
    '''

    data = data_store.get()
    token_user = get_user_from_token(token)
    if is_valid_dm(dm_id) == False:
        raise InputError ("Invalid dm given")
    if is_member_of_dm(token_user, dm_id) == False:
        raise AccessError ("Not member of dm")
    if len(message) < 1 or len(message) > 1000:
        raise InputError(
            "length of message is not within 1 to 1000 characters inclusive")

    data = data_store.get()
    msg_id = len(data['messages']) + 1    
    user_id = (get_user_from_token(token))['u_id']
    new_msg = {
        "message_id": msg_id,
        "u_id": user_id,
        "message": message,
        "time_sent": datetime.timestamp(datetime.now()),
        "reacts": [],
    }

    # append msg to datastore messages
    data['messages'].append(new_msg)
    data_store.set(data)

    # append msg_id to channel['messages']
    dms = data['dms']
    dm = dms[dm_id-1]
    dm['messages'].append(msg_id)

    # Creates a notification if tagging someone
    data = data_store.get()
    tagged_user = ""
    token_handle = token_user['handle_str']
    start_of_tag = False
    edited_message = message + ' '
    for char in edited_message:
        if start_of_tag == True and (char == " " ): 
            start_of_tag = False
            for user in data['users']:
                if user['handle_str'] == tagged_user:
                    notification_dict = {
                        'channel_id': -1,
                        'dm_id': dm_id,
                        'notification_message': f"{token_handle} tagged you in {dm['name']}: {(message[0:20])}",
                    }
#                    raise InputError (notification_dict)
                    user['notifications'].append(notification_dict)
        if start_of_tag == True:
            tagged_user += char
        if char == '@':
            start_of_tag = True
    return msg_id

def get_user_from_token(token):
    token_user = decode_jwt(token)
    data = data_store.get()
    for user in data['users']:
        if token_user['u_id'] == user['u_id']:
            return user

def is_valid_dm(dm_id):
    data = data_store.get()
    for dm in data['dms']:
        if dm['dm_id'] == dm_id:
            return True
    return False
    
def is_member_of_dm(user, dm_id):
    data = data_store.get()
    for dm in data['dms']:
        if dm['dm_id'] == dm_id:
            for member in dm['members']:
                if member == user:
                    return True
    return False
    
def get_dm_from_dm_id(dm_id):
    data = data_store.get()
    for dm in data['dms']:
        if dm['dm_id'] == dm_id:
            return dm

