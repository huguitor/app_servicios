# /app_escritorio/presupuestos_manager.py
from api_client import APIClient, Endpoints
from tkinter import messagebox
import json

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