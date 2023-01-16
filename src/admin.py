from src.data_store import data_store
from src.error import InputError, AccessError
from json import dumps
from flask import Flask, request, Response
from src.tokens import decode_jwt

def admin_user_remove_v1(token, u_id):
    '''
    Removes a user from Seams based on the u_id passed if the token is a global owner and no exception errors (stated below) occur.

    Arguments:
        token (string)   - special string to identify user, can be decoded to give user id and session id
        u_id (integer)    - an id used to determine which specific user the token user wants to remove

    Exceptions:
        InputError  - When u_id does not refer to a valid u_id
        InputError  - When the u_id refers to the only global owner
        AccessError - When the token user is not a global owner

    Return Value:
        Nothing
    '''

    token_user = get_user_from_token(token)
    data = data_store.get()
    if not is_valid_user_id(u_id):
        raise InputError ("Not a valid user id")
    if token_user['permission_id'] == 2:
        raise AccessError ("Not an owner, can't remove")
    for user in data['users']:
        if user['u_id'] == u_id:
            if user['permission_id'] == 1:
                if only_one_owner():
                    raise InputError ("Cannot remove owner when there is only one")

    for dm in data['dms']:
        for member in dm['members']:
            if member['u_id'] == u_id:
                dm['members'].remove(member)
        for owner in dm['owner']:
            if owner['u_id'] == u_id:
                dm['owner'].remove(member)

    for channel in data['channels']:
        for member in channel['all_members']:
            if member['u_id'] == u_id:
                channel['all_members'].remove(member)
        for owner in channel['owner_members']:
            if owner['u_id'] == u_id:
                channel['owner_members'].remove(owner)

    for message in data['messages']:
        if message['u_id'] == u_id:
            message['message'] = "Removed user"

    for user in data['users']:
        if user['u_id'] == u_id:
            user['name_first'] = "Removed"
            user['name_last'] = "user"
            user['handle_str'] = "RemovedUsersHandlestring " + user['handle_str']
            user['email'] = "RemovedUsersemail " + user['email']
            user['u_id'] = u_id * -1
    return ()
    
def admin_userpermission_change_v1(token, u_id, permission_id):
    '''
    Changes the permissions of the specified u_id to either owner or member if the token user is an owner himself and no exception errors(stated below) occur

    Arguments:
        token (string)   - special string to identify user, can be decoded to give user id and session id
        u_id (integer)    - an id used to determine which specific user the token user wants to change permissions
        permission_id (integer) - used to determine which permission to change to with the value of '1' being owner and '2' being member 

    Exceptions:
        InputError  - When u_id does not refer to a valid u_id
        InputError  - When the u_id refers to the only global owner and they are being demoted to member
        InputError  - When permission_id does not refer to a valid permission id (1 and 2 being the only valid ids)
        InputError  - When permission_id does not refer to a different  permission id level the user already has i.e. owner -> owner
        AccessError - When the token user is not a global owner

    Return Value:
        Nothing
    '''

    token_user = get_user_from_token(token)
    data = data_store.get()
    if not is_valid_user_id(u_id):
        raise InputError ("Not a valid user id")
    if token_user['permission_id'] == 2:
        raise AccessError ("Not an owner, can't remove")
    if permission_id != 1 and permission_id != 2:
        raise InputError ("invalid permission id given")

    for user in data['users']:
        if user['u_id'] == u_id:
            if user['permission_id'] == permission_id:
                raise InputError ("Failed to change permissions, user already has that permission level")
            if permission_id == 1:
                user['permission_id'] = 1
            else: #permission_id = 2
                if only_one_owner():
                    raise InputError ("Cannot demote owner when there is only one")
                user['permission_id'] = 2

def get_user_from_token(token):
    token_user = decode_jwt(token)
    data = data_store.get()
    for user in data['users']:
        if token_user['u_id'] == user['u_id']:
            return user

def is_valid_user_id(u_id):
    data = data_store.get()
    for user in data['users']:
        if user['u_id'] == u_id:
            return True
    return False

def only_one_owner():
    data = data_store.get()
    num_of_owners = 0
    for user in data['users']:
        if user['permission_id'] == 1:
            num_of_owners +=1
    if num_of_owners > 1:
        return False
    return True
