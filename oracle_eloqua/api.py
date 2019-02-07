from oracle_eloqua.session import EloquaSession
from oracle_eloqua.config import API_VERSION, PAGE_SIZE

import json
from warnings import warn
from copy import deepcopy

class EloquaApi:
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
        url_prefix = self._session.api_urls[api_type]
        if not isinstance(path, str):
            url = '/'.join((
                url_prefix.strip('/'), 
                '/'.join(map(str, path))
            )).strip('/')
        
        # Ensure correct parameters are set
        if method in ['GET', 'DELETE']:
            params = params or {}
            json = {}
        else:
            json = params or {}
            params = {}

        response = self._session.session.request(
            method=method, url=url, params=params, json=json,
            timeout=self._session.timeout
        )

        return response 

class EloquaRequest:
    def __init__(self, method, endpoint, api_type=None,
                 obj_id=None, api=None):
        self._api = api or EloquaApi.get_default_api()
        self._method = method
        self._endpoint = list(filter(None, endpoint.split('/')))
        self._id = obj_id or ''
        self._api_type = (api_type or 'REST').upper()
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
    """
    A cursor for handling GET requests, including an iterator
    for handling large responses 
    """
    def __init__(self, params=None, path=None, 
                 api=None, api_type=None):
        self._params = params or {}
        self._path = path
        self._api = api
        self._api_type = (api_type or 'REST').upper()
       
        self._response = self._data = {}
        self._queue = []
        self._pages = params['page'] if 'page' in params else None
        self._finished = False
        self._total = None

        # Explicit BULK API Handling
        low_limit = ['fields','lists','','','']
        if self._api_type == 'BULK':
            if 'limit' not in self._params:
                if 'data' in self._path:
                    self._params['limit'] = 50000
                else:
                    self._params['limit'] = 1000
            if 'offset' not in self._params:
                self._params['offset'] = 0

    def __iter__(self):
        return self

    def __next__(self):
        if not self._queue and not self.load():
            raise StopIteration()
        else:
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
        
        self._data = deepcopy(response)
        
        self._total = 1
        for key in ['total', 'totalResults']:
            if key in response:
                self._total = response[key]

        if self._api_type == 'BULK':
            self._params['offset'] += self._params['limit']
            if 'hasMore' in response:
                self._finished = not response['hasMore']
            else:
                self._finished = True
        else:
            pages = self._pages or int((self._total - 1) / PAGE_SIZE) + 1
            page = response['page'] if 'page' in response else 1
            self._params['page'] = page + 1
            self._finished = not (page < pages) # "not pages left"
        for key in ['elements', 'items']:
            if key in response:
                self._queue = response[key]
                del self._data[key]

        return len(self._queue) > 0
    
    def execute(self):

        if self._api_type == 'BULK':
            self._response['items'] = []
            for queue in self:
                self._response['items'].append(queue)
        else:
            self._response['elements'] = []
            for element in self:
                element = element # trivial until object work is done
                self._response['elements'].append(element)
        
        # append data features
        for key in list(self._data):
            self._response[key] = self._data[key]

        # cleanup unneeded or empty features
        dropkeys = ['page', 'pageSize', 'limit', 'offset', 'count']
        for key in list(self._response):
            if not self._response[key] or key in dropkeys:
                del self._response[key]
        
        # detatch data
        del self._data

        return self._response

