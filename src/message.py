from src.helper_functions import is_user_in_dm
from src.data_store import data_store
from src.error import InputError, AccessError
from src.tokens import check_token_valid, decode_jwt, get_userid_from_token
from datetime import date, datetime, timezone


import threading
import time

from src.helper_functions import channel_lookup, is_user_in_channel, search_msg_in_channels_and_dms_user_in, has_msg_edit_perms, is_owner, has_msg_pin_perms, dm_lookup
from src.tokens import get_userid_from_token
from src.dm import message_senddm_v1

from src.helper_functions import channel_lookup, is_user_in_channel, search_msg_in_channels_and_dms_user_in, has_msg_edit_perms, is_owner, has_msg_pin_perms, is_msg_in_channel, is_msg_in_dm
from src.notifications import get_user_from_token


def message_send_v1(token, channel_id, message):
    """ Send a message from an authorised user to a channel specified by channel id

    Returns:
        message_id (int)
    """


    if not check_token_valid(token):
        raise AccessError("Token is invalid")

    if not channel_lookup(channel_id):
        raise InputError("channel_id does not refer to a valid channel")

    if len(message) < 1 or len(message) > 1000:
        raise InputError(
            "length of message is not within 1 to 1000 characters inclusive")
    # Raise access error if user is not member of the channel
    user = decode_jwt(token)
    user_id = user['u_id']
    if not is_user_in_channel(user_id, channel_id):
        raise AccessError("Authorised user is not a member of the channel")

    # Creates a notification if tagging someone
    data = data_store.get()
    tagged_user = ""
    token_handle = (get_user_from_token(token)['handle_str'])
    start_of_tag = False
    channel_name = data['channels'][channel_id-1]['name']
    for char in message:
        if start_of_tag == True and (char == " " ): #or char == message[-1]
            start_of_tag = False
            for user in data['users']:
                if user['handle_str'] == tagged_user:
                    notification_dict = {
                        'channel_id': channel_id,
                        'dm_id': -1,
                        'notification_message': f"{token_handle} tagged you in {channel_name}: {(message[0:20])}",
                    }
                    user['notifications'].append(notification_dict)
#                    raise InputError(notification_dict)
        if start_of_tag == True:
            tagged_user += char
        if char == '@':
            start_of_tag = True

    data = data_store.get()
    msg_id = len(data['messages']) + 1

    new_msg = {
        "message_id": msg_id,
        "u_id": user_id,
        "message": message,
        "time_sent": int(datetime.timestamp(datetime.now())),
        "reacts": [],
        "is_pinned": False,


    }
    # add that data to the stats of that user_id
    
    for user in data['users']:
        if user_id == user['u_id']:
            stats = user['user_stats']
            num_sent = len(stats['messages_sent']) 
            msg_sent = {'num_messages_sent': num_sent, 'time_stamp': datetime.timestamp(datetime.now())}
            stats['messages_sent'].append(msg_sent)
    #data_store.set(data)
    
    # append msg to datastore messages
    data['messages'].append(new_msg)
    data_store.set(data)

    # append msg_id to channel['messages']
    channels = data['channels']
    channel = channels[channel_id-1]
    channel['messages'].append(msg_id)

    return msg_id


def message_edit_v1(token, message_id, message):
    """
    Given a message, update its text with new text. If the new message is an empty string, the message is deleted.
    """

    if not check_token_valid(token):
        raise AccessError("Token is invalid")
    user = decode_jwt(token)
    user_id = user['u_id']

    if len(message) > 1000:
        raise InputError(
            "Length of message must be within 1 to 1000 characters inclusive")

    if not search_msg_in_channels_and_dms_user_in(user_id, message_id):
        raise InputError(
            "message_id does not refer to a valid message within a channel/DM that the authorised user has joined")

    if not has_msg_edit_perms(user_id, message_id):
        raise AccessError("Msg was not send by user and user does not have owner permissions")

    data = data_store.get()
    messages = data['messages']
    msg = messages[message_id-1]

    if len(message) < 1:
        msg.clear()
    else:
        msg['message'] = message

    return

