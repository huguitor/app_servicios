# app_escritorio/image_helper.py
import os
from PIL import Image
import requests
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class ImageHelper:
    @staticmethod
    def convert_webp_to_png(webp_path, png_path=None):
        """
        Convierte archivo WEBP a PNG automáticamente
        """
        try:
            if png_path is None:
                png_path = webp_path.replace('.webp', '.png')
            
            img = Image.open(webp_path)
            
            # Convertir a RGB si es necesario (WEBP puede tener modo RGBA)
            if img.mode in ('RGBA', 'LA'):
                # Crear fondo blanco para imágenes con transparencia
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            img.save(png_path, "PNG", optimize=True)
            logger.info(f"✅ WEBP convertido: {webp_path} -> {png_path}")
            return png_path
            
        except Exception as e:
            logger.error(f"❌ Error convirtiendo WEBP {webp_path}: {e}")
            return None

    @staticmethod
    def load_image_for_tkinter(image_path, max_size=None):
        """
        Carga cualquier imagen y la convierte a formato compatible con Tkinter
        Retorna objeto PIL Image listo para convertir a PhotoImage
        """
        supported_formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        
        try:
            # Si ya es formato compatible, usar directamente
            if image_path.lower().endswith(supported_formats):
                img = Image.open(image_path)
            
            # Si es WEBP, convertir a PNG
            elif image_path.lower().endswith('.webp'):
                png_path = image_path.replace('.webp', '.png')
                
                # Convertir si no existe el PNG o el WEBP es más reciente
                if not os.path.exists(png_path) or \
                   (os.path.exists(image_path) and os.path.getmtime(image_path) > os.path.getmtime(png_path)):
                    png_path = ImageHelper.convert_webp_to_png(image_path, png_path)
                
                if png_path and os.path.exists(png_path):
                    img = Image.open(png_path)
                else:
                    return None
                    
            else:
                logger.warning(f"⚠️ Formato no soportado: {image_path}")
                return None
            
            # Redimensionar si se especifica tamaño máximo
            if max_size:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
            return img
                
        except Exception as e:
            logger.error(f"❌ Error cargando imagen {image_path}: {e}")
            return None

    @staticmethod
    def create_tkinter_photo(image_path, max_size=(300, 300)):
        """
        Crea un objeto PhotoImage de Tkinter desde cualquier formato de imagen
        """
        try:
            img = ImageHelper.load_image_for_tkinter(image_path, max_size)
            if img:
                from PIL import ImageTk
                return ImageTk.PhotoImage(img)
            return None
        except Exception as e:
            logger.error(f"❌ Error creando PhotoImage: {e}")
            return None
        
    @staticmethod
    def create_tkinter_photo_from_bytes(image_buffer, max_size=(300, 300)):
        """
        Crea un objeto PhotoImage de Tkinter desde bytes de imagen
        """
        try:
            from PIL import Image, ImageTk
            
            # Cargar imagen desde bytes
            image_buffer.seek(0)  # Ir al inicio del buffer
            img = Image.open(image_buffer)
            
            # Redimensionar si se especifica tamaño máximo
            if max_size:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
            return ImageTk.PhotoImage(img)
            
        except Exception as e:
            logger.error(f"❌ Error creando PhotoImage desde bytes: {e}")
            return None
    @staticmethod
    def is_webp_format(image_path):
        """Verifica si un archivo es formato WEBP"""
        return image_path.lower().endswith('.webp') if image_path else False