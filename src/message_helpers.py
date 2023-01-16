from src.error import InputError
from datetime import datetime
import threading
from src.tokens import get_userid_from_token

def check_time(time_sent):
    countdown = time_sent - datetime.timestamp(datetime.now())
    if countdown < 0:
        raise InputError("Time_sent has to indicate a future time")
    return countdown

