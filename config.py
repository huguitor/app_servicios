# app_escritorio/config.py
import os

class Config:
    # API Configuration
    API_BASE_URL = "http://127.0.0.1:8000"
    API_TIMEOUT = 30
    
    # Auth
    TOKEN_FILE = "token.txt"
    
    # UI
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 700
    THEME = "clam"
    
    # Colors
    PRIMARY_COLOR = "#2c3e50"
    SECONDARY_COLOR = "#3498db"
    SUCCESS_COLOR = "#27ae60"
    WARNING_COLOR = "#e67e22"
    DANGER_COLOR = "#e74c3c"
    
    @classmethod
    def get_api_url(cls, endpoint):
        return f"{cls.API_BASE_URL}{endpoint}"