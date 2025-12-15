# app_escritorio/login_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from auth_manager import AuthManager
from styles import Styles
from configuracion_manager import ConfiguracionManager
import os
from PIL import Image, ImageTk
import sys


class LoginWindow:
    """
    Ventana de inicio de sesión para el sistema de gestión.
    Esta versión optimizada evita el parpadeo de ventana blanca
    al inicializar la ventana solo después de cargar toda la configuración.
    """
    
    def __init__(self, on_login_success):
        """
        Constructor de la clase LoginWindow.
        
        Args:
            on_login_success: Función callback que se ejecuta cuando el login es exitoso
        """
        self.on_login_success = on_login_success  # Callback para cuando el login tiene éxito
        self.auth_manager = AuthManager()  # Gestor de autenticación
        self.config_manager = ConfiguracionManager()  # Gestor de configuración
        self.config_login = None  # Aquí almacenaremos la configuración específica del login
        self.window = None  # Inicializamos la ventana como None (se creará después)
        
        print("🔄 Inicializando LoginWindow...")
        
        # PASO 1: Cargar configuración SIN crear ventana aún
        # Esto evita que Tkinter muestre una ventana vacía mientras se cargan datos
        self.cargar_configuracion_login()
        
        # PASO 2: Crear y configurar la ventana con todo ya cargado
        self.crear_ventana()
        
        # PASO 3: Verificar si ya hay una sesión activa (token válido)
        self.check_existing_token()
    
    def cargar_configuracion_login(self):
        """
        Carga la configuración específica para el login desde el backend.
        Este método se ejecuta ANTES de crear la ventana de Tkinter
        para evitar mostrar una ventana vacía durante la carga.
        """
        try:
            print("🔄 Cargando configuración para login...")
            
            # Obtener configuración del gestor de configuración
            self.config_login = self.config_manager.obtener_config_login()
            
            if self.config_login:
                # Mostrar el nombre de fantasía cargado (para debug)
                nombre = self.config_login.get('nombre_fantasia', 'Sin nombre')
                print(f"✅ Login config cargada: {nombre}")
            else:
                print("⚠️ No se pudo cargar configuración login")
                
        except Exception as e:
            # Si hay error, usar valores por defecto
            print(f"❌ Error cargando configuración login: {e}")
            self.config_login = {
                'nombre_fantasia': 'Servicios Tecnológicos',
                'descripcion_sistema': 'Sistema de Gestión Comercial',
                'logo_url': None
            }
    
    def crear_ventana(self):
        """
        Crea y configura la ventana de Tkinter.
        Se ejecuta DESPUÉS de cargar toda la configuración necesaria.
        """
        print("🔄 Creando ventana de login...")
        
        # 1. Crear la ventana principal de Tkinter
        self.window = tk.Tk()
        self.window.title("Sistema de Gestión")
        self.window.geometry("400x350")  # Tamaño fijo
        self.window.resizable(False, False)  # No redimensionable
        self.window.configure(bg=Styles.BG_SECONDARY)  # Color de fondo
        
        # 2. OCULTAR la ventana temporalmente (IMPORTANTE)
        # withdraw() hace que la ventana no sea visible mientras la configuramos
        self.window.withdraw()
        
        # 3. Configurar el icono de la ventana
        self.set_icon()
        
        # 4. Aplicar el tema visual a los widgets
        self.set_theme()
        
        # 5. Crear todos los widgets (etiquetas, campos, botones)
        self.create_widgets()
        
        # 6. Centrar la ventana en la pantalla
        self.center_window(400, 350)
        
        # 7. Programar la visualización de la ventana para dentro de 100ms
        # Esto asegura que todo esté completamente cargado antes de mostrar
        self.window.after(100, self.mostrar_ventana)
        
        print("✅ Ventana creada y configurada (oculta temporalmente)")
    
    def mostrar_ventana(self):
        """
        Muestra la ventana cuando todo está listo.
        Se llama automáticamente después de que todos los componentes estén configurados.
        """
        print("🔄 Mostrando ventana de login...")
        
        # deiconify() hace visible la ventana que estaba oculta con withdraw()
        self.window.deiconify()
        
        # Actualizar la ventana para asegurar que se muestre correctamente
        self.window.update()
        
        print("✅ Ventana de login visible")
    
    def set_icon(self):
        """
        Configura el icono de la ventana.
        Intenta cargar el icono desde varias fuentes en orden de prioridad.
        """
        print("🔄 Configurando icono en ventana de login...")
        
        # PRIORIDAD 1: Intentar usar logo desde el backend (configuración dinámica)
        if self.config_login and self.config_login.get('logo_absolute_url'):
            try:
                # Descargar imagen desde la URL proporcionada en la configuración
                logo_image = self.config_manager.descargar_imagen(self.config_login['logo_absolute_url'])
                if logo_image:
                    # Establecer el icono en la ventana
                    self.window.iconphoto(True, logo_image)
                    
                    # Guardar referencia para evitar que el garbage collector la elimine
                    if not hasattr(self, '_icon_photo'):
                        self._icon_photo = logo_image
                    
                    print("✅ Login - Icono cargado desde backend")
                    return  # Salir si se cargó exitosamente
                    
            except Exception as e:
                print(f"❌ Login - Error cargando icono desde backend: {e}")
        
        # PRIORIDAD 2: Intentar cargar desde archivos locales (fallback)
        # Lista de posibles rutas de iconos, en orden de prioridad
        icon_paths = [
            "logo_lab.ico",      # Icono de Windows (.ico)
            "logo_64.png",       # PNG de 64x64
            "logo_48.png",       # PNG de 48x48
            "logo_32.png",       # PNG de 32x32
            "logo_128.png",      # PNG de 128x128
            "logo_16.png",       # PNG de 16x16
            "logo_lab.png",      # Logo general PNG
            "icono.ico",         # Icono genérico
            "assets/logo_lab.ico", # En carpeta assets
        ]
        
        icon_loaded = False  # Bandera para saber si se cargó algún icono
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    print(f"🔍 Login - Intentando cargar: {icon_path}")
                    
                    # Para archivos .ICO (Windows)
                    if icon_path.lower().endswith('.ico'):
                        self.window.iconbitmap(icon_path)
                        print(f"✅ Login - Icono ICO cargado: {icon_path}")
                        icon_loaded = True
                        break
                    
                    # Para archivos .PNG (multi-plataforma)
                    elif icon_path.lower().endswith('.png'):
                        # Abrir imagen con PIL
                        img = Image.open(icon_path)
                        # Convertir a formato compatible con Tkinter
                        photo = ImageTk.PhotoImage(img)
                        
                        # Establecer como icono
                        self.window.iconphoto(True, photo)
                        self.window.iconphoto(False, photo)
                        
                        # Guardar referencia
                        if not hasattr(self, '_icon_photo'):
                            self._icon_photo = photo
                        
                        print(f"✅ Login - Icono PNG cargado: {icon_path}")
                        icon_loaded = True
                        break
                    
                except Exception as e:
                    print(f"❌ Login - Error cargando {icon_path}: {e}")
                    continue  # Intentar con el siguiente icono
        
        # Si no se pudo cargar ningún icono personalizado
        if not icon_loaded:
            print("⚠️ Login - No se pudo cargar ningún icono personalizado")
            # Intentar eliminar el icono por defecto de Tkinter
            self._remove_default_icon_login()
    
    def _remove_default_icon_login(self):
        """
        Intenta eliminar el icono por defecto de Tkinter.
        Esto es útil para tener una ventana sin icono en lugar del icono genérico de Tk.
        """
        try:
            # Diferentes métodos según el sistema operativo
            if sys.platform == "win32":
                self.window.iconbitmap("")  # Windows
            elif sys.platform == "linux":
                self.window.tk.call('wm', 'iconphoto', self.window._w, '')  # Linux
            
            print("🔧 Login - Icono por defecto removido")
        except:
            print("⚠️ Login - No se pudo remover el icono por defecto")
    
    def center_window(self, width, height):
        """
        Centra la ventana en la pantalla.
        
        Args:
            width: Ancho de la ventana
            height: Alto de la ventana
        """
        # Obtener dimensiones de la pantalla
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calcular posición para centrar
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Aplicar nueva geometría (tamaño + posición)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
        print(f"📍 Ventana centrada en posición ({x}, {y})")
    
    def set_theme(self):
        """
        Configura el tema visual de los widgets ttk.
        Intenta usar temas más modernos si están disponibles.
        """
        try:
            # Crear objeto Style para manejar temas
            style = ttk.Style()
            
            # Obtener lista de temas disponibles en el sistema
            available_themes = style.theme_names()
            
            # Preferir temas más modernos
            if 'clam' in available_themes:
                style.theme_use('clam')  # Tema Clam (moderno)
                print("🎨 Tema 'clam' aplicado")
            elif 'vista' in available_themes:
                style.theme_use('vista')  # Tema Vista (Windows)
                print("🎨 Tema 'vista' aplicado")
            else:
                # Usar el primer tema disponible o 'default'
                style.theme_use(available_themes[0] if available_themes else 'default')
                print(f"🎨 Tema '{available_themes[0] if available_themes else 'default'}' aplicado")
                
        except Exception as e:
            print(f"❌ Error configurando tema en login: {e}")
    
    def create_widgets(self):
        """
        Crea todos los widgets de la interfaz gráfica.
        """
        print("🔄 Creando widgets de la interfaz...")
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.window, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar sistema de grid para expansión
        self.window.columnconfigure(0, weight=1)  # Columna 0 se expande
        self.window.rowconfigure(0, weight=1)     # Fila 0 se expande
        main_frame.columnconfigure(1, weight=1)   # Columna 1 del frame se expande
        
        # === SECCIÓN DE LOGO Y TÍTULO ===
        
        # Intentar cargar logo desde backend si está disponible
        logo_image = None
        if self.config_login and self.config_login.get('logo_absolute_url'):
            try:
                logo_image = self.config_manager.descargar_imagen(self.config_login['logo_absolute_url'])
                print("✅ Logo descargado desde backend")
            except Exception as e:
                print(f"❌ Error descargando logo login: {e}")
        
        # Frame para título (logo + nombre)
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Mostrar logo si está disponible
        if logo_image:
            logo_label = ttk.Label(title_frame, image=logo_image)
            logo_label.image = logo_image  # Guardar referencia para evitar GC
            logo_label.pack(side=tk.LEFT, padx=(0, 15))
            print("✅ Logo mostrado en interfaz")
        
        # Obtener textos dinámicos desde configuración o usar valores por defecto
        nombre_fantasia = self.config_login.get('nombre_fantasia', 'LAB Servicios') if self.config_login else 'LAB Servicios'
        descripcion_sistema = self.config_login.get('descripcion_sistema', 'Sistema de Gestión Comercial') if self.config_login else 'Sistema de Gestión Comercial'
        
        # Etiqueta con nombre de fantasía
        title_label = ttk.Label(
            title_frame,
            text=nombre_fantasia,
            font=("Arial", 16, "bold"),
            foreground="#2c3e50"  # Color gris oscuro
        )
        title_label.pack(side=tk.LEFT)
        
        # Subtítulo con descripción del sistema
        subtitle_label = ttk.Label(
            main_frame,
            text=descripcion_sistema,
            font=("Arial", 10),
            foreground="#7f8c8d"  # Color gris medio
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # === SECCIÓN DE CAMPOS DE ENTRADA ===
        
        # Campo de usuario
        ttk.Label(main_frame, text="👤 Usuario:", font=("Arial", 9)).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.username_entry = ttk.Entry(main_frame, width=25, font=("Arial", 10))
        self.username_entry.grid(row=2, column=1, pady=(0, 15), padx=(10, 0), sticky=tk.W+tk.E)
        
        # Campo de contraseña
        ttk.Label(main_frame, text="🔒 Contraseña:", font=("Arial", 9)).grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.password_entry = ttk.Entry(
            main_frame, 
            width=25, 
            show="•",  # Mostrar puntos en lugar de texto
            font=("Arial", 10)
        )
        self.password_entry.grid(row=3, column=1, pady=(0, 20), padx=(10, 0), sticky=tk.W+tk.E)
        
        # === BOTÓN DE LOGIN ===
        
        self.login_button = ttk.Button(
            main_frame,
            text="🚀 Iniciar Sesión",
            command=self.handle_login,
            style="Accent.TButton"  # Estilo especial para botón principal
        )
        self.login_button.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # === INFORMACIÓN DE AYUDA ===
        
        help_label = ttk.Label(
            main_frame,
            text="💡 Presiona Enter para iniciar sesión",
            font=("Arial", 8),
            foreground="#95a5a6"  # Color gris claro
        )
        help_label.grid(row=5, column=0, columnspan=2, pady=(15, 0))
        
        # === CONFIGURACIÓN DE EVENTOS DE TECLADO ===
        
        # Asociar la tecla Enter en el campo de contraseña al login
        self.password_entry.bind('<Return>', lambda e: self.handle_login())
        
        # Poner el foco en el campo de usuario al iniciar
        self.username_entry.focus()
        
        print("✅ Widgets creados exitosamente")
    
    def check_existing_token(self):
        """
        Verifica si ya existe un token de sesión válido.
        Si existe, salta directamente al callback de éxito.
        """
        print("🔍 Verificando sesión existente...")
        
        if self.auth_manager.check_auth():
            print("✅ Sesión válida encontrada, saltando login...")
            # Usar after para dar tiempo a que la ventana se cierre correctamente
            self.window.after(100, self.on_login_success)
        else:
            print("ℹ️ No hay sesión activa, mostrando formulario de login")
    
    def handle_login(self):
        """
        Maneja el proceso de inicio de sesión cuando se presiona el botón.
        """
        print("🔄 Procesando inicio de sesión...")
        
        # Obtener valores de los campos
        username = self.username_entry.get().strip()  # trim() para eliminar espacios
        password = self.password_entry.get()
        
        # Validar que los campos no estén vacíos
        if not username or not password:
            messagebox.showerror("Error", "❌ Por favor complete todos los campos")
            self.password_entry.focus()  # Volver al campo de contraseña
            return
        
        # Deshabilitar interfaz durante el login
        self.login_button.config(state="disabled")  # Deshabilitar botón
        self.window.config(cursor="watch")          # Cambiar cursor a reloj de espera
        self.window.update()                        # Forzar actualización visual
        
        try:
            print(f"🔐 Intentando login para usuario: {username}")
            
            # Intentar autenticación
            success, message = self.auth_manager.login(username, password)
            
            if success:
                # Login exitoso
                print(f"✅ Login exitoso para: {username}")
                messagebox.showinfo("Éxito", "✅ " + message)
                
                # Cerrar ventana de login
                self.window.destroy()
                
                # Ejecutar callback de éxito
                self.on_login_success()
            else:
                # Login fallido
                print(f"❌ Login fallido: {message}")
                messagebox.showerror("Error", "❌ " + message)
                
                # Limpiar campo de contraseña y poner foco
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
                
        except Exception as e:
            # Error inesperado
            print(f"💥 Error durante login: {e}")
            messagebox.showerror("Error", f"💥 Error inesperado: {str(e)}")
            
        finally:
            # Siempre restaurar la interfaz
            self.login_button.config(state="normal")  # Habilitar botón
            self.window.config(cursor="")             # Restaurar cursor normal
            print("🔄 Interfaz restaurada después de login")
    
    def run(self):
        """
        Inicia el loop principal de Tkinter.
        Este método mantiene la aplicación corriendo.
        """
        print("🚀 Iniciando loop principal de Tkinter...")
        self.window.mainloop()
        print("👋 Loop principal finalizado")