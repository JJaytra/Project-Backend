from src.data_store import data_store
from src.error import InputError, AccessError
from src.helper_functions import email_input, email_lookup, handle_lookup, return_user
import hashlib
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from src import config
from datetime import datetime


def auth_login_v1(email, password):
    '''   
    <Brief description of what the function does>
        This function returns the auth_user_id of a given email and password 

    Arguments:
        email(string)        - email of the registered user
        password(string)     - password of the users registered account

    Exceptions:
        InputError  - Occurs when the email format in terms of spelling is invalid,
            the entered email does not belong to any account, the entered passwords do not match
        AccessError - Occurs when user is not a member of the given channel

    Return Value:
        returns a dicionary with the name of the channel, public/private status, 
        owners of the channel and members of the channel. 
    '''

    # Case 1: Check if it is a valid email format in terms of spelling
    if not email_input(email):
        raise InputError("The entered email address isn't valid.")

    info = data_store.get()
    # Case 2: Check if the user is registered/has acc
    if not email_lookup(email):
        raise InputError("The entered email does not belong to any account.")

    person = return_user(email)
    # Case 3: Check if the password matches the given email
    
            

    for user in info['users']:
        if (user['email'] == email):
            if (user['password'] != hash_string(password)):
                raise InputError("The entered password isn't correct.")

    u_id = 0
    for item in info['users']:
        if (item['u_id'] == person['u_id']):
            u_id = item['u_id']

    return {
        'auth_user_id': u_id
    }


def auth_register_v1(email, password, name_first, name_last):
    '''
    <Given a user's first and last name, email address, and password, create a new account for them and return a new `auth_user_id`.>

    Arguments:
        <email> (string)    - email
        <password> (string)    - passsword
        <name_first> (string)   - first name
        <name_last> (string)    - last name


    Exceptions:
        InputError  - email not valid, email already used, length of pasword is less than 6 chars, first and last name not between 1-50
        chars inclusive


    Return Value:
        Returns {auth_user_id} on successful join
    '''

    # Case 1: Check if email format is valid
    if not email_input(email):
        raise InputError("The entered email address isn't valid.")

    # Case 2: Check if the email is already registered
    if email_lookup(email):
        raise InputError("The entered email is already being used.")

    # Case 3: The length of the password is less than six characters
    if (len(password)) < 6:
        raise InputError("The entered password is too short")

    # Case 4: both names are invalid length
    if ((len(name_first)) < 1 or (len(name_first)) > 50) and ((len(name_last)) < 1 or (len(name_last)) > 50):
       raise InputError("The entered first and last name are not within 1-50 characters inclusive")
    
    # Case 4: Check if the first name is within 1-50 inclusive

    if (len(name_first)) < 1 or (len(name_first)) > 50:
        raise InputError(
            "The entered first name is not within 1-50 characters inclusive")

    # Case 5: Check if the last name is within 1-50 inclusive

    if (len(name_last)) < 1 or (len(name_last)) > 50:
        raise InputError(
            "The entered last name is not within 1-50 characters inclusive")



    # Create handle
    # combine first and last name and make lowercase
    combined_lower_names = (name_first + name_last).lower()
    # remove non alphanumeric characters     
    handle = ''.join(ch for ch in combined_lower_names if ch.isalnum())
    # cut string to length of 20       
    handle = handle[:20]                                       
    
    # check if handle already exists for another user
    handle_plus = handle_lookup(handle)                         
    
    # if handle already exists, adds lowest number to end of handle
    if handle_plus > 0:                                        
        handle = handle + str(handle_plus)

    # create a new account
    # populate, email, first and last name, password, id, handle

    new = data_store.get()  # get current data
    new_id = len(new['users']) + 1

    # Gets appropriate permission id based on if its the first user
    permission_id = 2
    if new['users'] == []:
        permission_id = 1
    
    # initial state 
    chnl_stats = []
    dms_stats = []
    msg_stats = []
    
    channels_joined = {'num_channels_joined': 0, 'time_stamp': int(datetime.timestamp(datetime.now()))}
    chnl_stats.append(channels_joined)
    
    dms_joined = {'num_dms_joined': 0, 'time_stamp': int(datetime.timestamp(datetime.now()))}
    dms_stats.append(dms_joined)
    
    messages_sent = {'num_messages_sent': 0, 'time_stamp': int(datetime.timestamp(datetime.now()))}
    msg_stats.append(messages_sent)
    
    user_stats = {
        'channels_joined': chnl_stats,
        'dms_joined': dms_stats,
        'messages_sent': msg_stats,
        'involvement_rate': 0
    }
    
    info = {
            'channels_exist': [{'num_channels_exist': 0, 'time_stamp': int(datetime.timestamp(datetime.now()))}],
            'dms_exist': [{'num_dms_exist': 0, 'time_stamp': int(datetime.timestamp(datetime.now()))}],
            'messages_exist': [{'num_messages_exist': 0, 'time_stamp': int(datetime.timestamp(datetime.now()))}],
            'utilization_rate': 0
 
    }
    new['workspace_stats'] = info
    
    #new['workspace_stats'].append(info)
    
    new_user = {
        'email': email,
        'password': hash_string(password),
        'name_first': name_first,
        'name_last': name_last,
        'handle_str': handle,
        'u_id': new_id,
        'sessions': [],
        'permission_id': permission_id,
        'reset': None,
        'profile_img_url': config.url + 'static/dbrc.jpg',
        'notifications': [],
        'user_stats': user_stats,
    }

    new['users'].append(new_user)

    data_store.set(new)
    return {
        'auth_user_id': new_id
    }


