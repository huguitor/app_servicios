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
from image_helper import ImageHelper
import tempfile
import requests
from api_client import APIClient

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
        
        # VARIABLES DE ORDENAMIENTO
        self.orden_actual = None
        self.direccion_orden = True  # True = ascendente, False = descendente
        self.columna_orden_actual = None
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Productos - Lab Servicios")
       
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
            self.proveedores = self.proveedores_manager.obtener_proveedores()
            self.categorias = self.categorias_manager.obtener_categorias()
            self.marcas = self.marcas_manager.obtener_marcas()
            self.impuestos = self.impuestos_manager.obtener_impuestos()
           
            self.proveedores = [p for p in self.proveedores if p.get('activo', True)]
            self.categorias = [c for c in self.categorias if c.get('activo', True)]
            self.marcas = [m for m in self.marcas if m.get('activo', True)]
            self.impuestos = [i for i in self.impuestos if i.get('activo', True)]
           
        except Exception as e:
            print(f"Error cargando datos para combobox: {e}")
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
       
        # Configurar columnas CON ORDENAMIENTO
        self.configurar_columnas_ordenamiento()
       
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
       
        # Bind eventos
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_producto)
        self.tree.bind('<Double-1>', lambda e: self.editar_producto())

    def configurar_columnas_ordenamiento(self):
        """Configurar columnas con capacidad de ordenamiento"""
        # Definir columnas con sus textos y anchos
        columnas_config = [
            ('id', 'ID', 50),
            ('codigo', 'Código', 80),
            ('nombre', 'Nombre', 200),
            ('precio_venta', 'Precio Venta', 90),
            ('costo_compra', 'Costo Compra', 90),
            ('stock', 'Stock', 60),
            ('categoria', 'Categoría', 120),
            ('marca', 'Marca', 120),
            ('proveedor', 'Proveedor', 150),
            ('activo', 'Estado', 70)
        ]
        
        for col_id, texto, ancho in columnas_config:
            self.tree.heading(col_id, text=texto, command=lambda c=col_id: self.ordenar_por_columna(c))
            self.tree.column(col_id, width=ancho)

    def ordenar_por_columna(self, columna):
        """Ordenar productos por columna específica"""
        try:
            # Determinar dirección del orden
            if self.columna_orden_actual == columna:
                self.direccion_orden = not self.direccion_orden
            else:
                self.columna_orden_actual = columna
                self.direccion_orden = True
            
            # Ordenar los productos
            productos_ordenados = self.ordenar_lista_productos(self.productos, columna, self.direccion_orden)
            
            # Actualizar treeview con productos ordenados
            self.actualizar_treeview_con_datos(productos_ordenados)
            
            # Actualizar indicadores visuales
            self.actualizar_indicadores_ordenamiento(columna)
            
        except Exception as e:
            print(f"Error al ordenar: {e}")
            # Fallback: ordenar por nombre como respaldo
            productos_ordenados = sorted(self.productos, key=lambda x: str(x.get('nombre', '')).lower())
            self.actualizar_treeview_con_datos(productos_ordenados)
            messagebox.showwarning("Advertencia", "Error al ordenar, se aplicó ordenamiento por nombre")

    def ordenar_lista_productos(self, productos, columna, ascendente=True):
        """Ordenar lista de productos según columna y dirección"""
        try:
            if columna == 'id':
                return sorted(productos, 
                            key=lambda x: x.get('id', 0) or 0, 
                            reverse=not ascendente)
            
            elif columna in ['precio_venta', 'costo_compra']:
                return sorted(productos, 
                            key=lambda x: float(x.get(columna, 0) or 0), 
                            reverse=not ascendente)
            
            elif columna == 'stock':
                return sorted(productos, 
                            key=lambda x: int(x.get('stock', 0) or 0), 
                            reverse=not ascendente)
            
            elif columna == 'activo':
                return sorted(productos, 
                            key=lambda x: bool(x.get('activo', False)), 
                            reverse=not ascendente)
            
            elif columna == 'codigo':
                return sorted(productos, 
                            key=lambda x: str(x.get('sku', '')).lower(), 
                            reverse=not ascendente)
            
            elif columna in ['categoria', 'marca', 'proveedor']:
                return sorted(productos, 
                            key=lambda x: self.obtener_texto_relacion(x, columna).lower(), 
                            reverse=not ascendente)
            
            else:  # 'nombre' y otras columnas de texto
                return sorted(productos, 
                            key=lambda x: str(x.get(columna, '')).lower(), 
                            reverse=not ascendente)
                
        except Exception as e:
            print(f"Error en ordenamiento específico: {e}")
            # Fallback a ordenamiento por nombre
            return sorted(productos, key=lambda x: str(x.get('nombre', '')).lower())

    def obtener_texto_relacion(self, producto, tipo_relacion):
        """Obtener texto para relaciones (categoría, marca, proveedor)"""
        try:
            if tipo_relacion == 'categoria' and producto.get('categoria'):
                return self.obtener_nombre_por_id(self.categorias, producto['categoria']) or ''
            elif tipo_relacion == 'marca' and producto.get('marca'):
                return self.obtener_nombre_por_id(self.marcas, producto['marca']) or ''
            elif tipo_relacion == 'proveedor' and producto.get('proveedor'):
                return self.obtener_nombre_por_id(self.proveedores, producto['proveedor']) or ''
            return ''
        except:
            return ''

    def actualizar_indicadores_ordenamiento(self, columna_actual):
        """Actualizar indicadores visuales ▲ ▼ en los headers"""
        for col in self.tree['columns']:
            texto_actual = self.tree.heading(col)['text']
            # Remover indicadores existentes
            texto_limpio = texto_actual.replace(' ▲', '').replace(' ▼', '')
            
            if col == columna_actual:
                indicador = ' ▲' if self.direccion_orden else ' ▼'
                self.tree.heading(col, text=texto_limpio + indicador)
            else:
                self.tree.heading(col, text=texto_limpio)

    def cargar_productos(self, filtros=None):
        """Cargar lista de productos"""
        self.productos = self.manager.obtener_productos(filtros)
        
        # Aplicar ordenamiento actual si existe
        if self.columna_orden_actual:
            self.productos = self.ordenar_lista_productos(
                self.productos, 
                self.columna_orden_actual, 
                self.direccion_orden
            )
            self.actualizar_indicadores_ordenamiento(self.columna_orden_actual)
        
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
        """Actualizar el treeview con los productos actuales"""
        self.actualizar_treeview_con_datos(self.productos)

    def actualizar_treeview_con_datos(self, productos):
        """Actualizar treeview con lista específica de productos"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
   
        # Llenar con datos
        for producto in productos:
            estado_display = "Activo" if producto['activo'] else "Inactivo"
            categoria_nombre = self.obtener_nombre_por_id(self.categorias, producto.get('categoria'))
            marca_nombre = self.obtener_nombre_por_id(self.marcas, producto.get('marca'))
            proveedor_nombre = self.obtener_nombre_por_id(self.proveedores, producto.get('proveedor'))
       
            precio_venta = producto.get('precio_venta')
            costo_compra = producto.get('costo_compra')
           
            precio_venta_str = f"${float(precio_venta):.2f}" if precio_venta else ''
            costo_compra_str = f"${float(costo_compra):.2f}" if costo_compra else ''
       
            self.tree.insert('', tk.END, values=(
                producto['id'],
                producto['sku'] or '',
                producto['nombre'],
                precio_venta_str,
                costo_compra_str,
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
        self.foto_preview = None
        self.plano_url = None
        
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
       
        # Fila 5: Relaciones
        row5 = ttk.Frame(main_frame)
        row5.pack(fill=tk.X, pady=10)
       
        # Proveedor
        ttk.Label(row5, text="Proveedor:").pack(side=tk.LEFT)
        proveedor_frame = ttk.Frame(row5)
        proveedor_frame.pack(side=tk.LEFT, padx=(10, 20))
        proveedor_combo = ttk.Combobox(proveedor_frame, textvariable=self.proveedor_var, width=18)
        proveedor_combo['values'] = [prov['nombre'] for prov in self.proveedores if prov.get('activo', True)]
        proveedor_combo.pack(side=tk.LEFT)
       
        # Categoría
        ttk.Label(row5, text="Categoría:").pack(side=tk.LEFT)
        categoria_frame = ttk.Frame(row5)
        categoria_frame.pack(side=tk.LEFT, padx=(10, 20))
        categoria_combo = ttk.Combobox(categoria_frame, textvariable=self.categoria_var, width=18)
        categoria_combo['values'] = [cat['nombre'] for cat in self.categorias if cat.get('activo', True)]
        categoria_combo.pack(side=tk.LEFT)

        # Marca
        ttk.Label(row5, text="Marca:").pack(side=tk.LEFT)
        marca_frame = ttk.Frame(row5)
        marca_frame.pack(side=tk.LEFT, padx=(10, 0))
        marca_combo = ttk.Combobox(marca_frame, textvariable=self.marca_var, width=18)
        marca_combo['values'] = [marca['nombre'] for marca in self.marcas if marca.get('activo', True)]
        marca_combo.pack(side=tk.LEFT)
  
        # Fila 6: Estado
        row6 = ttk.Frame(main_frame)
        row6.pack(fill=tk.X, pady=10)
       
        ttk.Label(row6, text="Estado:*").pack(side=tk.LEFT)
        ttk.Checkbutton(row6, text="Activo", variable=self.activo_var).pack(side=tk.LEFT, padx=(10, 0))
   
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
        """Crear pestaña para gestión de archivos - VERSIÓN CORREGIDA"""
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
       
        # Frame para foto
        foto_frame = ttk.LabelFrame(main_frame, text="📷 Foto del Producto", padding="10")
        foto_frame.pack(fill=tk.BOTH, expand=True, pady=5)
       
        # Frame para preview de imagen
        self.preview_frame = ttk.Frame(foto_frame)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
       
        # Label para mostrar la imagen (inicialmente vacío)
        self.foto_preview_label = ttk.Label(self.preview_frame, text="No hay imagen seleccionada")
        self.foto_preview_label.pack(expand=True)
       
        # Frame para controles
        controls_frame = ttk.Frame(foto_frame)
        controls_frame.pack(fill=tk.X, pady=5)
       
        self.foto_label = ttk.Label(controls_frame, text="No se ha seleccionado foto")
        self.foto_label.pack(side=tk.LEFT, padx=5)
       
        ttk.Button(controls_frame, text="Seleccionar Foto", command=self.seleccionar_foto).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Eliminar Foto", command=self.eliminar_foto).pack(side=tk.LEFT, padx=5)
       
        # Frame para plano
        plano_frame = ttk.LabelFrame(main_frame, text="📄 Plano/Especificación", padding="10")
        plano_frame.pack(fill=tk.X, pady=5)
    
        # Label para información del plano
        self.plano_label = ttk.Label(plano_frame, text="No se ha seleccionado archivo")
        self.plano_label.pack(pady=5)
    
        # Frame para botones del plano
        plano_buttons_frame = ttk.Frame(plano_frame)
        plano_buttons_frame.pack(pady=5)
    
        ttk.Button(plano_buttons_frame, text="Seleccionar Plano", 
                command=self.seleccionar_plano).pack(side=tk.LEFT, padx=5)
        ttk.Button(plano_buttons_frame, text="Abrir Plano", 
                command=self.abrir_plano).pack(side=tk.LEFT, padx=5)
        ttk.Button(plano_buttons_frame, text="Eliminar Plano", 
                command=self.eliminar_plano).pack(side=tk.LEFT, padx=5)

    # ==============================
    # MÉTODOS PARA MANEJAR PLANOS
    # ==============================

    def abrir_plano(self):
        """Abrir el plano PDF existente - MÉTODO QUE FALTABA"""
        try:
            # Verificar si hay plano cargado
            if not hasattr(self, 'plano_url') and not self.plano_path:
                messagebox.showinfo("Información", "No hay ningún plano para abrir")
                return
            
            # Si hay un plano nuevo seleccionado (aún no guardado)
            if self.plano_path:
                self.abrir_archivo_local(self.plano_path)
                return
                
            # Si hay un plano existente en el servidor
            if hasattr(self, 'plano_url') and self.plano_url:
                # Descargar y abrir el plano
                self.descargar_y_abrir_plano(self.plano_url)
                
        except Exception as e:
            print(f"❌ Error abriendo plano: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el plano: {e}")

    def abrir_archivo_local(self, file_path):
        """Abrir archivo local con aplicación predeterminada"""
        try:
            import os
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
                
            print(f"✅ Abriendo archivo: {file_path}")
            
        except Exception as e:
            print(f"❌ Error abriendo archivo local: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

    def descargar_y_abrir_plano(self, url_plano):
        """Descargar plano desde URL y abrirlo"""
        try:
            import tempfile
            
            # Si es una URL relativa, construir la URL completa
            if url_plano.startswith('/'):
                from config import Config
                base_url = getattr(Config, 'BASE_URL', 'http://localhost:8000')
                url_plano = f"{base_url}{url_plano}"
            
            print(f"DEBUG - Descargando plano desde: {url_plano}")
            
            # Descargar el archivo usando APIClient para mantener autenticación
            client = APIClient()
            
            response = client.session.get(url_plano, timeout=30)
            if response.status_code == 200:
                # Determinar extensión del archivo
                content_type = response.headers.get('content-type', '')
                extension = '.pdf'  # Por defecto PDF
                if 'pdf' in content_type.lower():
                    extension = '.pdf'
                elif 'image' in content_type.lower():
                    extension = '.png'
                elif 'word' in content_type.lower():
                    extension = '.docx'
                
                # Crear archivo temporal
                with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
                    temp_file.write(response.content)
                    temp_path = temp_file.name
                
                # Abrir el archivo temporal
                self.abrir_archivo_local(temp_path)
                
                print(f"✅ Plano descargado y abierto: {temp_path}")
                
            else:
                messagebox.showerror("Error", f"No se pudo descargar el plano (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"❌ Error descargando plano: {e}")
            messagebox.showerror("Error", f"No se pudo descargar el plano: {e}")

    def seleccionar_plano(self):
        """Seleccionar archivo de plano"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Plano",
            filetypes=[
                ("PDF", "*.pdf"), 
                ("Documentos", "*.doc *.docx"), 
                ("Imágenes", "*.jpg *.jpeg *.png *.webp"),
                ("Archivos DWG", "*.dwg *.dxf"),
                ("Todos los archivos", "*.*")
            ]
        )
        if file_path:
            self.plano_path = file_path
            self.plano_label.config(text=os.path.basename(file_path))
            # Limpiar URL de plano existente si se selecciona uno nuevo
            self.plano_url = None

    def eliminar_plano(self):
        """Eliminar plano seleccionado"""
        self.plano_path = None
        self.plano_data = None
        self.plano_url = None
        self.plano_label.config(text="No se ha seleccionado archivo")

    # ==============================
    # MÉTODOS PARA FOTOS
    # ==============================

    def seleccionar_foto(self):
        """Seleccionar archivo de foto"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Foto",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("Todos los archivos", "*.*")
            ]
        )
        if file_path:
            self.foto_path = file_path
            self.foto_label.config(text=os.path.basename(file_path))
            self.mostrar_preview_foto(file_path)

    def mostrar_preview_foto(self, image_path):
        """Mostrar preview de la imagen seleccionada"""
        try:
            # Limpiar preview anterior
            for widget in self.preview_frame.winfo_children():
                widget.destroy()
            
            # Cargar y mostrar imagen usando ImageHelper
            photo = ImageHelper.create_tkinter_photo(image_path, max_size=(300, 300))
            
            if photo:
                self.foto_preview_label = ttk.Label(self.preview_frame, image=photo)
                self.foto_preview_label.image = photo
                self.foto_preview_label.pack(expand=True)
                
                # Mostrar información del formato
                formato = "WEBP" if ImageHelper.is_webp_format(image_path) else "Compatible"
                info_label = ttk.Label(self.preview_frame, 
                                     text=f"Formato: {formato} | Tamaño: 300x300px",
                                     font=("Arial", 8))
                info_label.pack()
            else:
                self.foto_preview_label = ttk.Label(self.preview_frame, 
                                                  text="❌ No se pudo cargar la imagen\nFormato no compatible")
                self.foto_preview_label.pack(expand=True)
                
        except Exception as e:
            print(f"Error mostrando preview: {e}")
            self.foto_preview_label = ttk.Label(self.preview_frame, 
                                              text="❌ Error al cargar la imagen")
            self.foto_preview_label.pack(expand=True)

    def eliminar_foto(self):
        """Eliminar foto seleccionada"""
        self.foto_path = None
        self.foto_data = None
        self.foto_label.config(text="No se ha seleccionado foto")
        
        # Limpiar preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        self.foto_preview_label = ttk.Label(self.preview_frame, text="No hay imagen seleccionada")
        self.foto_preview_label.pack(expand=True)

    # ==============================
    # MÉTODO GUARDAR
    # ==============================

    def guardar(self):
        """Guardar producto - USANDO MULTIPART/FORM-DATA"""
        if not self.validar_formulario():
            return

        # Preparar datos básicos
        datos = {
            'nombre': self.nombre_var.get().strip(),
            'costo_compra': float(self.costo_compra_var.get().strip()),
            'precio_venta': float(self.precio_venta_var.get().strip()),
            'stock': int(self.stock_var.get()) if self.stock_var.get() else 0,
            'activo': self.activo_var.get()
        }

        # Campos opcionales
        codigo = self.codigo_var.get().strip()
        if codigo:
            datos['sku'] = codigo
        elif self.es_nuevo:
            datos['sku'] = None

        codigo_barras = self.codigo_barras_var.get().strip()
        if codigo_barras and codigo_barras != "None":
            datos['codigo_barras'] = codigo_barras
        else:
            datos['codigo_barras'] = ""

        descripcion = self.descripcion_text.get('1.0', tk.END).strip()
        if descripcion:
            datos['descripcion'] = descripcion
        else:
            datos['descripcion'] = ""

        # Manejar relaciones
        if self.proveedor_var.get():
            proveedor_id = next((prov['id'] for prov in self.proveedores
                        if prov['nombre'] == self.proveedor_var.get()), None)
            if proveedor_id:
                datos['proveedor'] = proveedor_id
        else:
            datos['proveedor'] = None

        if self.categoria_var.get():
            categoria_id = next((cat['id'] for cat in self.categorias
                        if cat['nombre'] == self.categoria_var.get()), None)
            if categoria_id:
                datos['categoria'] = categoria_id
        else:
            datos['categoria'] = None

        if self.marca_var.get():
            marca_id = next((marca['id'] for marca in self.marcas
                    if marca['nombre'] == self.marca_var.get()), None)
            if marca_id:
                datos['marca'] = marca_id
        else:
            datos['marca'] = None

        # Agregar impuestos seleccionados
        if self.impuestos_seleccionados:
            datos['productoimpuesto_set'] = json.dumps([
                {
                    'impuesto_id': imp_sel['impuesto_id'],
                    'tipo': imp_sel['tipo']
                }
                for imp_sel in self.impuestos_seleccionados
            ])

        print(f"DEBUG - Datos a enviar: {datos}")

        # PREPARAR ARCHIVOS
        files = {}
        
        # Procesar foto
        if self.foto_path:
            try:
                files['foto'] = (
                    os.path.basename(self.foto_path),
                    open(self.foto_path, 'rb'),
                    'image/jpeg'
                )
            except Exception as e:
                print(f"❌ Error cargando foto: {e}")
                messagebox.showerror("Error", f"No se pudo cargar la foto: {e}")
                return

        # Procesar plano
        if self.plano_path:
            try:
                files['plano'] = (
                    os.path.basename(self.plano_path),
                    open(self.plano_path, 'rb'),
                    'application/octet-stream'
                )
            except Exception as e:
                print(f"❌ Error cargando plano: {e}")
                messagebox.showerror("Error", f"No se pudo cargar el plano: {e}")
                return

        # Llamar al manager
        manager = ProductosManager()
        if self.es_nuevo:
            resultado = manager.crear_producto(datos, files if files else None)
        else:
            resultado = manager.actualizar_producto(self.producto_data['id'], datos, files if files else None)

        # Cerrar archivos después de enviarlos
        for file_tuple in files.values():
            file_tuple[1].close()

        if resultado:
            self.productos_window.cargar_productos()
            self.window.destroy()
        else:
            messagebox.showerror("Error", "No se pudo guardar el producto. Verifique los datos e intente nuevamente.")

    # ==============================
    # MÉTODOS PARA CARGAR DATOS EXISTENTES
    # ==============================

    def cargar_datos(self):
        """Cargar datos del producto en el formulario"""
        if not self.producto_data:
            return
        
        self.codigo_var.set(self.producto_data.get('sku', ''))
        
        codigo_barras = self.producto_data.get('codigo_barras')
        if codigo_barras is None:
            self.codigo_barras_var.set('')
        else:
            self.codigo_barras_var.set(codigo_barras)
    
        self.nombre_var.set(self.producto_data.get('nombre', ''))
        
        # Limpiar descripción antes de insertar
        self.descripcion_text.delete('1.0', tk.END)
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

        # CARGAR FOTO EXISTENTE
        self.cargar_foto_existente()
        
        # CARGAR PLANO EXISTENTE
        self.cargar_plano_existente()

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

    def cargar_foto_existente(self):
        """Cargar y mostrar la foto existente del producto"""
        try:
            foto_url = self.producto_data.get('foto_url')
            
            if not foto_url:
                self.foto_label.config(text="No hay foto cargada")
                self.limpiar_preview_foto()
                return
                
            print(f"DEBUG - Foto URL: {foto_url}")
            self.foto_label.config(text="Foto cargada desde servidor")
            
            # Mostrar preview de la foto existente
            self.mostrar_preview_desde_url(foto_url)
                
        except Exception as e:
            print(f"❌ Error cargando foto existente: {e}")
            self.foto_label.config(text="Error cargando foto")
            self.limpiar_preview_foto()

    def cargar_plano_existente(self):
        """Cargar y mostrar información del plano existente"""
        try:
            # El backend devuelve la URL del plano en el campo 'plano'
            plano_url = self.producto_data.get('plano')
            
            if not plano_url:
                self.plano_label.config(text="No se ha seleccionado archivo")
                return
                
            print(f"DEBUG - Plano URL: {plano_url}")
            
            # Guardar URL para poder abrirla después
            self.plano_url = plano_url
            
            # Mostrar nombre del archivo
            nombre_archivo = plano_url.split('/')[-1] if '/' in plano_url else "Plano"
            self.plano_label.config(text=f"📄 {nombre_archivo} (listo para descargar)")
                
        except Exception as e:
            print(f"❌ Error cargando plano existente: {e}")
            self.plano_label.config(text="❌ Error cargando plano")

    def mostrar_preview_desde_url(self, url_foto):
        """Mostrar preview de foto desde URL"""
        try:
            # Descargar imagen
            client = APIClient()
            response = client.session.get(url_foto, timeout=10)
            
            if response.status_code == 200:
                # Crear imagen desde los datos descargados
                from io import BytesIO
                image_data = BytesIO(response.content)
                self.mostrar_preview_desde_bytes(image_data, "Foto del producto")
            else:
                print(f"❌ Error HTTP {response.status_code} al descargar foto")
                self.limpiar_preview_foto()
                
        except Exception as e:
            print(f"❌ Error descargando foto: {e}")
            self.limpiar_preview_foto()

    def mostrar_preview_desde_bytes(self, image_buffer, descripcion):
        """Mostrar preview desde buffer de imagen"""
        try:
            # Limpiar preview anterior
            self.limpiar_preview_foto()
            
            # Cargar y mostrar imagen usando ImageHelper
            from image_helper import ImageHelper
            photo = ImageHelper.create_tkinter_photo_from_bytes(image_buffer, max_size=(300, 300))
            
            if photo:
                self.foto_preview_label = ttk.Label(self.preview_frame, image=photo)
                self.foto_preview_label.image = photo
                self.foto_preview_label.pack(expand=True)
                
                info_label = ttk.Label(self.preview_frame,
                                    text=f"{descripcion} | Tamaño: 300x300px",
                                    font=("Arial", 8))
                info_label.pack()
            else:
                error_label = ttk.Label(self.preview_frame,
                                      text="❌ No se pudo cargar la imagen",
                                      justify=tk.CENTER)
                error_label.pack(expand=True)
                
        except Exception as e:
            print(f"❌ Error mostrando preview desde bytes: {e}")
            error_label = ttk.Label(self.preview_frame,
                                  text="❌ Error al cargar la imagen",
                                  justify=tk.CENTER)
            error_label.pack(expand=True)

    def limpiar_preview_foto(self):
        """Limpiar el área de preview de foto"""
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        self.foto_preview_label = ttk.Label(self.preview_frame, text="No hay imagen seleccionada")
        self.foto_preview_label.pack(expand=True)

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