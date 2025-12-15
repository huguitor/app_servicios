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

    # Module Colors
    MODULE_COLORS = {
        "presupuestos": "#3498db",  # Azul
        "clientes": "#27ae60",      # Verde
        "productos": "#e67e22",     # Naranja
        "servicios": "#9b59b6",     # Violeta
        "proveedores": "#16a085",   # Teal
        "configuracion": "#7f8c8d", # Gris
        "remitos": "#e74c3c",       # Rojo
        "default": PRIMARY_COLOR
    }
    
    @classmethod
    def get_api_url(cls, endpoint):
        """URL para endpoints que requieren autenticación"""
        return f"{cls.API_BASE_URL}{endpoint}"
    
    @classmethod
    def get_public_url(cls, endpoint):
        """URL para endpoints públicos (como config_login)"""
        return f"{cls.API_BASE_URL}{endpoint}"