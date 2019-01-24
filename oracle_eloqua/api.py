from .session import EloquaSession
from .config import API_VERSION 

class EloquaApi:
    def __init__(self, session, api_version=None):
        self._session = session
        self._api_version = api_version or API_VERSION
    
    @classmethod
    def init(cls, company=None, username=None, password=None, 
             api_version=None, proxies=None, timeout=None):
        
        session = EloquaSession(company, username, password, proxies, timeout)

        return cls(session, api_version)

    @classmethod
    def from_json(cls, filepath, 
                  api_version=None, proxies=None, timeout=None):
        with open(filepath, mode='r') as f:
            j = json.load(f)
        company = j['company']
        username = j['username']
        password = j['password']

        session = EloquaSession(company, username, password, proxies, timeout)

        return cls(session, api_version)

    @classmethod
    def from_string(cls, credentials, 
                    api_version=None, proxies=None, timeout=None):
        [user, password] = credentials.split(':', 1)
        [company, username] = user.split('//', 1)

        session = EloquaSession(company, username, password, proxies, timeout)

        return cls(session, api_version)

