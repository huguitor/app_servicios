# /app_escritorio/impuestos_manager.py
from api_client import APIClient, Endpoints
from tkinter import messagebox


class ImpuestosManager:
    def __init__(self):
        self.client = APIClient()
   
    def obtener_impuestos(self, filtros=None):
        """Obtener lista de impuestos con filtros opcionales"""
        try:
            data, error = self.client.get(Endpoints.IMPUESTOS, params=filtros)
            if error:
                return []
            return data if data else []
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener impuestos: {str(e)}")
            return []
   
    def obtener_impuesto_por_id(self, impuesto_id):
        """Obtener un impuesto específico por ID"""
        try:
            data, error = self.client.get(f"{Endpoints.IMPUESTOS}{impuesto_id}/")
            if error:
                messagebox.showerror("Error", f"No se pudo obtener el impuesto: {error}")
                return None
            return data
        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión: {str(e)}")
            return None
   
    def crear_impuesto(self, datos_impuesto):
        """Crear un nuevo impuesto"""
        try:
            # Agregar validación adicional
            if not self.validar_datos_impuesto(datos_impuesto):
                return None
            
            # **DEBUG:** Mostrar datos que se enviarán
            print(f"[DEBUG] Datos a enviar al crear impuesto: {datos_impuesto}")
                
            data, error = self.client.post(Endpoints.IMPUESTOS, datos_impuesto)
            
            if error:
                # **DEBUG:** Mostrar error detallado
                print(f"[DEBUG] Error al crear impuesto: {error}")
                messagebox.showerror("Error", f"No se pudo crear el impuesto: {error}")
                return None
            
            # **DEBUG:** Mostrar respuesta
            print(f"[DEBUG] Respuesta del servidor: {data}")
            
            messagebox.showinfo("Éxito", "Impuesto creado correctamente")
            return data
        except Exception as e:
            print(f"[DEBUG] Excepción al crear impuesto: {str(e)}")
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
            return None
   
    def actualizar_impuesto(self, impuesto_id, datos_impuesto):
        """Actualizar un impuesto existente"""
        try:
            if not self.validar_datos_impuesto(datos_impuesto):
                return None
            
            # **DEBUG:** Mostrar datos que se enviarán
            print(f"[DEBUG] Datos a enviar al actualizar impuesto {impuesto_id}: {datos_impuesto}")
                
            data, error = self.client.put(f"{Endpoints.IMPUESTOS}{impuesto_id}/", datos_impuesto)
            
            if error:
                # **DEBUG:** Mostrar error detallado
                print(f"[DEBUG] Error al actualizar impuesto: {error}")
                messagebox.showerror("Error", f"No se pudo actualizar el impuesto: {error}")
                return None
            
            # **DEBUG:** Mostrar respuesta
            print(f"[DEBUG] Respuesta del servidor: {data}")
            
            messagebox.showinfo("Éxito", "Impuesto actualizado correctamente")
            return data
        except Exception as e:
            print(f"[DEBUG] Excepción al actualizar impuesto: {str(e)}")
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
            return None
   
    def eliminar_impuesto(self, impuesto_id):
        """Eliminar un impuesto con confirmación de dependencias"""
        try:
            # Verificar si el impuesto está siendo usado
            if self.verificar_dependencias(impuesto_id):
                messagebox.showwarning(
                    "No se puede eliminar",
                    "Este impuesto está siendo utilizado en productos o servicios. "
                    "Debe eliminar o modificar esas dependencias primero."
                )
                return False
            
            data, error = self.client.delete(f"{Endpoints.IMPUESTOS}{impuesto_id}/")
            if error:
                messagebox.showerror("Error", f"No se pudo eliminar el impuesto: {error}")
                return False
            messagebox.showinfo("Éxito", "Impuesto eliminado correctamente")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")
            return False
    
    def verificar_dependencias(self, impuesto_id):
        """Verificar si el impuesto está siendo utilizado"""
        # TODO: Implementar lógica para verificar dependencias
        # Por ejemplo, buscar en productos o servicios que usen este impuesto
        # Por ahora retornamos False (no implementado)
        return False
   
    def validar_porcentaje(self, porcentaje):
        """Validar formato de porcentaje"""
        try:
            porcentaje_float = float(porcentaje)
            if porcentaje_float < 0:
                return False, "El porcentaje no puede ser negativo"
            if porcentaje_float > 100:
                return False, "El porcentaje no puede ser mayor a 100"
            return True, ""
        except ValueError:
            return False, "El porcentaje debe ser un número válido"
    
    def validar_datos_impuesto(self, datos):
        """Validación completa de datos del impuesto"""
        if 'nombre' not in datos or not datos['nombre'].strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return False
        
        if 'porcentaje' not in datos:
            messagebox.showerror("Error", "El porcentaje es obligatorio")
            return False
        
        if 'tipo' not in datos or datos['tipo'] not in ['compra', 'venta', 'ambos']:
            messagebox.showerror("Error", "El tipo debe ser: compra, venta o ambos")
            return False
        
        return True