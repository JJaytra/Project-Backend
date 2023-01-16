from lib2to3.pgen2 import token
from ssl import CHANNEL_BINDING_TYPES
import sys
import signal
import pickle
import json
import os.path
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src.error import InputError, AccessError
from src import config
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1, dm_details_v1, dm_leave_v1, dm_messages_v1, message_senddm_v1

from src.auth import auth_login_v1, auth_register_v1, auth_logout_v1, auth_passwordreset_reset_v1, auth_passwordreset_request_v1
from src.tokens import generate_jwt, generate_session_id, decode_jwt, add_session_to_user, check_token_valid, get_userid_from_token, get_sessionid_from_token
from src.other import clear_v1
from src.data_store import data_store

 
from src.tokens import generate_jwt, generate_session_id, decode_jwt, add_session_to_user, check_token_valid, get_userid_from_token, get_sessionid_from_token
from src.channels import channels_create_v1, channels_listall_v1, channels_list_v1
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_messages_v1, channel_addowner_v1, channel_removeowner_v1, channel_leave_v1
from src.other import clear_v1
from src.user import user_profile_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1, users_all_v1, user_profile_uploadphoto_v1

from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_react_v1, message_unreact_v1
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1

from src.search import search_v1
from src.statistics import user_stats_v1, users_stats_v1

from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1, message_sendlater_v1, message_sendlaterdm_v1, message_share_v1
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1
from src.standup import standup_start_v1, standup_send_v1, standup_active_v1
from src.notifications import notifications_get_v1
from src.data_store import data_store

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

@APP.route("/auth/login/v2", methods=['POST'])
def auth_login():
    """ Logs user in with email and password
    Args:
        email (string)
        password (string)
    Returns:
        Token (string): Made using u_id and sessionID
        auth_user_id: u_id
    """
    data_persistence_load()
    info = request.get_json()
    email = info['email']
    password = info['password']         # hash this password and compare it in the actual auth_login function

    auth_user_id = auth_login_v1(email, password)   
    u_id = auth_user_id['auth_user_id']

    session_id = generate_session_id()
    add_session_to_user(u_id, session_id)       # add session to user data

    token = generate_jwt(u_id, session_id)
    data_persistence_save()    
    return dumps({
        'token': token,
        'auth_user_id': u_id,
    })


@APP.route("/auth/register/v2", methods=['POST'])
def auth_register():
    """ Registers user in with email and password
    Returns:
        token: generated using u_id and session_id
        auth_user_id: dictionary containing u_id
    """
    data_persistence_load()
    info = request.get_json()
    # Get all arguments
    email = info['email']
    password = info['password']     # hash this and store in auth_register_v2
    name_first = info['name_first']
    name_last = info['name_last']

    auth_user_id = auth_register_v1(email, password, name_first, name_last)
    u_id = auth_user_id['auth_user_id']
    session_id = generate_session_id()

    add_session_to_user(u_id, session_id)       # add session to user data

    token = generate_jwt(u_id, session_id)

    data_persistence_save()
    return dumps({
        'token': token,
        'auth_user_id': u_id,
    })

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create():
    """ Creates a new channel
    Returns: channel id of new channel
    """
    info = request.get_json()

    token = info['token']

    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")

    u_id = get_userid_from_token(token)
    name = info['name']
    is_public = info['is_public']

    channel_id = channels_create_v1(u_id, name, is_public)

    data_persistence_save()
    return dumps({
        'channel_id': channel_id['channel_id']
    })


@APP.route("/channels/list/v2", methods=['GET'])
def channels_list():
    """Provide a list of all channels (and their associated details) that the authorised user is part of.
    """

    token = request.args.get('token')

    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")

    u_id = get_userid_from_token(token)

    channel_dict = channels_list_v1(u_id)
    channels = channel_dict["channels"]
    
    data_persistence_save()
    return dumps({
        'channels': channels
    })

@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    """Provide a list of all channels, including private channels, (and their associated details)
    """

    token = request.args.get('token')
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    
    u_id = get_userid_from_token(token)
    channels_listall_response = channels_listall_v1(u_id)
    channels_all_listed = channels_listall_response["channels"]
    
    data_persistence_save()
    return dumps({
        'channels': channels_all_listed
    })