def message_remove_v1(token, message_id):
    """
    Given a message_id for a message, this message is removed from the channel/DM
    """
    if not check_token_valid(token):
        raise AccessError("Token is invalid")
    user = decode_jwt(token)
    user_id = user['u_id']

    if not search_msg_in_channels_and_dms_user_in(user_id, message_id):
        raise InputError(
            "message_id does not refer to a valid message within a channel/DM that the authorised user has joined")

    if not has_msg_edit_perms(user_id, message_id):
        raise AccessError("Msg was not send by user and user does not have owner permissions")


    data = data_store.get()
    channels = data['channels']
    for channel in channels:
        if message_id in channel['messages']:
            channel['messages'].remove(message_id)
    data = data_store.get()
    for dm in data['dms']:
        if message_id in dm['messages']:
            dm['messages'].remove(message_id)

    return



def message_react_v1(token, message_id, react_id):
    """
    Given a message within a channel or DM the authorised user is part of, add a "react" to that particular message.

    token: token -> converted to u_id and session_id
    message_id: int identifier for message
    react_id int identifier for react

    Returns:
        {}
    """
    # Input Error raised if token is invalid
    if not check_token_valid(token):
        raise AccessError("Invalid Token")

    u_id = get_userid_from_token(token)

    # Input Error is raised if msg_id is not in a channel or dm user is in
    if not search_msg_in_channels_and_dms_user_in(u_id, message_id):
        raise InputError("message_id is not a valid message within a channel or DM that the authorised user has joined")

    # Input Error raised if react_id not valid, only react_id == 1 is valid
    if react_id != 1:
        raise InputError("react_id is not a valid react ID")
    
    data = data_store.get()
    messages = data['messages']
    message = messages[message_id-1]

    if len(message['reacts']) > 0:
        for react in message['reacts']:
            if react['react_id'] == react_id:
                if u_id in react['u_ids']:
                    raise InputError("User has already reacted to this message")
                else:
                    react['u_ids'].append(u_id)
                    return 

    #create notification that it has been reacted
    token_handle = (get_user_from_token(token)['handle_str'])
    channel_id = -1
    dm_id = -1
    for dm in data['dms']:
        for dm_message in dm['messages']:
            if dm_message == message_id:
                dm_chan_name = dm['name']
                dm_id = dm['dm_id']
    for channel in data['channels']:
        for ch_message in channel['messages']:
            if ch_message == message_id:
                dm_chan_name = channel['name']
                channel_id = channel['channel_id']
#                raise InputError("hm")
    for message in data['messages']:
        if message['message_id'] == message_id:
            senders_id = message['u_id']
    for user in data['users']:
        if user['u_id'] == senders_id:
            notification_dict = {
                'channel_id': channel_id,
                'dm_id': dm_id,
                'notification_message': f"{token_handle} reacted to your message in {dm_chan_name}",
            }
            user['notifications'].append(notification_dict)



    new_react = {
        'react_id': react_id,
        'u_ids': [u_id],
        'is_this_user_reacted': True,
    }

    message['reacts'].append(new_react)


    return


def message_unreact_v1(token, message_id, react_id):
    """
    Given a message within a channel or DM the authorised user is part of, remove a "react" to that particular message.

    token: token -> converted to u_id and session_id
    message_id: int identifier for message
    react_id int identifier for react

    Returns:
        {}

    """
    
    # Input Error raised if token is invalid
    if not check_token_valid(token):
        raise AccessError("Invalid Token")

    u_id = get_userid_from_token(token)

    # Input Error is raised if msg_id is not in a channel or dm user is in
    if not search_msg_in_channels_and_dms_user_in(u_id, message_id):
        raise InputError("message_id is not a valid message within a channel or DM that the authorised user has joined")

    # Input Error raised if react_id not valid, only react_id == 1 is valid
    if react_id != 1:
        raise InputError("React_id is not a valid react ID")

    
    if not find_react(react_id, message_id):
        raise InputError("The message does not contain a react with ID react_id from the authorised user")

    data = data_store.get()
    messages = data['messages']
    message = messages[message_id-1]
    for react in message['reacts']:
        if react['react_id'] == react_id:
            react['u_ids'].remove(u_id)
    

    return 

def find_react(react_id, message_id):
    data = data_store.get()
    messages = data['messages']
    message = messages[message_id-1]
    for react in message['reacts']:
        if react['react_id'] == react_id:
            return True
    return False


