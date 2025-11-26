# app_escritorio/login_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from auth_manager import AuthManager
from styles import Styles
from configuracion_manager import ConfiguracionManager  # 👈 IMPORTAR NUEVO
import os
from PIL import Image, ImageTk
import sys


class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.auth_manager = AuthManager()
        self.config_manager = ConfiguracionManager()  # 👈 NUEVO
        self.config_login = None  # 👈 NUEVO
       
        # Crear ventana
        self.window = tk.Tk()
        self.window.title("Sistema de Gestión")  # 👈 TÍTULO GENÉRICO
        self.window.geometry("400x350")
        self.window.resizable(False, False)
        self.window.configure(bg=Styles.BG_SECONDARY)
       
        # Cargar configuración del login
        self.cargar_configuracion_login()  # 👈 NUEVO
       
        # Configurar icono
        self.set_icon()
       
        # Centrar ventana
        self.center_window(400, 350)
       
        # Aplicar tema
        self.set_theme()
       
        # Crear interfaz
        self.create_widgets()
       
        # Verificar si ya hay token válido
        self.check_existing_token()

    def cargar_configuracion_login(self):
        """Cargar configuración específica para el login"""
        try:
            print("🔄 Cargando configuración para login...")
            self.config_login = self.config_manager.obtener_config_login()
            if self.config_login:
                print(f"✅ Login config cargada: {self.config_login.get('nombre_fantasia', 'Sin nombre')}")
            else:
                print("⚠️ No se pudo cargar configuración login")
        except Exception as e:
            print(f"❌ Error cargando configuración login: {e}")
            # Usar valores por defecto si hay error
            self.config_login = {
                'nombre_fantasia': 'Def. Servicios',
                'descripcion_sistema': 'Def.Sistema de Gestión Comercial',
                'logo_url': None
            }

    def set_icon(self):
        """Método MEJORADO para configurar el icono en login"""
        print("🔄 Configurando icono en ventana de login...")
       
        # 👇 PRIMERO INTENTAR USAR LOGO DESDE BACKEND
        if self.config_login and self.config_login.get('logo_absolute_url'):
            try:
                logo_image = self.config_manager.descargar_imagen(self.config_login['logo_absolute_url'])
                if logo_image:
                    self.window.iconphoto(True, logo_image)
                    if not hasattr(self, '_icon_photo'):
                        self._icon_photo = logo_image
                    print("✅ Login - Icono cargado desde backend")
                    return
            except Exception as e:
                print(f"❌ Login - Error cargando icono desde backend: {e}")
       
        # 👇 FALLBACK A ICONOS LOCALES
        icon_paths = [
            "logo_lab.ico",
            "logo_64.png",
            "logo_48.png",
            "logo_32.png",
            "logo_128.png",
            "logo_16.png",
            "logo_lab.png",
            "icono.ico",
            "assets/logo_lab.ico",
        ]
       
        icon_loaded = False
       
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    print(f"🔍 Login - Intentando cargar: {icon_path}")
                   
                    if icon_path.lower().endswith('.ico'):
                        self.window.iconbitmap(icon_path)
                        print(f"✅ Login - Icono ICO cargado: {icon_path}")
                        icon_loaded = True
                        break
                       
                    elif icon_path.lower().endswith('.png'):
                        img = Image.open(icon_path)
                        photo = ImageTk.PhotoImage(img)
                       
                        self.window.iconphoto(True, photo)
                        self.window.iconphoto(False, photo)
                       
                        if not hasattr(self, '_icon_photo'):
                            self._icon_photo = photo
                           
                        print(f"✅ Login - Icono PNG cargado: {icon_path}")
                        icon_loaded = True
                        break
                       
                except Exception as e:
                    print(f"❌ Login - Error cargando {icon_path}: {e}")
                    continue
       
        if not icon_loaded:
            print("⚠️ Login - No se pudo cargar ningún icono personalizado")
            self._remove_default_icon_login()

    def _remove_default_icon_login(self):
        """Intentar eliminar el icono por defecto en login"""
        try:
            if sys.platform == "win32":
                self.window.iconbitmap("")
            elif sys.platform == "linux":
                self.window.tk.call('wm', 'iconphoto', self.window._w, '')
            print("🔧 Login - Icono por defecto removido")
        except:
            print("⚠️ Login - No se pudo remover el icono por defecto")

    def center_window(self, width, height):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def set_theme(self):
        """Configurar el tema de Tkinter para login"""
        try:
            style = ttk.Style()
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif 'vista' in available_themes:
                style.theme_use('vista')
            else:
                style.theme_use(available_themes[0] if available_themes else 'default')
        except Exception as e:
            print(f"Error configurando tema en login: {e}")

    def create_widgets(self):
        # Frame principal con mejor diseño
        main_frame = ttk.Frame(self.window, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
       
        # Configurar grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
       
        # 👇 LOGO DESDE BACKEND (SI ESTÁ DISPONIBLE)
        logo_image = None
        if self.config_login and self.config_login.get('logo_absolute_url'):
            try:
                logo_image = self.config_manager.descargar_imagen(self.config_login['logo_absolute_url'])
            except Exception as e:
                print(f"❌ Error descargando logo login: {e}")
       
        # Título con icono
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))
       
        # Mostrar logo si está disponible
        if logo_image:
            logo_label = ttk.Label(title_frame, image=logo_image)
            logo_label.image = logo_image  # Guardar referencia
            logo_label.pack(side=tk.LEFT, padx=(0, 15))
       
        # 👇 USAR CONFIGURACIÓN DINÁMICA DEL BACKEND
        nombre_fantasia = self.config_login.get('nombre_fantasia', 'LAB Servicios') if self.config_login else 'LAB Servicios'
        descripcion_sistema = self.config_login.get('descripcion_sistema', 'Sistema de Gestión Comercial') if self.config_login else 'Sistema de Gestión Comercial'
       
        title_label = ttk.Label(
            title_frame,
            text=nombre_fantasia,  # 👈 DINÁMICO
            font=("Arial", 16, "bold"),
            foreground="#2c3e50"
        )
        title_label.pack(side=tk.LEFT)
       
        subtitle_label = ttk.Label(
            main_frame,
            text=descripcion_sistema,  # 👈 DINÁMICO
            font=("Arial", 10),
            foreground="#7f8c8d"
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
       
        # Campos de entrada
        ttk.Label(main_frame, text="👤 Usuario:", font=("Arial", 9)).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.username_entry = ttk.Entry(main_frame, width=25, font=("Arial", 10))
        self.username_entry.grid(row=2, column=1, pady=(0, 15), padx=(10, 0), sticky=tk.W+tk.E)
       
        ttk.Label(main_frame, text="🔒 Contraseña:", font=("Arial", 9)).grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.password_entry = ttk.Entry(
            main_frame, width=25, show="•", font=("Arial", 10)
        )
        self.password_entry.grid(row=3, column=1, pady=(0, 20), padx=(10, 0), sticky=tk.W+tk.E)
       
        # Botón de login
        self.login_button = ttk.Button(
            main_frame,
            text="🚀 Iniciar Sesión",
            command=self.handle_login,
            style="Accent.TButton"
        )
        self.login_button.grid(row=4, column=0, columnspan=2, pady=(10, 0))
       
        # Información de ayuda
        help_label = ttk.Label(
            main_frame,
            text="💡 Presiona Enter para iniciar sesión",
            font=("Arial", 8),
            foreground="#95a5a6"
        )
        help_label.grid(row=5, column=0, columnspan=2, pady=(15, 0))
       
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.handle_login())
       
        # Focus en usuario
        self.username_entry.focus()

    # ... resto de métodos se mantienen igual ...
    def check_existing_token(self):
        """Verificar si ya existe un token válido"""
        if self.auth_manager.check_auth():
            self.window.after(100, self.on_login_success)

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
       
        if not username or not password:
            messagebox.showerror("Error", "❌ Por favor complete todos los campos")
            return
       
        # Deshabilitar botón durante login
        self.login_button.config(state="disabled")
        self.window.config(cursor="watch")
        self.window.update()
       
        try:
            success, message = self.auth_manager.login(username, password)
           
            if success:
                messagebox.showinfo("Éxito", "✅ " + message)
                self.window.destroy()
                self.on_login_success()
            else:
                messagebox.showerror("Error", "❌ " + message)
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
               
        finally:
            self.login_button.config(state="normal")
            self.window.config(cursor="")

    def run(self):
        self.window.mainloop()