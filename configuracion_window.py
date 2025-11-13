# app_escritorio/configuracion_window.py (VERSIÓN CORREGIDA)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from configuracion_manager import ConfiguracionManager
import os
from PIL import Image, ImageTk

class ConfiguracionWindow:
    def __init__(self, parent):
        self.parent = parent
        self.manager = ConfiguracionManager()
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Configuración del Sistema - Lab Servicios")
        self.window.geometry("900x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.center_window(900, 700)
        self.set_icon()
        
        # Variables
        self.config_data = {}
        self.logo_images = {}
        self.logo_files = {}
        
        # Cargar datos
        self.cargar_configuracion()
        
        # Crear interfaz
        self.create_widgets()

    def set_icon(self):
        """Configurar icono"""
        icon_paths = [
            "logo_lab.ico",
            "logo_32.png", 
            "logo_48.png",
            "logo_64.png",
            "logo_lab.png",
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    if icon_path.lower().endswith('.ico'):
                        self.window.iconbitmap(icon_path)
                    elif icon_path.lower().endswith('.png'):
                        img = Image.open(icon_path)
                        photo = ImageTk.PhotoImage(img)
                        self.window.iconphoto(True, photo)
                        if not hasattr(self, '_icon_photo'):
                            self._icon_photo = photo
                    break
                except:
                    continue

    def center_window(self, width, height):
        """Centrar ventana"""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def cargar_configuracion(self):
        """Cargar configuración actual"""
        try:
            print("🔄 Cargando configuración del sistema...")
            self.config_data = self.manager.obtener_configuracion_actual()
            if self.config_data:
                print(f"✅ Configuración cargada: {self.config_data.get('nombre_empresa', 'Sin nombre')}")
            else:
                print("❌ No se pudo cargar la configuración")
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            messagebox.showerror("Error", f"No se pudo cargar la configuración: {e}")

    def create_widgets(self):
        """Crear interfaz gráfica"""
        # Frame principal con scroll
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook (pestañas)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Pestaña: Información de la Empresa
        empresa_frame = ttk.Frame(notebook, padding="10")
        notebook.add(empresa_frame, text="🏢 Empresa")
        
        # Pestaña: Configuración Presupuestos
        presupuestos_frame = ttk.Frame(notebook, padding="10")
        notebook.add(presupuestos_frame, text="💰 Presupuestos")
        
        # Pestaña: Logos e Imágenes
        logos_frame = ttk.Frame(notebook, padding="10")
        notebook.add(logos_frame, text="🖼️ Logos e Imágenes")
        
        # Crear contenido de las pestañas
        self.create_empresa_tab(empresa_frame)
        self.create_presupuestos_tab(presupuestos_frame)
        self.create_logos_tab(logos_frame)
        
        # Botones de acción
        self.create_action_buttons(main_frame)

    def create_empresa_tab(self, parent):
        """Crear pestaña de información de la empresa"""
        # Variables
        self.nombre_empresa_var = tk.StringVar(value=self.config_data.get('nombre_empresa', ''))
        self.cuit_var = tk.StringVar(value=self.config_data.get('cuit', ''))
        self.direccion_var = tk.StringVar(value=self.config_data.get('direccion', ''))
        self.telefono_var = tk.StringVar(value=self.config_data.get('telefono', ''))
        self.email_var = tk.StringVar(value=self.config_data.get('email', ''))
        self.pagina_web_var = tk.StringVar(value=self.config_data.get('pagina_web', ''))
        self.pais_var = tk.StringVar(value=self.config_data.get('pais', 'Argentina'))
        self.idioma_var = tk.StringVar(value=self.config_data.get('idioma', 'es'))
        
        # Campos de la empresa
        ttk.Label(parent, text="Nombre de la Empresa:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.nombre_empresa_var, width=50).grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=(10, 0))
        
        ttk.Label(parent, text="CUIT:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.cuit_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(parent, text="Dirección:*").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.direccion_var, width=50).grid(row=2, column=1, sticky=tk.W+tk.E, pady=5, padx=(10, 0))
        
        ttk.Label(parent, text="Teléfono:*").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.telefono_var, width=20).grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(parent, text="Email:*").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.email_var, width=30).grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(parent, text="Página Web:").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.pagina_web_var, width=30).grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(parent, text="País:*").grid(row=6, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.pais_var, width=20).grid(row=6, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(parent, text="Idioma:*").grid(row=7, column=0, sticky=tk.W, pady=5)
        idioma_combo = ttk.Combobox(parent, textvariable=self.idioma_var, width=10, state="readonly")
        idioma_combo['values'] = ['es', 'en', 'pt']
        idioma_combo.grid(row=7, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        parent.columnconfigure(1, weight=1)

    def create_presupuestos_tab(self, parent):
        """Crear pestaña de configuración de presupuestos"""
        # Variables
        self.iva_por_defecto_var = tk.StringVar(value=str(self.config_data.get('iva_por_defecto', '21.00')))
        self.dias_validez_var = tk.StringVar(value=str(self.config_data.get('dias_validez_presupuesto', '30')))
        self.moneda_var = tk.StringVar(value=self.config_data.get('moneda', 'ARS'))
        self.condiciones_comerciales_var = tk.StringVar(value=self.config_data.get('condiciones_comerciales', ''))
        
        # Campos de presupuestos
        ttk.Label(parent, text="IVA por Defecto (%):*").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.iva_por_defecto_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(parent, text="Días de Validez:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.dias_validez_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(parent, text="Moneda:*").grid(row=2, column=0, sticky=tk.W, pady=5)
        moneda_combo = ttk.Combobox(parent, textvariable=self.moneda_var, width=10, state="readonly")
        moneda_combo['values'] = ['ARS', 'USD', 'EUR']
        moneda_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(parent, text="Condiciones Comerciales por Defecto:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.condiciones_text = tk.Text(parent, width=50, height=8)
        self.condiciones_text.grid(row=3, column=1, sticky=tk.W+tk.E, pady=5, padx=(10, 0))
        
        # Cargar condiciones existentes
        condiciones = self.config_data.get('condiciones_comerciales', '')
        self.condiciones_text.insert('1.0', condiciones.replace('\r\n', '\n'))
        
        parent.columnconfigure(1, weight=1)

    def create_logos_tab(self, parent):
        """Crear pestaña de logos e imágenes"""
        # Frame con scroll
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 🔥 LOGOS PRINCIPALES
        logos_principales_frame = ttk.LabelFrame(scrollable_frame, text="📋 Logos Principales", padding="10")
        logos_principales_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Logo Principal
        self.crear_logo_frame(logos_principales_frame, 
                            "logo_principal", 
                            "Logo Principal (Documentos):", 
                            "Usado en presupuestos, facturas y documentos formales",
                            "Recomendado: 300x100 px")
        
        # Logo Tkinter
        self.crear_logo_frame(logos_principales_frame, 
                            "logo_tkinter", 
                            "Logo Tkinter (Aplicación):", 
                            "Usado en la interfaz de la aplicación desktop", 
                            "Recomendado: 64x64 px")
        
        # Logo Favicon
        self.crear_logo_frame(logos_principales_frame, 
                            "logo_favicon", 
                            "Favicon (Web/Pequeño):", 
                            "Usado en navegadores web y lugares con espacio limitado",
                            "Recomendado: 32x32 px")
        
        # 🔥 IMÁGENES PUBLICITARIAS
        imagenes_frame = ttk.LabelFrame(scrollable_frame, text="🎴 Imágenes Publicitarias", padding="10")
        imagenes_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Imágenes publicitarias (3)
        for i in range(1, 4):
            self.crear_logo_frame(imagenes_frame, 
                                f"imagen_publicitaria_{i}", 
                                f"Imagen Publicitaria {i}:", 
                                "Usada en documentos promocionales y presentaciones",
                                "Recomendado: 400x300 px")
        
        # Cargar imágenes existentes
        self.cargar_imagenes_existentes()

    def crear_logo_frame(self, parent, logo_type, title, description, size_info):
        """Crear frame individual para cada logo"""
        logo_frame = ttk.Frame(parent)
        logo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(logo_frame, text=title, font=("Arial", 9, "bold")).pack(anchor=tk.W)
        ttk.Label(logo_frame, text=description, font=("Arial", 8), foreground="gray").pack(anchor=tk.W)
        
        # Crear label para mostrar la imagen
        label_name = f'{logo_type}_label'
        setattr(self, label_name, ttk.Label(logo_frame, text=f"No cargado\n{size_info}", 
                                           justify=tk.CENTER))
        getattr(self, label_name).pack(pady=5)
        
        # Botón para cargar
        ttk.Button(logo_frame, text="📁 Cargar Imagen", 
                  command=lambda lt=logo_type: self.cargar_logo(lt)).pack(pady=5)

    def cargar_logo(self, tipo_logo):
        """Cargar logo según el tipo especificado"""
        file_types = [
            ("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("Iconos", "*.ico"),
            ("Todos los archivos", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title=f"Seleccionar {tipo_logo.replace('_', ' ').title()}",
            filetypes=file_types
        )
        
        if file_path:
            try:
                image = Image.open(file_path)
                
                # Definir tamaños según el tipo de logo
                sizes = {
                    'logo_principal': (300, 200),
                    'logo_tkinter': (150, 150),
                    'logo_favicon': (100, 100),
                    'imagen_publicitaria_1': (250, 200),
                    'imagen_publicitaria_2': (250, 200),
                    'imagen_publicitaria_3': (250, 200)
                }
                
                max_size = sizes.get(tipo_logo, (200, 200))
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # Guardar imagen y archivo
                self.logo_images[tipo_logo] = photo
                self.logo_files[tipo_logo] = file_path
                
                # Actualizar label correspondiente
                label_name = f'{tipo_logo}_label'
                if hasattr(self, label_name):
                    getattr(self, label_name).configure(image=photo, text="")
                
                print(f"✅ {tipo_logo} cargado: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")

    def cargar_imagenes_existentes(self):
        """Cargar imágenes existentes desde la configuración"""
        try:
            if not self.config_data:
                return
                
            # Mapeo de campos de la API a nuestros tipos de logo
            logo_fields = {
                'logo_principal': 'logo_principal_absolute_url',
                'logo_tkinter': 'logo_tkinter_absolute_url', 
                'logo_favicon': 'logo_favicon_absolute_url',
                'imagen_publicitaria_1': 'imagen_publicitaria_1_absolute_url',
                'imagen_publicitaria_2': 'imagen_publicitaria_2_absolute_url',
                'imagen_publicitaria_3': 'imagen_publicitaria_3_absolute_url'
            }
            
            for logo_type, api_field in logo_fields.items():
                logo_url = self.config_data.get(api_field)
                if logo_url:
                    print(f"🔄 Cargando {logo_type} desde: {logo_url}")
                    image = self.manager.descargar_imagen(logo_url)
                    if image:
                        self.logo_images[logo_type] = image
                        label_name = f'{logo_type}_label'
                        if hasattr(self, label_name):
                            getattr(self, label_name).configure(image=image, text="")
                        print(f"✅ {logo_type} cargado desde configuración")
                    else:
                        print(f"❌ No se pudo cargar {logo_type}")
                    
        except Exception as e:
            print(f"❌ Error cargando imágenes existentes: {e}")

    def create_action_buttons(self, parent):
        """Crear botones de acción"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="💾 Guardar Configuración", 
                  command=self.guardar_configuracion).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🔄 Recargar", 
                  command=self.recargar_configuracion).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="❌ Cancelar", 
                  command=self.window.destroy).pack(side=tk.LEFT, padx=5)

    def validar_formulario(self):
        """Validar datos del formulario"""
        if not self.nombre_empresa_var.get().strip():
            messagebox.showerror("Error", "El nombre de la empresa es obligatorio")
            return False
        
        if not self.cuit_var.get().strip():
            messagebox.showerror("Error", "El CUIT es obligatorio")
            return False
        
        try:
            iva = float(self.iva_por_defecto_var.get())
            if iva < 0:
                messagebox.showerror("Error", "El IVA no puede ser negativo")
                return False
        except ValueError:
            messagebox.showerror("Error", "El IVA debe ser un número válido")
            return False
        
        try:
            dias_validez = int(self.dias_validez_var.get())
            if dias_validez <= 0:
                messagebox.showerror("Error", "Los días de validez deben ser mayores a 0")
                return False
        except ValueError:
            messagebox.showerror("Error", "Los días de validez deben ser un número entero")
            return False
        
        return True

    def guardar_configuracion(self):
        """Guardar configuración incluyendo logos"""
        if not self.validar_formulario():
            return
        
        try:
            # Preparar datos básicos
            datos = {
                'nombre_empresa': self.nombre_empresa_var.get().strip(),
                'cuit': self.cuit_var.get().strip(),
                'direccion': self.direccion_var.get().strip(),
                'telefono': self.telefono_var.get().strip(),
                'email': self.email_var.get().strip(),
                'pagina_web': self.pagina_web_var.get().strip(),
                'pais': self.pais_var.get(),
                'idioma': self.idioma_var.get(),
                'iva_por_defecto': float(self.iva_por_defecto_var.get()),
                'dias_validez_presupuesto': int(self.dias_validez_var.get()),
                'moneda': self.moneda_var.get(),
                'condiciones_comerciales': self.condiciones_text.get('1.0', tk.END).strip(),
            }
            
            print("💾 Guardando configuración...")
            print(f"📦 Datos a guardar: {datos}")
            
            # Preparar archivos para subir
            archivos = {}
            for logo_type, file_path in self.logo_files.items():
                if file_path and os.path.exists(file_path):
                    archivos[logo_type] = file_path
                    print(f"📎 Archivo a subir: {logo_type} -> {file_path}")
            
            # Guardar configuración
            if self.manager.actualizar_configuracion(datos):
                messagebox.showinfo("Éxito", "Configuración guardada correctamente")
                self.window.destroy()
            else:
                messagebox.showerror("Error", "No se pudo guardar la configuración")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")
            print(f"💥 Error guardando configuración: {e}")

    def recargar_configuracion(self):
        """Recargar configuración desde el servidor"""
        try:
            self.cargar_configuracion()
            # Recargar imágenes también
            self.cargar_imagenes_existentes()
            messagebox.showinfo("Éxito", "Configuración recargada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo recargar la configuración: {e}")