def message_pin_v1(token, message_id):
    """
    Given a message within a channel or DM, mark it as "pinned".

    token: token -> converted to u_id and session_id
    message_id: int identifier for message

    returns {}
    """

    # Raise access error if token invalid
    if not check_token_valid(token):
        raise AccessError("Invalid Token")

    u_id = get_userid_from_token(token)

    # Input Error is raised if msg_id is not in a channel or dm user is in
    if not search_msg_in_channels_and_dms_user_in(u_id, message_id):
        raise InputError("message_id is not a valid message within a channel or DM that the authorised user has joined")
    
    data = data_store.get()
    messages = data['messages']
    message = messages[message_id-1]
    # Input Error if message is already pinned
    if message["is_pinned"] == True:
        raise InputError("The message is already pinned")
    
    # Access Error if user does not have owner permissions
    if not has_msg_pin_perms(u_id, message_id):
        raise AccessError("message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM")
    
    message['is_pinned'] = True
    data_store.set(data)

    return


def message_unpin_v1(token, message_id):
    """
    Given a message within a channel or DM, remove its mark as pinned.

    token: token -> converted to u_id and session_id
    message_id: int identifier for message
    
    returns {}
    """

     # Raise access error if token invalid
    if not check_token_valid(token):
        raise AccessError("Invalid Token")

    u_id = get_userid_from_token(token)

    # Input Error is raised if msg_id is not in a channel or dm user is in
    if not search_msg_in_channels_and_dms_user_in(u_id, message_id):
        raise InputError("message_id is not a valid message within a channel or DM that the authorised user has joined")
    
    data = data_store.get()
    messages = data['messages']
    message = messages[message_id-1]
    # Input Error if message is not already pinned
    if message["is_pinned"] == False:
        raise InputError("The message is not already pinned")

    # Access Error if user does not have owner permissions
    if not has_msg_pin_perms(u_id, message_id):
        raise AccessError("message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM")
    
    message['is_pinned'] = False
    data_store.set(data)
    return



def message_sendlater_v1(token, channel_id, message, time_sent):
    """
    Send a message from the authorised user to the channel specified by channel_id automatically at a specified time in the future.

    Args:
    token: a jwt of u_id and session_id
    channel_id: int identifer of channel
    message: string contained message
    time_sent: time message should be sent

    Returns:
    Message_id: int identifier of message
    """

    time_sent = float(time_sent)

    if not check_token_valid(token):
        raise AccessError("Invalid Token")
    
    if not channel_lookup(channel_id):
        raise InputError("Invalid channel_id")

    if len(message) < 1 or len(message) > 1000:
        raise InputError("Message has to be between 1 and 1000 characters inclusive")
        
    u_id = get_userid_from_token(token)

    if not is_user_in_channel(u_id, channel_id):
        raise AccessError("User is not in the channel")


    countdown = time_sent - float(time.time())
    if countdown < 0:
        raise InputError("Time_sent has to indicate a future time")

    data = data_store.get()
    placeholder_message_id = message_send_v1(token, channel_id, "FAKE MESSAGE")
    message_sending = threading.Timer(countdown, message_sendlater_channel_finish, args = [token, channel_id, message, placeholder_message_id])
    message_sending.start()

    #create invalid message id from messages
    for message in data['messages']:
        if placeholder_message_id == message['message_id']:
            message['message_id'] = (message['message_id']*-1)
    #remove msg id from channel messages
    for channel in data['channels']:
        for message in channel['messages']:
            if placeholder_message_id == message:
                channel['messages'].remove(message)
    return placeholder_message_id

