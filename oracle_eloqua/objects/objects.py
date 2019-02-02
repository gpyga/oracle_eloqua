from oracle_eloqua.api import EloquaRequest, EloquaApi
from warnings import warn

class EloquaObject:
    """ 
    Generic object class for Eloqua objects. Can retrieve attributes
    as items in dict or as attributes in object (similar to 
    pandas.DataFrame).
    """

    def __init__(self, obj_id=None, api=None):
        self._id = obj_id
        self._api = api or EloquaApi.get_default_api()
        self._data = {}
    
    def __getitem__(self, key):
        return self._data[key]

    def __delitem__(self, key):
        del self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        setattr(self, key, value)

    def __contains__(self, key):
        return key in self._data
    
    def __setattr__(self, key, value):
        if hasattr(self, '_data'):
            self._data[key] = value
        super().__setattr__(key, value)
        
    def _set_data(self, data):
        self._data = data
        for key, value in self._data.items():
            setattr(self, key, value)
        if not hasattr(self, '_id'):
            self._id = self['id']

    @classmethod
    def create_object(cls, data, api=None):
        """
        Creates an ojbect from data (json dump)
        """        
        obj = cls(api=api)
        obj._set_data(data)

        return obj

    ## CRUD methods
    @classmethod
    def create(cls, api=None, **kwargs):
        """ 
        Creates a new object from the server
        """
        request = EloquaRequest(
            method='POST',
            endpoint='',
            api=api,
            api_type='rest'
        )
        request.add_params(kwargs)
        response = request.execute()

        return cls.create_object(response, api=api)
        
    def read(self):
        """ 
        Reads data on the server and updates local object attributes. 
        Requires obj_id to be set
        """
        request = EloquaRequest(
            method='GET',
            enpoint='',
            obj_id=self._id,
            api=self._api,
            api_type='rest'
        )

        response = request.execute()
        self._set_data(response)

    def update(self):
        warn('This method is intentially left blank')

    def delete(self):
        # Will work on this after permission
        warn('This method is intentially left blank')