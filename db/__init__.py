import sys
from importlib import util

class DBInit:
    db_not_found_string = 'No database setup found, script aborted.'
    static_folder_found = util.find_spec('static') is not None
    def __init__(self):
        if static_folder_found:
            db_credentials_found = util.find_spec('static.config')
            if not db_credentials_found:
                print(db_not_found_string)
                sys.exit()
        else:
            print(db_not_found_string)
            sys.exit()

from static.config import credentials
from db.Database import Database

WCA_Database = Database(
        credentials['db'],
        credentials['host'],
        credentials['user'],
        credentials['passwd'],
        socket=credentials.get('socket', None),
        port=credentials.get('port', 3306)
    )