@APP.route("/channel/details/v2", methods=['GET'])
def channels_details():
    """
    Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.
    """

    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    
    auth_user_id = get_userid_from_token(token)

    response = channel_details_v1(auth_user_id, channel_id)
    
    data_persistence_save()
    return dumps({
        'name': response['name'],
        'is_public': response['is_public'],
        'owner_members': response['owner_members'],
        'all_members': response['all_members']
    })

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join():
    """Given a channel_id of a channel that the authorised user can join, adds them to that channel.
    """
    info = request.get_json()

    token = info['token']
    channel_id = int(info['channel_id'])
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")

    u_id = get_userid_from_token(token)
    channel_join_v1(u_id, channel_id)

    data_persistence_save()
    return {}
    


@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite():
    """
    Invites a user with ID u_id to join a channel with ID channel_id. Once invited, the user is added to the channel immediately. 
    """
    info = request.get_json()
    token = info['token']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    channel_id = int(info['channel_id'])
    invite_user = info['u_id']
    auth_user_id = get_userid_from_token(token)

    channel_invite_v1(auth_user_id, channel_id, invite_user)
    data_persistence_save()
    return {}

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    """
    Given a channel with ID channel_id that the authorised user is a member of, return up to 50 messages between index "start" and "start + 50".
    """
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))

    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")

    auth_user_id = get_userid_from_token(token)
    
    response = channel_messages_v1(auth_user_id, channel_id, start)

    data_persistence_save()
    return dumps({
        'messages': response['messages'],
        'start': response['start'],
        'end': response['end']
    })


@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    """
    Resets the internal data of the application to its intial state
    """
    clear_v1()
    return {}

@APP.route('/dm/create/v1', methods = ['POST'])
def server_dm_create():
    request_data = request.get_json()
    token = request_data['token']
    u_ids = request_data['u_ids']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    dm_id = dm_create_v1(token, u_ids)

    data_persistence_save()
    return (
        dm_id
    )

@APP.route('/dm/list/v1', methods = ['GET'])
def server_dm_list():
    request_data = request.args.get('token')
    token = request_data
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    dms = dm_list_v1(token)

    data_persistence_save()
    return dumps(
        dms
    )

@APP.route('/dm/remove/v1', methods = ['DELETE'])
def server_dm_remove():
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
        
    dm_remove_v1(token, dm_id)
    data_persistence_save()
    return {}
    
@APP.route('/dm/details/v1', methods = ['GET'])
def server_dm_details():
    request_data = request.args.get('token')
    token = request_data
    request_data = request.args.get('dm_id', type = int)
    dm_id = request_data
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    dm_details = dm_details_v1(token, dm_id)
    
    data_persistence_save()
    return (dm_details)

@APP.route('/dm/leave/v1', methods = ['POST'])
def server_dm_leave():
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    dm_leave_v1(token, dm_id)
    data_persistence_save()
    return {}

@APP.route('/dm/messages/v1', methods = ['GET'])
def server_dm_messages():
    request_data = request.args.get('token')
    token = request_data
    request_data = request.args.get('dm_id', type = int)
    dm_id = request_data
    request_data = request.args.get('start', type = int)
    start = request_data
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    dm_messages = dm_messages_v1(token, dm_id, start)
    
    data_persistence_save()
    return (dm_messages)
    
@APP.route("/message/senddm/v1", methods=['POST'])
def server_dm_message_send():
    info = request.get_json()
    token = info['token']
    dm_id = info['dm_id']
    message = info['message']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    message_id = message_senddm_v1(token, dm_id, message)
    
    data_persistence_save()
    return dumps({
        'message_id': message_id
    })

@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout():
    """
    Given an active token, invalidates the token to log the user out
    """
    info = request.get_json()
    token = info['token']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")

    auth_user_id = get_userid_from_token(token)
    session_id = get_sessionid_from_token(token)

    auth_logout_v1(auth_user_id, session_id)

    data_persistence_save()
    return {}
    
@APP.route("/user/profile/v1", methods=["GET"])
def user_profile():
    '''
    The function takes the token and user_id as inputs and returns the details
    of the user, while doing error checking for validity of user_id.
    '''
    token = request.args.get('token')
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
  
    user_id = request.args.get('u_id', type=int)
    profile = user_profile_v1(token, user_id)
    
    data_persistence_save()
    return dumps({'user': profile})
    
