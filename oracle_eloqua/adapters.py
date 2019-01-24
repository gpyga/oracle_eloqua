from requests.adapters import HTTPAdapter

# retrieved from https://stackoverflow.com/a/50215614/10624667
# tends to pass when there is no proxy issue; as confirmed on personal Mac
class SSLContextAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        kwargs['ssl_context'] = context
        context.load_default_certs()
        return super(SSLContextAdapter, self).init_poolmanager(*args, **kwargs)

