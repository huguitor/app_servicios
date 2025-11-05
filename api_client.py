# app_escritorio/api_client.py
import requests
import os
import json
from tkinter import messagebox
from config import Config


class Endpoints:
    # Auth
    TOKEN = "/api/token/"
   
    # Data
    CLIENTES = "/clientes/"
    PROVEEDORES = "/proveedores/"
    PRODUCTOS = "/productos/productos/"
    SERVICIOS = "/productos/servicios/"
    PRESUPUESTOS = "/presupuestos/"
    IMPUESTOS = "/impuestos/"
    CATEGORIAS = "/categorias/"
    MARCAS = "/marcas/"
    COMPROBANTES = "/comprobantes/"


class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.load_token()
   
    def load_token(self):
        """Cargar token desde archivo"""
        try:
            if os.path.exists(Config.TOKEN_FILE):
                with open(Config.TOKEN_FILE, 'r') as f:
                    self.token = f.read().strip()
                if self.token:
                    self.session.headers.update({
                        'Authorization': f'Token {self.token}'
                    })
        except Exception as e:
            print(f"Error cargando token: {e}")
   
    def save_token(self, token):
        """Guardar token en archivo"""
        try:
            self.token = token
            self.session.headers.update({
                'Authorization': f'Token {self.token}'
            })
            with open(Config.TOKEN_FILE, 'w') as f:
                f.write(token)
        except Exception as e:
            print(f"Error guardando token: {e}")
   
    def clear_token(self):
        """Eliminar token"""
        self.token = None
        self.session.headers.pop('Authorization', None)
        try:
            if os.path.exists(Config.TOKEN_FILE):
                os.remove(Config.TOKEN_FILE)
        except:
            pass
   
    def login(self, username, password):
        """Iniciar sesión y obtener token"""
        try:
            url = Config.get_api_url(Endpoints.TOKEN)
            response = self.session.post(
                url,
                data={'username': username, 'password': password},
                timeout=Config.API_TIMEOUT
            )
           
            if response.status_code == 200:
                token = response.json().get('token')
                if token:
                    self.save_token(token)
                    return True, "Login exitoso"
                else:
                    return False, "No se recibió token"
            else:
                error_msg = self._get_error_message(response)
                return False, error_msg
               
        except requests.exceptions.ConnectionError:
            return False, "Error de conexión con el servidor"
        except requests.exceptions.Timeout:
            return False, "Timeout - Servidor no responde"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
   
    def _get_error_message(self, response):
        """Obtener mensaje de error de la respuesta"""
        try:
            data = response.json()
            if isinstance(data, dict):
                if 'non_field_errors' in data:
                    return data['non_field_errors'][0]
                elif 'detail' in data:
                    return data['detail']
                else:
                    return "Credenciales inválidas"
            return "Error de autenticación"
        except:
            return f"Error {response.status_code}: {response.text}"
   
    def test_connection(self):
        """Probar conexión con el servidor"""
        try:
            response = self.session.get(
                Config.get_api_url(Endpoints.CLIENTES),
                timeout=10
            )
            return response.status_code in [200, 401, 403]
        except:
            return False
   
    def get(self, endpoint, params=None):
        """GET request"""
        try:
            url = Config.get_api_url(endpoint)
            response = self.session.get(url, params=params, timeout=Config.API_TIMEOUT)
            return self._handle_response(response)
        except Exception as e:
            return None, f"Error de conexión: {str(e)}"
   
    def post(self, endpoint, data):
        """POST request"""
        try:
            url = Config.get_api_url(endpoint)
            response = self.session.post(url, json=data, timeout=Config.API_TIMEOUT)
            return self._handle_response(response)
        except Exception as e:
            return None, f"Error de conexión: {str(e)}"
   
    def put(self, endpoint, data):
        """PUT request - Para actualizaciones completas"""
        try:
            url = Config.get_api_url(endpoint)
            response = self.session.put(url, json=data, timeout=Config.API_TIMEOUT)
            return self._handle_response(response)
        except Exception as e:
            return None, f"Error de conexión: {str(e)}"
   
    def patch(self, endpoint, data):
        """PATCH request - Para actualizaciones parciales"""
        try:
            url = Config.get_api_url(endpoint)
            response = self.session.patch(url, json=data, timeout=Config.API_TIMEOUT)
            return self._handle_response(response)
        except Exception as e:
            return None, f"Error de conexión: {str(e)}"
   
    def delete(self, endpoint):
        """DELETE request"""
        try:
            url = Config.get_api_url(endpoint)
            response = self.session.delete(url, timeout=Config.API_TIMEOUT)
            return self._handle_response(response)
        except Exception as e:
            return None, f"Error de conexión: {str(e)}"
   
    def _handle_response(self, response):
        """Manejar respuesta de la API"""
        if response.status_code in [200, 201]:
            return response.json(), None
        elif response.status_code == 204:  # No Content (para DELETE exitoso)
            return True, None
        elif response.status_code == 401:
            self.clear_token()
            return None, "Sesión expirada - Por favor inicie sesión nuevamente"
        elif response.status_code == 403:
            return None, "No tiene permisos para esta acción"
        elif response.status_code == 404:
            return None, "Recurso no encontrado"
        else:
            try:
                error_data = response.json()
                return None, f"Error {response.status_code}: {error_data}"
            except:
                return None, f"Error {response.status_code}: {response.text}"

