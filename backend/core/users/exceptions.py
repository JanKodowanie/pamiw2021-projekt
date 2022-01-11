
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
        self.detail = 'Kod do resetu hasła utracił ważność.'
        super().__init__(self.detail)
        
        
class PasswordResetCodeNotFound(Exception):
    def __init__(self):
        self.detail = 'Nie znaleziono kodu do resetu hasła.'
        super().__init__(self.detail)