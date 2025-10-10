from PIL import Image, ImageDraw
import os

def redimensionar_logo_mantener_proporcion():
    """Redimensionar el logo manteniendo la proporción ovalada"""
    try:
        original_path = "logo_lab.png"
        if not os.path.exists(original_path):
            print("❌ No se encontró logo_lab.png")
            return
        
        img = Image.open(original_path)
        print(f"📐 Tamaño original: {img.size}")
        print(f"🎯 Proporción original: {img.size[0]}/{img.size[1]} = {img.size[0]/img.size[1]:.2f}")
        
        # Mantener la proporción original
        original_ratio = img.size[0] / img.size[1]
        
        # Tamaños para iconos manteniendo proporción
        sizes = {
            "logo_16.png": (16, int(16 / original_ratio)),
            "logo_32.png": (32, int(32 / original_ratio)),
            "logo_48.png": (48, int(48 / original_ratio)),
            "logo_64.png": (64, int(64 / original_ratio)),
            "logo_128.png": (128, int(128 / original_ratio)),
        }
        
        # Crear versiones redimensionadas manteniendo proporción
        for filename, size in sizes.items():
            # Asegurar que el tamaño sea válido
            width, height = size
            if height < 1:
                height = 1
            
            resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
            resized_img.save(filename)
            print(f"✅ Creado: {filename} - {resized_img.size} (proporción: {resized_img.size[0]/resized_img.size[1]:.2f})")
        
        # Crear versión ICO (Windows necesita tamaño cuadrado con fondo transparente)
        ico_size = 64
        ico_img = Image.new('RGBA', (ico_size, ico_size), (0, 0, 0, 0))  # Fondo transparente
        
        # Calcular tamaño para mantener proporción dentro del cuadrado
        if original_ratio > 1:  # Más ancho que alto
            new_width = ico_size
            new_height = int(ico_size / original_ratio)
        else:  # Más alto que ancho
            new_height = ico_size
            new_width = int(ico_size * original_ratio)
        
        # Redimensionar manteniendo proporción
        resized_for_ico = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Centrar en el canvas cuadrado
        x_offset = (ico_size - new_width) // 2
        y_offset = (ico_size - new_height) // 2
        
        ico_img.paste(resized_for_ico, (x_offset, y_offset))
        ico_img.save("logo_lab.ico", format="ICO")
        print(f"✅ Creado: logo_lab.ico - {ico_size}x{ico_size} (con fondo transparente)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    redimensionar_logo_mantener_proporcion()