from src.data_store import data_store
import urllib.request
import imgspy
import os
from PIL import Image
from src.error import InputError, AccessError
from json import dumps
from flask import Flask, request, Response
from src.tokens import decode_jwt, check_token_valid
from src.helper_functions import is_user_valid, return_user_by_id, email_input, email_input, email_lookup
from src.tokens import get_userid_from_token
from src import config 
def user_profile_v1(token, u_id):
    '''
    Inputs:
        token - string 
        u_id - integer
    
    function_description:
        given a token and user_id the function returns all the details of the 
        matching user (user_id, name, lastname, email, handle).
        
    Errors:
        - InputError is raised when the given user_id doesn't belogn to a valid user
    
    Returns:
        - returns the users' information in a form of dictionary 
    '''
     
    data = data_store.get()  
    
    user_id_found = False
    for user in data['users']:   
        if user['u_id'] == int(u_id):
            user_id_found = True
        if user['u_id'] < 0: #-1 indicates removed user
            user_id_found = True
    if user_id_found == False:
        raise InputError("Provided user_id doesn't belong to a valid user.")
    
    
    for user in data['users']:
        if user['u_id'] == int(u_id) or (user['u_id']*-1) == int(u_id):
            return {'u_id': u_id,
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle_str'],
                'profile_img_url': user['profile_img_url']            
               }        
    
def user_profile_setname_v1(token, firstname, lastname): 
    '''
    Inputs:
        token - string 
        firstname - string
        lastname - string
    
    function_description:
        given a token, first and last name, the function updates the users' first
        and last name to the provided ones - only if they meet the length criteria.
        
    Errors:
        - InputError is raised when the given first and last name doesn't meet the 
        length criteria
    
    Returns:
        - This function doesn't returnanything. it just updates the dictionary in place.  
    '''
    
    # checking whether token is valid
    if not check_token_valid(token):
        raise AccessError("The provided token is invalid")
        
    # checking whether firstname is within length boundaries
    if (len(firstname) <= 1) or (len(firstname) > 50):
        raise InputError("First name doesn't meet the length criteria (1 - 50 characters inclusive).")
        
    # checking whether firstname is within length boundaries
    if (len(lastname) <= 1) or (len(lastname) > 50):
        raise InputError("Last name doesn't meet the length criteria (1 - 50 characters inclusive).")
        
    users_token = get_userid_from_token(token)
  
    info =  data_store.get()
    
    # update first and last name in 'users' dictionary
    for user in info['users']:

        if user['u_id'] == users_token:
            user['name_first'] = firstname
            user['name_last'] = lastname
    
    info = data_store.get()
    
    # update first and last name in 'channels' dictionary        
    for channel in info['channels']:
        for member in channel['owner_members']:
            if member['u_id'] == users_token:
                member['name_first'] = firstname
                member['name_last'] = lastname
        for member_2 in channel['all_members']:
            if member_2['u_id'] == users_token:
                member['name_first'] = firstname
                member['name_last'] = lastname
	
    data_store.set(info)
       
    return {
    
    }
    
    
def user_profile_setemail_v1(token, email):
    
    # check for valid email format
    if email_input(email) == False:
        raise InputError("The provided email doesn't have a valid format.")
    
    # check if email is already used
    if email_lookup(email) == True:
        raise InputError("This email is already in use.")  
    
    users_token = get_userid_from_token(token)
     
    info =  data_store.get()
    
    # update the email in 'users' dictionary
    for user in info['users']:
        if user['u_id'] == users_token:
            user['email'] = email

    # update email in 'channels' dictionary       
    for channel in info['channels']:
        for member in channel['owner_members']:
            if member['auth_user_id'] == users_token:
                member['email'] = email
         
        for member_2 in channel['all_members']:
            if member_2['auth_user_id'] == users_token:
                member_2['email'] = email
            
    data_store.set(info)
    return {
    
    }  
    