@APP.route("/user/profile/setname/v1", methods=["PUT"])
def user_setname():
    
    info = request.get_json()
    token = info['token']
    
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    
    name = info['name_first']
    surname = info['name_last']
    
    user_profile_setname_v1(token, name, surname)
    
    data_persistence_save()
    return dumps({})
    
@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_setemail():
    
    info = request.get_json()
    
    token = info['token']
    email = info['email']
    
    user_profile_setemail_v1(token, email)
    
    data_persistence_save()
    return dumps({})

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_sethandle():
    
    info = request.get_json()
    
    token = info['token']
    handle = info['handle_str']
    
    user_profile_sethandle_v1(token, handle)
    
    data_persistence_save()
    return dumps({})
    
@APP.route("/users/all/v1", methods=['GET'])
def user_listall():
    
    token = request.args.get('token')
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
  
    users = users_all_v1(token)
  
    data_persistence_save()
    return dumps({
        'users': users['users']
    })


@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_image():
    
    info = request.get_json()
    token = info['token']

    # check token validity    
    if not check_token_valid(token):        
        raise AccessError("Invalid Token")
    
    user_profile_uploadphoto_v1(token, info['img_url'], info['x_start'], info['y_start'], info['x_end'], info['y_end'])
    
    return dumps({
    
    })    

@APP.route('/static/<path:path>')#, methods=['GET'])
def send_js(path):
    #picture = request.args.get('file')
    return send_from_directory('', path)  #("/static/", path)
       
@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    
    info = request.get_json()
    token = info['token']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    channel_id = info['channel_id']
    message = info['message']

    message_id = message_send_v1(token, channel_id, message)

    data_persistence_save()
    
    return dumps({
        'message_id': message_id
    })

@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    info = request.get_json()
    message_id = info['message_id']
    message = info['message']
    token = info['token']
    # token = str(request.args.get('token'))
    # message_id = int(request.args.get('message_id'))
    # message = str(request.args.get('message'))
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")

    message_edit_v1(token, message_id, message)

    data_persistence_save()
    return {}

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    info = request.get_json()
    token = info['token']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    message_id = info['message_id']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")    
    message_remove_v1(token, message_id)

    data_persistence_save()
    return {}

@APP.route('/channel/leave/v1', methods=['POST'])
def channel_leave():
    request_data = request.get_json()
    channel_id = request_data['channel_id']
    token = request_data['token']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    channel_leave_v1(token, channel_id)    
    
    data_persistence_save()
    return dumps({})

@APP.route('/channel/addowner/v1', methods=['POST'])
def channel_addowner():
    request_data = request.get_json()
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    token = request_data['token']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")    
    channel_addowner_v1(token, channel_id, u_id)

    data_persistence_save()
    return dumps({})
    
       
@APP.route('/channel/removeowner/v1', methods=['POST'])
def channel_removeowner():
    request_data = request.get_json()
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    token = request_data['token']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    channel_removeowner_v1(token, channel_id, u_id)
    
    data_persistence_save()
    return dumps({})
    
@APP.route('/admin/user/remove/v1', methods=['DELETE'])
def admin_user_remove():
    request_data = request.get_json()
    token = request_data['token']
    u_id = request_data['u_id']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    admin_user_remove_v1(token, u_id)
    
    data_persistence_save()
    return dumps({})

@APP.route('/admin/userpermission/change/v1', methods=['POST'])
def admin_user_permission_change():
    request_data = request.get_json()
    token = request_data['token']
    u_id = request_data['u_id']
    permission_id = request_data['permission_id']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    admin_userpermission_change_v1(token, u_id, permission_id)
    
    data_persistence_save()
    return dumps({})

@APP.route('/auth/passwordreset/request/v1', methods=['POST'])
def auth_passwordreset_request():
    request_data = request.get_json()
    email = request_data['email']
    auth_passwordreset_request_v1(email)
    data_persistence_save()
    return dumps({})

