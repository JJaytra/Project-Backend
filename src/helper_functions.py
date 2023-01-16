import re
from src.data_store import data_store
import hashlib
from src.tokens import decode_jwt

# Function to check if the email input satisfies the given format
def email_input(email):

    format = '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'
    value = bool(re.match(format, email))
    
    if (value):
        return True
    else:
        return False

# checks if email is already used
def email_lookup(email):

    info = data_store.get()
    
    for user in info['users']:
        if (user['email'] == email):
            return True
    return False


# Looks up for any identical handles 
def handle_lookup(handle):
    lowest = -1
    info = data_store.get()
    for user in info['users']:
        if (user['handle_str'] == handle):
            lowest = lowest + 1
    
    return lowest

# returns user 
def return_user(email):
    info = data_store.get()
    
    for user in info['users']:
        if user['email'] == email:
            return user
   
        

# Checks whether the channel is valid
def channel_lookup(channel_id):                        
    info = data_store.get()
    for channel in info['channels']:
        if channel['channel_id'] == channel_id:
            return True
    return False

def return_user_by_id(user_id):
    data = data_store.get()
    
    for user in data['users']:
        if user_id == user['u_id']:
            return user
    
    return None   

# gets user id from token 
def get_user_from_token(token):
    token_user = decode_jwt(token)
    
    data =  data_store.get()
    for user in data['users']:
        if user['u_id'] == int(token_user['u_id']):
            return user['u_id']
    return "invalid token/no one with that token"


def return_channel(ch_id):
    data = data_store.get()
    
    for channel in data['channels']:
        if int(ch_id) == channel['channel_id']:
            return channel
       
    return None    



# Cheks if the user is in the specified channel
def is_user_in_channel(user_id, channel_id):

    info = data_store.get()
    for channel in info['channels']:
        if channel_id == channel['channel_id']:
            for user in channel['all_members']:
                if user['u_id'] == user_id:
                    return True

    return False


# Checks if the channel is private
def is_channel_private(user_id, channel_id):
    info = data_store.get()
    channels = info['channels']
    channel = channels[channel_id-1]
    if channel['is_public'] == True:
        return True        
    return False                                    # returns false if private and user is not global owner

def check_handle(first, last, original_handle):
    combined = first + last
    new_handle = ''.join(ch for ch in combined if ch.isalnum())       # remove non alphanumeric characters
    new_handle = new_handle[:20]                                        # cut string to length of 20

    handle_plus = handle_lookup(new_handle)                         # check if handle already exists for another user

    if handle_plus > 0:                                        # if handle already exists, adds lowest number to end of handle
        new_handle = new_handle + str(handle_plus)
    
    if new_handle == original_handle:
        return True
    else:
        return False


# Checks if user is valid
def is_user_valid(user_id):
    info = data_store.get()
    users = info['users']
    for user in users:
        if user['u_id'] == user_id:
            if user['handle_str'][0] == "RemovedUsersHandlestring":
                return False
            return True
    return False


# Checks if given u_id is already an owner
def is_owner(user_id, channel_id):
    info = data_store.get()
    for channel in info['channels']:
        if channel_id == channel['channel_id']:
            for user in channel['owner_members']:
                if user['u_id'] == user_id:
                    return True

    return False
       
def check_user(user_id):
    info = data_store.get()
    
    for channel in info['channels']:
        for owners in channel['owner_members']:
            if user_id == owners['u_id']:
                return True
        for others in channel['all_members']:
            if user_id == others['u_id']:
                return True    
    
    return False


def hash_string(input_string):
    """ Hashes the input string with sha256
    """
    return hashlib.sha256(input_string.encode()).hexdigest()

def search_msg_in_channels_and_dms_user_in(user_id, message_id):
    data = data_store.get()
    for channel in data['channels']:
        channel_users = channel['all_members']
        for user in channel_users:
            if user_id == user['u_id']:
                if message_id in channel['messages']:
                    return True

    for dm in data['dms']:
        for user in dm['members']:
            if user_id == user['u_id']:
                if message_id in dm['messages']:
                    return True
    return False

def is_msg_in_channel(msg_id):
    data = data_store.get()
    channels = data['channels']
    for channel in channels:
        if msg_id in channel['messages']:
            return True
    return False


def is_msg_in_dm(msg_id):
    data = data_store.get()
    dms = data['dms']
    for dm in dms:
        if msg_id in dm['messages']:
            return True
    return False


def has_msg_edit_perms(user_id, msg_id):
    
    # return true if message was written by user (has permission to edit)
    if get_message_author(msg_id, user_id):
        return True
    # otherwise, looks if user has owner permissions 
    # look where the msg is located, channel or dm
    data = data_store.get()
    
    if is_msg_in_channel(msg_id):
        ch_id = is_msg_in_channel_return_id(msg_id)
        channels = data['channels']
        channel = channels[ch_id - 1]
        owner_users = channel['owner_members']
        for user in owner_users:
            if user['u_id'] == user_id:
                return True

    
    if is_msg_in_dm(msg_id):
        dm_id = is_msg_in_dm_return_id(msg_id)
        dms = data['dms']
        dm = dms[dm_id - 1]
        if user in dm['owner']:
            return True
    return False

def get_message_author(msg_id, u_id):

    data = data_store.get()
    for message in data['messages']:
        if message['message_id'] == msg_id:
            if message['u_id'] == u_id:
                return True
    return False

def is_msg_in_channel_return_id(msg_id):
    data = data_store.get()
    channels = data['channels']
    for channel in channels:
        if msg_id in channel['messages']:
            return channel['channel_id']
    


def is_msg_in_dm_return_id(msg_id):
    data = data_store.get()
    dms = data['dms']
    for dm in dms:
        if msg_id in dm['messages']:
            return dm['dm_id']
    


def has_msg_pin_perms(user_id, msg_id):
    
    data = data_store.get()
    
    if is_msg_in_channel(msg_id):
        ch_id = is_msg_in_channel_return_id(msg_id)
        channels = data['channels']
        channel = channels[ch_id - 1]
        owner_users = channel['owner_members']
        for user in owner_users:
            if user['u_id'] == user_id:
                return True

    
    if is_msg_in_dm(msg_id):
        dm_id = is_msg_in_dm_return_id(msg_id)
        dms = data['dms']
        dm = dms[dm_id - 1]
        if user in dm['owner']:
            return True
    return False

def dm_lookup(dm_id):
    data = data_store.get()
    for dm in data['dms']:
        if dm['dm_id'] == dm_id:
            return True
    return False




def is_user_in_dm(user, dm_id):
    data = data_store.get()
    for dm in data['dms']:
        if dm['dm_id'] == dm_id:
            for member in dm['members']:
                if member['u_id'] == user:
                    return True
    return False
