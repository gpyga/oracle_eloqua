class AuthorizationError(Exception):
    """ 
    Exception raised when user does not have appropriate credentials
    Used for 301 & 401 HTTP Status codes
    """
    def __init__(self, expression, message):
        self.message = message

class ForbiddenError(Exception):
    """ 
    Exception raised when user does not have appropriate credentials
    Used for the 403 HTTP error code.
    """
    def __init__(self, expression, message):
        self.message = message