def user_profile_sethandle_v1(token, handle):

    # check for length of handle 
    if (len(handle) < 3) or (len(handle) > 20):
        raise InputError("The provided handle doesn't meet the length requirements (3 - 20 chars incusive).")
        
    # check for non alphanumeric chars
    result = handle.isalnum()
    if result == False:
        raise InputError("Handle contains non alphanumeric characters")
   
    users_token = get_userid_from_token(token)
    info = data_store.get()
    
    for user in info['users']:
        if user['handle_str'] == handle:
            raise InputError("The provided handle is used by another user.")
  
    # update the handle in 'users' dictionary
    for user in info['users']:
        if user['u_id'] == users_token:
            user['handle_str'] = handle

    # update email in 'channels' dictionary       
    for channel in info['channels']:
        for member in channel['owner_members']:
            if member['auth_user_id'] == users_token:
                member['handle_str'] = handle
         
        for member_2 in channel['all_members']:
            if member_2['auth_user_id'] == users_token:
                member_2['handle_str'] = handle
    
    data_store.set(info)        
    return {
    
    } 
    
def users_all_v1(token):
    info = data_store.get()
    list_of_users = {
            'users':[]
            }
    
    for user in info['users']:
        if user['u_id'] < 0:
            continue
        list_of_users['users'].append({
            'u_id': user['u_id'],
            'email': user['email'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'handle_str': user['handle_str'],
            'profile_img_url': user['profile_img_url'] 
        })

    return list_of_users
 
 
def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Inputs:
        token - string 
        img_url - url, request object
        x_start, x_end, y_start, y_end - integers
    
    function_description:
        given a token, img_url and dimensions of a picture, the function first 
        fetches the image from the given url. Upon successful retrieving it crops
        the picture to provided dimensions and uploads it to the given users profile
        
    Errors:
        - InputError:
            - raised when the given url is in a non HTTP format
            - raised when the croping dimensions are out of bound 
            - raised when the ending points are less than or equal than the starting points
            - raised when then image is not in a JPG format
    Returns:
        - This function doesn't return anything it just updates the profile photo  
    '''  
    info  = data_store.get()
    
    # checking if the url is HTTP format
    url = img_url
    if (url.find('http://')) == -1:
        raise InputError("img_url returns a HTTP status other than 200.")
  
    # checking image format 
    if imgspy.info(img_url)['type'] != 'jpg':
        raise InputError("The given image is not in valid format (JPG).")
    
      
    # creating directory to store the image if it doesn't exist
    if not os.path.exists('./src/static'):
        os.mkdir('./src/static')
    
    # creating an address to store the image 
    person = get_userid_from_token(token)
    
    for user in info['users']:
        if user['u_id'] == person:
            hndl = user['handle_str']
    
    image_address = './src/static/' + hndl + '.jpg'
    urllib.request.urlretrieve(img_url, image_address)
    
    # getting the dimensions of the image
    image_open = Image.open(image_address)
    img_width, img_height = image_open.size 
    
    # checking whether x,y starting points are within picture dimensions
    if (int(x_start) > img_width) or (int(x_start) < 0) or (int(y_start) > img_height) or (int(y_start) < 0):
        raise InputError("The provided dimensions are out of bound.")
    
    # checking whether x,y end points are within picture dimensions
    if (int(x_end) > img_width) or (int(x_end) < 0) or (int(y_end) > img_height) or (int(y_end) < 0):
        raise InputError("The provided dimensions are out of bound.")
        
    # checking if x_end, y_end are <= x_start, y_start
    if (int(x_end) <= int(x_start)) or (int(y_end) <= int(y_start)):
        raise InputError("The ending points are less than or equal to the starting points.")
        
    cropped_image = image_open.crop((int(x_start), int(y_start), int(x_end), int(y_end)))
    cropped_image.save(image_address)  
    
    
    # generating the image url 
    image_url = config.url + 'static/' + hndl + '.jpg'
    
    # upload photo to users profile 
    for user in info['users']:
        if user['u_id'] == person:
            user['profile_img_url'] = image_url
            
    # upload photo in all channels the user is a member of 
    for chnl in info['channels']:
        for owner in chnl['owner_members']:
            if owner['u_id'] == person:
                owner['profile_img_url'] = image_url
               
        for member in chnl['all_members']:
            if member['u_id'] == person:
                member['profile_img_url'] = image_url
    
    data_store.set(info)
    
    return {
    
    }
