# /app_escritorio/main_app.py
import tkinter as tk
from tkinter import ttk, messagebox
from auth_manager import AuthManager
from config import Config
from configuracion_window import ConfiguracionWindow
from clientes_window import ClientesWindow
from proveedores_window import ProveedoresWindow
from impuestos_window import ImpuestosWindow
from categorias_window import CategoriasWindow
from marcas_window import MarcasWindow
from productos_window import ProductosWindow
from servicios_window import ServiciosWindow
from presupuestos_window import PresupuestosWindow
import os
from PIL import Image, ImageTk
import sys

# Importar los managers para obtener datos reales
from clientes_manager import ClientesManager
from proveedores_manager import ProveedoresManager
from impuestos_manager import ImpuestosManager
from categorias_manager import CategoriasManager
from marcas_manager import MarcasManager
from productos_manager import ProductosManager
from servicios_manager import ServiciosManager
from presupuestos_manager import PresupuestosManager

class MainApp:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.window = tk.Tk()
       
        # Inicializar managers para obtener datos reales
        self.clientes_manager = ClientesManager()
        self.proveedores_manager = ProveedoresManager()
        self.impuestos_manager = ImpuestosManager()
        self.categorias_manager = CategoriasManager()
        self.marcas_manager = MarcasManager()
        self.productos_manager = ProductosManager()
        self.servicios_manager = ServiciosManager()
        self.presupuestos_manager = PresupuestosManager()
       
        self.setup_window()
        self.set_icon()
        self.set_theme()
        self.create_menu()
        self.create_main_frame()
   
    def setup_window(self):
        self.window.title("Sistema de Gestión Comercial")
       
        # OBTENER DIMENSIONES DE LA PANTALLA Y USAR TODO EL ANCHO
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
       
        # Usar 95% del ancho de pantalla y 90% del alto
        window_width = int(screen_width * 0.95)
        window_height = int(screen_height * 0.90)
       
        self.window.geometry(f"{window_width}x{window_height}")
        self.window.minsize(1000, 600)
       
        # Centrar ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"+{x}+{y}")
       
        # Hacer ventana maximizada
        try:
            self.window.state('zoomed')
        except:
            try:
                self.window.attributes('-zoomed', True)
            except:
                pass
       
        # Manejar cierre de ventana
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.fullscreen = False
       
        # Forzar actualización de la ventana
        self.window.update_idletasks()
   
    def set_icon(self):
        """Método MEJORADO para configurar el icono - Eliminar la pluma de Tkinter"""
        print("🔄 Configurando icono de la aplicación...")
       
        # Lista priorizada de iconos (empezar con ICO para Windows)
        icon_paths = [
            "logo_lab.ico",           # ICO - Mejor para Windows
            "icono_16x16.png",        # PNG pequeños
            "icono_32x32.png",
            "icono_48x48.png",
            "icono_64x64.png",
            "icono_128x128.png",
            "logo_lab.png",           # Original (como último recurso)
            "icono.ico",
            "icono.png",
            "icon.ico",
            "icon.png",
            "favicon.ico",
            "assets/logo_lab.ico",
            "assets/logo_lab.png"
        ]
       
        icon_loaded = False
       
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    print(f"🔍 Intentando cargar: {icon_path}")
                   
                    if icon_path.lower().endswith('.ico'):
                        # Método para ICO (más confiable en Windows)
                        self.window.iconbitmap(icon_path)
                        print(f"✅ Icono ICO cargado: {icon_path}")
                        icon_loaded = True
                        break
                       
                    elif icon_path.lower().endswith('.png'):
                        # Método para PNG
                        img = Image.open(icon_path)
                        photo = ImageTk.PhotoImage(img)
                       
                        # Múltiples intentos para asegurar que se aplique
                        self.window.iconphoto(True, photo)
                        self.window.iconphoto(False, photo)
                       
                        # Guardar referencia para evitar garbage collection
                        if not hasattr(self, '_icon_photo'):
                            self._icon_photo = photo
                           
                        print(f"✅ Icono PNG cargado: {icon_path}")
                        icon_loaded = True
                        break
                       
                except Exception as e:
                    print(f"❌ Error cargando {icon_path}: {e}")
                    continue
       
        if not icon_loaded:
            print("⚠️ No se pudo cargar ningún icono personalizado")
            # Intentar método alternativo para eliminar icono por defecto
            self._remove_default_icon()
   
    def _remove_default_icon(self):
        """Intentar eliminar el icono por defecto de Tkinter"""
        try:
            # En algunos sistemas, esto puede ayudar
            if sys.platform == "win32":
                # En Windows, intentar con un icono vacío
                self.window.iconbitmap("")
            elif sys.platform == "linux":
                # En Linux, intentar configurar icono vacío
                self.window.tk.call('wm', 'iconphoto', self.window._w, '')
            else:
                # macOS
                pass
               
            print("🔧 Icono por defecto removido")
        except:
            print("⚠️ No se pudo remover el icono por defecto")
   
    def set_theme(self):
        """Configurar el tema de Tkinter"""
        try:
            style = ttk.Style()
            available_themes = style.theme_names()
           
            # Preferir temas más modernos
            preferred_themes = ['vista', 'clam', 'alt', 'default']
           
            for theme in preferred_themes:
                if theme in available_themes:
                    style.theme_use(theme)
                    print(f"🎨 Tema aplicado: {theme}")
                    break
            else:
                style.theme_use(available_themes[0] if available_themes else 'default')
               
        except Exception as e:
            print(f"❌ Error configurando tema: {e}")

    def get_presupuestos_stats(self):
        """Obtener estadísticas detalladas de presupuestos"""
        try:
            # Obtener todos los presupuestos
            presupuestos = self.presupuestos_manager.obtener_presupuestos()
           
            # Contadores por estado
            total = len(presupuestos)
            borrador = 0
            enviado = 0
            aceptado = 0
            rechazado = 0
           
            # Calcular totales
            subtotal_total = 0
            iva_total = 0
            total_general = 0
           
            for presupuesto in presupuestos:
                estado = presupuesto.get('estado', 'borrador')
               
                if estado == 'borrador':
                    borrador += 1
                elif estado == 'enviado':
                    enviado += 1
                elif estado == 'aceptado':
                    aceptado += 1
                elif estado == 'rechazado':
                    rechazado += 1
               
                # Acumular montos
                subtotal_total += float(presupuesto.get('subtotal', 0))
                iva_total += float(presupuesto.get('iva_valor', 0))
                total_general += float(presupuesto.get('total', 0))
           
            # Calcular tasa de conversión
            tasa_conversion = (aceptado / total * 100) if total > 0 else 0
           
            return {
                "total": total,
                "borrador": borrador,
                "enviado": enviado,
                "aceptado": aceptado,
                "rechazado": rechazado,
                "tasa_conversion": round(tasa_conversion, 1),
                "subtotal_total": round(subtotal_total, 2),
                "iva_total": round(iva_total, 2),
                "total_general": round(total_general, 2)
            }
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas de presupuestos: {e}")
            return {
                "total": 0,
                "borrador": 0,
                "enviado": 0,
                "aceptado": 0,
                "rechazado": 0,
                "tasa_conversion": 0,
                "subtotal_total": 0,
                "iva_total": 0,
                "total_general": 0
            }

    def get_real_stats(self):
        """Obtener estadísticas reales de la base de datos"""
        try:
            # Obtener datos reales de cada manager
            clientes = self.clientes_manager.obtener_clientes()
            proveedores = self.proveedores_manager.obtener_proveedores()
            impuestos = self.impuestos_manager.obtener_impuestos()
            categorias = self.categorias_manager.obtener_categorias()
            marcas = self.marcas_manager.obtener_marcas()
            productos = self.productos_manager.obtener_productos()
            servicios = self.servicios_manager.obtener_servicios()
           
            # Filtrar solo los activos
            clientes_activos = [c for c in clientes if c.get('activo', True)]
            proveedores_activos = [p for p in proveedores if p.get('activo', True)]
            impuestos_activos = [i for i in impuestos if i.get('activo', True)]
            categorias_activas = [c for c in categorias if c.get('activo', True)]
            marcas_activas = [m for m in marcas if m.get('activo', True)]
            productos_activos = [p for p in productos if p.get('activo', True)]
            servicios_activos = [s for s in servicios if s.get('activo', True)]
           
            # Obtener estadísticas de presupuestos
            presupuestos_stats = self.get_presupuestos_stats()
           
            return {
                "clientes": len(clientes_activos),
                "proveedores": len(proveedores_activos),
                "impuestos": len(impuestos_activos),
                "categorias": len(categorias_activas),
                "marcas": len(marcas_activas),
                "productos": len(productos_activos),
                "servicios": len(servicios_activos),
                "presupuestos": presupuestos_stats
            }
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas reales: {e}")
            # En caso de error, retornar valores por defecto
            return {
                "clientes": 0,
                "proveedores": 0,
                "impuestos": 0,
                "categorias": 0,
                "marcas": 0,
                "productos": 0,
                "servicios": 0,
                "presupuestos": {
                    "total": 0,
                    "borrador": 0,
                    "enviado": 0,
                    "aceptado": 0,
                    "rechazado": 0,
                    "tasa_conversion": 0,
                    "subtotal_total": 0,
                    "iva_total": 0,
                    "total_general": 0
                }
            }
   
    def create_menu(self):
        menubar = tk.Menu(self.window)
       
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="📊 Dashboard", command=self.show_dashboard)
        file_menu.add_separator()
        file_menu.add_command(label="🖥️ Pantalla Completa (F11)", command=self.toggle_fullscreen)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Cerrar Sesión", command=self.logout)
        file_menu.add_command(label="❌ Salir", command=self.on_closing)
        menubar.add_cascade(label="📁 Archivo", menu=file_menu)
       
        # Menú Gestión
        management_menu = tk.Menu(menubar, tearoff=0)
        management_menu.add_command(label="👥 Clientes", command=self.show_clientes)
        management_menu.add_command(label="🏢 Proveedores", command=self.show_proveedores)
        management_menu.add_separator()
        management_menu.add_command(label="📦 Productos", command=self.show_productos)
        management_menu.add_command(label="🔧 Servicios", command=self.show_servicios)
        management_menu.add_separator()
        management_menu.add_command(label="💰 Impuestos", command=self.show_impuestos)
        management_menu.add_command(label="📑 Categorías", command=self.show_categorias)
        management_menu.add_command(label="🏷️ Marcas", command=self.show_marcas)
        management_menu.add_separator()
        management_menu.add_command(label="💰 Presupuestos", command=self.show_presupuestos)
        menubar.add_cascade(label="📊 Gestión", menu=management_menu)
        
        # Menú Configuración
        config_menu = tk.Menu(menubar, tearoff=0)
        config_menu.add_command(label="⚙️ Configuración del Sistema", command=self.show_configuracion)
        menubar.add_cascade(label="🔧 Configuración", menu=config_menu)
        
        # Menú Ventana
        window_menu = tk.Menu(menubar, tearoff=0)
        window_menu.add_command(label="📐 Tamaño Normal", command=self.normal_size)
        window_menu.add_command(label="🖥️ Maximizar", command=self.maximize_window)
        window_menu.add_separator()
        window_menu.add_command(label="🔄 Actualizar", command=self.refresh_app)
        menubar.add_cascade(label="🪟 Ventana", menu=window_menu)
       
        self.window.config(menu=menubar)
       
        # Atajos de teclado
        self.window.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.window.bind('<Escape>', lambda e: self.exit_fullscreen())
        self.window.bind('<F5>', lambda e: self.refresh_app())
        self.window.bind('<Control-n>', lambda e: self.show_clientes())
   
    def create_main_frame(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
       
        # Mostrar dashboard por defecto
        self.show_dashboard()

    def show_dashboard(self):
        self.clear_main_frame()

        # Obtener estadísticas reales
        stats = self.get_real_stats()
        presupuestos_stats = stats["presupuestos"]

        # Frame principal con scroll para asegurar que todo sea visible
        main_canvas = tk.Canvas(self.main_frame)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        # 🔥 CENTRAR USANDO CONTENEDOR INTERMEDIO
        canvas_window = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        # 🔥 Función para centrar el contenido dinámicamente
        def update_scroll_position(event=None):
            canvas_width = main_canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            
            if canvas_width > frame_width and canvas_width > 1:
                # Calcular padding para centrar
                x_offset = (canvas_width - frame_width) // 2
                main_canvas.coords(canvas_window, x_offset, 0)
            else:
                # Si el frame es más ancho que el canvas, alinear a la izquierda
                main_canvas.coords(canvas_window, 0, 0)
        
        # Bind para actualizar cuando cambie el tamaño
        main_canvas.bind("<Configure>", update_scroll_position)
        scrollable_frame.bind("<Configure>", lambda e: update_scroll_position())
        
        # Llamar después de renderizar
        main_canvas.after(100, update_scroll_position)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 🔥 OBTENER CONFIGURACIÓN DEL LOGIN PARA TÍTULOS DINÁMICOS
        from configuracion_manager import ConfiguracionManager
        config_manager = ConfiguracionManager()
        config_login = config_manager.obtener_config_login()
        
        # Usar configuración dinámica o valores por defecto
        nombre_fantasia = config_login.get('nombre_fantasia', 'Servicios')
        descripcion_sistema = config_login.get('descripcion_sistema', 'Sistema de Gestión Integral')
        
        # Título principal - CENTRADO Y DINÁMICO
        ttk.Label(scrollable_frame, text=f"🔧 {nombre_fantasia}",
                font=("Arial", 20, "bold"), foreground="#2c3e50").pack(pady=15)
        
        ttk.Label(scrollable_frame, text=descripcion_sistema,
                font=("Arial", 12), foreground="#7f8c8d").pack(pady=5)

        # Separador
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=15, padx=30)

        # ========== SECCIÓN DE ESTADÍSTICAS GENERALES ==========
        ttk.Label(scrollable_frame, text="📊 Resumen General del Sistema",
                font=("Arial", 14, "bold"), foreground="#2c3e50").pack(pady=8)

        stats_frame = ttk.Frame(scrollable_frame)
        stats_frame.pack(pady=10, fill=tk.X)

        stats_data = [
            ("👥 Clientes", str(stats["clientes"]), "#3498db", "clientes"),
            ("🏢 Proveedores", str(stats["proveedores"]), "#f39c12", "proveedores"),
            ("💰 Impuestos", str(stats["impuestos"]), "#9b59b6", "impuestos"),
            ("📑 Categorías", str(stats["categorias"]), "#e74c3c", "categorias"),
            ("🏷️ Marcas", str(stats["marcas"]), "#27ae60", "marcas"),
            ("📦 Productos", str(stats["productos"]), "#1abc9c", "productos"),
            ("🔧 Servicios", str(stats["servicios"]), "#d35400", "servicios")
        ]

        # Crear grid de 4 columnas para estadísticas generales - TARJETAS MÁS PEQUEÑAS
        for i, (title, value, color, command) in enumerate(stats_data):
            row = i // 4
            col = i % 4
            
            if col == 0:
                row_frame = ttk.Frame(stats_frame)
                row_frame.pack(fill=tk.X, pady=3)
            
            stat_card = self.create_stat_card(row_frame, title, value, color, command)
            stat_card.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # ========== SECCIÓN DE PRESUPUESTOS ==========
        # Título clickable para presupuestos
        presupuestos_title_frame = ttk.Frame(scrollable_frame)
        presupuestos_title_frame.pack(pady=(20, 8), fill=tk.X)
        
        presupuestos_label = ttk.Label(
            presupuestos_title_frame, 
            text="💰 Gestión de Presupuestos",
            font=("Arial", 14, "bold"), 
            foreground="#2c3e50",
            cursor="hand2"
        )
        presupuestos_label.pack()
        
        # Tooltip para el título
        tooltip_label = ttk.Label(
            presupuestos_title_frame,
            text="💡 Haz click aquí para ir directamente a Presupuestos",
            font=("Arial", 7),
            foreground="#95a5a6"
        )
        tooltip_label.pack(pady=(1, 0))
        
        # Bind del evento click al título
        presupuestos_label.bind("<Button-1>", lambda e: self.show_presupuestos())
        presupuestos_label.bind("<Enter>", lambda e: presupuestos_label.configure(foreground="#2980b9"))
        presupuestos_label.bind("<Leave>", lambda e: presupuestos_label.configure(foreground="#2c3e50"))

        # Frame principal para presupuestos
        presupuestos_main_frame = ttk.Frame(scrollable_frame)
        presupuestos_main_frame.pack(pady=8, fill=tk.X)

        # 🔥 CORRECCIÓN: Estadísticas detalladas de presupuestos - 6 RECTÁNGULOS MÁS PEQUEÑOS
        presupuestos_stats_data = [
            ("📋 Total", str(presupuestos_stats["total"]), "#2c3e50", "Todos los presupuestos"),
            ("📝 Borrador", str(presupuestos_stats["borrador"]), "#f39c12", "Pendientes de envío"),
            ("📤 Enviados", str(presupuestos_stats["enviado"]), "#3498db", "Enviados a clientes"),
            ("✅ Aceptados", str(presupuestos_stats["aceptado"]), "#27ae60", "Aceptados por clientes"),
            ("❌ Rechazados", str(presupuestos_stats["rechazado"]), "#e74c3c", "Rechazados por clientes"),
            ("📈 Conversión", f"{presupuestos_stats['tasa_conversion']}%", "#9b59b6", "Tasa de aceptación")
        ]

        # 🔥 CORRECCIÓN: Crear 2 filas con 3 columnas cada una para los 6 recuadros MÁS PEQUEÑOS
        for row_index in range(2):  # 2 filas
            row_frame = ttk.Frame(presupuestos_main_frame)
            row_frame.pack(fill=tk.X, pady=3)
            
            # 3 recuadros por fila
            for col_index in range(3):
                index = row_index * 3 + col_index
                if index < len(presupuestos_stats_data):
                    title, value, color, tooltip = presupuestos_stats_data[index]
                    
                    # Crear tarjeta MÁS PEQUEÑA para consistencia
                    stat_card = self.create_presupuesto_stat_card(
                        row_frame, 
                        title, 
                        value, 
                        color, 
                        "presupuestos",
                        tooltip
                    )
                    stat_card.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

        # ========== RESUMEN FINANCIERO ==========
        if presupuestos_stats["total_general"] > 0:
            ttk.Label(scrollable_frame, text="💵 Resumen Financiero",
                    font=("Arial", 12, "bold"), foreground="#2c3e50").pack(pady=(15, 8))
        
            financiero_frame = ttk.Frame(scrollable_frame)
            financiero_frame.pack(pady=8, fill=tk.X)
        
            financiero_data = [
                ("Subtotal", f"${presupuestos_stats['subtotal_total']:,.2f}", "#34495e"),
                ("IVA", f"${presupuestos_stats['iva_total']:,.2f}", "#7f8c8d"),
                ("Total General", f"${presupuestos_stats['total_general']:,.2f}", "#27ae60")
            ]
        
            for i, (title, value, color) in enumerate(financiero_data):
                fin_card = self.create_stat_card(financiero_frame, title, value, color, "presupuestos")
                fin_card.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Actualizar el scrollable frame
        main_canvas.update_idletasks()
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    def create_stat_card(self, parent, title, value, color, command=None):
        """Crear una tarjeta de estadística MÁS PEQUEÑA y clickable"""
        card_frame = ttk.Frame(parent, relief="solid", borderwidth=1)
        card_frame.configure(style="Card.TFrame")
        
        # Configurar estilo para la tarjeta
        style = ttk.Style()
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        
        # Hacer la tarjeta clickable si tiene un comando
        if command:
            card_frame.configure(cursor="hand2")
            card_frame.bind("<Button-1>", lambda e, cmd=command: self.execute_command(cmd))
            # Efecto hover
            card_frame.bind("<Enter>", lambda e: card_frame.configure(style="CardHover.TFrame"))
            card_frame.bind("<Leave>", lambda e: card_frame.configure(style="Card.TFrame"))
            style.configure("CardHover.TFrame", background="#f8f9fa", relief="solid", borderwidth=2)
        
        # Frame interno para mejor control del contenido - MÁS PEQUEÑO
        content_frame = ttk.Frame(card_frame, style="Card.TFrame")
        content_frame.pack(expand=True, fill=tk.BOTH, padx=8, pady=8)
        
        # Contenido de la tarjeta - MÁS COMPACTO
        value_label = ttk.Label(
            content_frame, 
            text=value, 
            font=("Arial", 14, "bold"),  # 🔥 TEXTO MÁS PEQUEÑO
            foreground=color, 
            background="white",
            wraplength=100
        )
        value_label.pack(pady=(2, 1))
        
        title_label = ttk.Label(
            content_frame, 
            text=title, 
            font=("Arial", 8),  # 🔥 TEXTO MÁS PEQUEÑO
            foreground="#7f8c8d", 
            background="white",
            wraplength=100
        )
        title_label.pack(pady=(0, 2))
        
        # Hacer también los labels clickables
        if command:
            for label in [value_label, title_label]:
                label.configure(cursor="hand2")
                label.bind("<Button-1>", lambda e, cmd=command: self.execute_command(cmd))
                label.bind("<Enter>", lambda e: card_frame.configure(style="CardHover.TFrame"))
                label.bind("<Leave>", lambda e: card_frame.configure(style="Card.TFrame"))
        
        return card_frame
    
    def create_presupuesto_stat_card(self, parent, title, value, color, command=None, tooltip=""):
        """Crear una tarjeta de estadística específica para presupuestos con mejor formato"""
        card_frame = ttk.Frame(parent, relief="solid", borderwidth=1)
        card_frame.configure(style="Card.TFrame")
        
        # Configurar estilo para la tarjeta
        style = ttk.Style()
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        
        # Hacer la tarjeta clickable si tiene un comando
        if command:
            card_frame.configure(cursor="hand2")
            card_frame.bind("<Button-1>", lambda e, cmd=command: self.execute_command(cmd))
            # Efecto hover
            card_frame.bind("<Enter>", lambda e: card_frame.configure(style="CardHover.TFrame"))
            card_frame.bind("<Leave>", lambda e: card_frame.configure(style="Card.TFrame"))
            style.configure("CardHover.TFrame", background="#f8f9fa", relief="solid", borderwidth=2)
        
        # Frame interno para mejor control del contenido
        content_frame = ttk.Frame(card_frame, style="Card.TFrame")
        content_frame.pack(expand=True, fill=tk.BOTH, padx=12, pady=12)
        
        # Contenido de la tarjeta - MEJOR FORMATEADO
        value_label = ttk.Label(
            content_frame, 
            text=value, 
            font=("Arial", 16, "bold"),
            foreground=color, 
            background="white",
            justify=tk.CENTER
        )
        value_label.pack(pady=(5, 3))
        
        title_label = ttk.Label(
            content_frame, 
            text=title, 
            font=("Arial", 9),
            foreground="#7f8c8d", 
            background="white",
            justify=tk.CENTER,
            wraplength=100
        )
        title_label.pack(pady=(0, 3))
        
        # Tooltip pequeño
        if tooltip:
            tooltip_label = ttk.Label(
                content_frame,
                text=tooltip,
                font=("Arial", 7),
                foreground="#bdc3c7",
                background="white",
                justify=tk.CENTER,
                wraplength=120
            )
            tooltip_label.pack(pady=(0, 2))
        
        # Hacer también los labels clickables
        if command:
            for label in [value_label, title_label]:
                label.configure(cursor="hand2")
                label.bind("<Button-1>", lambda e, cmd=command: self.execute_command(cmd))
                label.bind("<Enter>", lambda e: card_frame.configure(style="CardHover.TFrame"))
                label.bind("<Leave>", lambda e: card_frame.configure(style="Card.TFrame"))
        
        return card_frame

    def execute_command(self, command):
        """Ejecutar comando basado en el string del comando"""
        command_map = {
            "clientes": self.show_clientes,
            "proveedores": self.show_proveedores,
            "impuestos": self.show_impuestos,
            "categorias": self.show_categorias,
            "marcas": self.show_marcas,
            "productos": self.show_productos,
            "servicios": self.show_servicios,
            "presupuestos": self.show_presupuestos
        }
        
        if command in command_map:
            command_map[command]()

    # MÉTODOS PARA LOS MÓDULOS
    def show_impuestos(self):
        """Abrir ventana de gestión de impuestos"""
        ImpuestosWindow(self.window)
   
    def show_categorias(self):
        """Abrir ventana de gestión de categorías"""
        CategoriasWindow(self.window)
   
    def show_marcas(self):
        """Abrir ventana de gestión de marcas"""
        MarcasWindow(self.window)
   
    def show_clientes(self):
        """Abrir ventana de gestión de clientes"""
        ClientesWindow(self.window)
   
    def show_proveedores(self):
        """Abrir ventana de gestión de proveedores"""
        ProveedoresWindow(self.window)
   
    def show_productos(self):
        """Abrir ventana de gestión de productos"""
        ProductosWindow(self.window)
   
    def show_servicios(self):
        """Abrir ventana de gestión de servicios"""
        ServiciosWindow(self.window)
   
    def show_presupuestos(self):
        """Abrir ventana de gestión de presupuestos"""
        PresupuestosWindow(self.window)

    def show_configuracion(self):
        """Abrir ventana de configuración del sistema"""
        try:        
            ConfiguracionWindow(self.window)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la configuración: {e}")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
   
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.window.attributes('-fullscreen', self.fullscreen)
       
        if not self.fullscreen:
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            window_width = int(screen_width * 0.95)
            window_height = int(screen_height * 0.90)
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
   
    def exit_fullscreen(self):
        if self.fullscreen:
            self.window.attributes('-fullscreen', False)
            self.fullscreen = False
   
    def normal_size(self):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.exit_fullscreen()
   
    def maximize_window(self):
        try:
            self.window.state('zoomed')
        except:
            try:
                self.window.attributes('-zoomed', True)
            except:
                pass
   
    def refresh_app(self):
        self.show_dashboard()
        messagebox.showinfo("Actualizar", "✅ Aplicación actualizada")
   
    def logout(self):
        confirmacion = messagebox.askyesno(
            "🚪 Cerrar Sesión",
            "¿Está seguro de que desea cerrar sesión?\n\nSe perderán los cambios no guardados."
        )
       
        if confirmacion:
            self.auth_manager.logout()
            self.window.destroy()
            from main import main
            main()
   
    def on_closing(self):
        if messagebox.askokcancel(
            "❌ Salir del Sistema",
            "¿Está seguro de que desea salir del sistema?\n\nAsegúrese de haber guardado todos los cambios."
        ):
            self.window.quit()
   
    def run(self):
        self.window.mainloop()