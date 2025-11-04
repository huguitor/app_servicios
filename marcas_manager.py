from api_client import APIClient, Endpoints
from tkinter import messagebox


class MarcasManager:
    def __init__(self):
        self.client = APIClient()
   
    def obtener_marcas(self, filtros=None):
        """Obtener lista de marcas con filtros opcionales"""
        data, error = self.client.get(Endpoints.MARCAS, params=filtros)
        if error:
            return []
        return data if data else []
   
    def obtener_marca_por_id(self, marca_id):
        """Obtener una marca específica por ID"""
        data, error = self.client.get(f"{Endpoints.MARCAS}{marca_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo obtener la marca: {error}")
            return None
        return data
   
    def crear_marca(self, datos_marca):
        """Crear una nueva marca"""
        data, error = self.client.post(Endpoints.MARCAS, datos_marca)
        if error:
            messagebox.showerror("Error", f"No se pudo crear la marca: {error}")
            return None
        messagebox.showinfo("Éxito", "Marca creada correctamente")
        return data
   
    def actualizar_marca(self, marca_id, datos_marca):
        """Actualizar una marca existente"""
        data, error = self.client.put(f"{Endpoints.MARCAS}{marca_id}/", datos_marca)
        if error:
            messagebox.showerror("Error", f"No se pudo actualizar la marca: {error}")
            return None
        messagebox.showinfo("Éxito", "Marca actualizada correctamente")
        return data
   
    def eliminar_marca(self, marca_id):
        """Eliminar una marca"""
        data, error = self.client.delete(f"{Endpoints.MARCAS}{marca_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo eliminar la marca: {error}")
            return False
        messagebox.showinfo("Éxito", "Marca eliminada correctamente")
        return True