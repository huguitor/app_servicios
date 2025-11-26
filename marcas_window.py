# /app_escritorio/marcas_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from marcas_manager import MarcasManager
import os
from PIL import Image, ImageTk


class MarcasWindow:
    def __init__(self, parent):
        self.parent = parent
        self.manager = MarcasManager()
        self.marcas = []
        self.marca_seleccionada = None
        
        # Variables para ordenamiento
        self.sort_column = None
        self.sort_reverse = False
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Marcas - Lab Servicios")
       
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
        self.estado_filter_var = tk.StringVar(self.window)
       
        self.create_widgets()
        self.cargar_marcas()
   
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
        self.search_entry.bind('<KeyRelease>', self.buscar_marcas)
       
        # Filtros
        ttk.Label(search_frame, text="Estado:").pack(side=tk.LEFT, padx=(20, 5))
        self.estado_filter = ttk.Combobox(
            search_frame,
            textvariable=self.estado_filter_var,
            values=["Todos", "Activas", "Inactivas"],
            state="readonly",
            width=12
        )
        self.estado_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.estado_filter.bind('<<ComboboxSelected>>', self.aplicar_filtros)
       
        # Botones
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(side=tk.RIGHT)
       
        ttk.Button(button_frame, text="➕ Nueva Marca", command=self.nueva_marca).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Editar", command=self.editar_marca).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Eliminar", command=self.eliminar_marca).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Recargar", command=self.cargar_marcas).pack(side=tk.LEFT, padx=5)
       
        # Treeview para lista de marcas
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
       
        columns = ('id', 'nombre', 'descripcion', 'activo', 'display_name')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
       
        # Configurar columnas con bindings para ordenamiento
        column_configs = [
            ('id', 'ID', 50),
            ('nombre', 'Nombre', 200),
            ('descripcion', 'Descripción', 250),
            ('activo', 'Estado', 80),
            ('display_name', 'Nombre Display', 200)
        ]
        
        for col_id, heading, width in column_configs:
            self.tree.heading(col_id, text=heading, command=lambda c=col_id: self.ordenar_columnas(c))
            self.tree.column(col_id, width=width)
       
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
       
        # Bind eventos
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_marca)
        self.tree.bind('<Double-1>', lambda e: self.editar_marca())
    
    def ordenar_columnas(self, column):
        """Ordenar las columnas al hacer clic en el encabezado"""
        # Si hacemos clic en la misma columna, invertir el orden
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Obtener todos los items del treeview
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]
        
        # Determinar el tipo de datos para ordenar correctamente
        if column in ['id']:
            # Ordenar como número
            items.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0, reverse=self.sort_reverse)
        elif column == 'activo':
            # Ordenar por estado (Activa/Inactiva)
            items.sort(key=lambda x: x[0] == 'Activa', reverse=self.sort_reverse)
        else:
            # Ordenar como texto (nombre, descripción, display_name)
            items.sort(key=lambda x: x[0].lower(), reverse=self.sort_reverse)
        
        # Reorganizar items en el treeview
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Actualizar indicadores visuales de ordenamiento
        self.actualizar_indicadores_ordenamiento()

    def actualizar_indicadores_ordenamiento(self):
        """Actualizar los indicadores visuales en los encabezados de columna"""
        for col in self.tree['columns']:
            current_text = self.tree.heading(col)['text']
            # Remover indicadores anteriores
            if current_text.endswith(' ▲') or current_text.endswith(' ▼'):
                current_text = current_text[:-2]
            
            # Agregar nuevo indicador si es la columna ordenada
            if col == self.sort_column:
                indicator = ' ▼' if self.sort_reverse else ' ▲'
                self.tree.heading(col, text=current_text + indicator)
   
    def cargar_marcas(self, filtros=None):
        """Cargar lista de marcas"""
        self.marcas = self.manager.obtener_marcas(filtros)
        self.actualizar_treeview()
   
    def actualizar_treeview(self):
        """Actualizar el treeview con las marcas"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
       
        # Llenar con datos
        for marca in self.marcas:
            estado_display = "Activa" if marca['activo'] else "Inactiva"
           
            self.tree.insert('', tk.END, values=(
                marca['id'],
                marca['nombre'],
                marca['descripcion'] or '',
                estado_display,
                marca['display_name']
            ))
        
        # Restaurar ordenamiento si existe
        if self.sort_column:
            self.ordenar_columnas(self.sort_column)
   
    def seleccionar_marca(self, event):
        """Manejar selección de marca"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            marca_id = item['values'][0]
            self.marca_seleccionada = next(
                (m for m in self.marcas if m['id'] == marca_id), None
            )
   
    def buscar_marcas(self, event=None):
        """Buscar marcas en tiempo real"""
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
       
        # Filtro de estado
        estado_seleccionado = self.estado_filter_var.get()
        if estado_seleccionado == "Activas":
            filtros['activo'] = 'true'
        elif estado_seleccionado == "Inactivas":
            filtros['activo'] = 'false'
       
        self.cargar_marcas(filtros)
   
    def nueva_marca(self):
        """Abrir formulario para nueva marca"""
        FormularioMarca(self.window, self, None)
   
    def editar_marca(self):
        """Abrir formulario para editar marca seleccionada"""
        if not self.marca_seleccionada:
            messagebox.showwarning("Advertencia", "Por favor seleccione una marca para editar")
            return
       
        FormularioMarca(self.window, self, self.marca_seleccionada)
   
    def eliminar_marca(self):
        """Eliminar marca seleccionada"""
        if not self.marca_seleccionada:
            messagebox.showwarning("Advertencia", "Por favor seleccione una marca para eliminar")
            return
       
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar la marca:\n{self.marca_seleccionada['nombre']}?"
        )
       
        if confirmacion:
            if self.manager.eliminar_marca(self.marca_seleccionada['id']):
                self.cargar_marcas()




