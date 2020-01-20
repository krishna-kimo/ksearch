from datetime import datetime

f_name = 'kimo'

def get_file_name(name=f_name):
    
    return '{}_{}'.format(name, datetime.utcnow().date())