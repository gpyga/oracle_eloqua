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

    def call(self, method, path, api_type=None, params=None):
        if method in ('GET','DELETE'):
            params = params or {}
            data = {}
        else:
            data = params or {}
            params = {}
        
        if not isinstance(path, str):
            path = '/'.join((
                _session.api_urls[api_type.lower() or 'rest'], 
                '/'.join(map(str, path))
            ))
        
        response = self._session.request(
            method=method, path=path, params=params, data=data,
            timeout=self._session.timeout
        )

        # might create an object associated to response to allow for things
        # like EloquaResponse.to_dataframe()
        return response
        

class EloquaRequest:
    '''
    '''

    def __init__(self, method, endpoint, 
                 obj_id=None, api=None, api_type=None):
        self._api = api or EloquaApi.get_default_api()
        self._method = method
        self._endpoint = list(filter(endpoint.split('/')))
        self._id = [obj_id] or []
        self._path = self._endpoint + self._id
        self._api_type = api_type or 'post'
        self._params = {}

    def add_params(self, params):
        if params:
            for key, value in params.items():
                # add method for validating parameters
                self._params[key] = value

        return self
        
    def execute(self):
        if self._method =='GET':
            cursor = Cursor(
                params=self._params,
                endpoint=self._endpoint,
                api=self._api,
                api_type=self._api_type
            )

            cursor.load()
            return cursor
        else:
            response = self._api.call(
                    method=self._methd,
                    path=self._path,
                    params=self._params,
                    api_type=self._api_type
            )
            return response

# create method to load each page into single json
class Cursor:
    '''
    '''
    def __init__(self, params=None, endpoint=None, api=None, api_type=None):
        pass