def auth_logout_v1(u_id, session_id):
    data = data_store.get()
    for user in data['users']:
        if user['u_id'] == u_id and session_id in user['sessions']:
            user['sessions'].remove(session_id)

    return

def auth_passwordreset_request_v1(email):
    '''
    <Given an email address, if the user is a registered user, sends them an email containing a specific secret code, that when entered in auth/passwordreset/reset, shows that the user trying to reset the password is the one who got sent this email. No error should be raised when passed an invalid email, as that would pose a security/privacy concern. When a user requests a password reset, they should be logged out of all current sessions.>

    Arguments:
        <email> (string)    - email
     
    Return Value:
        Returns {} 
    '''    
    data = data_store.get()
    
    # Log out user from all exisiting sessions              
    code = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(100))
    for user in data['users']:
        if user['email'] == email:
            user['reset'] = code 
            user['sessions'].clear()
                 
    sender_email = 'projectbackendcomp1531@gmail.com'
    sender_pass = 'channel.py1'
    message = MIMEMultipart()
    message['Subject'] = 'Seams Password Reset'
    message['From'] = sender_email
    message['To'] = email
    # Message that needs sending
    message.attach(MIMEText(code, 'plain'))
    
    # Creating and then terminating SMTP session          
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender_email, sender_pass)
    mail = message.as_string()
    smtp.sendmail(sender_email, email, mail)
    smtp.quit()                   
            
    return {
    }

def auth_passwordreset_reset_v1(reset_code, new_password):
    '''
    <Given a reset code for a user, set that user's new password to the password provided. Once a reset code has been used, it is then invalidated.>

    Arguments:
        <reset_code> (string)    - email
        <new_password> (string)  - passsword
        
    Exceptions:
        InputError  - When reset_code entered is not a valid reset code
                    - When the new_password entered is less than 6 characters long 

    Return Value:
        Returns {} on successful password reset
    '''
    data = data_store.get()  
    invalid = True
            
    # InputError: If new password entered is less than 6 characters long
    if len(new_password) < 6:
        raise InputError("Password entered is less than 6 characters long")
     
    for user in data['users']:
            if user['reset'] == reset_code:                        
                invalid = False
                user['password'] = hash_string(new_password)
                user['reset'] = None
                                  
    # InputError: If reset code is invalid
    if invalid is True:
        raise InputError("Reset code entered is invalid")    
    
    return {
    }

def hash_string(password):
    """Hashes the input string with sha256
    """
    return hashlib.sha256(password.encode()).hexdigest()