@APP.route('/auth/passwordreset/reset/v1', methods=['POST'])
def auth_passwordreset_reset():
    request_data = request.get_json()
    reset_code = request_data['reset_code']
    new_password = request_data['new_password']
    auth_passwordreset_reset_v1(reset_code, new_password)
    data_persistence_save()
    return dumps({})

def data_persistence_save():
    data = data_store.get()
    with open("data_store_as_json.json", 'w') as FILE:
        json.dump(data, FILE)
    return()

def data_persistence_load():
    if os.path.exists('data_store_as_json'):
        data = data_store.get()
        pickled = open ("data_store_as_json", "rb")
        unpickled = pickle.load(pickled)
        data.append("do nothing, this is solely for a pylint error for data")
        data = unpickled
    return()

#--------Iteration 3-----------------------

@APP.route('/message/react/v1', methods=['POST'])
def message_react():
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']
    react_id = request_data['react_id']

    message_react_v1(token, message_id, react_id)

    return {}

@APP.route('/message/unreact/v1', methods=['POST'])
def message_unreact():
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']
    react_id = request_data['react_id']

    message_unreact_v1(token, message_id, react_id)

    return {}

@APP.route('/message/pin/v1', methods=['POST'])
def message_pin():
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']

    message_pin_v1(token, message_id)

    return {}

@APP.route('/message/unpin/v1', methods=['POST'])
def message_unpin():
    request_data = request.get_json()
    token = request_data['token']
    message_id = request_data['message_id']

    message_unpin_v1(token, message_id)

    return {}


@APP.route('/message/sendlater/v1', methods=['POST'])
def message_sendlater():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    message = request_data['message']
    time_sent = request_data['time_sent']

    message_id = message_sendlater_v1(token, channel_id, message, time_sent)

    return dumps({
         'message_id': message_id
     })

@APP.route('/message/sendlaterdm/v1', methods=['POST'])
def message_sendlaterdm():
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']
    message = request_data['message']
    time_sent = request_data['time_sent']

    message_id = message_sendlaterdm_v1(token, dm_id, message, time_sent)

    return dumps({
        'message_id': message_id
    })
    
@APP.route('/message/share/v1', methods=['POST'])
def message_share():
    request_data = request.get_json()
    token = request_data['token']
    og_message_id = request_data['og_message_id']
    message = request_data['message']
    channel_id = request_data['channel_id']
    dm_id = request_data['dm_id']
    
    shared_message_id = message_share_v1(token, og_message_id, message, channel_id, dm_id)
    return dumps({
        'shared_message_id': shared_message_id
    })

@APP.route('/standup/start/v1', methods = ['POST'])
def server_standup_start():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    length = request_data['length']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    finish_time = standup_start_v1(token, channel_id, length)
    data_persistence_save()
    return (finish_time)

@APP.route('/standup/send/v1', methods = ['POST'])
def server_standup_send():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    message = request_data['message']
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    standup_send_v1(token, channel_id, message)
    data_persistence_save()
    return {}

@APP.route('/standup/active/v1', methods = ['GET'])
def server_standup_active():
    request_data = request.args.get('token')
    token = request_data
    request_data = request.args.get('channel_id', type = int)
    channel_id = request_data
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    standup_active = standup_active_v1(token, channel_id)
    data_persistence_save()
    return standup_active

@APP.route('/notifications/get/v1', methods = ['GET'])
def server_notifications_get():
    request_data = request.args.get('token')
    token = request_data
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
    notification = notifications_get_v1(token)
    data_persistence_save()
    return notification
@APP.route('/search/v1', methods=['GET'])
def search_for_message():
    
    token = request.args.get('token')
    if not check_token_valid(token):        # check token is valid
        raise AccessError("Invalid Token")
  
    word = request.args.get('query_str')
    
    found = search_v1(token, word)
    
    return dumps({
        'messages': found['messages']
    })

@APP.route('/user/stats/v1', methods=['GET'])
def get_user_statistics():
    token = request.args.get('token')
    
    stat = user_stats_v1(token)
    
    return dumps({
        'user_stats': stat['user_stats']
    })
   
   
@APP.route('/users/stats/v1', methods=['GET'])
def get_worspace_stats():
    token = request.args.get('token')
    
    stat = users_stats_v1(token)
    
    return dumps({
        'workspace_stats': stat['workspace_stats']
    })
#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
