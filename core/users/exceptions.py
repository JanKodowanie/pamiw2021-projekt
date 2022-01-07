
class AccountNotFound(Exception):
    def __init__(self):
        self.detail = 'Account not found'
        super().__init__(self.detail)


class CredentialsAlreadyTaken(Exception):
    def __init__(self, message: str, detail=dict):
        self.detail = detail
        super().__init__(message)

            
class PasswordResetCodeExpired(Exception):
    def __init__(self):
        self.detail = 'Password reset code has expired'
        super().__init__(self.detail)
        
        
class PasswordResetCodeNotFound(Exception):
    def __init__(self):
        self.detail = 'Password reset code not found'
        super().__init__(self.detail)