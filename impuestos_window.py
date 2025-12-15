# /app_escritorio/impuestos_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from impuestos_manager import ImpuestosManager
from styles import Styles
import os
from PIL import Image, ImageTk


class ImpuestosWindow:
    def __init__(self, parent):
        self.parent = parent
        self.manager = ImpuestosManager()
        self.impuestos = []
        self.impuesto_seleccionado = None
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Impuestos - Lab Servicios")
        
        # Color coding
        module_color = Styles.get_module_style("configuracion")
        self.header_strip = tk.Frame(self.window, bg=module_color, height=5)
        self.header_strip.pack(fill=tk.X, side=tk.TOP)
       
        # USAR 80% DEL ANCHO DE PANTALLA
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        self.window.geometry(f"{window_width}x{window_height}")
       
        self.window.transient(parent)
        self.window.grab_set()
       
        # Configurar icono
        self.set_icon()
        self.center_window(window_width, window_height)
       
        # INICIALIZAR VARIABLES
        self.search_var = tk.StringVar(self.window)
        self.tipo_filter_var = tk.StringVar(self.window)
       
        self.create_widgets()
        self.cargar_impuestos()
   
    def set_icon(self):
        """Configurar el icono en ventanas hijas"""
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
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
   
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
       
        # Frame de búsqueda y botones
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
       
        # Búsqueda
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.buscar_impuestos)
       
        # Filtros
        ttk.Label(search_frame, text="Tipo:").pack(side=tk.LEFT, padx=(20, 5))
        self.tipo_filter = ttk.Combobox(
            search_frame,
            textvariable=self.tipo_filter_var,
            values=["Todos", "Compra", "Venta", "Ambos"],
            state="readonly",
            width=15
        )
        self.tipo_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.tipo_filter.bind('<<ComboboxSelected>>', self.aplicar_filtros)
       
        # Botones
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(side=tk.RIGHT)
       
        ttk.Button(button_frame, text="➕ Nuevo Impuesto", command=self.nuevo_impuesto).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Editar", command=self.editar_impuesto).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Eliminar", command=self.eliminar_impuesto).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Recargar", command=self.cargar_impuestos).pack(side=tk.LEFT, padx=5)
       
        # Treeview para lista de impuestos
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
       
        columns = ('id', 'nombre', 'porcentaje', 'tipo', 'display_name')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
       
        # Configurar columnas
        self.tree.heading('id', text='ID')
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('porcentaje', text='Porcentaje (%)')
        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('display_name', text='Nombre Display')
       
        self.tree.column('id', width=50)
        self.tree.column('nombre', width=200)
        self.tree.column('porcentaje', width=100)
        self.tree.column('tipo', width=100)
        self.tree.column('display_name', width=200)
       
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
       
        # Bind eventos
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_impuesto)
        self.tree.bind('<Double-1>', lambda e: self.editar_impuesto())
   
    def cargar_impuestos(self, filtros=None):
        """Cargar lista de impuestos"""
        self.impuestos = self.manager.obtener_impuestos(filtros)
        self.actualizar_treeview()
   
    def actualizar_treeview(self):
        """Actualizar el treeview con los impuestos"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
       
        # Mapeo para tipos legibles
        tipo_map = {
            "compra": "Compra",
            "venta": "Venta", 
            "ambos": "Ambos"
        }
       
        # Llenar con datos
        for impuesto in self.impuestos:
            tipo_display = tipo_map.get(impuesto['tipo'], impuesto['tipo'])
           
            self.tree.insert('', tk.END, values=(
                impuesto['id'],
                impuesto['nombre'],
                f"{impuesto['porcentaje']}%",
                tipo_display,
                impuesto.get('display_name', '')  # Usar get para compatibilidad
            ))
   
    def seleccionar_impuesto(self, event):
        """Manejar selección de impuesto"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            impuesto_id = item['values'][0]
            self.impuesto_seleccionado = next(
                (i for i in self.impuestos if i['id'] == impuesto_id), None
            )
   
    def buscar_impuestos(self, event=None):
        """Buscar impuestos en tiempo real"""
        texto_busqueda = self.search_var.get().lower()
        if len(texto_busqueda) >= 2 or texto_busqueda == "":
            self.aplicar_filtros()
   
    def aplicar_filtros(self, event=None):
        """Aplicar todos los filtros"""
        filtros = {}
       
        # Filtro de búsqueda
        texto_busqueda = self.search_var.get()
        if texto_busqueda:
            filtros['search'] = texto_busqueda
       
        # Filtro de tipo
        tipo_seleccionado = self.tipo_filter_var.get()
        if tipo_seleccionado == "Compra":
            filtros['tipo'] = 'compra'
        elif tipo_seleccionado == "Venta":
            filtros['tipo'] = 'venta'
        elif tipo_seleccionado == "Ambos":
            filtros['tipo'] = 'ambos'
        # "Todos" no envía filtro de tipo
       
        self.cargar_impuestos(filtros)
   
    def nuevo_impuesto(self):
        """Abrir formulario para nuevo impuesto"""
        FormularioImpuesto(self.window, self, None)
   
    def editar_impuesto(self):
        """Abrir formulario para editar impuesto seleccionado"""
        if not self.impuesto_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un impuesto para editar")
            return
       
        FormularioImpuesto(self.window, self, self.impuesto_seleccionado)
   
    def eliminar_impuesto(self):
        """Eliminar impuesto seleccionado"""
        if not self.impuesto_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un impuesto para eliminar")
            return
       
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar el impuesto:\n{self.impuesto_seleccionado['nombre']} ({self.impuesto_seleccionado['porcentaje']}%)?"
        )
       
        if confirmacion:
            if self.manager.eliminar_impuesto(self.impuesto_seleccionado['id']):
                self.cargar_impuestos()


