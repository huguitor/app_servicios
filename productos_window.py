# /app_escritorio/productos_window.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from productos_manager import ProductosManager
from proveedores_manager import ProveedoresManager
from categorias_manager import CategoriasManager
from marcas_manager import MarcasManager
from impuestos_manager import ImpuestosManager
import os
from PIL import Image, ImageTk
import json
import base64


class ProductosWindow:
    def __init__(self, parent):
        self.parent = parent
        self.manager = ProductosManager()
        self.proveedores_manager = ProveedoresManager()
        self.categorias_manager = CategoriasManager()
        self.marcas_manager = MarcasManager()
        self.impuestos_manager = ImpuestosManager()
        
        self.productos = []
        self.proveedores = []
        self.categorias = []
        self.marcas = []
        self.impuestos = []
        self.producto_seleccionado = None
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Productos - Lab Servicios")
       
        # USAR 90% DEL ANCHO DE PANTALLA (más grande por la complejidad)
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
        self.marca_filter_var = tk.StringVar(self.window)
        self.proveedor_filter_var = tk.StringVar(self.window)
        self.estado_filter_var = tk.StringVar(self.window)
       
        self.create_widgets()
        self.cargar_datos_combobox()
        self.cargar_productos()
   
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
            # Cargar sin filtros para obtener todos los registros
            self.proveedores = self.proveedores_manager.obtener_proveedores()
            self.categorias = self.categorias_manager.obtener_categorias()
            self.marcas = self.marcas_manager.obtener_marcas()
            self.impuestos = self.impuestos_manager.obtener_impuestos()
            
            # Filtrar solo activos localmente si es necesario
            self.proveedores = [p for p in self.proveedores if p.get('activo', True)]
            self.categorias = [c for c in self.categorias if c.get('activo', True)]
            self.marcas = [m for m in self.marcas if m.get('activo', True)]
            self.impuestos = [i for i in self.impuestos if i.get('activo', True)]
            
        except Exception as e:
            print(f"Error cargando datos para combobox: {e}")
            # Inicializar listas vacías para evitar errores
            self.proveedores = []
            self.categorias = []
            self.marcas = []
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
        self.search_entry.bind('<KeyRelease>', self.buscar_productos)
       
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
       
        ttk.Label(search_frame, text="Marca:").pack(side=tk.LEFT, padx=(10, 5))
        self.marca_filter = ttk.Combobox(
            search_frame,
            textvariable=self.marca_filter_var,
            state="readonly",
            width=15
        )
        self.marca_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.marca_filter.bind('<<ComboboxSelected>>', self.aplicar_filtros)
       
        ttk.Label(search_frame, text="Proveedor:").pack(side=tk.LEFT, padx=(10, 5))
        self.proveedor_filter = ttk.Combobox(
            search_frame,
            textvariable=self.proveedor_filter_var,
            state="readonly",
            width=15
        )
        self.proveedor_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.proveedor_filter.bind('<<ComboboxSelected>>', self.aplicar_filtros)
       
        ttk.Label(search_frame, text="Estado:").pack(side=tk.LEFT, padx=(10, 5))
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
       
        ttk.Button(button_frame, text="➕ Nuevo Producto", command=self.nuevo_producto).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Editar", command=self.editar_producto).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Eliminar", command=self.eliminar_producto).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Actualizar Stock", command=self.actualizar_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Recargar", command=self.cargar_productos).pack(side=tk.LEFT, padx=5)
       
        # Treeview para lista de productos
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
       
        columns = ('id', 'codigo', 'nombre', 'precio_venta', 'costo_compra', 'stock', 'categoria', 'marca', 'proveedor', 'activo')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
       
        # Configurar columnas
        self.tree.heading('id', text='ID')
        self.tree.heading('codigo', text='Código')
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('precio_venta', text='Precio Venta')
        self.tree.heading('costo_compra', text='Costo Compra')
        self.tree.heading('stock', text='Stock')
        self.tree.heading('categoria', text='Categoría')
        self.tree.heading('marca', text='Marca')
        self.tree.heading('proveedor', text='Proveedor')
        self.tree.heading('activo', text='Estado')
       
        self.tree.column('id', width=50)
        self.tree.column('codigo', width=80)
        self.tree.column('nombre', width=200)
        self.tree.column('precio_venta', width=90)
        self.tree.column('costo_compra', width=90)
        self.tree.column('stock', width=60)
        self.tree.column('categoria', width=120)
        self.tree.column('marca', width=120)
        self.tree.column('proveedor', width=150)
        self.tree.column('activo', width=70)
       
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
       
        # Bind eventos
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_producto)
        self.tree.bind('<Double-1>', lambda e: self.editar_producto())
   
    def cargar_productos(self, filtros=None):
        """Cargar lista de productos"""
        self.productos = self.manager.obtener_productos(filtros)
        self.actualizar_treeview()
        self.actualizar_filtros_combobox()
   
    def actualizar_filtros_combobox(self):
        """Actualizar los combobox de filtros con datos actualizados"""
        # Categorías
        categorias_nombres = ["Todos"] + [cat['nombre'] for cat in self.categorias if cat.get('activo', True)]
        self.categoria_filter['values'] = categorias_nombres
        
        # Marcas
        marcas_nombres = ["Todos"] + [marca['nombre'] for marca in self.marcas if marca.get('activo', True)]
        self.marca_filter['values'] = marcas_nombres
        
        # Proveedores
        proveedores_nombres = ["Todos"] + [prov['nombre'] for prov in self.proveedores if prov.get('activo', True)]
        self.proveedor_filter['values'] = proveedores_nombres
   
    def actualizar_treeview(self):
        """Actualizar el treeview con los productos"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
    
        # Llenar con datos
        for producto in self.productos:
            estado_display = "Activo" if producto['activo'] else "Inactivo"
            categoria_nombre = self.obtener_nombre_por_id(self.categorias, producto.get('categoria'))
            marca_nombre = self.obtener_nombre_por_id(self.marcas, producto.get('marca'))
            proveedor_nombre = self.obtener_nombre_por_id(self.proveedores, producto.get('proveedor'))
        
            # CORRECCIÓN: Convertir precios a float antes de formatear
            precio_venta = producto.get('precio_venta')
            costo_compra = producto.get('costo_compra')
            
            precio_venta_str = f"${float(precio_venta):.2f}" if precio_venta else ''
            costo_compra_str = f"${float(costo_compra):.2f}" if costo_compra else ''
        
            self.tree.insert('', tk.END, values=(
                producto['id'],
                producto['sku'] or '',
                producto['nombre'],
                precio_venta_str,  # Usar la variable corregida
                costo_compra_str,  # Usar la variable corregida
                producto['stock'],
                categoria_nombre or '',
                marca_nombre or '',
                proveedor_nombre or '',
                estado_display
            ))
   
    def obtener_nombre_por_id(self, lista, id_buscado):
        """Obtener nombre de una lista por ID"""
        if not id_buscado:
            return ""
        for item in lista:
            if item['id'] == id_buscado:
                return item['nombre']
        return ""
   
    def seleccionar_producto(self, event):
        """Manejar selección de producto"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            producto_id = item['values'][0]
            self.producto_seleccionado = next(
                (p for p in self.productos if p['id'] == producto_id), None
            )
   
    def buscar_productos(self, event=None):
        """Buscar productos en tiempo real"""
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
       
        # Filtro de marca
        marca_seleccionada = self.marca_filter_var.get()
        if marca_seleccionada != "Todos":
            marca_id = next((marca['id'] for marca in self.marcas if marca['nombre'] == marca_seleccionada), None)
            if marca_id:
                filtros['marca'] = marca_id
       
        # Filtro de proveedor
        proveedor_seleccionado = self.proveedor_filter_var.get()
        if proveedor_seleccionado != "Todos":
            proveedor_id = next((prov['id'] for prov in self.proveedores if prov['nombre'] == proveedor_seleccionado), None)
            if proveedor_id:
                filtros['proveedor'] = proveedor_id
       
        # Filtro de estado
        estado_seleccionado = self.estado_filter_var.get()
        if estado_seleccionado == "Activos":
            filtros['activo'] = 'true'
        elif estado_seleccionado == "Inactivos":
            filtros['activo'] = 'false'
       
        self.cargar_productos(filtros)
   
    def nuevo_producto(self):
        """Abrir formulario para nuevo producto"""
        FormularioProducto(self.window, self, None)
   
    def editar_producto(self):
        """Abrir formulario para editar producto seleccionado"""
        if not self.producto_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto para editar")
            return
       
        FormularioProducto(self.window, self, self.producto_seleccionado)
   
    def eliminar_producto(self):
        """Eliminar producto seleccionado"""
        if not self.producto_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto para eliminar")
            return
       
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar el producto:\n{self.producto_seleccionado['nombre']}?"
        )
       
        if confirmacion:
            if self.manager.eliminar_producto(self.producto_seleccionado['id']):
                self.cargar_productos()
   
    def actualizar_stock(self):
        """Ventana para actualizar stock por código de barras"""
        if not self.producto_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto para actualizar stock")
            return
        
        # Implementar ventana de actualización de stock
        VentanaActualizarStock(self.window, self, self.producto_seleccionado)


