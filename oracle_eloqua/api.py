from .session import EloquaSession
from .config import API_VERSION 

class EloquaApi:
    '''
    '''
    def __init__(self, session):
        self._session = session
        self._api_version = api_version or API_VERSION
        self.REST_API_URL = session.REST_API_URL 
    
    @classmethod
    def init(cls, company=None, username=None, password=None, 
             api_version=None, proxies=None, timeout=None):
        
        session = EloquaSession(
                company, username, password, 
                api_version, proxies, timeout)
        api = cls(session, api_version)
        cls.set_default_api(api)
        
        return cls(session, api_version)

    @classmethod
    def from_json(cls, filepath, 
                  api_version=None, proxies=None, timeout=None):
        with open(filepath, mode='r') as f:
            j = json.load(f)
        company = j['company']
        username = j['username']
        password = j['password']

        return cls.init(company, username, password, 
                        api_version, proxies, timeout)

    @classmethod
    def from_string(cls, credentials, 
                    api_version=None, proxies=None, timeout=None):
        [user, password] = credentials.split(':', 1)
        [company, username] = user.split('//', 1)

        return cls.init(company, username, password, 
                        api_version, proxies, timeout)

    @classmethod
    def set_default_api(cls, api):
        cls._default_api = api

    @classmethod
    def get_default_api(cls):
        return cls._default_api


class EloquaRequest:
    '''
    '''

    def __init__(self, method, endpoint, api=None):
        self._api = api or EloquaApi.get_default_api()
        self._method = method
        self._endpoint = endpoint


