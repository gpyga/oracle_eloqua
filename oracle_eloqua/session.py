import json
from requests import Session

from .config import LOGIN_URL, API_VERSION
from .exceptions import AuthorizationError
from .adapters import SSLContextAdapter

class EloquaSession:
    def __init__(self, company=None, username=None, password=None,
                 api_version=None, proxies=None, timeout=None):

        self.company = company
        self.username = username
        self.proxies = proxies
        self.timeout = timeout
        self._api_version = api_version or API_VERSION
        self.session = Session()

        if self.proxies:
            self.session.proxies.update(self.proxies)
        
        # Get SSL Context from OS defaults
        adapter = SSLContextAdapter()
        # Set connection adapters to only accept login by default
        self.session.mount(LOGIN_URL, adapter)
        
        # Ensure successful login
        response = self.session.get(LOGIN_URL, 
                auth=(company + '\\' + username, password)
        r = response.json()
        
        if r == 'Not authenticated.':
            raise AuthorizationError('Could not authenticate ' + username)
        else:
            # Set auth for requests
            self.session.auth = (company + '\\' + username, password)

            self.BASE_URL = r['urls']['base']
            self.REST_API_URL = r['urls']['apis']['rest']['standard'].format(
                version=self._api_version
            )
            self.BULK_API_URL = r['urls']['apis']['rest']['bulk'].format(
                version=self._api_version
            )

            # Mount the base url
            self.session.mount(self.BASE_URL, adapter)