class FormularioProducto:
    def __init__(self, parent, productos_window, producto_data):
        self.parent = parent
        self.productos_window = productos_window
        self.producto_data = producto_data
        self.es_nuevo = producto_data is None
        
        self.proveedores = productos_window.proveedores
        self.categorias = productos_window.categorias
        self.marcas = productos_window.marcas
        self.impuestos = productos_window.impuestos
        
        # Variables para archivos
        self.foto_path = None
        self.plano_path = None
        self.foto_data = None
        self.plano_data = None
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Nuevo Producto" if self.es_nuevo else "Editar Producto")
        self.window.geometry("800x700")
        self.window.transient(parent)
        self.window.grab_set()
       
        self.center_window(800, 700)
       
        # INICIALIZAR VARIABLES
        self.codigo_var = tk.StringVar(self.window)
        self.codigo_barras_var = tk.StringVar(self.window)
        self.nombre_var = tk.StringVar(self.window)
        self.descripcion_var = tk.StringVar(self.window)
        self.costo_compra_var = tk.StringVar(self.window)
        self.precio_venta_var = tk.StringVar(self.window)
        self.stock_var = tk.StringVar(self.window, value="0")
        self.proveedor_var = tk.StringVar(self.window)
        self.categoria_var = tk.StringVar(self.window)
        self.marca_var = tk.StringVar(self.window)
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
        tab_impuestos = ttk.Frame(notebook)  # CORRECCIÓN: Frame separado para impuestos
        notebook.add(tab_impuestos, text="💰 Impuestos")
    
        # Pestaña 3: Archivos
        tab_archivos = ttk.Frame(notebook)
        notebook.add(tab_archivos, text="📎 Archivos")
    
        self.crear_pestania_basica(tab_basica)
        self.crear_pestania_impuestos(tab_impuestos)  # CORRECCIÓN: Pasar el frame correcto
        self.crear_pestania_archivos(tab_archivos)
    
        # Botones en la parte inferior
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
    
        ttk.Button(button_frame, text="💾 Guardar Producto", command=self.guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)   
    
    def crear_pestania_basica(self, parent):
        """Crear pestaña de información básica"""
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Fila 1: Código y Código de Barras
        row1 = ttk.Frame(main_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Código:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(row1, textvariable=self.codigo_var, width=15).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row1, text="Código Barras:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(row1, textvariable=self.codigo_barras_var, width=20).pack(side=tk.LEFT)
        
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
        
        ttk.Label(row4, text="Costo Compra:*").pack(side=tk.LEFT)
        ttk.Entry(row4, textvariable=self.costo_compra_var, width=15).pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Label(row4, text="Precio Venta:*").pack(side=tk.LEFT)
        ttk.Entry(row4, textvariable=self.precio_venta_var, width=15).pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Label(row4, text="Stock:").pack(side=tk.LEFT)
        ttk.Entry(row4, textvariable=self.stock_var, width=10).pack(side=tk.LEFT, padx=(10, 0))
        
        # Fila 5: Relaciones (MEJORADA con botones para crear nuevos)
        row5 = ttk.Frame(main_frame)
        row5.pack(fill=tk.X, pady=10)
        
        # Proveedor
        ttk.Label(row5, text="Proveedor:").pack(side=tk.LEFT)
        proveedor_frame = ttk.Frame(row5)
        proveedor_frame.pack(side=tk.LEFT, padx=(10, 20))
        proveedor_combo = ttk.Combobox(proveedor_frame, textvariable=self.proveedor_var, width=18)
        proveedor_combo['values'] = [prov['nombre'] for prov in self.proveedores if prov.get('activo', True)]
        proveedor_combo.pack(side=tk.LEFT)
        
        # Categoría con botón para crear nueva
        ttk.Label(row5, text="Categoría:").pack(side=tk.LEFT)
        categoria_frame = ttk.Frame(row5)
        categoria_frame.pack(side=tk.LEFT, padx=(10, 20))
        categoria_combo = ttk.Combobox(categoria_frame, textvariable=self.categoria_var, width=18)
        categoria_combo['values'] = [cat['nombre'] for cat in self.categorias if cat.get('activo', True)]
        categoria_combo.pack(side=tk.LEFT)
        # Botón para crear nueva categoría
        ttk.Button(categoria_frame, text="➕", width=2, 
                  command=self.crear_nueva_categoria).pack(side=tk.LEFT, padx=(2, 0))
        
        # Marca con botón para crear nueva
        ttk.Label(row5, text="Marca:").pack(side=tk.LEFT)
        marca_frame = ttk.Frame(row5)
        marca_frame.pack(side=tk.LEFT, padx=(10, 0))
        marca_combo = ttk.Combobox(marca_frame, textvariable=self.marca_var, width=18)
        marca_combo['values'] = [marca['nombre'] for marca in self.marcas if marca.get('activo', True)]
        marca_combo.pack(side=tk.LEFT)
        # Botón para crear nueva marca
        ttk.Button(marca_frame, text="➕", width=2, 
                  command=self.crear_nueva_marca).pack(side=tk.LEFT, padx=(2, 0))
        
        # Fila 6: Estado
        row6 = ttk.Frame(main_frame)
        row6.pack(fill=tk.X, pady=10)
        
        ttk.Label(row6, text="Estado:*").pack(side=tk.LEFT)
        ttk.Checkbutton(row6, text="Activo", variable=self.activo_var).pack(side=tk.LEFT, padx=(10, 0))
    
    def crear_nueva_categoria(self):
        """Abrir formulario rápido para crear nueva categoría"""
        from categorias_window import FormularioCategoriaRapida
        FormularioCategoriaRapida(self.window, self.actualizar_combobox_categorias)
    
    def crear_nueva_marca(self):
        """Abrir formulario rápido para crear nueva marca"""
        from marcas_window import FormularioMarcaRapida
        FormularioMarcaRapida(self.window, self.actualizar_combobox_marcas)
    
    def actualizar_combobox_categorias(self):
        """Actualizar combobox de categorías después de crear una nueva"""
        self.productos_window.cargar_datos_combobox()
        self.categorias = self.productos_window.categorias
        # Buscar y actualizar combobox de categorías
        for widget in self.window.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab in widget.winfo_children():
                    self.actualizar_combobox_en_tab(tab, 'categoria')
    
    def actualizar_combobox_marcas(self):
        """Actualizar combobox de marcas después de crear una nueva"""
        self.productos_window.cargar_datos_combobox()
        self.marcas = self.productos_window.marcas
        # Buscar y actualizar combobox de marcas
        for widget in self.window.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab in widget.winfo_children():
                    self.actualizar_combobox_en_tab(tab, 'marca')
    
    def actualizar_combobox_en_tab(self, parent, tipo):
        """Buscar y actualizar combobox específico en los widgets hijos"""
        for widget in parent.winfo_children():
            if isinstance(widget, ttk.Combobox):
                current_value = widget.get()
                if tipo == 'categoria' and current_value:
                    widget['values'] = [cat['nombre'] for cat in self.categorias if cat.get('activo', True)]
                elif tipo == 'marca' and current_value:
                    widget['values'] = [marca['nombre'] for marca in self.marcas if marca.get('activo', True)]
            elif isinstance(widget, (ttk.Frame, ttk.LabelFrame)):
                self.actualizar_combobox_en_tab(widget, tipo)
    
    def crear_pestania_impuestos(self, parent):
        """Crear pestaña de gestión de impuestos"""
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para instrucciones
        instrucciones_frame = ttk.Frame(main_frame)
        instrucciones_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(instrucciones_frame, text="Seleccione los impuestos que aplican para este producto:", 
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
            # CORRECCIÓN: Verificar si el impuesto está activo (si existe el campo)
            # Si no existe el campo 'activo', asumimos que está activo
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
        
        # Frame para foto
        foto_frame = ttk.LabelFrame(main_frame, text="📷 Foto del Producto", padding="10")
        foto_frame.pack(fill=tk.X, pady=5)
        
        self.foto_label = ttk.Label(foto_frame, text="No se ha seleccionado foto")
        self.foto_label.pack(pady=5)
        
        ttk.Button(foto_frame, text="Seleccionar Foto", command=self.seleccionar_foto).pack(pady=5)
        
        # Frame para plano
        plano_frame = ttk.LabelFrame(main_frame, text="📄 Plano/Especificación", padding="10")
        plano_frame.pack(fill=tk.X, pady=5)
        
        self.plano_label = ttk.Label(plano_frame, text="No se ha seleccionado archivo")
        self.plano_label.pack(pady=5)
        
        ttk.Button(plano_frame, text="Seleccionar Plano", command=self.seleccionar_plano).pack(pady=5)
    
    def seleccionar_foto(self):
        """Seleccionar archivo de foto"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Foto",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.foto_path = file_path
            self.foto_label.config(text=os.path.basename(file_path))
            # Aquí podrías cargar la imagen para previsualización
    
    def seleccionar_plano(self):
        """Seleccionar archivo de plano"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Plano",
            filetypes=[("PDF", "*.pdf"), ("Documentos", "*.doc *.docx"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.plano_path = file_path
            self.plano_label.config(text=os.path.basename(file_path))
    
    def cargar_datos(self):
        """Cargar datos del producto en el formulario"""
        if not self.producto_data:
            return
        
        self.codigo_var.set(self.producto_data.get('sku', ''))
        self.codigo_barras_var.set(self.producto_data.get('codigo_barras', ''))
        self.nombre_var.set(self.producto_data.get('nombre', ''))
        self.descripcion_text.insert('1.0', self.producto_data.get('descripcion', ''))
        self.costo_compra_var.set(str(self.producto_data.get('costo_compra', '')))
        self.precio_venta_var.set(str(self.producto_data.get('precio_venta', '')))
        self.stock_var.set(str(self.producto_data.get('stock', 0)))
        self.activo_var.set(self.producto_data.get('activo', True))
        
        # Cargar relaciones
        if self.producto_data.get('proveedor'):
            proveedor_nombre = self.obtener_nombre_por_id(self.proveedores, self.producto_data['proveedor'])
            self.proveedor_var.set(proveedor_nombre)
        
        if self.producto_data.get('categoria'):
            categoria_nombre = self.obtener_nombre_por_id(self.categorias, self.producto_data['categoria'])
            self.categoria_var.set(categoria_nombre)
        
        if self.producto_data.get('marca'):
            marca_nombre = self.obtener_nombre_por_id(self.marcas, self.producto_data['marca'])
            self.marca_var.set(marca_nombre)
        
        # Cargar impuestos existentes
        if 'productoimpuesto_set' in self.producto_data:
            for impuesto in self.producto_data['productoimpuesto_set']:
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
        costo = self.costo_compra_var.get().strip()
        precio = self.precio_venta_var.get().strip()
        
        if not costo:
            messagebox.showerror("Error", "El costo de compra es obligatorio")
            return False
        
        if not precio:
            messagebox.showerror("Error", "El precio de venta es obligatorio")
            return False
        
        es_valido, mensaje_error = self.productos_window.manager.validar_precios(costo, precio)
        if not es_valido:
            messagebox.showerror("Error", mensaje_error)
            return False
        
        # Validar stock
        try:
            stock = int(self.stock_var.get()) if self.stock_var.get() else 0
            if stock < 0:
                messagebox.showerror("Error", "El stock no puede ser negativo")
                return False
        except ValueError:
            messagebox.showerror("Error", "El stock debe ser un número entero")
            return False
        
        return True
    
    def guardar(self):
        """Guardar producto - USAR PATCH para actualización parcial"""
        if not self.validar_formulario():
            return
        
        # Preparar datos básicos - SOLO campos modificados para PATCH
        datos = {
            'nombre': self.nombre_var.get().strip(),
            'costo_compra': float(self.costo_compra_var.get().strip()),
            'precio_venta': float(self.precio_venta_var.get().strip()),
            'stock': int(self.stock_var.get()) if self.stock_var.get() else 0,
            'activo': self.activo_var.get()
        }
        
        # Solo incluir campos opcionales si tienen valor o son nuevos
        codigo = self.codigo_var.get().strip()
        if codigo:
            datos['sku'] = codigo
        elif self.es_nuevo:
            datos['sku'] = None  # Para nuevo producto, None genera SKU automático
        
        codigo_barras = self.codigo_barras_var.get().strip()
        if codigo_barras:
            datos['codigo_barras'] = codigo_barras
        else:
            datos['codigo_barras'] = ""
        
        descripcion = self.descripcion_text.get('1.0', tk.END).strip()
        if descripcion:
            datos['descripcion'] = descripcion
        else:
            datos['descripcion'] = ""
        
        # Manejar relaciones - solo si están seleccionadas
        if self.proveedor_var.get():
            proveedor_id = next((prov['id'] for prov in self.proveedores
                           if prov['nombre'] == self.proveedor_var.get()), None)
            if proveedor_id:
                datos['proveedor'] = proveedor_id
        else:
            # Para actualización, si no hay selección, mantener el valor existente
            if not self.es_nuevo and 'proveedor' in self.producto_data:
                datos['proveedor'] = self.producto_data['proveedor']
            else:
                datos['proveedor'] = None
        
        if self.categoria_var.get():
            categoria_id = next((cat['id'] for cat in self.categorias
                           if cat['nombre'] == self.categoria_var.get()), None)
            if categoria_id:
                datos['categoria'] = categoria_id
        else:
            if not self.es_nuevo and 'categoria' in self.producto_data:
                datos['categoria'] = self.producto_data['categoria']
            else:
                datos['categoria'] = None
        
        if self.marca_var.get():
            marca_id = next((marca['id'] for marca in self.marcas
                       if marca['nombre'] == self.marca_var.get()), None)
            if marca_id:
                datos['marca'] = marca_id
        else:
            if not self.es_nuevo and 'marca' in self.producto_data:
                datos['marca'] = self.producto_data['marca']
            else:
                datos['marca'] = None
        
        # Agregar impuestos seleccionados
        if self.impuestos_seleccionados:
            datos['productoimpuesto_set'] = []
            for imp_sel in self.impuestos_seleccionados:
                datos['productoimpuesto_set'].append({
                    'impuesto_id': imp_sel['impuesto_id'],
                    'tipo': imp_sel['tipo']
                })
        elif not self.es_nuevo:
            # Para actualización, mantener impuestos existentes si no hay cambios
            if 'productoimpuesto_set' in self.producto_data:
                datos['productoimpuesto_set'] = self.producto_data['productoimpuesto_set']
        
        print(f"DEBUG - Datos a enviar: {datos}")
        
        manager = ProductosManager()
        if self.es_nuevo:
            resultado = manager.crear_producto(datos)
        else:
            resultado = manager.actualizar_producto(self.producto_data['id'], datos)
        
        if resultado:
            self.productos_window.cargar_productos()
            self.window.destroy()


class VentanaActualizarStock:
    def __init__(self, parent, productos_window, producto_data):
        self.parent = parent
        self.productos_window = productos_window
        self.producto_data = producto_data
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title(f"Actualizar Stock - {producto_data['nombre']}")
        self.window.geometry("400x200")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.center_window(400, 200)
        
        # Variables
        self.cantidad_var = tk.StringVar(self.window, value="0")
        
        self.create_widgets()
    
    def center_window(self, width, height):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información del producto
        ttk.Label(main_frame, text=f"Producto: {self.producto_data['nombre']}", 
                 font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(main_frame, text=f"Stock actual: {self.producto_data['stock']}", 
                 font=("Arial", 9)).pack(anchor=tk.W, pady=(0, 15))
        
        # Entrada de cantidad
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Cantidad a agregar/restar:").pack(side=tk.LEFT)
        cantidad_entry = ttk.Entry(input_frame, textvariable=self.cantidad_var, width=10)
        cantidad_entry.pack(side=tk.LEFT, padx=(10, 0))
        cantidad_entry.focus()
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="➕ Agregar Stock", 
                  command=lambda: self.actualizar_stock(True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="➖ Restar Stock", 
                  command=lambda: self.actualizar_stock(False)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancelar", 
                  command=self.window.destroy).pack(side=tk.LEFT, padx=5)
    
    def actualizar_stock(self, es_adicion):
        """Actualizar el stock del producto"""
        try:
            cantidad = int(self.cantidad_var.get())
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return
            
            stock_actual = self.producto_data['stock']
            if es_adicion:
                nuevo_stock = stock_actual + cantidad
            else:
                nuevo_stock = stock_actual - cantidad
                if nuevo_stock < 0:
                    messagebox.showerror("Error", "No se puede tener stock negativo")
                    return
            
            # Actualizar producto
            datos = {
                'stock': nuevo_stock
            }
            
            manager = ProductosManager()
            resultado = manager.actualizar_producto(self.producto_data['id'], datos)
            
            if resultado:
                messagebox.showinfo("Éxito", f"Stock actualizado correctamente\nNuevo stock: {nuevo_stock}")
                self.productos_window.cargar_productos()
                self.window.destroy()
                
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero válido")