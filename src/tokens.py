import hashlib
import jwt
from src.data_store import data_store

SESSION_TRACKER = 0
SECRET = 'DINGOW11A'


def generate_session_id():
    """
    Generates a new sequential session ID

    Returns:
        integer: the next session ID
    """

    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER

def reset_session_id():
    """ Reset sessions to 0
    """
    global SESSION_TRACKER
    SESSION_TRACKER = 0
    return SESSION_TRACKER
    

def generate_jwt(u_id, session_id):
    """
    Generates a JWT using the global SECRET

    Args:
        u_id ([int]): The id of a user
        session_id ([int]) : The session id, if none provided, generates a new one

    Returns:
        string: An encoded JWT string
    """
    if session_id is None:
        session_id = generate_session_id()
    return jwt.encode({"u_id": u_id, "session_id": session_id}, SECRET, algorithm='HS256')


def decode_jwt(encoded_jwt):
    """
    Decodes a JWT string 

    Args:
        encoded_jwt (string): JWT encoded as a string

    Returns:
        Object: Stores the body of the JWT encoded string, decoded
    """
    return jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])


def check_token_valid(encoded_jwt):
    """
    Checks whether a token is valid

    Args:
        encoded_jwt (string): JWT aka Token, encoded as a string

    Returns:
        True if token is valid (user id is valid and that associated user is logged into session specified in JWT)
        False otherwise
    """
    info = jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
    data = data_store.get()
    for user in data['users']:
        if user['u_id'] == info['u_id']:
            if user['handle_str'][0] == "RemovedUsersHandlestring":
                return False
    
    for user in data['users']:
        if user['u_id'] == info['u_id']:
            if info['session_id'] in user['sessions']:
                return True
    return False


def get_userid_from_token(encoded_jwt):
    """Decodes jwt and returns u_id
    """
    decoded_token = jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
    return int(decoded_token['u_id'])

def get_sessionid_from_token(encoded_jwt):
    """Decodes jwt and returns session_id
    """
    decoded_token = jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
    return decoded_token['session_id']



def add_session_to_user(u_id, session_id):
    """ Adds session to user data_store
    """
    data = data_store.get()
    for user in data['users']:
        if u_id == user["u_id"]:
            user['sessions'].append(session_id)
            data_store.set(data)

