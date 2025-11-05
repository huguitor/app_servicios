# app_escritorio/servicios_manager.py
from api_client import APIClient, Endpoints
from tkinter import messagebox
import json

class ServiciosManager:
    def __init__(self):
        self.client = APIClient()
    
    def obtener_servicios(self, filtros=None):
        """Obtener lista de servicios con filtros opcionales"""
        data, error = self.client.get(Endpoints.SERVICIOS, params=filtros)
        if error:
            messagebox.showerror("Error", f"No se pudieron obtener los servicios: {error}")
            return []
        return data if data else []
    
    def obtener_servicio_por_id(self, servicio_id):
        """Obtener un servicio específico por ID"""
        data, error = self.client.get(f"{Endpoints.SERVICIOS}{servicio_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo obtener el servicio: {error}")
            return None
        return data
    
    def crear_servicio(self, datos_servicio):
        """Crear un nuevo servicio"""
        # Convertir impuestos a formato JSON si es necesario
        if 'servicioimpuesto_set' in datos_servicio and isinstance(datos_servicio['servicioimpuesto_set'], list):
            datos_servicio['servicioimpuesto_set'] = json.dumps(datos_servicio['servicioimpuesto_set'])
        
        data, error = self.client.post(Endpoints.SERVICIOS, datos_servicio)
        if error:
            messagebox.showerror("Error", f"No se pudo crear el servicio: {error}")
            return None
        messagebox.showinfo("Éxito", "Servicio creado correctamente")
        return data
    
    def actualizar_servicio(self, servicio_id, datos_servicio):
        """Actualizar un servicio existente"""
        # Convertir impuestos a formato JSON si es necesario
        if 'servicioimpuesto_set' in datos_servicio and isinstance(datos_servicio['servicioimpuesto_set'], list):
            datos_servicio['servicioimpuesto_set'] = json.dumps(datos_servicio['servicioimpuesto_set'])
            
        data, error = self.client.patch(f"{Endpoints.SERVICIOS}{servicio_id}/", datos_servicio)
        if error:
            messagebox.showerror("Error", f"No se pudo actualizar el servicio: {error}")
            return None
        messagebox.showinfo("Éxito", "Servicio actualizado correctamente")
        return data
    
    def eliminar_servicio(self, servicio_id):
        """Eliminar un servicio (soft delete)"""
        datos = {'activo': False}
        data, error = self.client.patch(f"{Endpoints.SERVICIOS}{servicio_id}/", datos)
        if error:
            messagebox.showerror("Error", f"No se pudo eliminar el servicio: {error}")
            return False
        messagebox.showinfo("Éxito", "Servicio eliminado correctamente")
        return True
    
    def obtener_categorias(self):
        """Obtener lista de categorías para combobox"""
        data, error = self.client.get(Endpoints.CATEGORIAS)
        return data if data else []
    
    def obtener_impuestos(self):
        """Obtener lista de impuestos para asignar"""
        data, error = self.client.get(Endpoints.IMPUESTOS)
        return data if data else []
    
    def validar_precios(self, costo_base, precio_base):
        """Validar que los precios sean válidos"""
        try:
            costo = float(costo_base) if costo_base else 0
            precio = float(precio_base) if precio_base else 0
            
            if costo < 0:
                return False, "El costo base no puede ser negativo"
            if precio < 0:
                return False, "El precio base no puede ser negativo"
            if precio > 0 and costo > precio:
                return False, "El costo no puede ser mayor al precio base"
                
            return True, ""
        except ValueError:
            return False, "Los precios deben ser números válidos"