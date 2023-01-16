from src.data_store import data_store
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.channels import channels_create_v1, channels_list_v1
from src.helper_functions import email_input, email_lookup, handle_lookup, return_user, channel_lookup, is_user_in_channel, is_user_valid, is_channel_private, check_handle, is_owner, return_user_by_id, return_channel
from src.tokens import get_userid_from_token
from datetime import datetime

def channel_invite_v1(auth_user_id, channel_id, u_id):
    
    '''
    <Invites a user with ID u_id to join a channel with ID channel_id. Once invited, the user is added to the channel immediately. 
    In both public and private channels, all members are able to invite users..>

    Arguments:
        <auth_user_id> (integer)    - special value to identify user
        <channel_id> (integer)    - specify value to identify channel
        <u_id>  (integer)           - special value to identify a second user
        

    Exceptions:
        InputError  - Occurs when channel_id is not valid, u_id does not refer to a valid user, u_id refers to a user who is already a member
        AccessError - authorised user is not a member of the channel
        

    Return Value:
        Returns {} on successful join
    '''

    # Case 1:   channel_id does not refer to a valid channel
    if not channel_lookup(channel_id):
        raise InputError('channel_id does not refer to a valid channel')
    
    # Case 2:   u_id does not refer to a valid user
    if not is_user_valid(u_id):
        raise InputError('u_id is not valid')
    
    # Case 3: u_id refers to a user who is already a member of the channel
    if is_user_in_channel(u_id, channel_id):
        raise InputError('u_id refers to a user who is already a member of the channel')
    
    # Case 4: Channel_id is valid but the authorised user is not a member of the channel
    if not is_user_in_channel(auth_user_id, channel_id):
        raise AccessError('Channel_id is valid but the authorised user is not a member of the channel')

    info = data_store.get()
    
    for user in info['users']:
        if u_id == user['u_id']:
            joining_user = {'u_id': u_id, 
                            'email': user['email'] , 
                            'name_first': user['name_first'] , 
                            'name_last': user['name_last'] , 
                            'handle_str': user['handle_str']
                            
                            }
            #notification that user was invited
            for user in info['users']:
                if user['u_id'] == auth_user_id:
                    inviter_handle = user['handle_str']
            for channel in info['channels']:
                if channel['channel_id'] == channel_id:
                    channel_name = channel['name']

            notification_dict = {
                'channel_id': channel_id,
                'dm_id': -1,
                'notification_message': f"{inviter_handle} added you to {channel_name}",
            }
            user['notifications'].append(notification_dict)
#            raise AccessError ("check")

    
    for ch in info['channels']:
        if ch['channel_id'] == channel_id:
            ch['all_members'].append(joining_user)


    return {
    }
    

def channel_details_v1(auth_user_id, channel_id):
    '''   
    <Brief description of what the function does>
    This function returns details about a certain channel which the user is part of.
    The details included are: the name of the channel, publi/private status, the owners
    of channels and all the members if the channel. 

    Arguments:
        auth_user_id(integer)    - the id value of the registered user
        channel_id(integer)      - the id of the channel that the user created

    Exceptions:
        InputError  - Occurs when the channel_id is invalid
        AccessError - Occurs when user is not a member of the given channel

    Return Value:
        returns a dicionary with the name of the channel, public/private status, 
        owners of the channel and members of the channel. 
    '''    
    # check if the channel_id is valid
    if not channel_lookup(channel_id):
        raise InputError("The provided channel_id doesn't belong to any channel")
    
    info = data_store.get()    
    
    # check if the user is part of channel
    if not is_user_in_channel(auth_user_id, channel_id):
        raise AccessError('The given user is not a member of this channel.')
    
    # get_handle = ""
    # get_last = ""
    # get_name = ""
    # for user in info['users']:
    #     if auth_user_id == user['u_id']:
    #         get_handle = user['handle_str']
    #         get_name = user['name_first']
    #         get_last = user['name_last']
    
    # if not check_handle(get_name, get_last, get_handle):      # what is this?
    #     raise InputError("Handles not generated correctly.")                        

    for channel in info['channels']:
        if channel['channel_id'] == channel_id:
         
            return {'name': channel['name'], 
                    'is_public': channel['is_public'], 
                    'owner_members': channel['owner_members'], 
                    'all_members': channel['all_members']
            }

            

