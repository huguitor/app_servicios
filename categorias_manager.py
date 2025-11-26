# /app_escritorio/categorias_manager.py
from api_client import APIClient, Endpoints
from tkinter import messagebox


class CategoriasManager:
    def __init__(self):
        self.client = APIClient()
   
    def obtener_categorias(self, filtros=None):
        """Obtener lista de categorías con filtros opcionales"""
        data, error = self.client.get(Endpoints.CATEGORIAS, params=filtros)
        if error:
            return []
        return data if data else []
   
    def obtener_categoria_por_id(self, categoria_id):
        """Obtener una categoría específica por ID"""
        data, error = self.client.get(f"{Endpoints.CATEGORIAS}{categoria_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo obtener la categoría: {error}")
            return None
        return data
   
    def crear_categoria(self, datos_categoria):
        """Crear una nueva categoría"""
        data, error = self.client.post(Endpoints.CATEGORIAS, datos_categoria)
        if error:
            messagebox.showerror("Error", f"No se pudo crear la categoría: {error}")
            return None
        messagebox.showinfo("Éxito", "Categoría creada correctamente")
        return data
   
    def actualizar_categoria(self, categoria_id, datos_categoria):
        """Actualizar una categoría existente"""
        data, error = self.client.put(f"{Endpoints.CATEGORIAS}{categoria_id}/", datos_categoria)
        if error:
            messagebox.showerror("Error", f"No se pudo actualizar la categoría: {error}")
            return None
        messagebox.showinfo("Éxito", "Categoría actualizada correctamente")
        return data
   
    def eliminar_categoria(self, categoria_id):
        """Eliminar una categoría"""
        data, error = self.client.delete(f"{Endpoints.CATEGORIAS}{categoria_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo eliminar la categoría: {error}")
            return False
        messagebox.showinfo("Éxito", "Categoría eliminada correctamente")
        return True
    