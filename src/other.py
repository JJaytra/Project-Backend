from src.data_store import data_store
from src.tokens import reset_session_id


def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['messages'] = []
    store['dms'] = []
    store['standups'] = []    
    data_store.set(store)

    reset_session_id()
    
    return store


