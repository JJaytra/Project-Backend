from src.data_store import data_store
from src.tokens import get_userid_from_token, check_token_valid
from src.error import InputError, AccessError
import operator
from datetime import datetime

def user_stats_v1(token):
    '''
    Function description: 
        This function takes the token as an input and fetches the statistics of the user.
        Removing messages doesn't impact the number overall as we are only inserting the 
        data in the stats when the message is created. So, even if it is later deleted, 
        we have already attached it to the dict. 
    
    Input:
        token
    
    Return:
        the user_stats dictionary
    '''
    
    info = data_store.get()
    
    user_id = get_userid_from_token(token)
    
    for user in info['users']:
        if user_id == user['u_id']:
            person_data = user['user_stats']
    
    # before obtaining the dms and channels joined, the channels_joined and 
    # dms_joined dict to be set to there inital state as there will be constant
    # increase and decrease in the number 
    person_data['channels_joined'] = [{'num_channels_joined': 0, 'time_stamp': 0}]
    person_data['dms_joined'] = [{'num_dms_joined': 0, 'time_stamp': 0}]
    
   
    num_chnls_joined = 1
    for chnl in info['channels']:
        for member in chnl['all_members']:
            if user_id == member['u_id']:
                num_chnls_joined +=1
                chnl_joined = {'num_channels_joined': num_chnls_joined, 'time_stamp': int(member['time_stamp'])}
                person_data['channels_joined'].append(chnl_joined)
    
    # sorting by time_stamp
    person_data['channels_joined'].sort(key=operator.itemgetter('time_stamp'))
    
    total_dms_joined = 1
    for dm in info['dms']:
        if user_id in dm['members']:
            total_dms_joined += 1
            dms_joined = {'num_dms_joined': total_dms_joined, 'time_stamp': int(dm['time_stamp'])}
            person_data['dms_joined'].append(dms_joined)
    
    # sorting by time_stamp
    person_data['dms_joined'].sort(key=operator.itemgetter('time_stamp'))
    
    # messages_sent is obtained in the message_create part and it is added by timestamp
    num_msg = len(person_data['messages_sent'])
    
    total_chnls = 0
    for chnl in info['channels']:
        total_chnls += 1
    
    total_dms = 0
    for dm in info['dms']:
        total_dms += 0
    
    total_msg = len(info['messages'])
    #for msg in info['messages']:
    
    
    top = num_chnls_joined + total_dms_joined + num_msg
    bottom = total_chnls + total_dms + total_msg
    
    if bottom == 0:
        invl_rate = 0
    else:
        invl_rate = top/bottom
    
        if invl_rate > 1:
            invl_rate = 1
        
        person_data['involvement_rate'] = invl_rate 
 
            
    data_store.set(person_data)

    return {
        'user_stats': person_data
    }
    
def users_stats_v1(token):
    '''
    Function description:
        - this function takes the token as input and returns the stats of the whole 
        session, not specific user.
    Input: 
        - token
    
    Return: 
        - a dictionary, with details such as num of channels, dms and messages in the requested moment
    '''
    info = data_store.get()
    stats = info['workspace_stats']
    
    
    # The inital state is already set so do not duplicate. 
    # get the number of channels at that time and create a new entry, and sort by time_stamp 
    num_chnls = len(info['channels'])
    if num_chnls != 0:
        chnl = {'num_channels_exist': num_chnls, 'time_stamp': int(datetime.timestamp(datetime.now()))}
        stats['channels_exist'].append(chnl)
        stats['channels_exist'].sort(key=operator.itemgetter('time_stamp'))

    # count the current number of dms, add to dicionary and sort by time_stamp, if there are new dms
    num_dms = len(info['dms'])
    if num_dms != 0:
        dms = {'num_dms_exist': num_dms, 'time_stamp': int(datetime.timestamp(datetime.now()))}
        stats['dms_exist'].append(dms)
        stats['dms_exist'].sort(key=operator.itemgetter('time_stamp'))
      
    # count the current number of messages, add to dicionary and sort by time_stamp, if there are new messages
    num_msg = len(info['messages'])
    if num_msg != 0:    
        msg = {'num_messages_exist': num_msg, 'time_stamp': int(datetime.timestamp(datetime.now()))}
        stats['messages_exist'].append(msg)
        stats['messages_exist'].sort(key=operator.itemgetter('time_stamp'))
        
    num_users_chnl = 0
    for chnl in info['channels']:
        #for member in chnl['all_members']:
        num_users_chnl += len(chnl['all_members'])
        
    num_dms = 0
    for dm in info['dms']:
        num_dms += len(dm['members'])
        
    num_users = len(info['users'])
    #for user in info['users']:
        #num_users += 1
    
    if num_dms != 0 and num_chnls != 0 and num_users != 1:
        stats['utilization_rate'] = (num_users_chnl + num_dms) / num_users
       
    data_store.set(info)
    
    return {
        'workspace_stats': stats   
    }        
     
    
