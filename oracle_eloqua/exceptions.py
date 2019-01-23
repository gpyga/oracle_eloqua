class AuthorizationError(Exception):
    ''' Exception raised when user does not have appropriate credentials
        Used for the following HTTP error codes:
            301, 401            
    '''
    def __init__(self, expression, message):
        self.message = message

class ForbiddenError(Exception):
    ''' Exception raised when user does not have appropriate credentials
        Used for the following HTTP error codes:
            403
    '''
    def __init__(self, expression, message):
        self.message = message


