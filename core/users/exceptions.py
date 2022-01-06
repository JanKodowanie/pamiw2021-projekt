class AccountNotFound(Exception):
    def __init__(self):
        self.detail = 'Account not found'
        super().__init__(self.detail)


class CredentialsAlreadyTaken(Exception):
    
    def __init__(self, message: str, detail=dict):
        self.detail = detail
        super().__init__(message)
        
        
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
        
        
class PasswordResetCodeExpired(Exception):
    def __init__(self):
        self.detail = 'Password reset code has expired'
        super().__init__(self.detail)
        
        
class PasswordResetCodeNotFound(Exception):
    def __init__(self):
        self.detail = 'Password reset code not found'
        super().__init__(self.detail)