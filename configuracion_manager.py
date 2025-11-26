# app_escritorio/configuracion_manager.py
from api_client import APIClient, Endpoints
from tkinter import messagebox
import os
import requests
from PIL import Image, ImageTk
import io
import json
import time


class ConfiguracionManager:
    def __init__(self):
        print("🔄 CONFIGURACION_MANAGER INICIADO!")
        self.client = APIClient()
        self.configuracion_actual = None
        
        # 🔥 CACHE MEJORADO
        self._cache_config_presupuestos = None
        self._cache_datos_empresa = None
        self._cache_config_login = None
        
        # 🔒 CACHE LOCAL SEGURO
        self.cache_file = "config_login_cache.json"
        self.cache_expiry_hours = 24  # Cache válido por 24 horas
    
    def obtener_configuracion_actual(self):
        """Obtener la configuración activa actual"""
        try:
            # 🔥 USAR ENDPOINT CORRECTO PARA CONFIGURACIÓN GENERAL
            data, error = self.client.get(Endpoints.CONFIGURACION)
            if error:
                print(f"❌ Error obteniendo configuración: {error}")
                return self._crear_configuracion_por_defecto()
           
            if data and len(data) > 0:
                self.configuracion_actual = data[0]  # Tomar el primer registro
                print(f"✅ Configuración obtenida: {self.configuracion_actual.get('nombre_empresa', 'Sin nombre')}")
                return self.configuracion_actual
            else:
                print("⚠️ No hay configuración en la respuesta")
                return self._crear_configuracion_por_defecto()
               
        except Exception as e:
            print(f"💥 Error crítico obteniendo configuración: {e}")
            return self._crear_configuracion_por_defecto()
   
    def obtener_config_login(self):
        """Obtener configuración para login con cache local seguro"""
        try:
            # 1. 🔥 PRIMERO INTENTAR CACHE EN MEMORIA
            if self._cache_config_login:
                print("🔐 Usando cache en memoria para login")
                return self._cache_config_login
            
            # 2. 🔥 LUEGO INTENTAR CACHE LOCAL
            cached_config = self._cargar_cache_local()
            if cached_config and self._cache_es_valido(cached_config):
                print("🔐 Usando cache local para login")
                self._cache_config_login = cached_config['data']
                return cached_config['data']
            
            # 3. 🔥 FINALMENTE OBTENER DEL SERVIDOR
            print("🔐 Obteniendo configuración de login desde API...")
            config_servidor = self._obtener_config_login_servidor()
            
            if config_servidor:
                # 🔒 GUARDAR EN CACHE
                self._cache_config_login = config_servidor
                self._guardar_cache_local(config_servidor)
                print("✅ Configuración login obtenida y cacheada")
                return config_servidor
            else:
                print("❌ No se pudo obtener configuración del servidor")
                return self._config_login_por_defecto()
               
        except Exception as e:
            print(f"❌ Error obteniendo config login: {e}")
            return self._config_login_por_defecto()

    def _obtener_config_login_servidor(self):
        """Obtener configuración login desde el servidor (público)"""
        try:
            from config import Config
            endpoint = Config.get_public_url("/configuracion/configuracion/config_login/")
            
            print(f"🔗 Conectando a: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Configuración login del servidor: {data}")
                return data
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error conectando al servidor: {e}")
            return None

    def _cargar_cache_local(self):
        """Cargar configuración desde cache local"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    print("🔐 Cache local cargado exitosamente")
                    return cache_data
        except Exception as e:
            print(f"❌ Error cargando cache local: {e}")
        return None

    def _guardar_cache_local(self, config_data):
        """Guardar configuración en cache local"""
        try:
            cache_data = {
                'timestamp': time.time(),
                'data': config_data
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print("💾 Cache local guardado exitosamente")
        except Exception as e:
            print(f"❌ Error guardando cache local: {e}")

    def _cache_es_valido(self, cache_data):
        """Verificar si el cache local sigue siendo válido"""
        try:
            cache_time = cache_data.get('timestamp', 0)
            current_time = time.time()
            expiry_seconds = self.cache_expiry_hours * 3600
            
            if current_time - cache_time < expiry_seconds:
                return True
            else:
                print("🔐 Cache local expirado")
                return False
        except:
            return False

    def _config_login_por_defecto(self):
        """Configuración por defecto para login"""
        print("⚠️ Usando configuración de login por defecto (fallback)")
        return {
            'nombre_fantasia': 'LAB Servicios',
            'descripcion_sistema': 'Sistema de Gestión Comercial',
            'logo_url': None,
            'logo_absolute_url': None
        }

    def obtener_datos_empresa(self):
        """Obtener solo los datos de la empresa"""
        try:
            # 🔥 USAR CACHE PARA EVITAR LLAMADAS REPETIDAS
            if self._cache_datos_empresa:
                return self._cache_datos_empresa
               
            data, error = self.client.get(Endpoints.CONFIGURACION)
            if error:
                print(f"❌ Error obteniendo datos empresa: {error}")
                return {}
           
            if data and len(data) > 0:
                empresa_data = data[0]
                self._cache_datos_empresa = empresa_data
                return empresa_data
            return {}
           
        except Exception as e:
            print(f"❌ Error obteniendo datos empresa: {e}")
            return {}
   
    def obtener_config_presupuestos(self):
        """Obtener configuración para presupuestos"""
        try:
            # 🔥 USAR CACHE PARA EVITAR LLAMADAS REPETIDAS
            if self._cache_config_presupuestos:
                return self._cache_config_presupuestos
               
            print("🔧 Obteniendo configuración de presupuestos desde API...")
           
            # 🔥 OBTENER CONFIGURACIÓN GENERAL Y EXTRAER DATOS DE PRESUPUESTOS
            config_data = self.obtener_configuracion_actual()
            if not config_data:
                print("⚠️ No se pudo obtener configuración general")
                return self._config_presupuestos_por_defecto()
           
            # 🔥 CORREGIR: USAR LOS NOMBRES EXACTOS DE LOS CAMPOS DE LA API
            config_presupuestos = {
                'iva_por_defecto': float(config_data.get('iva_por_defecto', 21.0)),
                'dias_validez': int(config_data.get('dias_validez_presupuesto', 30)),
                'condiciones_comerciales': config_data.get('condiciones_comerciales', ''),
                'moneda': config_data.get('moneda', 'ARS')
            }
           
            print(f"✅ Configuración presupuestos procesada: {config_presupuestos}")
           
            # 🔥 GUARDAR EN CACHE
            self._cache_config_presupuestos = config_presupuestos
            return config_presupuestos
           
        except Exception as e:
            print(f"❌ Error obteniendo config presupuestos: {e}")
            return self._config_presupuestos_por_defecto()
   
    def actualizar_configuracion(self, datos_configuracion):
        """Actualizar la configuración global"""
        try:
            # Obtener el ID de la configuración actual
            config_actual = self.obtener_configuracion_actual()
            if not config_actual or 'id' not in config_actual:
                messagebox.showerror("Error", "No se pudo obtener la configuración actual")
                return False
           
            config_id = config_actual['id']
            endpoint = f"{Endpoints.CONFIGURACION}{config_id}/"
           
            # Usar PATCH para actualización parcial
            data, error = self.client.patch(endpoint, datos_configuracion)
           
            if error:
                messagebox.showerror("Error", f"No se pudo actualizar la configuración: {error}")
                return False
           
            messagebox.showinfo("Éxito", "Configuración actualizada correctamente")
           
            # 🔥 LIMPIAR CACHE AL ACTUALIZAR
            self.configuracion_actual = data
            self._cache_config_presupuestos = None
            self._cache_datos_empresa = None
            self._cache_config_login = None
           
            # 🔒 ELIMINAR CACHE LOCAL AL ACTUALIZAR CONFIGURACIÓN
            self._limpiar_cache_local()
           
            return True
           
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando configuración: {e}")
            return False

    def _limpiar_cache_local(self):
        """Limpiar cache local"""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                print("🧹 Cache local limpiado")
        except Exception as e:
            print(f"❌ Error limpiando cache local: {e}")

    def descargar_imagen(self, url_imagen):
        """Descargar imagen desde URL y convertir para Tkinter"""
        try:
            if not url_imagen:
                print("❌ URL de imagen vacía")
                return None
           
            # Si es una URL relativa, construir la URL completa
            if url_imagen.startswith('/'):
                from config import Config
                base_url = Config.BASE_URL.rstrip('/')
                url_imagen = f"{base_url}{url_imagen}"
           
            print(f"🔄 Descargando imagen desde: {url_imagen}")
           
            # Descargar imagen (pública, sin auth)
            response = requests.get(url_imagen, timeout=10)
            response.raise_for_status()
           
            # Convertir a imagen de Tkinter
            image_data = io.BytesIO(response.content)
            pil_image = Image.open(image_data)
           
            # Redimensionar si es muy grande (máximo 500px de ancho/alto)
            max_size = (500, 500)
            pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
           
            return ImageTk.PhotoImage(pil_image)
           
        except Exception as e:
            print(f"❌ Error descargando imagen {url_imagen}: {e}")
            return None
   
    def obtener_logo_principal(self):
        """Obtener el logo principal para la aplicación"""
        if not self.configuracion_actual:
            self.obtener_configuracion_actual()
       
        if self.configuracion_actual and self.configuracion_actual.get('logo_principal_url'):
            return self.descargar_imagen(self.configuracion_actual['logo_principal_url'])
        return None
   
    def obtener_logo_tkinter(self):
        """Obtener el logo específico para Tkinter"""
        if not self.configuracion_actual:
            self.obtener_configuracion_actual()
       
        if self.configuracion_actual and self.configuracion_actual.get('logo_tkinter_url'):
            return self.descargar_imagen(self.configuracion_actual['logo_tkinter_url'])
        return None
   
    def obtener_condiciones_comerciales(self):
        """Obtener las condiciones comerciales por defecto"""
        config = self.obtener_configuracion_actual()
        return config.get('condiciones_comerciales', '')
   
    def obtener_iva_por_defecto(self):
        """Obtener el IVA por defecto"""
        config = self.obtener_configuracion_actual()
        return float(config.get('iva_por_defecto', 21.0))
   
    def _crear_configuracion_por_defecto(self):
        """Crear configuración por defecto si no se puede obtener del servidor"""
        print("⚠️ Usando configuración por defecto (fallback)")
        return {
            'nombre_empresa': 'LAB Servicios',
            'nombre_fantasia': 'LAB Servicios',
            'descripcion_sistema': 'Sistema de Gestión Comercial',
            'cuit': '23-14852171-9',
            'direccion': 'Río Neuquén 4100 - Plottier - Neuquén',
            'telefono': '+542995576550',
            'email': 'labservicios@outlook.com',
            'pagina_web': '',
            'condiciones_comerciales': 'Precios expresados en pesos Argentinos\nPlazo de entrega: Inmediata\nForma de Pago: 30 días',
            'iva_por_defecto': 21.00,
            'dias_validez_presupuesto': 30,
            'moneda': 'ARS',
            'pais': 'Argentina',
            'idioma': 'es'
        }
   
    def _config_presupuestos_por_defecto(self):
        """Configuración por defecto para presupuestos"""
        print("⚠️ Usando configuración de presupuestos por defecto (fallback)")
        return {
            'condiciones_comerciales': 'Precios expresados en pesos Argentinos\nPlazo de entrega: Inmediata\nForma de Pago: 30 días',
            'iva_por_defecto': 21.0,
            'dias_validez': 30
        }
   
    def debug_mostrar_almacenamiento(self):
        """Muestra dónde y qué se está almacenamiento"""
        print("🔍 DEBUG - ALMACENAMIENTO EN MEMORIA:")
        print(f"📍 self.configuracion_actual: {self.configuracion_actual is not None}")
       
        if self.configuracion_actual:
            print(f"🏢 Empresa: {self.configuracion_actual.get('nombre_empresa')}")
            print(f"📞 Teléfono: {self.configuracion_actual.get('telefono')}")
            print(f"💰 IVA: {self.configuracion_actual.get('iva_por_defecto')}")
            print(f"📅 Días validez: {self.configuracion_actual.get('dias_validez_presupuesto')}")
       
        print(f"📍 Cache presupuestos: {self._cache_config_presupuestos is not None}")
        print(f"📍 Cache empresa: {self._cache_datos_empresa is not None}")
        print(f"📍 Cache login: {self._cache_config_login is not None}")
       
        # Verificar cache local
        cache_local = self._cargar_cache_local()
        print(f"📍 Cache local: {cache_local is not None}")
       
        if self._cache_config_presupuestos:
            print(f"📋 Cache presupuestos: {self._cache_config_presupuestos}")
        if self._cache_config_login:
            print(f"🔐 Cache login: {self._cache_config_login}")

    def verificar_conexion_api(self):
        """Verificar si podemos conectarnos a la API de configuración"""
        try:
            print("🔍 Verificando conexión con API de configuración...")
            data, error = self.client.get(Endpoints.CONFIGURACION)
           
            if error:
                print(f"❌ Error de conexión: {error}")
                return False
           
            if data and len(data) > 0:
                print(f"✅ Conexión exitosa. Configuraciones encontradas: {len(data)}")
                return True
            else:
                print("⚠️ Conexión exitosa pero no hay configuraciones")
                return True
               
        except Exception as e:
            print(f"💥 Error de conexión: {e}")
            return False