from src.data_store import data_store
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.helper_functions import return_user, return_channel, is_user_valid

def channels_create_v1(auth_user_id, name, is_public):
    '''
    channel_dict = {
        'channel_id': 1,
        'owner_members':[],
        'all_members':[],
        'is_public': TRUE,
        'name' : name,
    }
    
    both 'owner_members' and 'all_members' = {
        'auth_user_id': ,
        'email': 'example@gmail.com'
        'name_first':  ,
        'name_last':  ,
        'handle_str': 'haydenjacobs'
    
    }


    '''
    if is_public == True:
        is_public = True
    elif is_public == False:
        is_public = False
              
    # When length of name is more than 20 characters InputError        
    if len(name) > 20:
        raise InputError("The name is longer than 20 characters")
    # When length of channel name is less than a character - blank
    elif (len(name)) < 1:
        raise InputError("The name is shorter than 1 character")   
        
        
    data = data_store.get()  
    channel_id = len(data['channels']) + 1    

    # for user in data['users']:
    #     if auth_user_id != user['u_id']:
    #         raise AccessError("Invalid user_id.")

    if not is_user_valid(auth_user_id):
        raise AccessError("Invalid user_id")

    channel_dict = {
        
        'name': name,
        'channel_id': channel_id,
        'is_public': is_public,
        'owner_members':[],
        'all_members':[],
        'messages': [],      
    }
    
    name_user = ""
    surname_user = ""
    email_user = ""
    handle_user = ""       
    for user in data['users']:
        if auth_user_id == user['u_id']:
            name_user = user['name_first']
            surname_user = user['name_last']
            email_user = user['email']
            handle_user = user['handle_str']
    
   
    channel_dict['owner_members'].append({'u_id': auth_user_id, 'email': email_user, 'name_first': name_user, 'name_last': surname_user, 'handle_str': handle_user})
    channel_dict['all_members'].append({'u_id': auth_user_id, 'email': email_user, 'name_first': name_user, 'name_last': surname_user, 'handle_str': handle_user})   
    data['channels'].append(channel_dict)
    data_store.set(data)
                   
    return {
        'channel_id': channel_id
    }


def channels_list_v1(auth_user_id):
    list_of_channels = []
    
    data = data_store.get()
    
    
    for channel in data['channels']:
        for user in channel['all_members']:
            if auth_user_id == user['u_id']:
            	list_of_channels.append({'channel_id': channel['channel_id'], 'name': channel['name']})
                   
    return {
        'channels': list_of_channels
    }
    

def channels_listall_v1(auth_user_id):
    list_of_channels = []
    data = data_store.get()

    for channel in data['channels']:
        channel_to_add = {
    		'channel_id': channel['channel_id'],
    		'name': channel['name'],
		}
        list_of_channels.append(channel_to_add)
        
    return {
        'channels': list_of_channels
    }   

