from oracle_eloqua.session import EloquaSession
from oracle_eloqua.config import API_VERSION

import json
from warnings import warn
from copy import deepcopy

class EloquaApi:
    '''
    '''
    def __init__(self, session):
        self._session = session
    
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

    def call(self, method, path, api_type, params=None):
        ''' Always returns a json response
        '''
        # ensures data or params is set properly on methods
        if method in ('GET','DELETE'):
            params = params or {}
            data = {}
        else:
            data = params or {}
            params = {}
        
        url_prefix = self._session.api_urls[api_type]
        if not isinstance(path, str):
            url = '/'.join((
                url_prefix.strip('/'), 
                '/'.join(map(str, path))
            )).strip('/')
        
        response = self._session.session.request(
            method=method, url=url, params=params, data=data,
            timeout=self._session.timeout
        )

        response.raise_for_status()

        # might create an object associated to response to allow for 
        # methods like EloquaResponse.to_dataframe()
        return response
        

class EloquaRequest:
    ''' 
    '''
    def __init__(self, method, endpoint, api_type=None,
                 obj_id=None, api=None):
        self._api = api or EloquaApi.get_default_api()
        self._method = method
        self._endpoint = list(filter(None, endpoint.split('/')))
        self._id = obj_id or ''
        self._api_type = (api_type or 'rest').lower()
        self._path = self._endpoint + [self._id]
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
                api_type=self._api_type,
                api=self._api
            )
            response = cursor.execute()

            return response

        else:
            response = self._api.call(
                method=self._method,
                path=self._path,
                api_type=self._api_type,
                params=self._params
            ).json()

            return response

class Cursor:
    '''
        A cursor for handling GET requests, including an iterator
        for handling large responses (>1000 results)
    '''
    def __init__(self, params=None, path=None, 
                 api=None, api_type=None):
        self._params = params or {}
        self._path = path
        self._api = api
        self._api_type = (api_type or 'rest').lower()
       
        self._response = self._data = {}
        self._queue = []
        self._pages = params['page'] if 'page' in params else None
        self._finished = False
        self._total = None

    def __iter__(self):
        return self

    def __next__(self):
        if not self._queue and not self.load():
            raise StopIteration()
        return self._queue.pop(0)

    def __repr__(self):
        return str(self._response)

    def __len__(self):
        return len(self._response)

    def __getitem__(self, index):
        return self._response[index]
    
    def load(self):
        if self._finished:
            return False

        response = self._api.call(
            method='GET',
            path=self._path,
            api_type=self._api_type,
            params=self._params
        ).json()
    
        # calculate number of pages
        self._total = response['total'] if 'total' in response else 1
        pages = int((self._total - 1) / 1000) + 1
        self._pages = self._pages if self._pages else pages

        self._page = response['page'] if 'page' in response else 1

        # determine whether to continue iterating
        if self._page < self._pages:
            self._params['page'] = self._page + 1
        else:
            # terminate iteration
            self._finished = True
            
        self._data = deepcopy(response)

        if 'elements' in response:
            self._queue = response['elements']
            del self._data['elements']
        else:
            self._response = self._data

        return len(self._queue) > 0
    
    def execute(self):
        for row in self:
            if self._queue and 'elements' in self._response:
                self._response['elements'].append(row)
            elif self._queue:
                self._response = self._data
                self._response['elements'] = [row]

        return self._response


