# app_escritorio/servicios_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from servicios_manager import ServiciosManager
from categorias_manager import CategoriasManager
from impuestos_manager import ImpuestosManager
from categorias_window import CategoriasWindow
import os
from PIL import Image, ImageTk
import json

class ServiciosWindow:
    def __init__(self, parent):
        self.parent = parent
        self.manager = ServiciosManager()
        self.categorias_manager = CategoriasManager()
        self.impuestos_manager = ImpuestosManager()
        
        self.servicios = []
        self.categorias = []
        self.impuestos = []
        self.servicio_seleccionado = None
        # Estado de ordenamiento (columna y dirección)
        self.sort_column = None
        self.sort_reverse = False
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Servicios - Lab Servicios")
        
        # USAR 90% DEL ANCHO DE PANTALLA
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        self.window.geometry(f"{window_width}x{window_height}")
        
        self.window.transient(parent)
        self.window.grab_set()
        
        # Configurar icono
        self.set_icon()
        self.center_window(window_width, window_height)
        
        # INICIALIZAR VARIABLES
        self.search_var = tk.StringVar(self.window)
        self.categoria_filter_var = tk.StringVar(self.window)
        self.estado_filter_var = tk.StringVar(self.window)
        
        self.create_widgets()
        self.cargar_datos_combobox()
        self.cargar_servicios()
    
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
    
    def cargar_datos_combobox(self):
        """Cargar datos para los combobox de filtros"""
        try:
            self.categorias = self.categorias_manager.obtener_categorias()
            self.impuestos = self.impuestos_manager.obtener_impuestos()
            
            # Filtrar solo activos localmente
            self.categorias = [c for c in self.categorias if c.get('activo', True)]
            self.impuestos = [i for i in self.impuestos if i.get('activo', True)]
            
        except Exception as e:
            print(f"Error cargando datos para combobox: {e}")
            self.categorias = []
            self.impuestos = []

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de búsqueda y botones
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Búsqueda
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.buscar_servicios)
        
        # Filtros
        ttk.Label(search_frame, text="Categoría:").pack(side=tk.LEFT, padx=(20, 5))
        self.categoria_filter = ttk.Combobox(
            search_frame,
            textvariable=self.categoria_filter_var,
            state="readonly",
            width=15
        )
        self.categoria_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.categoria_filter.bind('<<ComboboxSelected>>', self.aplicar_filtros)
        
        ttk.Label(search_frame, text="Estado:").pack(side=tk.LEFT, padx=(20, 5))
        self.estado_filter = ttk.Combobox(
            search_frame,
            textvariable=self.estado_filter_var,
            values=["Todos", "Activos", "Inactivos"],
            state="readonly",
            width=12
        )
        self.estado_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.estado_filter.bind('<<ComboboxSelected>>', self.aplicar_filtros)
        
        # Botones
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="➕ Nuevo Servicio", command=self.nuevo_servicio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Editar", command=self.editar_servicio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Eliminar", command=self.eliminar_servicio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Recargar", command=self.cargar_servicios).pack(side=tk.LEFT, padx=5)
        
        # Treeview para lista de servicios
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('id', 'codigo', 'nombre', 'precio_base', 'costo_base', 'categoria', 'activo')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        # Configurar columnas con ordenamiento para todas las relevantes
        self.tree.heading('id', text='ID', command=lambda: self.ordenar_por_columna('id'))
        self.tree.heading('codigo', text='Código', command=lambda: self.ordenar_por_columna('codigo'))
        self.tree.heading('nombre', text='Nombre', command=lambda: self.ordenar_por_columna('nombre'))
        self.tree.heading('precio_base', text='Precio Base', command=lambda: self.ordenar_por_columna('precio_base'))
        self.tree.heading('costo_base', text='Costo Base', command=lambda: self.ordenar_por_columna('costo_base'))
        self.tree.heading('categoria', text='Categoría', command=lambda: self.ordenar_por_columna('categoria'))
        self.tree.heading('activo', text='Estado', command=lambda: self.ordenar_por_columna('activo'))
        
        self.tree.column('id', width=50)
        self.tree.column('codigo', width=80)
        self.tree.column('nombre', width=250)
        self.tree.column('precio_base', width=90)
        self.tree.column('costo_base', width=90)
        self.tree.column('categoria', width=150)
        self.tree.column('activo', width=70)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind eventos
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_servicio)
        self.tree.bind('<Double-1>', lambda e: self.editar_servicio())
    
    def cargar_servicios(self, filtros=None):
        """Cargar lista de servicios"""
        self.servicios = self.manager.obtener_servicios(filtros)
        
        # Re-aplicar ordenamiento si existe
        if self.sort_column:
            self.ordenar_por_columna(self.sort_column)
        else:
            self.actualizar_treeview()
            
        self.actualizar_filtros_combobox()
    
    def actualizar_filtros_combobox(self):
        """Actualizar los combobox de filtros con datos actualizados"""
        # Categorías
        categorias_nombres = ["Todos"] + [cat['nombre'] for cat in self.categorias if cat.get('activo', True)]
        self.categoria_filter['values'] = categorias_nombres
    
    def actualizar_treeview(self):
        """Actualizar el treeview con los servicios"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
    
        # Llenar con datos
        for servicio in self.servicios:
            estado_display = "Activo" if servicio['activo'] else "Inactivo"
            categoria_nombre = self.obtener_nombre_por_id(self.categorias, servicio.get('categoria'))
        
            # Convertir precios a float antes de formatear
            precio_base = servicio.get('precio_base')
            costo_base = servicio.get('costo_base')
            
            precio_base_str = f"${float(precio_base):.2f}" if precio_base else ''
            costo_base_str = f"${float(costo_base):.2f}" if costo_base else ''
    
            self.tree.insert('', tk.END, values=(
                servicio['id'],
                servicio['codigo_interno'] or '',
                servicio['nombre'],
                precio_base_str,
                costo_base_str,
                categoria_nombre or '',
                estado_display
            ))

        # Actualizar indicación de orden en los encabezados si corresponde
        self._actualizar_encabezados_con_orden()

    def ordenar_por_columna(self, col):
        """Ordenar la lista de servicios por una columna (alternar asc/desc)."""
        # Alternar dirección si ya estamos ordenando por la misma columna
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        try:
            if col in ['precio_base', 'costo_base']:
                # Manejar valores None o vacíos para números
                keyfunc = lambda s: float(s.get(col) or 0) if s.get(col) not in [None, ''] else 0
            elif col == 'activo':
                # Ordenar por estado (Activo/Inactivo)
                keyfunc = lambda s: s.get('activo', False)
            elif col == 'id':
                # Ordenar por ID numérico
                keyfunc = lambda s: s.get('id', 0)
            else:
                # Usar lower para orden alfabético, manejar None
                keyfunc = lambda s: (s.get(col) or '').lower()

            self.servicios.sort(key=keyfunc, reverse=self.sort_reverse)
        except Exception as e:
            print(f"Error ordenando por {col}: {e}")
            # Fallback a ordenamiento básico por nombre
            self.servicios.sort(key=lambda s: (s.get('nombre') or '').lower())

        # Refrescar vista
        self.actualizar_treeview()

    def _actualizar_encabezados_con_orden(self):
        """Mostrar una flecha en el encabezado de la columna ordenada (▲ asc, ▼ desc)."""
        # Mapping de columnas a textos base
        encabezados = {
            'id': 'ID',
            'codigo': 'Código',
            'nombre': 'Nombre',
            'precio_base': 'Precio Base',
            'costo_base': 'Costo Base',
            'categoria': 'Categoría',
            'activo': 'Estado'
        }

        for col, text in encabezados.items():
            display = text
            if col == self.sort_column:
                display += ' ' + ('▼' if self.sort_reverse else '▲')
            try:
                # Actualizar heading manteniendo el callback
                if col == 'id':
                    self.tree.heading(col, text=display, command=lambda: self.ordenar_por_columna('id'))
                elif col == 'codigo':
                    self.tree.heading(col, text=display, command=lambda: self.ordenar_por_columna('codigo'))
                elif col == 'nombre':
                    self.tree.heading(col, text=display, command=lambda: self.ordenar_por_columna('nombre'))
                elif col == 'precio_base':
                    self.tree.heading(col, text=display, command=lambda: self.ordenar_por_columna('precio_base'))
                elif col == 'costo_base':
                    self.tree.heading(col, text=display, command=lambda: self.ordenar_por_columna('costo_base'))
                elif col == 'categoria':
                    self.tree.heading(col, text=display, command=lambda: self.ordenar_por_columna('categoria'))
                elif col == 'activo':
                    self.tree.heading(col, text=display, command=lambda: self.ordenar_por_columna('activo'))
            except Exception as e:
                print(f"Error actualizando encabezado {col}: {e}")
    
    def obtener_nombre_por_id(self, lista, id_buscado):
        """Obtener nombre de una lista por ID"""
        if not id_buscado:
            return ""
        for item in lista:
            if item['id'] == id_buscado:
                return item['nombre']
        return ""
    
    def seleccionar_servicio(self, event):
        """Manejar selección de servicio"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            servicio_id = item['values'][0]
            self.servicio_seleccionado = next(
                (s for s in self.servicios if s['id'] == servicio_id), None
            )
    
    def buscar_servicios(self, event=None):
        """Buscar servicios en tiempo real"""
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
        
        # Filtro de categoría
        categoria_seleccionada = self.categoria_filter_var.get()
        if categoria_seleccionada != "Todos":
            categoria_id = next((cat['id'] for cat in self.categorias if cat['nombre'] == categoria_seleccionada), None)
            if categoria_id:
                filtros['categoria'] = categoria_id
        
        # Filtro de estado
        estado_seleccionado = self.estado_filter_var.get()
        if estado_seleccionado == "Activos":
            filtros['activo'] = 'true'
        elif estado_seleccionado == "Inactivos":
            filtros['activo'] = 'false'
        
        self.cargar_servicios(filtros)
    
    def nuevo_servicio(self):
        """Abrir formulario para nuevo servicio"""
        FormularioServicio(self.window, self, None)
    
    def editar_servicio(self):
        """Abrir formulario para editar servicio seleccionado"""
        if not self.servicio_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un servicio para editar")
            return
        
        FormularioServicio(self.window, self, self.servicio_seleccionado)
    
    def eliminar_servicio(self):
        """Eliminar servicio seleccionado"""
        if not self.servicio_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un servicio para eliminar")
            return
        
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar el servicio:\n{self.servicio_seleccionado['nombre']}?"
        )
        
        if confirmacion:
            if self.manager.eliminar_servicio(self.servicio_seleccionado['id']):
                self.cargar_servicios()


