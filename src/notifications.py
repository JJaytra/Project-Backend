from src.data_store import data_store
from src.error import InputError, AccessError
from datetime import timezone
import datetime
#from src.message import messsage_send_v1
from src.helper_functions import channel_lookup, is_user_in_channel
from src.tokens import check_token_valid, decode_jwt

def notifications_get_v1(token):

    token_user = get_user_from_token(token)
    notifications_list = []
    reversed_notifications = token_user['notifications']
    reversed_notifications.reverse()
    for notification in reversed_notifications:
        notifications_list.append(notification)
    return {'notifications': notifications_list}

def get_user_from_token(token):
    token_user = decode_jwt(token)
    data = data_store.get()
    for user in data['users']:
        if token_user['u_id'] == user['u_id']:
            return user
