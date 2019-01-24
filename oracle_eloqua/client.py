import json
import requests

from .config import LOGIN_URL, API_VERSION
from .exceptions import AuthorizationError
from .adapters import SSLContextAdapter

from requests.compat import OrderedDict
from requests.cookies import cookiejar_from_dict
from requests.utils import default_headers
from requests.models import DEFAULT_REDIRECT_LIMIT
from requests.hooks import default_hooks

 
class EloquaClient(requests.Session):
    def __init__(self, company, username, password):
        # Set headers to default in requests
        self.headers = default_headers()
        
        # These settings are the difference from requests.Sessions source.
        # Set auth to input
        self.auth = (company + '\\' + username, password)
        # Set connection adapters to only accept login by default
        self.adapters = OrderedDict()
        adapter = SSLContextAdapter()
        self.mount('https://login.eloqua.com', adapter)
        
        # These settings are all the same as requests.Sessions; see
        # https://github.com/requests/requests/blob/master/requests/sessions.py
        # for more details
        self.proxies = {}
        self.hooks = default_hooks()
        self.params = {}
        self.stream = False
        self.verify = True
        self.cert = None
        self.max_redirects = DEFAULT_REDIRECT_LIMIT
        self.trust_env = True
        self.cookies = cookiejar_from_dict({})

        response = self.get(LOGIN_URL, auth=self.auth)
        r = response.json()

        if r == 'Not authenticated.':
            raise AuthorizationError('Could not authenticate ' + username)
        else:
            self.BASE_URL = r['urls']['base']
            self.REST_API = r['urls']['apis']['rest']['standard'].format(
                version=API_VERSION
            )
            self.BULK_API = r['urls']['apis']['rest']['bulk'].format(
                version=API_VERSION
            )

            # Mount the base url
            self.mount(self.BASE_URL, adapter)

    @classmethod
    def from_json(cls, filepath):
        with open(filepath, mode='r') as f:
            j = json.load(f)
        return cls(j['company'], j['username'], j['password'])

    @classmethod
    def from_string(cls, credentials):
        [user, password] = credentials.split(':', 1)
        [company, username] = user.split('//', 1)
        return cls(company, username, password)
    

