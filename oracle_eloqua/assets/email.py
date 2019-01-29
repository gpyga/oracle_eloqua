from oracle_eloqua.api import EloquaRequest, EloquaApi


class Email:
    def __init__(self, asset_id, api=None):
        self._asset_id = asset_id # maybe int or array?
        self._api = api or EloquaApi.get_default_api()
        
    @classmethod
    def from_search(cls, search, api=None):
        # method for pulling asset_id from a search query
        pass

    @classmethod
    def create(cls, params)

    def get(self):