class FormularioMarca:
    def __init__(self, parent, marcas_window, marca_data):
        self.parent = parent
        self.marcas_window = marcas_window
        self.marca_data = marca_data
        self.es_nuevo = marca_data is None
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Nueva Marca" if self.es_nuevo else "Editar Marca")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
       
        self.center_window(500, 400)
       
        # INICIALIZAR VARIABLES
        self.nombre_var = tk.StringVar(self.window)
        self.descripcion_var = tk.StringVar(self.window)
        self.activo_var = tk.BooleanVar(self.window, value=True)
       
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
       
        # Nombre
        ttk.Label(main_frame, text="Nombre:*").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.nombre_entry = ttk.Entry(main_frame, textvariable=self.nombre_var, width=40)
        self.nombre_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=(0, 10), padx=(10, 0))
       
        # Descripción
        ttk.Label(main_frame, text="Descripción:").grid(row=1, column=0, sticky=tk.W+tk.N, pady=(0, 10))
        self.descripcion_text = tk.Text(main_frame, width=40, height=8)
        self.descripcion_text.grid(row=1, column=1, sticky=tk.W+tk.E, pady=(0, 10), padx=(10, 0))
       
        # Estado
        ttk.Label(main_frame, text="Estado:*").grid(row=2, column=0, sticky=tk.W, pady=(10, 20))
        ttk.Checkbutton(main_frame, text="Activa", variable=self.activo_var).grid(row=2, column=1, sticky=tk.W, pady=(10, 20), padx=(10, 0))
       
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
       
        ttk.Button(button_frame, text="💾 Guardar", command=self.guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
       
        # Configurar grid weights
        main_frame.columnconfigure(1, weight=1)
   
    def cargar_datos(self):
        """Cargar datos de la marca en el formulario"""
        if not self.marca_data:
            return
       
        self.nombre_var.set(self.marca_data['nombre'])
        self.descripcion_text.insert('1.0', self.marca_data['descripcion'] or '')
        self.activo_var.set(self.marca_data['activo'])
   
    def validar_formulario(self):
        """Validar datos del formulario"""
        # Validar nombre
        if not self.nombre_var.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return False
       
        return True
   
    def guardar(self):
        """Guardar marca"""
        if not self.validar_formulario():
            return
       
        # Preparar datos
        datos = {
            'nombre': self.nombre_var.get().strip(),
            'descripcion': self.descripcion_text.get('1.0', tk.END).strip(),
            'activo': self.activo_var.get()
        }
       
        manager = MarcasManager()
        if self.es_nuevo:
            resultado = manager.crear_marca(datos)
        else:
            resultado = manager.actualizar_marca(self.marca_data['id'], datos)
       
        if resultado:
            self.marcas_window.cargar_marcas()
            self.window.destroy()