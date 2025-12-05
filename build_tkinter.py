# /app_escritorio/build_tkinter.py
import os
import sys
import shutil
import subprocess
import time

print("🔨 COMPILANDO APP DE ESCRITORIO - LAB SERVICIOS")
print("=" * 60)

# ========== CONFIGURACIÓN ==========
APP_NAME = "LabServicios"
MAIN_FILE = "main.py"  # Tu archivo lanzador
VERSION = "1.0.0"

# ========== FUNCIONES ==========
def clean_previous_builds():
    """Elimina compilaciones anteriores"""
    print("\n🧹 Limpiando compilaciones anteriores...")
    
    # Esperar para liberar recursos
    time.sleep(1)
    
    folders = ['dist', 'build']
    for folder in folders:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder, ignore_errors=True)
                print(f"  ✓ {folder}/")
            except:
                os.system(f'rd /s /q "{folder}" 2>nul')
                print(f"  ✓ {folder}/ (forzado)")
    
    # Eliminar .spec
    spec_file = f'{APP_NAME}.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"  ✓ {spec_file}")

def verify_main_files():
    """Verifica archivos principales"""
    print("\n🔍 Verificando archivos...")
    
    required_files = ["main.py", "main_app.py", "auth_manager.py", "api_client.py"]
    missing = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            missing.append(file)
    
    if missing:
        print(f"\n❌ Faltan archivos requeridos:")
        for f in missing:
            print(f"   - {f}")
        return False
    
    return True

def build_executable():
    """Compila el ejecutable"""
    print("\n⚙️  Configurando PyInstaller...")
    
    # Comando PyInstaller optimizado
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',  # Sin consola para app GUI
        f'--name={APP_NAME}',
        '--clean',
        '--noconfirm',
        # Hidden imports críticos
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ImageTk',
        '--hidden-import=reportlab',
        '--hidden-import=reportlab.pdfgen',
        '--hidden-import=requests',
        '--hidden-import=urllib3',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=main_app',  # Tu módulo principal
        '--hidden-import=login_window',
        '--hidden-import=auth_manager',
        '--hidden-import=api_client',
        # Archivos de datos a incluir
        '--add-data=token.txt;.',
        '--add-data=config.py;.',
        '--add-data=styles.py;.',
        # Optimizaciones
        '--upx-exclude=vcruntime140.dll',
        '--runtime-tmpdir=.',
    ]
    
    # Agregar icono si existe
    if os.path.exists('icon.ico'):
        cmd.append('--icon=icon.ico')
        print("  ✓ Icono personalizado incluido")
    
    # Archivo principal
    cmd.append(MAIN_FILE)
    
    print(f"\n📦 Iniciando compilación...")
    print("   Esto puede tardar 2-5 minutos...")
    
    # Ejecutar
    try:
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n✅ Compilación exitosa en {elapsed_time:.1f} segundos")
            return True
        else:
            print(f"\n❌ Error en la compilación:")
            if result.stderr:
                print(result.stderr[:500])  # Mostrar primeros 500 chars
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def verify_result():
    """Verifica el resultado de la compilación"""
    print("\n🔍 Verificando ejecutable...")
    
    exe_path = os.path.join('dist', f'{APP_NAME}.exe')
    
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"  ✓ Ejecutable creado: {exe_path}")
        print(f"  ✓ Tamaño: {size_mb:.1f} MB")
        
        # Verificar dependencias
        print(f"\n📦 Dependencias incluidas:")
        print(f"  • Tkinter (interfaz gráfica)")
        print(f"  • PIL (manejo de imágenes)")
        print(f"  • ReportLab (generación de PDF)")
        print(f"  • Requests (conexión API)")
        print(f"  • Todos tus módulos personalizados")
        
        return True
    else:
        print(f"  ❌ No se encontró el ejecutable")
        return False

def main():
    """Función principal"""
    print(f"🎯 Aplicación: {APP_NAME} v{VERSION}")
    print(f"📁 Directorio: {os.getcwd()}")
    print(f"📄 Archivo principal: {MAIN_FILE}")
    
    # Paso 1: Limpiar
    clean_previous_builds()
    
    # Paso 2: Verificar archivos
    if not verify_main_files():
        input("\nPresiona Enter para salir...")
        return
    
    # Paso 3: Compilar
    print("\n" + "=" * 60)
    if not build_executable():
        print("\n💡 Consejos para solucionar problemas:")
        print("   1. Asegúrate de estar en la carpeta correcta")
        print("   2. Ejecuta como administrador si hay permisos")
        print("   3. Prueba sin --onefile primero: pyinstaller --windowed main.py")
        input("\nPresiona Enter para salir...")
        return
    
    # Paso 4: Verificar
    print("\n" + "=" * 60)
    if verify_result():
        print("\n" + "=" * 60)
        print("✅ ¡APP COMPILADA EXITOSAMENTE!")
        print("=" * 60)
        
        print(f"\n🚀 PARA USAR:")
        print(f"   1. Asegúrate que el BACKEND esté ejecutándose")
        print(f"      (BackendLabServicios.exe)")
        print(f"   2. Ejecuta: dist\\{APP_NAME}.exe")
        print(f"   3. Credenciales: admin / admin123")
    else:
        print("\n⚠️  Hubo problemas con la compilación")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Compilación cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPresiona Enter para salir...")