class FormularioImpuesto:
    def __init__(self, parent, impuestos_window, impuesto_data):
        self.parent = parent
        self.impuestos_window = impuestos_window
        self.impuesto_data = impuesto_data
        self.es_nuevo = impuesto_data is None
       
        # Mapeo de tipo: display -> valor real
        self.tipo_map = {
            "Compra": "compra",
            "Venta": "venta", 
            "Ambos": "ambos"
        }
       
        # Mapeo inverso para cargar datos
        self.tipo_reverse_map = {
            "compra": "Compra",
            "venta": "Venta",
            "ambos": "Ambos"
        }
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Nuevo Impuesto" if self.es_nuevo else "Editar Impuesto")
        
        # Color coding
        module_color = Styles.get_module_style("configuracion")
        self.header_strip = tk.Frame(self.window, bg=module_color, height=5)
        self.header_strip.pack(fill=tk.X, side=tk.TOP)
        # Aumentar tamaño para incluir display_name
        self.window.geometry("450x380")
        self.window.transient(parent)
        self.window.grab_set()
       
        self.center_window(450, 380)
       
        # INICIALIZAR VARIABLES
        self.nombre_var = tk.StringVar(self.window)
        self.porcentaje_var = tk.StringVar(self.window)
        self.tipo_var = tk.StringVar(self.window, value="Ambos")
        self.display_name_var = tk.StringVar(self.window)
       
        self.create_widgets()
        if not self.es_nuevo:
            self.cargar_datos()
   
    def center_window(self, width, height):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
   
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
       
        # GUÍA VISUAL DE EJEMPLOS
        guide_frame = ttk.LabelFrame(main_frame, text="📌 EJEMPLOS", padding="10")
        guide_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(0, 15), padx=(0, 0))
        
        guide_text = """• IVA_21 → IVA 21%
• IIBB_CABA → Ingresos Brutos CABA 3.5%
• IMP_INT_PINTURAS → Imp. Interno Pinturas 8%"""
        
        guide_label = ttk.Label(guide_frame, text=guide_text, justify=tk.LEFT)
        guide_label.pack(anchor=tk.W)
        
        # Nombre (técnico)
        ttk.Label(main_frame, text="Nombre:*", font=('TkDefaultFont', 9, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.nombre_entry = ttk.Entry(main_frame, textvariable=self.nombre_var, width=35)
        self.nombre_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(0, 5), padx=(10, 0))
        
        # Tooltip para nombre
        nombre_tip = ttk.Label(
            main_frame, 
            text="Técnico, sin espacios. Ej: IVA_21, IIBB_CABA", 
            font=('TkDefaultFont', 8),
            foreground='gray'
        )
        nombre_tip.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=(0, 10))
       
        # Porcentaje
        ttk.Label(main_frame, text="Porcentaje (%):*", font=('TkDefaultFont', 9, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.porcentaje_entry = ttk.Entry(main_frame, textvariable=self.porcentaje_var, width=35)
        self.porcentaje_entry.grid(row=3, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(0, 5), padx=(10, 0))
       
        # Tipo
        ttk.Label(main_frame, text="Tipo:*", font=('TkDefaultFont', 9, 'bold')).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5)
        )
        tipo_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.tipo_var, 
            state="readonly", 
            width=32
        )
        tipo_combo['values'] = list(self.tipo_map.keys())
        tipo_combo.grid(row=4, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(0, 10), padx=(10, 0))
       
        # Display Name (opcional)
        ttk.Label(main_frame, text="Display Name:", font=('TkDefaultFont', 9)).grid(
            row=5, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.display_name_entry = ttk.Entry(
            main_frame, 
            textvariable=self.display_name_var, 
            width=35
        )
        self.display_name_entry.grid(row=5, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(0, 5), padx=(10, 0))
        
        # Botón de ayuda para display name
        info_button = ttk.Button(
            main_frame, 
            text="ℹ️", 
            width=3,
            command=self.mostrar_info_display_name
        )
        info_button.grid(row=5, column=3, padx=(5, 0), pady=(0, 5))
        
        # Tooltip para display name
        display_tip = ttk.Label(
            main_frame, 
            text="Opcional - Aparece en facturas. Si se deja vacío, se genera automáticamente", 
            font=('TkDefaultFont', 8),
            foreground='gray'
        )
        display_tip.grid(row=6, column=1, columnspan=2, sticky=tk.W, pady=(0, 20))
       
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=4, pady=(10, 0))
       
        ttk.Button(
            button_frame, 
            text="💾 Guardar", 
            command=self.guardar,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="❌ Cancelar", 
            command=self.window.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
       
        # Configurar grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=0)
   
    def mostrar_info_display_name(self):
        """Mostrar información sobre display name"""
        info_text = """📌 GUÍA: NOMBRE vs DISPLAY NAME

NOMBRE (Técnico/Administrativo):
• Para el sistema interno
• Sin espacios, único
• No cambiar después de creado
• Ejemplo: IVA_21

DISPLAY NAME (Visual):
• Para mostrar al usuario
• Aparece en facturas y listados
• Puede incluir espacios y símbolos
• Personalizable
• Ejemplo: IVA 21%

⚠️ Si no completa Display Name:
Se generará automáticamente:
  'Nombre (Porcentaje%)'
  Ej: 'IVA_21 (21.00%)'"""
        
        messagebox.showinfo("Información - Display Name", info_text)
   
    def cargar_datos(self):
        """Cargar datos del impuesto en el formulario"""
        if not self.impuesto_data:
            return
       
        self.nombre_var.set(self.impuesto_data['nombre'])
        self.porcentaje_var.set(str(self.impuesto_data['porcentaje']))
       
        # Mapear tipo del backend al display
        tipo_display = self.tipo_reverse_map.get(
            self.impuesto_data['tipo'],
            "Ambos"
        )
        self.tipo_var.set(tipo_display)
        
        # Cargar display_name si existe
        if 'display_name' in self.impuesto_data and self.impuesto_data['display_name']:
            self.display_name_var.set(self.impuesto_data['display_name'])
   
    def validar_formulario(self):
        """Validar datos del formulario"""
        # Validar nombre
        nombre = self.nombre_var.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return False
        
        # Validar que el nombre no tenga espacios
        if ' ' in nombre:
            messagebox.showerror("Error", "El nombre no puede contener espacios. Use guiones bajos (_)")
            return False
       
        # Validar porcentaje
        porcentaje = self.porcentaje_var.get().strip()
        if not porcentaje:
            messagebox.showerror("Error", "El porcentaje es obligatorio")
            return False
       
        es_valido, mensaje_error = self.impuestos_window.manager.validar_porcentaje(porcentaje)
        if not es_valido:
            messagebox.showerror("Error", mensaje_error)
            return False
       
        return True

    def guardar(self):
        """Guardar impuesto"""
        if not self.validar_formulario():
            return
       
        # Convertir tipo de display a valor backend
        tipo_backend = self.tipo_map.get(self.tipo_var.get(), "ambos")
       
        # Preparar datos
        datos = {
            'nombre': self.nombre_var.get().strip(),
            'porcentaje': float(self.porcentaje_var.get().strip()),
            'tipo': tipo_backend
        }
        
        # **CAMBIOS AQUÍ:** Manejar display_name correctamente
        display_name = self.display_name_var.get().strip()
        if display_name:
            # Si el usuario escribió algo, enviarlo
            datos['display_name'] = display_name
        else:
            # **IMPORTANTE:** Si está vacío, enviar string vacío explícitamente
            # Esto permite que Django genere el display_name automáticamente
            datos['display_name'] = ''
        
        # Si estamos editando, NO enviar el ID como parte de datos
        # Django REST Framework ya sabe el ID por la URL
        # datos['id'] = self.impuesto_data['id']  # ¡QUITA ESTA LÍNEA!
       
        manager = ImpuestosManager()
        if self.es_nuevo:
            resultado = manager.crear_impuesto(datos)
        else:
            resultado = manager.actualizar_impuesto(self.impuesto_data['id'], datos)
       
        if resultado:
            self.impuestos_window.cargar_impuestos()
            self.window.destroy()