def channel_messages_v1(auth_user_id, channel_id, start):
    ''' 
    <Brief description of what the function does>
        This function returns a dicitonary with the messages and the start and end 
        position of the conversation

    Arguments:
        auth_user_id(integer)    - the id value of the registered user
        channel_id(integer)      - the id of the channel that the user created

    Exceptions:
        InputError  - Occurs when the given channel_id is invalid, the start of conversation
                  is larger then the message total
        AccessError - Occurs when the given user is not a member of the channel

    Return Value:
        returns a dicitonary with the messages and the start and end 
        position of the conversation
    '''
    
    info = data_store.get()
    
    # for channel in info['channels']:
    #     if channel['channel_id'] != channel_id:
    #         raise InputError("The given channel_id is invalid.")

    if not channel_lookup(channel_id):
        raise InputError("The given channel_id is invalid.")
    
    # message_length = 0
    # for channel in info['channels']:
    #     message_length = len(channel['messages'])

    
    # if start > message_length:
    #     raise InputError("The start is larger than the total number of messages.")

    

    channels = info['channels']
    channel = channels[channel_id-1]

    message_length = len(channel['messages'])

    if start > message_length:
        raise InputError("The start is larger than the total number of messages.")
        
    # for channel in info['channels']:
    #     for memb in channel['all_members']:
    #         if memb['u_id'] != auth_user_id:
    #             raise AccessError("The given user is not a member of this channel.")
    if not is_user_in_channel(auth_user_id, channel_id):
        raise AccessError("The given user is not a member of this channel.")
    
    end = 0
    
    # for channel in info['channels']:
    #     if channel['channel_id'] == channel_id:
    #         if message_length < (start + 50):
    #             end = -1
    #         else:
    #             end = start + 50

    if message_length < (start + 50):
        end = -1
    else:
        end = start + 50
                    
    messages_list = []
    
    channnel_messages = channel['messages']
    messages = info['messages']

    x = start
    
    while x < (start + 50) and x < message_length:
        i = channnel_messages[x]
        messages_list.append(messages[i-1])
        x+=1
    messages_list.reverse()
    message_dict = {
        'messages': messages_list,
        'start': start, 
        'end': end
      }
      
                
    return message_dict
            

def channel_join_v1(auth_user_id, channel_id):
    '''
    <Given a channel_id of a channel that the authorised user can join, adds them to that channel.>

    Arguments:
        <auth_user_id> (integer)    - special value to identify user
        <channel_id> (integer)    - specify value to identify channel
        

    Exceptions:
        InputError  - Occurs when channel_id is not valid, or when user is already in channel
        AccessError - Occurs when user tries to join private channel they are not already in, 
        and user is not a global owner

    Return Value:
        Returns {} on successful join
    '''

    #   return InputError: When channel_id does not refer to a valid channel
    if not channel_lookup(channel_id):               
        raise InputError('Channel_id does not refer to a valid channel')
    
    #   return InputError: when user is already in the channel
    if is_user_in_channel(auth_user_id, channel_id):
        raise InputError('User is already in the channel')

    # Channel is private and the user can't join
    if not is_channel_private(auth_user_id, channel_id):
        raise AccessError("The channel is private, unable to join.")
        
    info = data_store.get()
    
    for user in info['users']:
        if auth_user_id == user['u_id']:
            joining_user = {'u_id': auth_user_id, 
                            'email': user['email'] , 
                            'name_first': user['name_first'] , 
                            'name_last': user['name_last'] , 
                            'handle_str': user['handle_str'],
                            'time_stamp': datetime.timestamp(datetime.now())
                           }
  
    for ch in info['channels']:
        if ch['channel_id'] == channel_id:
            ch['all_members'].append(joining_user)

    return {
    }

def channel_leave_v1(token, channel_id):
    '''
    <Given a channel with ID channel_id that the authorised user is a member of, 
    remove them as a member of the channel. Their messages should remain in the 
    channel. If the only channel owner leaves, the channel will remain.>

    Arguments:
        <token> (integer)       - special string to identify user
        <channel_id> (integer)  - specific value to identify channel
        

    Exceptions:
        InputError  - Occurs when channel_id is not valid
        AccessError - Occurs when channel_id is valid and the authorised user is
                      not a member of the channel 

    Return Value:
        Returns {} on successful leave
    '''    
    channel = return_channel(channel_id)
    
    #  return InputError: When channel_id does not refer to a valid channel
    if not channel_lookup(channel_id):               
        raise InputError('Channel_id does not refer to a valid channel')
       
    u_id = get_userid_from_token(token)         
    #  return AccessError: When channel_id is valid and the autorised user is not a member of the channel
    if not is_user_in_channel(u_id, channel_id): 
        raise AccessError("Authorised user is not a member of channel")
    
    #  if u_id is a member, remove from list of all_members    
    for member in channel['all_members']:
        if u_id == member['u_id']:
            channel['all_members'].remove(member)
    
    #  if u_id is an owner, remove from list of owner_members 
    for owner in channel['owner_members']:
        if u_id == owner['u_id']:
            channel['owner_members'].remove(owner)
        
    return {
    }    
    
