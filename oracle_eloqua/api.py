from .session import EloquaSession
from .config import API_VERSION

import json
from warnings import warn

class EloquaApi:
    '''
    '''
    def __init__(self, session):
        self._session = session
        self._session._api_version = api_version or API_VERSION
         
    
    @classmethod
    def init(cls, company=None, username=None, password=None, 
             api_version=None, proxies=None, timeout=None):
        
        session = EloquaSession(
                company, username, password, 
                api_version, proxies, timeout)
        api = cls(session)
        cls.set_default_api(api)
        
        return api

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

    def call(self, method, path, params=None):
        ''' Always returns a json response
        '''
        if method in ('GET','DELETE'):
            params = params or {}
            data = {}
        else:
            data = params or {}
            params = {}
        
        if not isinstance(path, str):
            path = '/'.join((
                self._session.api_urls['rest'], 
                '/'.join(map(str, path))
            ))
        
        response = self._session.request(
            method=method, path=path, params=params, data=data,
            timeout=self._session.timeout
        )

        response.raise_for_status()

        # might create an object associated to response to allow for things
        # like EloquaResponse.to_dataframe()
        return response.json()
        

class EloquaRequest:
    '''
    '''

    def __init__(self, method, endpoint, 
                 obj_id=None, api=None):
        self._api = api or EloquaApi.get_default_api()
        self._method = method
        self._endpoint = list(filter(endpoint.split('/')))
        self._id = [obj_id] or []
        self._path = self._endpoint + self._id
        self._params = {}

    def add_params(self, params):
        if params:
            for key, value in params.items():
                # add method for validating parameters
                self._params[key] = value

        return self
        
    def execute(self):
        if self._method == 'GET':
            cursor = Cursor(
                params=self._params,
                path=self._path,
                api=self._api
            )

            cursor.execute()
            return cursor
        else:
            response = self._api.call(
                method=self._method,
                path=self._path,
                params=self._params
            )
            return response

class Cursor:
    '''
        A cursor for handling GET requests, especially with over 1000 results
    '''
    def __init__(self, params=None, path=None, api=None, api_type=None):
        self._params = params or {}
        self._path = path
        self._api = api
        self._api_type = api_type.lower() or 'rest'

    def totals(self):
        ''' Returns the total size of the query to handle.
        '''
        if 'count' in self._params.keys():
            return self._params['count']
        else:
            meta_params['page'] = 1
            meta_params['count'] = 1
            meta = self._api_call(
                method='GET',
                params=meta_params,
                path=self._path
            )
            return meta.json()['total']
    
    def execute(self):
        totals = self.totals()
        params = self._params

        # Calculates the total number of pages to download and sets queue
        if 'page' in params.keys():
            pages = [params['page']]
        else:
            pages = range(1, int((totals - 1) / 1000) + 2)
        
        queue = totals
        
        response = {
            'elements': [],
            'total': totals
        }

        for page in pages:
            params['page'] = page
            params['count'] = min(1000, queue)
            
            resp = self._api.call(
                method='GET',
                path=self._path,
                params=params
            )
            
            response['elements'].extend(resp['elements'])

            queue -= params['count']

        if queue > 0:
            warn('''{queue} records were not returned due to page constraint. 
            To suppress this message, do not set a count above 1k when 
            a page argument is passed.'''.format(queue=queue))

        return response