class FormularioServicio:
    def __init__(self, parent, servicios_window, servicio_data):
        self.parent = parent
        self.servicios_window = servicios_window
        self.servicio_data = servicio_data
        self.es_nuevo = servicio_data is None
        
        self.categorias = servicios_window.categorias
        self.impuestos = servicios_window.impuestos
        
        # Variables para archivos
        self.imagen_path = None
        self.adjunto_path = None
        self.imagen_data = None
        self.adjunto_data = None
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Nuevo Servicio" if self.es_nuevo else "Editar Servicio")
        self.window.geometry("600x600")  # Ventana más pequeña sin marcas
        self.window.transient(parent)
        self.window.grab_set()
        
        self.center_window(600, 600)
        
        # INICIALIZAR VARIABLES
        self.codigo_var = tk.StringVar(self.window)
        self.nombre_var = tk.StringVar(self.window)
        self.descripcion_var = tk.StringVar(self.window)
        self.costo_base_var = tk.StringVar(self.window, value="0.00")
        self.precio_base_var = tk.StringVar(self.window, value="0.00")
        self.categoria_var = tk.StringVar(self.window)
        self.activo_var = tk.BooleanVar(self.window, value=True)
        
        # Lista para impuestos seleccionados
        self.impuestos_seleccionados = []
        
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
        # Notebook para pestañas
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Pestaña 1: Información Básica
        tab_basica = ttk.Frame(notebook)
        notebook.add(tab_basica, text="📋 Información Básica")

        # Pestaña 2: Impuestos
        tab_impuestos = ttk.Frame(notebook)
        notebook.add(tab_impuestos, text="💰 Impuestos")

        # Pestaña 3: Archivos
        tab_archivos = ttk.Frame(notebook)
        notebook.add(tab_archivos, text="📎 Archivos")

        self.crear_pestania_basica(tab_basica)
        self.crear_pestania_impuestos(tab_impuestos)
        self.crear_pestania_archivos(tab_archivos)

        # Botones en la parte inferior
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="💾 Guardar Servicio", command=self.guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

    def crear_pestania_basica(self, parent):
        """Crear pestaña de información básica"""
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Fila 1: Código
        row1 = ttk.Frame(main_frame)
        row1.pack(fill=tk.X, pady=5)

        ttk.Label(row1, text="Código Interno:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(row1, textvariable=self.codigo_var, width=20).pack(side=tk.LEFT)
        ttk.Label(row1, text="(Se genera automáticamente si está vacío)", 
                 font=("Arial", 8), foreground="gray").pack(side=tk.LEFT, padx=(10, 0))

        # Fila 2: Nombre
        row2 = ttk.Frame(main_frame)
        row2.pack(fill=tk.X, pady=5)

        ttk.Label(row2, text="Nombre:*").pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=self.nombre_var, width=50).pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

        # Fila 3: Descripción
        row3 = ttk.Frame(main_frame)
        row3.pack(fill=tk.X, pady=5)

        ttk.Label(row3, text="Descripción:").pack(side=tk.LEFT)
        desc_frame = ttk.Frame(row3)
        desc_frame.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        self.descripcion_text = tk.Text(desc_frame, width=50, height=4)
        self.descripcion_text.pack(fill=tk.BOTH, expand=True)

        # Fila 4: Precios
        row4 = ttk.Frame(main_frame)
        row4.pack(fill=tk.X, pady=10)

        ttk.Label(row4, text="Costo Base:*").pack(side=tk.LEFT)
        ttk.Entry(row4, textvariable=self.costo_base_var, width=15).pack(side=tk.LEFT, padx=(10, 20))

        ttk.Label(row4, text="Precio Base:*").pack(side=tk.LEFT)
        ttk.Entry(row4, textvariable=self.precio_base_var, width=15).pack(side=tk.LEFT, padx=(10, 0))

        # Fila 5: Categoría
        row5 = ttk.Frame(main_frame)
        row5.pack(fill=tk.X, pady=10)

        ttk.Label(row5, text="Categoría:").pack(side=tk.LEFT)
        categoria_frame = ttk.Frame(row5)
        categoria_frame.pack(side=tk.LEFT, padx=(10, 0))
        categoria_combo = ttk.Combobox(categoria_frame, textvariable=self.categoria_var, width=25)
        categoria_combo['values'] = [cat['nombre'] for cat in self.categorias if cat.get('activo', True)]
        categoria_combo.pack(side=tk.LEFT)
        ttk.Button(categoria_frame, text="➕", width=2,
                  command=self.crear_nueva_categoria).pack(side=tk.LEFT, padx=(2, 0))

        # Fila 6: Estado
        row6 = ttk.Frame(main_frame)
        row6.pack(fill=tk.X, pady=10)

        ttk.Label(row6, text="Estado:*").pack(side=tk.LEFT)
        ttk.Checkbutton(row6, text="Activo", variable=self.activo_var).pack(side=tk.LEFT, padx=(10, 0))

    def crear_nueva_categoria(self):
        """Abrir formulario rápido para crear nueva categoría"""
        CategoriasWindow(self.window)

    def crear_pestania_impuestos(self, parent):
        """Crear pestaña de gestión de impuestos"""
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para instrucciones
        instrucciones_frame = ttk.Frame(main_frame)
        instrucciones_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(instrucciones_frame, text="Seleccione los impuestos que aplican para este servicio:",
                 font=("Arial", 9)).pack(anchor=tk.W)

        # Frame para la tabla de impuestos
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Crear treeview para impuestos
        columns = ('tipo', 'impuesto', 'porcentaje', 'aplicar')
        self.tree_impuestos = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)

        # Configurar columnas
        self.tree_impuestos.heading('tipo', text='Tipo')
        self.tree_impuestos.heading('impuesto', text='Impuesto')
        self.tree_impuestos.heading('porcentaje', text='Porcentaje')
        self.tree_impuestos.heading('aplicar', text='Aplicar')

        self.tree_impuestos.column('tipo', width=100)
        self.tree_impuestos.column('impuesto', width=150)
        self.tree_impuestos.column('porcentaje', width=80)
        self.tree_impuestos.column('aplicar', width=60)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_impuestos.yview)
        self.tree_impuestos.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_impuestos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Llenar treeview con impuestos disponibles
        self.cargar_impuestos_disponibles()

        # Bind para selección de impuestos
        self.tree_impuestos.bind('<Button-1>', self.toggle_impuesto)

    def cargar_impuestos_disponibles(self):
        """Cargar todos los impuestos disponibles en el treeview"""
        # Limpiar treeview
        for item in self.tree_impuestos.get_children():
            self.tree_impuestos.delete(item)

        # Agregar impuestos para compra y venta
        for impuesto in self.impuestos:
            activo = impuesto.get('activo', True)
            
            if activo:
                # Para compra
                if impuesto['tipo'] in ['compra', 'ambos']:
                    self.tree_impuestos.insert('', tk.END, values=(
                        'Compra',
                        impuesto['nombre'],
                        f"{impuesto['porcentaje']}%",
                        '❌'
                    ), tags=('compra', str(impuesto['id'])))
            
                # Para venta
                if impuesto['tipo'] in ['venta', 'ambos']:
                    self.tree_impuestos.insert('', tk.END, values=(
                        'Venta',
                        impuesto['nombre'],
                        f"{impuesto['porcentaje']}%",
                        '❌'
                    ), tags=('venta', str(impuesto['id'])))

    def toggle_impuesto(self, event):
        """Alternar aplicación de impuesto al hacer click"""
        item = self.tree_impuestos.identify_row(event.y)
        if item:
            col = self.tree_impuestos.identify_column(event.x)
            if col == '#4':  # Columna "Aplicar"
                valores = self.tree_impuestos.item(item, 'values')
                tags = self.tree_impuestos.item(item, 'tags')
                
                if valores[3] == '❌':
                    self.tree_impuestos.set(item, 'aplicar', '✅')
                    # Agregar a la lista de seleccionados
                    tipo = tags[0]
                    impuesto_id = int(tags[1])
                    self.impuestos_seleccionados.append({
                        'impuesto_id': impuesto_id,
                        'tipo': tipo
                    })
                else:
                    self.tree_impuestos.set(item, 'aplicar', '❌')
                    # Remover de la lista de seleccionados
                    tipo = tags[0]
                    impuesto_id = int(tags[1])
                    self.impuestos_seleccionados = [imp for imp in self.impuestos_seleccionados
                                                   if not (imp['impuesto_id'] == impuesto_id and imp['tipo'] == tipo)]

    def crear_pestania_archivos(self, parent):
        """Crear pestaña para gestión de archivos"""
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para imagen
        imagen_frame = ttk.LabelFrame(main_frame, text="🖼️ Imagen del Servicio", padding="10")
        imagen_frame.pack(fill=tk.X, pady=5)

        self.imagen_label = ttk.Label(imagen_frame, text="No se ha seleccionado imagen")
        self.imagen_label.pack(pady=5)

        ttk.Button(imagen_frame, text="Seleccionar Imagen", command=self.seleccionar_imagen).pack(pady=5)

        # Frame para adjunto
        adjunto_frame = ttk.LabelFrame(main_frame, text="📄 Documento Adjunto", padding="10")
        adjunto_frame.pack(fill=tk.X, pady=5)

        self.adjunto_label = ttk.Label(adjunto_frame, text="No se ha seleccionado archivo")
        self.adjunto_label.pack(pady=5)

        ttk.Button(adjunto_frame, text="Seleccionar Adjunto", command=self.seleccionar_adjunto).pack(pady=5)

    def seleccionar_imagen(self):
        """Seleccionar archivo de imagen"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Imagen",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.imagen_path = file_path
            self.imagen_label.config(text=os.path.basename(file_path))

    def seleccionar_adjunto(self):
        """Seleccionar archivo adjunto"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Adjunto",
            filetypes=[("PDF", "*.pdf"), ("Documentos", "*.doc *.docx"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.adjunto_path = file_path
            self.adjunto_label.config(text=os.path.basename(file_path))

    def cargar_datos(self):
        """Cargar datos del servicio en el formulario"""
        if not self.servicio_data:
            return

        self.codigo_var.set(self.servicio_data.get('codigo_interno', ''))
        self.nombre_var.set(self.servicio_data.get('nombre', ''))
        self.descripcion_text.insert('1.0', self.servicio_data.get('descripcion', ''))
        self.costo_base_var.set(str(self.servicio_data.get('costo_base', '0.00')))
        self.precio_base_var.set(str(self.servicio_data.get('precio_base', '0.00')))
        self.activo_var.set(self.servicio_data.get('activo', True))

        # Cargar categoría
        if self.servicio_data.get('categoria'):
            categoria_nombre = self.obtener_nombre_por_id(self.categorias, self.servicio_data['categoria'])
            self.categoria_var.set(categoria_nombre)

        # Cargar impuestos existentes
        if 'servicioimpuesto_set' in self.servicio_data:
            for impuesto in self.servicio_data['servicioimpuesto_set']:
                if impuesto.get('impuesto'):
                    impuesto_id = impuesto['impuesto']['id']
                    tipo = impuesto['tipo']
                    self.impuestos_seleccionados.append({
                        'impuesto_id': impuesto_id,
                        'tipo': tipo
                    })
            
            # Actualizar treeview de impuestos
            self.marcar_impuestos_seleccionados()

    def obtener_nombre_por_id(self, lista, id_buscado):
        """Obtener nombre de una lista por ID"""
        for item in lista:
            if item['id'] == id_buscado:
                return item['nombre']
        return ""

    def marcar_impuestos_seleccionados(self):
        """Marcar los impuestos seleccionados en el treeview"""
        for item in self.tree_impuestos.get_children():
            tags = self.tree_impuestos.item(item, 'tags')
            tipo = tags[0]
            impuesto_id = int(tags[1])
            
            # Verificar si este impuesto está seleccionado
            for imp_sel in self.impuestos_seleccionados:
                if imp_sel['impuesto_id'] == impuesto_id and imp_sel['tipo'] == tipo:
                    self.tree_impuestos.set(item, 'aplicar', '✅')
                    break

    def validar_formulario(self):
        """Validar datos del formulario"""
        # Validar nombre
        if not self.nombre_var.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return False

        # Validar precios
        costo = self.costo_base_var.get().strip()
        precio = self.precio_base_var.get().strip()

        if not costo:
            messagebox.showerror("Error", "El costo base es obligatorio")
            return False

        if not precio:
            messagebox.showerror("Error", "El precio base es obligatorio")
            return False

        es_valido, mensaje_error = self.servicios_window.manager.validar_precios(costo, precio)
        if not es_valido:
            messagebox.showerror("Error", mensaje_error)
            return False

        return True

    def guardar(self):
        """Guardar servicio"""
        if not self.validar_formulario():
            return

        # Preparar datos básicos
        datos = {
            'nombre': self.nombre_var.get().strip(),
            'costo_base': float(self.costo_base_var.get().strip()),
            'precio_base': float(self.precio_base_var.get().strip()),
            'activo': self.activo_var.get()
        }

        # Solo incluir campos opcionales si tienen valor o son nuevos
        codigo = self.codigo_var.get().strip()
        if codigo:
            datos['codigo_interno'] = codigo
        elif self.es_nuevo:
            datos['codigo_interno'] = None  # Para nuevo servicio, None genera código automático

        descripcion = self.descripcion_text.get('1.0', tk.END).strip()
        if descripcion:
            datos['descripcion'] = descripcion
        else:
            datos['descripcion'] = ""

        # Manejar categoría - solo si está seleccionada
        if self.categoria_var.get():
            categoria_id = next((cat['id'] for cat in self.categorias
                           if cat['nombre'] == self.categoria_var.get()), None)
            if categoria_id:
                datos['categoria'] = categoria_id
        else:
            if not self.es_nuevo and 'categoria' in self.servicio_data:
                datos['categoria'] = self.servicio_data['categoria']
            else:
                datos['categoria'] = None

        # Agregar impuestos seleccionados
        if self.impuestos_seleccionados:
            datos['servicioimpuesto_set'] = []
            for imp_sel in self.impuestos_seleccionados:
                datos['servicioimpuesto_set'].append({
                    'impuesto_id': imp_sel['impuesto_id'],
                    'tipo': imp_sel['tipo']
                })
        elif not self.es_nuevo:
            # Para actualización, mantener impuestos existentes si no hay cambios
            if 'servicioimpuesto_set' in self.servicio_data:
                datos['servicioimpuesto_set'] = self.servicio_data['servicioimpuesto_set']

        print(f"DEBUG - Datos a enviar: {datos}")

        manager = ServiciosManager()
        if self.es_nuevo:
            resultado = manager.crear_servicio(datos)
        else:
            resultado = manager.actualizar_servicio(self.servicio_data['id'], datos)

        if resultado:
            self.servicios_window.cargar_servicios()
            self.window.destroy()