def channel_addowner_v1(token, channel_id, u_id):
    '''
    <Make user with user id u_id an owner of the channel.>

    Arguments:
        <token> (string)        - special string to identify user
        <channel_id> (integer)  - specific value to identify channel
        <u_id> (integer)        - specific value to identify user
        

    Exceptions:
        InputError  - Occurs when channel_id is not valid
                    - Occurs when u_id is not valid
                    - Occurs when u_id refers to a user who is not a member of 
                      given channel
                    - Occurs when u_id refers to a user who is ALREADY an owner
        AccessError - Occurs when channel_id is valid and the authorised user 
                      does not have owner permissions
                       
    Return Value:
        Returns {} on successful addition of owner
    '''
    channel = return_channel(channel_id)
              
    #  return InputError: When channel_id does not refer to a valid channel
    if not channel_lookup(channel_id):                
        raise InputError("Channel_id does not refer to a valid channel")
           
    #  return InputError: When u_id does not refer to a valid user
    if not is_user_valid(u_id):
        raise InputError("u_id does not refer to a valid user") 
  
    #  return InputError: When u_id refers to a user who is not a member of the channel
    if not is_user_in_channel(u_id, channel_id): 
        raise InputError("User is not a member of the channel")
    auth_id = get_userid_from_token(token)
    #  return AccessError: When channel_id is valid and the authorised user does not have 
    #  owner permissions in the channel
    if not is_owner(auth_id, channel_id):
        raise AccessError("User does not have owner permissions in the channel")    
    
    #  return InputError: When u_id refers to a user who is already an owner of the channel
    if is_owner(u_id, channel_id):
        raise InputError("User is already an owner of the channel")
       
    user = return_user_by_id(u_id)
    channel['owner_members'].append({'u_id': user['u_id'], 'email': user['email'], 'name_first': user['name_first'], 'name_last' : user['name_last']})
        
    return {
    }      

def channel_removeowner_v1(token, channel_id, u_id):
    '''
    <Remove user with user id u_id as an owner of the channel.>

    Arguments:
        <token> (string)        - special string to identify user
        <channel_id> (integer)  - specific value to identify channel
        <u_id> (integer)        - specific value to identify user
        

    Exceptions:
        InputError  - Occurs when channel_id is not valid
                    - Occurs when u_id is not valid
                    - Occurs when u_id refers to a user who is not an OWNER of 
                      given channel
                    - Occurs when u_id refers to a user who is currently the ONLY
                      owner of given channel
        AccessError - Occurs when channel_id is valid and the authorised user 
                      does not have owner permissions
                       
    Return Value:
        Returns {} on successful removal of owner
    '''             
    
    channel = return_channel(channel_id)
         
    #  return InputError: When channel_id does not refer to a valid channel
    if not channel_lookup(channel_id):                
        raise InputError("Channel_id does not refer to a valid channel")
           
    #  return InputError: When u_id does not refer to a valid user
    if not is_user_valid(u_id):
        raise InputError("u_id does not refer to a valid user")

    #  return InputError: When u_id refers to a user who is not an owner of the channel
    if not is_owner(u_id, channel_id):
        raise InputError("User is not currently an owner of the channel")
    
    #  return InputError: When u_id refers to a user who is currently the ONLY owner of the channel
    if is_owner(u_id, channel_id) and len(channel['owner_members']) == 1:
        raise InputError("User is currently the only owner of this channel")
        
    auth_id = get_userid_from_token(token)
    #  return AccessError: When channel_id is valid and the authorised user does not have 
    #  owner permissions in the channel
    if not is_owner(auth_id, channel_id):
        raise AccessError("User does not have owner permissions in the channel")   
    
    user = return_user_by_id(u_id)
    channel['owner_members'].remove({'u_id': user['u_id'], 'email': user['email'], 'name_first': user['name_first'], 'name_last' : user['name_last']})    
            
    return {
    }  
    
       
    

