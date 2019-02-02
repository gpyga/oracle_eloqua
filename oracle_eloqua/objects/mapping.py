class ObjectMapper:
    """

    """
    def __init__(self, target_class=None):
        pass
"""
from oracle_eloqua import EloquaRequest
request = EloquaRequest(
    method='GET',
    api_type='REST',
    endpoint='assets/contact/fields',
    api=api
)
request.add_params(params={'depth':'complete'})
response = request.execute()
response
"""