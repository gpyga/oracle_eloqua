from oracle_eloqua.api import EloquaRequest, EloquaApi
from warnings import warn

class EloquaObject:
    """ Generic object class for Eloqua objects.
    """
    def __init__(self, obj_id=None, api=None):
        self._data = {}
        self._obj_id = obj_id
        self._api = api or EloquaApi.get_default_api()
    
    # Create is set up as a class method, so as to return the object id
    @classmethod
    def create(cls, api=None, **kwargs):
        request = EloquaRequest(
            method='POST',
            endpoint='',
            api=api,
            api_type='rest'
        )
        request.add_params(kwargs)
        response = request.execute()

        obj_id = request['id']

        return cls(obj_id, api)

    def read(self):
        request = EloquaRequest(
            method='GET',
            enpoint='',
            api=self._api,
            api_type='rest'
        )
        response = request.execute()

    def update(self, **kwargs):
        warn('This method doesn''t do anything yet')

    def delete(self):
        warn('This method doesn''t do anything yet')


class EloquaQuery:
    """ Generic object class for Eloqua queries (ie - campaigns)
    """
    def __init__(self, **kwargs):
        pass

    def search(self):
        pass
