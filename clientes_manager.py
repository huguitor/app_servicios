# app_escritorio/clientes_manager.py
from api_client import APIClient, Endpoints
from tkinter import messagebox
import json

class ClientesManager:
    def __init__(self):
        self.client = APIClient()
    
    def obtener_clientes(self, filtros=None):
        """Obtener lista de clientes con filtros opcionales"""
        data, error = self.client.get(Endpoints.CLIENTES, params=filtros)
        if error:
            messagebox.showerror("Error", f"No se pudieron obtener los clientes: {error}")
            return []
        return data if data else []
    
    def obtener_cliente_por_id(self, cliente_id):
        """Obtener un cliente específico por ID"""
        data, error = self.client.get(f"{Endpoints.CLIENTES}{cliente_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo obtener el cliente: {error}")
            return None
        return data
    
    def crear_cliente(self, datos_cliente):
        """Crear un nuevo cliente"""
        data, error = self.client.post(Endpoints.CLIENTES, datos_cliente)
        if error:
            messagebox.showerror("Error", f"No se pudo crear el cliente: {error}")
            return None
        messagebox.showinfo("Éxito", "Cliente creado correctamente")
        return data
    
    def actualizar_cliente(self, cliente_id, datos_cliente):
        """Actualizar un cliente existente - USAR PUT"""
        data, error = self.client.put(f"{Endpoints.CLIENTES}{cliente_id}/", datos_cliente)
        if error:
            messagebox.showerror("Error", f"No se pudo actualizar el cliente: {error}")
            return None
        messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
        return data
    
    def eliminar_cliente(self, cliente_id):
        """Eliminar un cliente (soft delete) - USAR PATCH para cambiar estado"""
        # En nuestro backend, usamos el campo 'activo' para soft delete
        datos = {'activo': False}
        data, error = self.client.patch(f"{Endpoints.CLIENTES}{cliente_id}/", datos)
        if error:
            messagebox.showerror("Error", f"No se pudo eliminar el cliente: {error}")
            return False
        messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
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