def message_sendlater_channel_finish(token, channel_id, message, placeholder_message_id):
    new_message_id = message_send_v1(token, channel_id, message)
    
    data = data_store.get()
    for message in data['messages']:
        if new_message_id == (message['message_id']):
            message_to_replace = message
            message_to_replace['message_id'] = placeholder_message_id
            data['messages'].remove(message)

    for channel in data['channels']:
        for message in channel['messages']:
            if message == new_message_id:
                channel['messages'].remove(message)
        if channel['channel_id'] == channel_id:
            channel['messages'].append(placeholder_message_id)

    for message in data['messages']:
        if placeholder_message_id == (message['message_id']*-1):
            i = data['messages'].index(message)
            data['messages'] = data['messages'][:i]+[message_to_replace]+data['messages'][i+1:]
    return()

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    """
    Send a message from the authorised user to the DM specified by dm_id automatically at a specified time in the future.

    Args:
    token: a jwt of u_id and session_id
    dm_id: int identifer of dmS
    message: string contained message
    time_sent: time message should be sent

    Returns:
    Message_id: int identifier of message
    """

    if not check_token_valid(token):
        raise AccessError("Invalid Token")

    if not dm_lookup(dm_id):
        raise InputError("Invalid DM")

    if len(message) < 1 or len(message) > 1000:
        raise InputError("Message must be within 1 to 1000 characters inclusive")
    
    countdown = time_sent - time.time()
    if countdown < 0:
        raise InputError("time_sent must indicate a time in the future")

    u_id = get_userid_from_token(token)

    if not is_user_in_dm(u_id, dm_id):
        raise AccessError("User is not in the dm")
    
    data = data_store.get()
    placeholder_message_id = message_senddm_v1(token, dm_id, "FAKE MESSAGE")
    message_sending_dm = threading.Timer(countdown, message_sendlater_dm_finish, args = [token, dm_id, message, placeholder_message_id])
    message_sending_dm.start()
    for message in data['messages']:
        if placeholder_message_id == message['message_id']:
            message['message_id'] = (message['message_id']*-1) #convert to neg so its invalid
    for dm in data['dms']:
        for message in dm['messages']:
            if placeholder_message_id == message:
                dm['messages'].remove(message)
    return placeholder_message_id

def message_sendlater_dm_finish(token, dm_id, message, placeholder_message_id):
    new_message_id = message_senddm_v1(token, dm_id, message)
    
    data = data_store.get()
    for message in data['messages']:
        if new_message_id == (message['message_id']):
            message_to_replace = message
            message_to_replace['message_id'] = placeholder_message_id
            data['messages'].remove(message)

    for dm in data['dms']:
        for message in dm['messages']:
            if message == new_message_id:
                dm['messages'].remove(message)
        if dm['dm_id'] == dm_id:
            dm['messages'].append(placeholder_message_id)

    for message in data['messages']:
        if placeholder_message_id == (message['message_id']*-1):
            i = data['messages'].index(message)
            data['messages'] = data['messages'][:i]+[message_to_replace]+data['messages'][i+1:]

    return()

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    """
    Share a message to another channel with an optional attached message

    Args:
        token (jwt): jwt of u_id and session_id
        og_mesage_id (int): identifier for original message
        message (str): string for optional additional message
        channel_id (int): identifer for channel. is -1 if message is being shared to dm
        dm_id (int): identifer for dm. is -1 is message being shared to channel

    Returns:
        shared_message_id (int): identifer for the shared message


    Example:
        If the original message is: 
            Hello there!

        The shared message should be:
           Wow, this is a shared message!
           '''
            Hello There!
           '''
    """

    if not channel_lookup(channel_id) and not dm_lookup(dm_id):
        raise InputError("Both channel and dms are invalid")

    if channel_id != -1 and dm_id != -1:
        raise InputError("Either channel_id or dm_id must be -1")
    
    u_id = get_userid_from_token(token)

    if not search_msg_in_channels_and_dms_user_in(u_id, og_message_id):
        raise InputError("Original message must be in a channel/dm user is in")
    
    if len(message) > 1000:
        raise InputError("Message cannot be over 1000 characters")

    if not is_user_in_channel(u_id, channel_id) and not is_user_in_dm(u_id, dm_id):
        raise AccessError("User is not in the channel/dm specified")

    data = data_store.get()
    messages = data['messages']
    og_message = messages[og_message_id-1]['message']
    new_message_str = message + '\n' + "    '" + og_message + "'"
    
    data = data_store.get()
    msg_id = len(data['messages']) + 1

    new_shared_msg = {
        "message_id": msg_id,
        "u_id": u_id,
        "message": new_message_str,
        "time_sent": datetime.timestamp(datetime.now()),
        "reacts": [],
        "is_pinned": False,

    }

    data['messages'].append(new_shared_msg)

    if dm_id == -1:
        channels = data['channels']
        channel = channels[channel_id-1]
        channel['messages'].append(msg_id)
    elif channel_id == -1:
        dms = data['dms']
        dm = dms[dm_id-1]
        dm['messages'].append(msg_id)

    return msg_id
    





    
