📁 ESTRUCTURA PARA REPOSITORIO FRONTEND:
text
app_servicios_frontend/          # Nuevo repo para Tkinter
├── app_escritorio/              # Tu código actual
│   ├── *.py                     # Todos tus archivos Python
│   ├── build_tkinter.py         # Script de compilación
│   └── requirements.txt         # Dependencias
├── docs/                        # Documentación
│   ├── INSTALACION.md
│   ├── USO.md
│   └── COMPILACION.md
├── scripts/                     # Scripts útiles
│   ├── launch.bat
│   ├── build.bat
│   └── install_deps.bat
├── .gitignore                   # Archivos a ignorar
├── README.md                    # Documentación principal
├── LICENSE                      # Licencia MIT
└── CHANGELOG.md                 # Historial de cambios
🚀 PASO 3: CREAR ESTRUCTURA COMPLETA
1. Crear carpeta base y organizar:
bash
# Crear carpeta principal
mkdir app_servicios_frontend
cd app_servicios_frontend

# Copiar tu app Tkinter (desde donde la tienes)
xcopy "C:\Users\panoz\Documents\Proyectos_tkinter\gestion_t\app_escritorio\*" "app_escritorio\" /E /I

# Crear estructura adicional
mkdir docs scripts
2. Crear archivos de documentación:
A) README.md (en raíz):

markdown
# 🖥️ Lab Servicios - App de Escritorio (Tkinter)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-orange)
![PyInstaller](https://img.shields.io/badge/PyInstaller-6.17.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

Aplicación de escritorio para gestión comercial desarrollada en Python con Tkinter. 
Conecta con backend Django REST API.

## 📦 Descarga

[![Download Executable](https://img.shields.io/badge/Download-LabServicios.exe-blue)](https://github.com/huguitor/app_servicios_frontend/releases)

**Versión más reciente:** [LabServicios.exe](https://github.com/huguitor/app_servicios_frontend/releases/latest)

## 🚀 Características

- ✅ Interfaz gráfica moderna con Tkinter
- ✅ Login con autenticación por tokens
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Gestión completa de:
  - 👥 Clientes
  - 🏢 Proveedores
  - 📦 Productos
  - 🔧 Servicios
  - 💰 Presupuestos (con generador PDF)
  - 📊 Impuestos
  - 📑 Categorías
  - 🏷️ Marcas
- ✅ Exportación a PDF (ReportLab)
- ✅ Conexión a API REST
- ✅ Compilable a .exe con PyInstaller

## 🏗️ Requisitos del Sistema

- **Windows** 10/11 (64-bit)
- **Backend Django** ejecutándose en `localhost:8000`
- 2 GB RAM mínimo
- 100 MB espacio en disco

## 📥 Instalación Rápida

1. **Descarga** la última versión de [Releases](https://github.com/huguitor/app_servicios_frontend/releases)
2. **Asegúrate** que el backend esté ejecutándose
3. **Ejecuta** `LabServicios.exe`
4. **Ingresa** las credenciales:
   - Usuario: `admin`
   - Contraseña: `admin123`

## 🛠️ Desarrollo

### Prerrequisitos
- Python 3.10 o superior
- pip actualizado

### 1. Clonar repositorio
```bash
git clone https://github.com/huguitor/app_servicios_frontend.git
cd app_servicios_frontend
2. Instalar dependencias
bash
cd app_escritorio
pip install -r requirements.txt
3. Ejecutar en modo desarrollo
bash
python main.py
🔨 Compilación
Compilar a .exe
bash
cd app_escritorio
python build_tkinter.py
El ejecutable se generará en app_escritorio/dist/LabServicios.exe

Opciones de compilación
Modo desarrollo: --console (para ver errores)

Modo producción: --windowed (sin consola)

Con icono: Agregar --icon=icono.ico

📁 Estructura del Proyecto
text
app_servicios_frontend/
├── app_escritorio/          # Código fuente principal
│   ├── main.py             # Punto de entrada (login)
│   ├── main_app.py         # Aplicación principal
│   ├── login_window.py     # Ventana de login
│   ├── *.py               # Módulos de gestión
│   ├── build_tkinter.py   # Script de compilación
│   └── requirements.txt   # Dependencias
├── docs/                  # Documentación
├── scripts/              # Scripts automatizados
└── README.md            # Este archivo
🎯 Módulos Principales
Módulo	Archivo	Descripción
Login	login_window.py	Autenticación de usuarios
Dashboard	main_app.py	Pantalla principal con estadísticas
Clientes	clientes_window.py	Gestión de clientes
Productos	productos_window.py	Gestión de productos
Presupuestos	presupuestos_window.py	Creación y gestión de presupuestos
PDF Generator	pdf_generator.py	Generación de PDFs
API Client	api_client.py	Conexión con backend Django
⚙️ Configuración
La configuración se encuentra en app_escritorio/config.py:

python
# URL del backend Django
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Configuración de la aplicación
APP_NAME = "Lab Servicios"
APP_VERSION = "1.0.0"
🔗 Dependencias Principales
tkinter: Interfaz gráfica

Pillow (PIL): Manipulación de imágenes

reportlab: Generación de PDFs

requests: Conexión HTTP con la API

pyinstaller: Compilación a .exe

🐛 Solución de Problemas
Error: "No se puede conectar al backend"
Verifica que el backend esté ejecutándose

Comprueba la URL en config.py

Prueba en el navegador: http://localhost:8000/api/

Error: "Módulo no encontrado"
Instala las dependencias: pip install -r requirements.txt

En .exe: Agrega el módulo a build_tkinter.py

App se cierra inesperadamente
Compila en modo debug: Cambia --windowed por --console

Revisa los logs en la consola

📄 Licencia
Este proyecto está bajo la Licencia MIT. Ver LICENSE para detalles.

👥 Contribución
Las contribuciones son bienvenidas. Por favor:

Fork el proyecto

Crea una rama para tu feature

Commit tus cambios

Push a la rama

Abre un Pull Request

📞 Contacto
Autor: huguitor

Repositorio: https://github.com/huguitor/app_servicios_frontend

Backend: https://github.com/huguitor/app_servicios

🙏 Agradecimientos
Django REST Framework

PyInstaller

Tkinter
