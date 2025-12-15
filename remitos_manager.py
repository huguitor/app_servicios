# /app_escritorio/remitos_manager.py
from api_client import APIClient, Endpoints
from tkinter import messagebox
import json
import os


class RemitosManager:
    def __init__(self):
        self.client = APIClient()
   
    def obtener_remitos(self, filtros=None):
        """Obtener lista de remitos con filtros opcionales"""
        data, error = self.client.get("/remitos/", params=filtros)
        if error:
            # No mostrar error para listas vacías normales
            return []
        return data if data else []
   
    def obtener_remito_por_id(self, remito_id):
        """Obtener un remito específico por ID"""
        data, error = self.client.get(f"/remitos/{remito_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo obtener el remito: {error}")
            return None
        return data
   
    def crear_remito(self, datos_remito):
        """Crear un nuevo remito"""
        print(f"DEBUG - Datos a enviar para crear remito: {datos_remito}")
       
        # Asegurar que los items tengan el formato correcto
        if 'items' in datos_remito:
            for item in datos_remito['items']:
                # Convertir cantidad a string (ya que es DecimalField en backend)
                if 'cantidad' in item:
                    item['cantidad'] = str(item['cantidad'])
                # Asegurar que no haya campos None
                for key in list(item.keys()):
                    if item[key] is None:
                        item[key] = ''
       
        data, error = self.client.post("/remitos/", datos_remito)
        if error:
            messagebox.showerror("Error", f"No se pudo crear el remito: {error}")
            return None
        messagebox.showinfo("Éxito", "Remito creado correctamente")
        return data
   
    def actualizar_remito(self, remito_id, datos_remito):
        """Actualizar un remito existente - USAR PATCH para actualización parcial"""
        print("🔧 DEBUG MANAGER - ACTUALIZAR REMITO")
        print(f"Remito ID: {remito_id}")
        print(f"Datos completos: {json.dumps(datos_remito, indent=2, default=str)}")
       
        # Verificar específicamente el campo estado
        estado = datos_remito.get('estado')
        print(f"🔧 Campo 'estado' en datos: {estado}")
       
        # Asegurar que los items tengan el formato correcto
        if 'items' in datos_remito:
            for item in datos_remito['items']:
                # Convertir cantidad a string
                if 'cantidad' in item:
                    item['cantidad'] = str(item['cantidad'])
                # Asegurar que no haya campos None
                for key in list(item.keys()):
                    if item[key] is None:
                        item[key] = ''
       
        # USAR PATCH en lugar de PUT para actualización parcial
        endpoint = f"/remitos/{remito_id}/"
        print(f"🔧 Endpoint: {endpoint}")
       
        data, error = self.client.patch(endpoint, datos_remito)
       
        if error:
            print(f"❌ ERROR en actualización: {error}")
            messagebox.showerror("Error", f"No se pudo actualizar el remito: {error}")
            return None
           
        print("✅ Remito actualizado correctamente")
        messagebox.showinfo("Éxito", "Remito actualizado correctamente")
        return data
   
    def eliminar_remito(self, remito_id):
        """Eliminar un remito"""
        data, error = self.client.delete(f"/remitos/{remito_id}/")
        if error:
            messagebox.showerror("Error", f"No se pudo eliminar el remito: {error}")
            return False
        messagebox.showinfo("Éxito", "Remito eliminado correctamente")
        return True
   
    def obtener_clientes(self):
        """Obtener lista de clientes para combobox"""
        data, error = self.client.get(Endpoints.CLIENTES)
        return data if data else []
   
    def obtener_comprobantes_remitos(self):
        """Obtener lista de comprobantes de tipo REMI"""
        data, error = self.client.get("/comprobantes/")
        if data:
            # Filtrar solo los de tipo REMI
            return [c for c in data if c.get('tipo') == 'REMI']
        return []
   
    def validar_items(self, items):
        """Validar que el remito tenga al menos un ítem"""
        if not items or len(items) == 0:
            return False, "El remito debe tener al menos un ítem"
        return True, ""
   
    def anular_remito(self, remito_id, motivo=""):
        """Anular un remito"""
        try:
            print(f"🔧 Anulando remito ID: {remito_id}")
            print(f"📝 Motivo: {motivo}")
           
            # Usar el endpoint de anulación específico para remitos
            endpoint = f"/remitos/{remito_id}/anular/"
            data, error = self.client.post(endpoint, {'motivo': motivo})
           
            if error:
                raise Exception(f"No se pudo anular el remito: {error}")
           
            print("✅ Remito anulado correctamente")
            return data
           
        except Exception as e:
            print(f"❌ Error anulando remito: {e}")
            raise
   
    def puede_anular_remito(self, remito_data):
        """Verificar si un remito puede ser anulado"""
        try:
            estado_actual = remito_data.get('estado', 'borrador')
           
            # Solo se pueden anular remitos en estado borrador o pendiente
            # No se pueden anular remitos entregados
            estados_anulables = ['borrador', 'pendiente']
           
            if estado_actual not in estados_anulables:
                return False, f"No se puede anular un remito en estado '{estado_actual.upper()}'"
           
            # Verificar que no esté ya anulado
            if estado_actual == 'anulado':
                return False, "El remito ya está anulado"
           
            return True, "Puede ser anulado"
           
        except Exception as e:
            print(f"Error verificando si se puede anular: {e}")
            return False, f"Error al verificar: {str(e)}"
   
    # 👇 MÉTODOS PARA ADJUNTOS (similares a presupuestos)
   
    def obtener_adjuntos(self, remito_id):
        """Obtener adjuntos de un remito"""
        try:
            data, error = self.client.get(f"/remitos/{remito_id}/adjuntos/")
            if error:
                print(f"Error obteniendo adjuntos: {error}")
                return []
            return data if data else []
        except Exception as e:
            print(f"Error obteniendo adjuntos: {e}")
            return []
   
    def agregar_adjunto(self, remito_id, archivo_path, tipo, descripcion=""):
        """Agregar un adjunto a un remito"""
        try:
            print(f"📤 Intentando subir archivo: {archivo_path}")
            print(f"📋 Remito ID: {remito_id}")
            print(f"🔧 Tipo: {tipo}")
            print(f"📝 Descripción: {descripcion}")
           
            # Verificar que el archivo existe
            if not os.path.exists(archivo_path):
                raise Exception(f"El archivo no existe: {archivo_path}")
           
            # Verificar tamaño del archivo (límite de 10MB)
            file_size = os.path.getsize(archivo_path) / (1024 * 1024)  # MB
            if file_size > 10:
                raise Exception(f"El archivo es demasiado grande: {file_size:.1f}MB (máximo 10MB)")
           
            # Usar el endpoint de adjuntos de remitos
            endpoint = f"/remitos/{remito_id}/adjuntos/"
            data, error = self.client.post(
                endpoint,
                data={'tipo': tipo, 'descripcion': descripcion},
                files={'archivo': (os.path.basename(archivo_path), open(archivo_path, 'rb'))}
            )
           
            if error:
                raise Exception(f"Error del servidor: {error}")
           
            print(f"✅ Archivo subido exitosamente: {data.get('nombre_original', 'N/A')}")
            return data
           
        except Exception as e:
            print(f"❌ Error subiendo adjunto: {e}")
            raise Exception(f"No se pudo subir el archivo: {str(e)}")
        finally:
            # Asegurarse de cerrar el archivo si se abrió
            try:
                if 'archivo' in locals():
                    locals()['archivo'].close()
            except:
                pass
   
    def obtener_tipos_adjunto(self):
        """Obtener tipos de adjuntos disponibles para remitos"""
        try:
            # Podemos usar los mismos tipos que presupuestos o definir específicos
            return [
                {'codigo': 'entrega', 'label': '📦 Comprobante de entrega'},
                {'codigo': 'firma', 'label': '✍️ Firma del cliente'},
                {'codigo': 'foto', 'label': '🖼️ Foto del producto/servicio'},
                {'codigo': 'documento', 'label': '📄 Documentación adicional'},
                {'codigo': 'otro', 'label': '📎 Otro'}
            ]
        except Exception as e:
            print(f"❌ Error obteniendo tipos: {e}")
            return [
                {'codigo': 'entrega', 'label': '📦 Comprobante de entrega'},
                {'codigo': 'firma', 'label': '✍️ Firma del cliente'},
                {'codigo': 'foto', 'label': '🖼️ Foto del producto/servicio'},
                {'codigo': 'documento', 'label': '📄 Documentación adicional'},
                {'codigo': 'otro', 'label': '📎 Otro'}
            ]
   
    def eliminar_adjunto(self, remito_id, adjunto_id):
        """Eliminar un adjunto de remito"""
        try:
            print(f"🗑️ Eliminando adjunto ID: {adjunto_id} del remito: {remito_id}")
           
            endpoint = f"/remitos/{remito_id}/adjuntos/{adjunto_id}/"
            data, error = self.client.delete(endpoint)
           
            if error:
                raise Exception(f"No se pudo eliminar el adjunto: {error}")
           
            print(f"✅ Adjunto {adjunto_id} eliminado correctamente")
            return True
           
        except Exception as e:
            print(f"❌ Error eliminando adjunto: {e}")
            raise
   
    def obtener_proximo_numero(self):
        """Obtener próximo número disponible para remitos"""
        try:
            data, error = self.client.get("/remitos/proximo_numero/")
            if error:
                return None, error
            return data, None
        except Exception as e:
            return None, f"Error obteniendo próximo número: {e}"