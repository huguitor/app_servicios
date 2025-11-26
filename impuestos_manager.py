# /app_escritorio/impuestos_manager.py
from api_client import APIClient, Endpoints
from tkinter import messagebox


class ImpuestosManager:
    def __init__(self):
        self.client = APIClient()
   
    def obtener_impuestos(self, filtros=None):
        """Obtener lista de impuestos con filtros opcionales"""
        data, error = self.client.get(Endpoints.IMPUESTOS, params=filtros)
        if error:
            return []
        return data if data else []
   
    def obtener_impuesto_por_id(self, impuesto_id):
        """Obtener un impuesto específico por ID"""
        data, error = self.client.get(f"{Endpoints.IMPUESTOS}{impuesto_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo obtener el impuesto: {error}")
            return None
        return data
   
    def crear_impuesto(self, datos_impuesto):
        """Crear un nuevo impuesto"""
        data, error = self.client.post(Endpoints.IMPUESTOS, datos_impuesto)
        if error:
            messagebox.showerror("Error", f"No se pudo crear el impuesto: {error}")
            return None
        messagebox.showinfo("Éxito", "Impuesto creado correctamente")
        return data
   
    def actualizar_impuesto(self, impuesto_id, datos_impuesto):
        """Actualizar un impuesto existente"""
        data, error = self.client.put(f"{Endpoints.IMPUESTOS}{impuesto_id}/", datos_impuesto)
        if error:
            messagebox.showerror("Error", f"No se pudo actualizar el impuesto: {error}")
            return None
        messagebox.showinfo("Éxito", "Impuesto actualizado correctamente")
        return data
   
    def eliminar_impuesto(self, impuesto_id):
        """Eliminar un impuesto"""
        data, error = self.client.delete(f"{Endpoints.IMPUESTOS}{impuesto_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo eliminar el impuesto: {error}")
            return False
        messagebox.showinfo("Éxito", "Impuesto eliminado correctamente")
        return True
   
    def validar_porcentaje(self, porcentaje):
        """Validar formato de porcentaje"""
        try:
            porcentaje_float = float(porcentaje)
            if porcentaje_float < 0:
                return False, "El porcentaje no puede ser negativo"
            return True, ""
        except ValueError:
            return False, "El porcentaje debe ser un número válido"