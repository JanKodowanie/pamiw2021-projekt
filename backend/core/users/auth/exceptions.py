    
class MalformedAccessToken(Exception):
    def __init__(self):
        self.detail = 'Access token is malformed'
        super().__init__(self.detail)
    
    
class AccessTokenExpired(Exception):
    def __init__(self):
        self.detail = 'Access token has expired'
        super().__init__(self.detail)

        
class InvalidCredentials(Exception):
    def __init__(self):
        self.detail = "Couldn't login with credentials given"
        super().__init__(self.detail)