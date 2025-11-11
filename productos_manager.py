# /app_escritorio/productos_manager.py
from api_client import APIClient, Endpoints
from tkinter import messagebox
from proveedores_manager import ProveedoresManager
from categorias_manager import CategoriasManager  
from marcas_manager import MarcasManager
from impuestos_manager import ImpuestosManager
import json


class ProductosManager:
    def __init__(self):
        self.client = APIClient()
   
    def obtener_productos(self, filtros=None):
        """Obtener lista de productos con filtros opcionales"""
        data, error = self.client.get(Endpoints.PRODUCTOS, params=filtros)
        if error:
            messagebox.showerror("Error", f"No se pudieron obtener los productos: {error}")
            return []
        return data if data else []
   
    def obtener_producto_por_id(self, producto_id):
        """Obtener un producto específico por ID"""
        data, error = self.client.get(f"{Endpoints.PRODUCTOS}{producto_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo obtener el producto: {error}")
            return None
        return data
   
    def crear_producto(self, datos_producto, files=None):
        """Crear un nuevo producto - USAR PUT para creación completa"""
        # Convertir impuestos a formato JSON si es necesario
        if 'productoimpuesto_set' in datos_producto and isinstance(datos_producto['productoimpuesto_set'], list):
            datos_producto['productoimpuesto_set'] = json.dumps(datos_producto['productoimpuesto_set'])
        
        data, error = self.client.post(Endpoints.PRODUCTOS, datos_producto, files=files)
        if error:
            messagebox.showerror("Error", f"No se pudo crear el producto: {error}")
            return None
        messagebox.showinfo("Éxito", "Producto creado correctamente")
        return data
   
    def actualizar_producto(self, producto_id, datos_producto, files=None):
        """Actualizar un producto existente - USAR PATCH para actualización parcial"""
        # Convertir impuestos a formato JSON si es necesario
        if 'productoimpuesto_set' in datos_producto and isinstance(datos_producto['productoimpuesto_set'], list):
            datos_producto['productoimpuesto_set'] = json.dumps(datos_producto['productoimpuesto_set'])
            
        # USAR PATCH en lugar de PUT para actualización parcial
        data, error = self.client.patch(f"{Endpoints.PRODUCTOS}{producto_id}/", datos_producto, files=files)
        if error:
            messagebox.showerror("Error", f"No se pudo actualizar el producto: {error}")
            return None
        messagebox.showinfo("Éxito", "Producto actualizado correctamente")
        return data
   
    def eliminar_producto(self, producto_id):
        """Eliminar un producto (soft delete)"""
        datos = {'activo': False}
        data, error = self.client.patch(f"{Endpoints.PRODUCTOS}{producto_id}/", datos)
        if error:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {error}")
            return False
        messagebox.showinfo("Éxito", "Producto eliminado correctamente")
        return True
   
    def obtener_proveedores(self, filtros=None):
        """Obtener lista de proveedores para combobox"""
        data, error = self.client.get(Endpoints.PROVEEDORES, params=filtros)
        return data if data else []
   
    def obtener_categorias(self):
        """Obtener lista de categorías para combobox"""
        data, error = self.client.get(Endpoints.CATEGORIAS)
        return data if data else []
   
    def obtener_marcas(self):
        """Obtener lista de marcas para combobox"""
        data, error = self.client.get(Endpoints.MARCAS)
        return data if data else []
   
    def obtener_impuestos(self):
        """Obtener lista de impuestos para asignar"""
        data, error = self.client.get(Endpoints.IMPUESTOS)
        return data if data else []
   
    def validar_precios(self, costo_compra, precio_venta):
        """Validar que los precios sean válidos"""
        try:
            costo = float(costo_compra) if costo_compra else 0
            precio = float(precio_venta) if precio_venta else 0
            
            if costo < 0:
                return False, "El costo de compra no puede ser negativo"
            if precio < 0:
                return False, "El precio de venta no puede ser negativo"
            if precio > 0 and costo > precio:
                return False, "El costo no puede ser mayor al precio de venta"
                
            return True, ""
        except ValueError:
            return False, "Los precios deben ser números válidos"