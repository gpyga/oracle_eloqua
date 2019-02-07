from oracle_eloqua.objects.objects import EloquaObject 
class EloquaBulkSchema(EloquaObject):
    """
    
    """
    def __init__(self, endpoint):
        self.endpoint = endpoint
        
        self.Fields = EloquaObject()
        self.set_schema()
        
        return super().__init__()



    def set_schema(self):
        request = EloquaRequest(
            method='GET',
            endpoint='{}/fields'.format(self.endpoint),
            api_type='BULK'
        )
        
        response = request.execute()
        for field in response['items']:
            self.Fields[
                field['internalName']
            ] = self.EloquaObject.create_object(data=field)
