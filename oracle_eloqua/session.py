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

 
class EloquaSession:
    def __init__(self, company=None, username=None, password=None,
                 proxies=None, timeout=None):
        self.company = company
        self.username = username
        self.proxies = proxies
        self.timeout = timeout
        self.requests = requests.Session()

        if self.proxies:
            self.requests.proxies.update(self.proxies)

        # Set connection adapters to only accept login by default
        adapter = SSLContextAdapter()
        self.requests.mount(LOGIN_URL, adapter)
        
        response = self.requests.get(LOGIN_URL, 
                auth=(company + '\\' + username, password)
        r = response.json()

        if r == 'Not authenticated.':
            raise AuthorizationError('Could not authenticate ' + username)
        else:
            # Set auth for requests
            self.requests.auth = (company + '\\' + username, password)

            self.BASE_URL = r['urls']['base']
            self.REST_API = r['urls']['apis']['rest']['standard'].format(
                version=API_VERSION
            )
            self.BULK_API = r['urls']['apis']['rest']['bulk'].format(
                version=API_VERSION
            )

            # Mount the base url
            self.requests.mount(self.BASE_URL, adapter)


