class AuthorizationError(Exception):
    '''Exception raised when user does not have appropriate credentials'''
    def __init__(self, expression, message):
        self.message = message

