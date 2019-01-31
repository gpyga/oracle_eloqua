from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

class SSLContextAdapter(HTTPAdapter):
    """
    HTTPAdapter set to grab machine's default SSL Certs
    initial code from https://stackoverflow.com/a/50215614/10624667
    adapted to accept proxies (for corprate folks)
    """
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        kwargs['ssl_context'] = context
        context.load_default_certs()
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, proxy, **kwargs):
        context = create_urllib3_context()
        kwargs['ssl_context'] = context
        context.load_default_certs()
        return super().proxy_manager_for(proxy, **kwargs)
