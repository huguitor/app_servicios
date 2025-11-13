# app_escritorio/configuracion_manager.py
from api_client import APIClient, Endpoints
from tkinter import messagebox
import os
import requests
from PIL import Image, ImageTk
import io

class ConfiguracionManager:
    def __init__(self):
        print("🔄 CONFIGURACION_MANAGER INICIADO!")
        self.client = APIClient()
        self.configuracion_actual = None
        # 🔥 AGREGAR CACHE PARA MEJOR PERFORMANCE
        self._cache_config_presupuestos = None
        self._cache_datos_empresa = None
    
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
        """Obtener configuración para presupuestos - VERSIÓN CORREGIDA"""
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
            
            print(f"📋 Configuración RAW de API: {config_data}")
            
            # 🔥 CORREGIR: USAR LOS NOMBRES EXACTOS DE LOS CAMPOS DE LA API
            config_presupuestos = {
                'iva_por_defecto': float(config_data.get('iva_por_defecto', 21.0)),
                'dias_validez': int(config_data.get('dias_validez_presupuesto', 1)),  # ← NOMBRE CORREGIDO
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
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando configuración: {e}")
            return False
    
    def descargar_imagen(self, url_imagen):
        """Descargar imagen desde URL y convertir para Tkinter"""
        try:
            if not url_imagen:
                return None
            
            # Si es una URL relativa, construir la URL completa
            if url_imagen.startswith('/'):
                from config import Config
                base_url = Config.BASE_URL.rstrip('/')
                url_imagen = f"{base_url}{url_imagen}"
            
            # Descargar imagen
            headers = {}
            if self.client.token:
                headers['Authorization'] = f'Token {self.client.token}'
            
            response = requests.get(url_imagen, headers=headers, timeout=10)
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
        
        if self._cache_config_presupuestos:
            print(f"📋 Cache presupuestos: {self._cache_config_presupuestos}")

    # 🔥 NUEVO MÉTODO: VERIFICAR CONEXIÓN CON LA API
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

    # 🔥 NUEVO MÉTODO: OBTENER CONFIGURACIÓN CON DEBUG DETALLADO
    def obtener_config_presupuestos_con_debug(self):
        """Obtener configuración con información detallada de debug"""
        print("🐛 DEBUG DETALLADO - CONFIGURACIÓN PRESUPUESTOS")
        
        # Obtener configuración general
        config_general = self.obtener_configuracion_actual()
        print(f"📋 Configuración general completa: {config_general}")
        
        # Extraer campos específicos
        iva_api = config_general.get('iva_por_defecto')
        dias_validez_api = config_general.get('dias_validez_presupuesto')
        condiciones_api = config_general.get('condiciones_comerciales')
        
        print(f"💰 IVA en API: {iva_api} (tipo: {type(iva_api)})")
        print(f"📅 Días validez en API: {dias_validez_api} (tipo: {type(dias_validez_api)})")
        print(f"📄 Condiciones en API: '{condiciones_api}'")
        
        # Procesar como lo haría el método normal
        config_presupuestos = self.obtener_config_presupuestos()
        print(f"🎯 Configuración final para presupuestos: {config_presupuestos}")
        
        return config_presupuestos