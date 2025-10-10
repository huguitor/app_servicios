# app_escritorio/auth_manager.py
from api_client import APIClient

class AuthManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthManager, cls).__new__(cls)
            cls._instance.client = APIClient()
            cls._instance.is_authenticated = cls._instance.client.token is not None
        return cls._instance
    
    def login(self, username, password):
        success, message = self.client.login(username, password)
        if success:
            self.is_authenticated = True
        return success, message
    
    def logout(self):
        self.client.clear_token()
        self.is_authenticated = False
    
    def check_auth(self):
        return self.is_authenticated and self.client.test_connection()