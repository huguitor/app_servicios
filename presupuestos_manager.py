# /app_escritorio/presupuestos_manager.py
from api_client import APIClient, Endpoints
from tkinter import messagebox
import json
import os  # 👈 AGREGAR ESTA IMPORTACIÓN

class PresupuestosManager:
    def __init__(self):
        self.client = APIClient()
   
    def obtener_presupuestos(self, filtros=None):
        """Obtener lista de presupuestos con filtros opcionales"""
        data, error = self.client.get(Endpoints.PRESUPUESTOS, params=filtros)
        if error:
            # No mostrar error para listas vacías normales
            return []
        return data if data else []
   
    def obtener_presupuesto_por_id(self, presupuesto_id):
        """Obtener un presupuesto específico por ID"""
        data, error = self.client.get(f"{Endpoints.PRESUPUESTOS}{presupuesto_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo obtener el presupuesto: {error}")
            return None
        return data
   
    def crear_presupuesto(self, datos_presupuesto):
        """Crear un nuevo presupuesto"""
        print(f"DEBUG - Datos a enviar para crear: {datos_presupuesto}")
       
        # Asegurar que los items tengan el formato correcto
        if 'items' in datos_presupuesto:
            for item in datos_presupuesto['items']:
                # Asegurar que los IDs sean enteros
                if item.get('producto'):
                    item['producto'] = int(item['producto'])
                if item.get('servicio'):
                    item['servicio'] = int(item['servicio'])
       
        data, error = self.client.post(Endpoints.PRESUPUESTOS, datos_presupuesto)
        if error:
            messagebox.showerror("Error", f"No se pudo crear el presupuesto: {error}")
            return None
        messagebox.showinfo("Éxito", "Presupuesto creado correctamente")
        return data
   
    def actualizar_presupuesto(self, presupuesto_id, datos_presupuesto):
        """Actualizar un presupuesto existente - USAR PATCH para actualización parcial"""
        print("🔧 DEBUG MANAGER - ACTUALIZAR PRESUPUESTO")
        print(f"Presupuesto ID: {presupuesto_id}")
        print(f"Datos completos: {json.dumps(datos_presupuesto, indent=2, default=str)}")
        
        # Verificar específicamente el campo estado
        estado = datos_presupuesto.get('estado')
        print(f"🔧 Campo 'estado' en datos: {estado}")
        print(f"🔧 Tipo de estado: {type(estado)}")
        
        # Asegurar que los items tengan el formato correcto
        if 'items' in datos_presupuesto:
            for item in datos_presupuesto['items']:
                # Asegurar que los IDs sean enteros
                if item.get('producto'):
                    item['producto'] = int(item['producto'])
                if item.get('servicio'):
                    item['servicio'] = int(item['servicio'])

        # USAR PATCH en lugar de PUT para actualización parcial
        endpoint = f"{Endpoints.PRESUPUESTOS}{presupuesto_id}/"
        print(f"🔧 Endpoint: {endpoint}")
        
        data, error = self.client.patch(endpoint, datos_presupuesto)
        
        if error:
            print(f"❌ ERROR en actualización: {error}")
            messagebox.showerror("Error", f"No se pudo actualizar el presupuesto: {error}")
            return None
            
        print("✅ Presupuesto actualizado correctamente")
        messagebox.showinfo("Éxito", "Presupuesto actualizado correctamente")
        return data
   
    def eliminar_presupuesto(self, presupuesto_id):
        """Eliminar un presupuesto"""
        data, error = self.client.delete(f"{Endpoints.PRESUPUESTOS}{presupuesto_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo eliminar el presupuesto: {error}")
            return False
        messagebox.showinfo("Éxito", "Presupuesto eliminado correctamente")
        return True
   
    def obtener_clientes(self):
        """Obtener lista de clientes para combobox"""
        data, error = self.client.get(Endpoints.CLIENTES)
        return data if data else []
   
    def obtener_productos(self):
        """Obtener lista de productos para combobox"""
        data, error = self.client.get(Endpoints.PRODUCTOS)
        return data if data else []
   
    def obtener_servicios(self):
        """Obtener lista de servicios para combobox"""
        data, error = self.client.get(Endpoints.SERVICIOS)
        return data if data else []
   
    def validar_items(self, items):
        """Validar que el presupuesto tenga al menos un ítem"""
        if not items or len(items) == 0:
            return False, "El presupuesto debe tener al menos un ítem"
        return True, ""
    

    # 👇 MÉTODOS NUEVOS PARA ADJUNTOS
    
    def obtener_adjuntos(self, presupuesto_id):
        """Obtener adjuntos de un presupuesto"""
        try:
            data, error = self.client.get_adjuntos_presupuesto(presupuesto_id)
            if error:
                print(f"Error obteniendo adjuntos: {error}")
                return []
            return data if data else []
        except Exception as e:
            print(f"Error obteniendo adjuntos: {e}")
            return []
    
    def agregar_adjunto(self, presupuesto_id, archivo_path, tipo, descripcion=""):
        """Agregar un adjunto a un presupuesto con mejor manejo de errores"""
        try:
            print(f"📤 Intentando subir archivo: {archivo_path}")
            print(f"📋 Presupuesto ID: {presupuesto_id}")
            print(f"🔧 Tipo: {tipo}")
            print(f"📝 Descripción: {descripcion}")
            
            # Verificar que el archivo existe
            if not os.path.exists(archivo_path):
                raise Exception(f"El archivo no existe: {archivo_path}")
            
            # Verificar tamaño del archivo (límite de 10MB)
            file_size = os.path.getsize(archivo_path) / (1024 * 1024)  # MB
            if file_size > 10:
                raise Exception(f"El archivo es demasiado grande: {file_size:.1f}MB (máximo 10MB)")
            
            data, error = self.client.subir_adjunto(presupuesto_id, archivo_path, tipo, descripcion)
            
            if error:
                raise Exception(f"Error del servidor: {error}")
            
            print(f"✅ Archivo subido exitosamente: {data.get('nombre_original', 'N/A')}")
            return data
            
        except Exception as e:
            print(f"❌ Error subiendo adjunto: {e}")
            raise Exception(f"No se pudo subir el archivo: {str(e)}")

    def obtener_tipos_adjunto(self):
        """Obtener tipos de adjuntos disponibles con mejor manejo de errores"""
        try:
            data, error = self.client.get_tipos_adjunto()
            
            if error:
                print(f"⚠️ No se pudieron obtener tipos desde API: {error}")
                # Retornar valores por defecto bien formateados
                return [
                    {'codigo': 'factura', 'label': '📄 Factura'},
                    {'codigo': 'contrato', 'label': '📝 Contrato'},
                    {'codigo': 'especificacion', 'label': '📋 Especificación Técnica'},
                    {'codigo': 'diagrama', 'label': '📐 Diagrama'},
                    {'codigo': 'imagen', 'label': '🖼️ Imagen'},
                    {'codigo': 'otro', 'label': '📎 Otro'}
                ]
            
            # Verificar que los datos tengan el formato esperado
            if not data or not isinstance(data, list):
                print("⚠️ Datos de tipos vacíos o formato incorrecto")
                return [
                    {'codigo': 'factura', 'label': '📄 Factura'},
                    {'codigo': 'contrato', 'label': '📝 Contrato'},
                    {'codigo': 'especificacion', 'label': '📋 Especificación Técnica'},
                    {'codigo': 'diagrama', 'label': '📐 Diagrama'},
                    {'codigo': 'imagen', 'label': '🖼️ Imagen'},
                    {'codigo': 'otro', 'label': '📎 Otro'}
                ]
                
            print(f"✅ Tipos obtenidos de API: {len(data)} tipos")
            return data
            
        except Exception as e:
            print(f"❌ Error crítico obteniendo tipos: {e}")
            return [
                {'codigo': 'factura', 'label': '📄 Factura'},
                {'codigo': 'contrato', 'label': '📝 Contrato'},
                {'codigo': 'especificacion', 'label': '📋 Especificación Técnica'},
                {'codigo': 'diagrama', 'label': '📐 Diagrama'},
                {'codigo': 'imagen', 'label': '🖼️ Imagen'},
                {'codigo': 'otro', 'label': '📎 Otro'}
            ]

    def eliminar_adjunto(self, adjunto_id, presupuesto_id):
        """Eliminar un adjunto - VERSIÓN CORREGIDA"""
        try:
            print(f"🗑️ Manager: Eliminando adjunto ID: {adjunto_id} del presupuesto: {presupuesto_id}")
            
            # 👇 PASAR AMBOS PARÁMETROS
            data, error = self.client.eliminar_adjunto(presupuesto_id, adjunto_id)
            
            if error:
                raise Exception(f"No se pudo eliminar el adjunto: {error}")
            
            print(f"✅ Adjunto {adjunto_id} eliminado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error eliminando adjunto: {e}")
            raise
    
    def get_estadisticas_adjuntos(self, presupuesto_id):
        """Obtener estadísticas de adjuntos"""
        try:
            adjuntos = self.obtener_adjuntos(presupuesto_id)
            estadisticas = {
                'total': len(adjuntos),
                'por_tipo': {},
                'tamaño_total': 0
            }
            
            for adjunto in adjuntos:
                tipo = adjunto['tipo']
                if tipo not in estadisticas['por_tipo']:
                    estadisticas['por_tipo'][tipo] = 0
                estadisticas['por_tipo'][tipo] += 1
                estadisticas['tamaño_total'] += adjunto.get('tamaño', 0)
            
            return estadisticas
        except Exception as e:
            print(f"Error calculando estadísticas: {e}")
            return {'total': 0, 'por_tipo': {}, 'tamaño_total': 0}