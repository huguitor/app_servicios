# app_escritorio/proveedores_manager.py
from api_client import APIClient, Endpoints
from tkinter import messagebox

class ProveedoresManager:
    def __init__(self):
        self.client = APIClient()
   
    def obtener_proveedores(self, filtros=None):
        """Obtener lista de proveedores con filtros opcionales"""
        data, error = self.client.get(Endpoints.PROVEEDORES, params=filtros)
        if error:
            # No mostrar error para evitar mensajes repetitivos
            return []
        return data if data else []
    
    def obtener_proveedor_por_id(self, proveedor_id):
        """Obtener un proveedor específico por ID"""
        data, error = self.client.get(f"{Endpoints.PROVEEDORES}{proveedor_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo obtener el proveedor: {error}")
            return None
        return data
    
    def crear_proveedor(self, datos_proveedor):
        """Crear un nuevo proveedor"""
        data, error = self.client.post(Endpoints.PROVEEDORES, datos_proveedor)
        if error:
            messagebox.showerror("Error", f"No se pudo crear el proveedor: {error}")
            return None
        messagebox.showinfo("Éxito", "Proveedor creado correctamente")
        return data
    
    def actualizar_proveedor(self, proveedor_id, datos_proveedor):
        """Actualizar un proveedor existente"""
        data, error = self.client.put(f"{Endpoints.PROVEEDORES}{proveedor_id}/", datos_proveedor)
        if error:
            messagebox.showerror("Error", f"No se pudo actualizar el proveedor: {error}")
            return None
        messagebox.showinfo("Éxito", "Proveedor actualizado correctamente")
        return data
    
    def eliminar_proveedor(self, proveedor_id):
        """Eliminar un proveedor (soft delete)"""
        datos = {'activo': False}
        data, error = self.client.patch(f"{Endpoints.PROVEEDORES}{proveedor_id}/", datos)
        if error:
            messagebox.showerror("Error", f"No se pudo eliminar el proveedor: {error}")
            return False
        messagebox.showinfo("Éxito", "Proveedor eliminado correctamente")
        return True
    
    def validar_documento(self, documento, tipo):
        """Validar formato de documento según tipo"""
        if not documento:
            return True  # Documento opcional
        
        if tipo == "fisica" and len(documento) != 8:
            return False
        elif tipo == "juridica" and len(documento) != 11:
            return False
        
        return documento.isdigit()