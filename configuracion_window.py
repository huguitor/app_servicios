import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from configuracion_manager import ConfiguracionManager
from styles import Styles
import os
from PIL import Image, ImageTk


class ConfiguracionWindow:
    def __init__(self, parent):
        self.parent = parent
        self.manager = ConfiguracionManager()
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Configuración del Sistema")

        # Color coding
        module_color = Styles.get_module_style("configuracion")
        self.header_strip = tk.Frame(self.window, bg=module_color, height=5)
        self.header_strip.pack(fill=tk.X, side=tk.TOP)
        self.window.geometry("900x750")  # Aumentada para nuevo campo
        self.window.transient(parent)
        self.window.grab_set()
       
        self.center_window(900, 750)
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
                # 🔥 DEBUG: Mostrar estado de sincronización
                estado_sync = self.config_data.get('estado_sincronizacion_numeracion', {})
                if estado_sync:
                    print(f"🔄 Estado sincronización: {estado_sync.get('mensaje', 'No disponible')}")
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
       
        # 👇 NUEVA PESTAÑA: Login & Branding
        login_frame = ttk.Frame(notebook, padding="10")
        notebook.add(login_frame, text="🔐 Login & Branding")
       
        # Pestaña: Información de la Empresa
        empresa_frame = ttk.Frame(notebook, padding="10")
        notebook.add(empresa_frame, text="🏢 Empresa")
       
        # Pestaña: Configuración Presupuestos (MODIFICADA)
        presupuestos_frame = ttk.Frame(notebook, padding="10")
        notebook.add(presupuestos_frame, text="💰 Presupuestos")
       
        # Pestaña: Logos e Imágenes
        logos_frame = ttk.Frame(notebook, padding="10")
        notebook.add(logos_frame, text="🖼️ Logos e Imágenes")
       
        # Crear contenido de las pestañas
        self.create_login_tab(login_frame)
        self.create_empresa_tab(empresa_frame)
        self.create_presupuestos_tab(presupuestos_frame)  # MODIFICADA
        self.create_logos_tab(logos_frame)
       
        # Botones de acción
        self.create_action_buttons(main_frame)

    def create_login_tab(self, parent):
        """👈 NUEVA PESTAÑA: Configuración específica para login"""
        # Variables
        self.nombre_fantasia_var = tk.StringVar(value=self.config_data.get('nombre_fantasia', 'LAB Servicios'))
        self.descripcion_sistema_var = tk.StringVar(value=self.config_data.get('descripcion_sistema', 'Sistema de Gestión Comercial'))
       
        ttk.Label(parent, text="Configuración de la Pantalla de Login", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))
       
        # Campo: Nombre Fantasía
        ttk.Label(parent, text="Nombre Fantasía (Login):*", 
                 font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(parent, text="Nombre comercial que se muestra en el login", 
                 font=("Arial", 8), foreground="gray").grid(row=1, column=1, sticky=tk.W, pady=2)
        nombre_entry = ttk.Entry(parent, textvariable=self.nombre_fantasia_var, width=40)
        nombre_entry.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 15))
       
        # Campo: Descripción del Sistema
        ttk.Label(parent, text="Descripción del Sistema:*", 
                 font=("Arial", 9, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(parent, text="Texto que aparece debajo del nombre en el login", 
                 font=("Arial", 8), foreground="gray").grid(row=3, column=1, sticky=tk.W, pady=2)
        descripcion_entry = ttk.Entry(parent, textvariable=self.descripcion_sistema_var, width=40)
        descripcion_entry.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 15))
       
        # Previsualización del Login
        ttk.Label(parent, text="Previsualización del Login:", 
                 font=("Arial", 9, "bold")).grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
       
        preview_frame = ttk.Frame(parent, relief="solid", borderwidth=1)
        preview_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 10))
        preview_frame.configure(width=300, height=100)
       
        # Mostrar previsualización
        preview_nombre = ttk.Label(
            preview_frame, 
            text=self.nombre_fantasia_var.get(),
            font=("Arial", 12, "bold"),
            foreground="#2c3e50"
        )
        preview_nombre.pack(pady=(10, 2))
       
        preview_desc = ttk.Label(
            preview_frame,
            text=self.descripcion_sistema_var.get(),
            font=("Arial", 9),
            foreground="#7f8c8d"
        )
        preview_desc.pack(pady=(0, 10))
       
        # Actualizar previsualización cuando cambien los valores
        def actualizar_preview(*args):
            preview_nombre.config(text=self.nombre_fantasia_var.get())
            preview_desc.config(text=self.descripcion_sistema_var.get())
       
        self.nombre_fantasia_var.trace("w", actualizar_preview)
        self.descripcion_sistema_var.trace("w", actualizar_preview)
       
        parent.columnconfigure(1, weight=1)

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
        """🔄 MODIFICADA: Crear pestaña de configuración de presupuestos con numeración"""
        # Variables existentes
        self.iva_por_defecto_var = tk.StringVar(value=str(self.config_data.get('iva_por_defecto', '21.00')))
        self.dias_validez_var = tk.StringVar(value=str(self.config_data.get('dias_validez_presupuesto', '30')))
        self.moneda_var = tk.StringVar(value=self.config_data.get('moneda', 'ARS'))
        self.condiciones_comerciales_var = tk.StringVar(value=self.config_data.get('condiciones_comerciales', ''))
       
        # ⭐⭐ NUEVA VARIABLE: Control de numeración
        self.proximo_numero_var = tk.StringVar(value=str(self.config_data.get('proximo_numero_presupuesto', '1')))
       
        # Frame para control de numeración
        numeracion_frame = ttk.LabelFrame(parent, text="🔢 Control de Numeración de Presupuestos", padding="10")
        numeracion_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 20))
       
        # Campo: Próximo número
        ttk.Label(numeracion_frame, text="Próximo Número de Presupuesto:*", 
                 font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Label(numeracion_frame, text="Próximo número que se usará para nuevos presupuestos", 
                 font=("Arial", 8), foreground="gray").grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        self.proximo_numero_entry = ttk.Entry(numeracion_frame, textvariable=self.proximo_numero_var, width=15)
        self.proximo_numero_entry.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
       
        # Botón para verificar sincronización
        self.sync_button = ttk.Button(numeracion_frame, text="🔄 Verificar Sincronización", 
                                     command=self.verificar_sincronizacion)
        self.sync_button.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
       
        # Label para mostrar estado de sincronización
        self.sync_status_label = ttk.Label(numeracion_frame, text="", font=("Arial", 9))
        self.sync_status_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
       
        # Frame para otros parámetros de presupuestos
        parametros_frame = ttk.LabelFrame(parent, text="⚙️ Parámetros Generales de Presupuestos", padding="10")
        parametros_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 20))
       
        # Campos de presupuestos (existentes, reorganizados)
        ttk.Label(parametros_frame, text="IVA por Defecto (%):*").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parametros_frame, textvariable=self.iva_por_defecto_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
       
        ttk.Label(parametros_frame, text="Días de Validez:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parametros_frame, textvariable=self.dias_validez_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
       
        ttk.Label(parametros_frame, text="Moneda:*").grid(row=2, column=0, sticky=tk.W, pady=5)
        moneda_combo = ttk.Combobox(parametros_frame, textvariable=self.moneda_var, width=10, state="readonly")
        moneda_combo['values'] = ['ARS', 'USD', 'EUR']
        moneda_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
       
        # Frame para condiciones comerciales
        condiciones_frame = ttk.LabelFrame(parent, text="📝 Condiciones Comerciales por Defecto", padding="10")
        condiciones_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, pady=(0, 10))
       
        ttk.Label(condiciones_frame, text="Condiciones Comerciales:").grid(row=0, column=0, sticky=tk.NW, pady=5)
        self.condiciones_text = tk.Text(condiciones_frame, width=50, height=8)
        self.condiciones_text.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S, pady=5, padx=(10, 0))
       
        # Cargar condiciones existentes
        condiciones = self.config_data.get('condiciones_comerciales', '')
        self.condiciones_text.insert('1.0', condiciones.replace('\r\n', '\n'))
       
        # Configurar expansión
        parent.columnconfigure(1, weight=1)
        condiciones_frame.columnconfigure(1, weight=1)
        condiciones_frame.rowconfigure(0, weight=1)
       
        # Verificar estado inicial de sincronización
        self.verificar_sincronizacion()

    def verificar_sincronizacion(self):
        """Verificar estado de sincronización con Comprobante"""
        try:
            # Obtener estado de sincronización desde la configuración
            estado_sync = self.config_data.get('estado_sincronizacion_numeracion', {})
           
            if not estado_sync:
                self.sync_status_label.config(
                    text="⚠️ No se pudo verificar estado",
                    foreground="orange"
                )
                return
           
            if estado_sync.get('sincronizado'):
                # Sincronizado correctamente
                mensaje = f"✅ SINCRONIZADO\nConfig: {estado_sync.get('configuracion', 'N/A')} | "
                mensaje += f"Comprobante: {estado_sync.get('comprobante', 'N/A')}"
                self.sync_status_label.config(
                    text=mensaje,
                    foreground="green"
                )
            else:
                # Desincronizado
                mensaje = f"⚠️ DESINCRONIZADO\nConfig: {estado_sync.get('configuracion', 'N/A')} | "
                mensaje += f"Comprobante: {estado_sync.get('comprobante', 'N/A')}"
               
                # Mostrar advertencia visual
                self.sync_status_label.config(
                    text=mensaje,
                    foreground="orange"
                )
               
                # Preguntar si quiere sincronizar automáticamente
                if messagebox.askyesno("Desincronización Detectada", 
                                      f"Hay una desincronización entre la configuración y el comprobante.\n\n"
                                      f"Configuración: {estado_sync.get('configuracion', 'N/A')}\n"
                                      f"Comprobante: {estado_sync.get('comprobante', 'N/A')}\n\n"
                                      "¿Desea sincronizar automáticamente con el comprobante?"):
                    self.sincronizar_automaticamente()
                   
        except Exception as e:
            print(f"❌ Error verificando sincronización: {e}")
            self.sync_status_label.config(
                text=f"❌ Error: {str(e)[:50]}...",
                foreground="red"
            )

    def sincronizar_automaticamente(self):
        """Sincronizar automáticamente con Comprobante"""
        try:
            # Obtener el próximo número actual del campo
            proximo_numero = self.proximo_numero_var.get()
           
            # Preparar datos para actualizar (esto activará la sincronización automática en Django)
            datos_actualizacion = {
                'proximo_numero_presupuesto': int(proximo_numero)
            }
           
            # Actualizar configuración (esto activará sync automático en models.py)
            if self.manager.actualizar_configuracion(datos_actualizacion):
                messagebox.showinfo("Éxito", "Sincronización iniciada. Se sincronizará automáticamente al guardar.")
               
                # Recargar configuración para ver estado actualizado
                self.cargar_configuracion()
                self.verificar_sincronizacion()
            else:
                messagebox.showerror("Error", "No se pudo iniciar la sincronización")
               
        except ValueError:
            messagebox.showerror("Error", "El próximo número debe ser un número entero válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error sincronizando: {e}")

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
                            "Usado en la interfaz de la aplicación desktop y login",
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
        """Validar datos del formulario incluyendo numeración"""
        if not self.nombre_empresa_var.get().strip():
            messagebox.showerror("Error", "El nombre de la empresa es obligatorio")
            return False
       
        if not self.nombre_fantasia_var.get().strip():
            messagebox.showerror("Error", "El nombre fantasía para el login es obligatorio")
            return False
       
        if not self.descripcion_sistema_var.get().strip():
            messagebox.showerror("Error", "La descripción del sistema es obligatoria")
            return False
       
        if not self.cuit_var.get().strip():
            messagebox.showerror("Error", "El CUIT es obligatorio")
            return False
       
        # ⭐⭐ NUEVA VALIDACIÓN: Próximo número
        try:
            proximo_numero = int(self.proximo_numero_var.get())
            if proximo_numero <= 0:
                messagebox.showerror("Error", "El próximo número debe ser mayor a 0")
                return False
            if proximo_numero > 999999:
                messagebox.showerror("Error", "El próximo número es demasiado grande")
                return False
        except ValueError:
            messagebox.showerror("Error", "El próximo número debe ser un número entero válido")
            return False
       
        # Validaciones existentes
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
        """🔄 MODIFICADA: Guardar configuración incluyendo numeración"""
        if not self.validar_formulario():
            return
       
        try:
            # Preparar datos básicos
            datos = {
                'nombre_empresa': self.nombre_empresa_var.get().strip(),
                'nombre_fantasia': self.nombre_fantasia_var.get().strip(),
                'descripcion_sistema': self.descripcion_sistema_var.get().strip(),
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
                # ⭐⭐ NUEVO CAMPO: Próximo número de presupuesto
                'proximo_numero_presupuesto': int(self.proximo_numero_var.get()),
            }
           
            print("💾 Guardando configuración con nuevo campo de numeración...")
            print(f"📦 Datos a guardar: {datos}")
           
            # Preparar archivos para subir
            archivos = {}
            for logo_type, file_path in self.logo_files.items():
                if file_path and os.path.exists(file_path):
                    archivos[logo_type] = file_path
                    print(f"📎 Archivo a subir: {logo_type} -> {file_path}")
           
            # Guardar configuración
            if self.manager.actualizar_configuracion(datos):
                messagebox.showinfo("Éxito", 
                                  "Configuración guardada correctamente.\n\n"
                                  "✅ El próximo número se sincronizará automáticamente con Comprobante.")
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
            # Actualizar campo de próximo número
            if 'proximo_numero_presupuesto' in self.config_data:
                self.proximo_numero_var.set(str(self.config_data['proximo_numero_presupuesto']))
           
            # Recargar imágenes
            self.cargar_imagenes_existentes()
           
            # Verificar sincronización actualizada
            self.verificar_sincronizacion()
           
            messagebox.showinfo("Éxito", "Configuración recargada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo recargar la configuración: {e}")