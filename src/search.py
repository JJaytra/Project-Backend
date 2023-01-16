from src.data_store import data_store
from src.error import InputError, AccessError
from src.tokens import check_token_valid, decode_jwt, get_userid_from_token
from src.helper_functions import check_user


def search_v1(token, query_str):
    
    info = data_store.get()
    
    # checking query_str length 
    if len(query_str) < 1 or len(query_str) > 1000:
        raise InputError("The given string doesn't have a valid length (1 - 1000 chars).")
    
    found_messages = []
          
    for message_data in info['messages']:
        if str(query_str) in str(message_data['message']):
            found_messages.append(message_data)
            
            
    return {
        'messages': found_messages
    }
    
