# /app_escritorio/presupuestos_window.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from presupuestos_manager import PresupuestosManager
from clientes_manager import ClientesManager
from productos_manager import ProductosManager
from servicios_manager import ServiciosManager
import os
from PIL import Image, ImageTk
from presupuestos_formulario import FormularioPresupuesto
from pdf_generator import generar_presupuesto_pdf
from dialogo_adjunto import DialogoAdjunto  # 👈 IMPORT CORRECTO




class PresupuestosWindow:
    def __init__(self, parent):
        self.parent = parent
        self.manager = PresupuestosManager()
        self.clientes_manager = ClientesManager()
        self.productos_manager = ProductosManager()
        self.servicios_manager = ServiciosManager()
       
        self.presupuestos = []
        self.clientes = []
        self.productos = []
        self.servicios = []
        self.presupuesto_seleccionado = None
       
        # Variables para ordenamiento
        self.sort_column = None
        self.sort_reverse = False
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Presupuestos - Lab Servicios")
       
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
        self.cliente_filter_var = tk.StringVar(self.window)
        self.estado_filter_var = tk.StringVar(self.window)
       
        self.create_widgets()
        self.cargar_datos_combobox()
        self.cargar_presupuestos()


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
            self.clientes = self.clientes_manager.obtener_clientes()
            self.productos = self.productos_manager.obtener_productos()
            self.servicios = self.servicios_manager.obtener_servicios()
           
            # Filtrar solo activos
            self.clientes = [c for c in self.clientes if c.get('activo', True)]
            self.productos = [p for p in self.productos if p.get('activo', True)]
            self.servicios = [s for s in self.servicios if s.get('activo', True)]
           
        except Exception as e:
            print(f"Error cargando datos para combobox: {e}")
            self.clientes = []
            self.productos = []
            self.servicios = []


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
        self.search_entry.bind('<KeyRelease>', self.buscar_presupuestos)
       
        # Filtros
        ttk.Label(search_frame, text="Cliente:").pack(side=tk.LEFT, padx=(20, 5))
        self.cliente_filter = ttk.Combobox(
            search_frame,
            textvariable=self.cliente_filter_var,
            state="readonly",
            width=20
        )
        self.cliente_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.cliente_filter.bind('<<ComboboxSelected>>', self.aplicar_filtros)
       
        ttk.Label(search_frame, text="Estado:").pack(side=tk.LEFT, padx=(20, 5))
        self.estado_filter = ttk.Combobox(
            search_frame,
            textvariable=self.estado_filter_var,
            values=["Todos", "Borrador", "Enviado", "Aceptado", "Rechazado", "Anulado"],
            state="readonly",
            width=12
        )
        self.estado_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.estado_filter.bind('<<ComboboxSelected>>', self.aplicar_filtros)
       
        # Botones
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(side=tk.RIGHT)
       
        ttk.Button(button_frame, text="➕ Nuevo Presupuesto", 
                  command=self.nuevo_presupuesto).pack(side=tk.LEFT, padx=5)
```python
# /app_escritorio/presupuestos_window.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from presupuestos_manager import PresupuestosManager
from clientes_manager import ClientesManager
from productos_manager import ProductosManager
from servicios_manager import ServiciosManager
import os
from PIL import Image, ImageTk
from presupuestos_formulario import FormularioPresupuesto
from pdf_generator import generar_presupuesto_pdf
from dialogo_adjunto import DialogoAdjunto  # 👈 IMPORT CORRECTO




class PresupuestosWindow:
    def __init__(self, parent):
        self.parent = parent
        self.manager = PresupuestosManager()
        self.clientes_manager = ClientesManager()
        self.productos_manager = ProductosManager()
        self.servicios_manager = ServiciosManager()
       
        self.presupuestos = []
        self.clientes = []
        self.productos = []
        self.servicios = []
        self.presupuesto_seleccionado = None
       
        # Variables para ordenamiento
        self.sort_column = None
        self.sort_reverse = False
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Presupuestos - Lab Servicios")
       
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
        self.cliente_filter_var = tk.StringVar(self.window)
        self.estado_filter_var = tk.StringVar(self.window)
       
        self.create_widgets()
        self.cargar_datos_combobox()
        self.cargar_presupuestos()


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
            self.clientes = self.clientes_manager.obtener_clientes()
            self.productos = self.productos_manager.obtener_productos()
            self.servicios = self.servicios_manager.obtener_servicios()
           
            # Filtrar solo activos
            self.clientes = [c for c in self.clientes if c.get('activo', True)]
            self.productos = [p for p in self.productos if p.get('activo', True)]
            self.servicios = [s for s in self.servicios if s.get('activo', True)]
           
        except Exception as e:
            print(f"Error cargando datos para combobox: {e}")
            self.clientes = []
            self.productos = []
            self.servicios = []


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
        self.search_entry.bind('<KeyRelease>', self.buscar_presupuestos)
       
        # Filtros
        ttk.Label(search_frame, text="Cliente:").pack(side=tk.LEFT, padx=(20, 5))
        self.cliente_filter = ttk.Combobox(
            search_frame,
            textvariable=self.cliente_filter_var,
            state="readonly",
            width=20
        )
        self.cliente_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.cliente_filter.bind('<<ComboboxSelected>>', self.aplicar_filtros)
       
        ttk.Label(search_frame, text="Estado:").pack(side=tk.LEFT, padx=(20, 5))
        self.estado_filter = ttk.Combobox(
            search_frame,
            textvariable=self.estado_filter_var,
            values=["Todos", "Borrador", "Enviado", "Aceptado", "Rechazado", "Anulado"],
            state="readonly",
            width=12
        )
        self.estado_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.estado_filter.bind('<<ComboboxSelected>>', self.aplicar_filtros)
       
        # Botones
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(side=tk.RIGHT)
       
        ttk.Button(button_frame, text="➕ Nuevo Presupuesto", 
                  command=self.nuevo_presupuesto).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Editar", 
                  command=self.editar_presupuesto).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📎 Adjuntos", 
                  command=self.gestionar_adjuntos).pack(side=tk.LEFT, padx=2)  # 👈 NUEVO BOTÓN
        ttk.Button(button_frame, text="🖨️ PDF", 
                  command=self.generar_pdf).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🚫 Anular", 
                  command=self.anular_presupuesto).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Recargar", 
                  command=self.cargar_presupuestos).pack(side=tk.LEFT, padx=5)
       
        # Treeview para lista de presupuestos
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
       
        columns = ('id', 'numero', 'cliente', 'fecha', 'subtotal', 'iva', 'total', 'estado')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
       
        # Configurar columnas con bindings para ordenamiento
        column_configs = [
            ('id', 'ID', 50),
            ('numero', 'Número', 80),
            ('cliente', 'Cliente', 200),
            ('fecha', 'Fecha', 100),
            ('subtotal', 'Subtotal', 80),
            ('iva', 'IVA', 80),
            ('total', 'Total', 90),
            ('estado', 'Estado', 90)
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
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_presupuesto)
        self.tree.bind('<Double-1>', lambda e: self.ver_detalle())


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
        if column in ['subtotal', 'iva', 'total']:
            # Ordenar como moneda (remover $ y convertir a float)
            items.sort(key=lambda x: float(x[0].replace('$', '').replace(',', '')), reverse=self.sort_reverse)
        elif column == 'numero':
            # Ordenar como número
            items.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0, reverse=self.sort_reverse)
        elif column == 'fecha':
            # Ordenar como fecha (formato YYYY-MM-DD)
            items.sort(key=lambda x: x[0], reverse=self.sort_reverse)
        elif column == 'id':
            # Ordenar como número
            items.sort(key=lambda x: int(x[0]), reverse=self.sort_reverse)
        else:
            # Ordenar como texto
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


    def cargar_presupuestos(self, filtros=None):
        """Cargar lista de presupuestos"""
        try:
            self.presupuestos = self.manager.obtener_presupuestos(filtros)
            self.actualizar_treeview()
            self.actualizar_filtros_combobox()
        except Exception as e:
            print(f"Error cargando presupuestos: {e}")
            self.presupuestos = []
            self.actualizar_treeview()


    def actualizar_filtros_combobox(self):
        """Actualizar los combobox de filtros con datos actualizados"""
        # Clientes
        clientes_nombres = ["Todos"] + [self.obtener_nombre_cliente(cliente_id) for cliente_id in
                                      list(set([p.get('cliente') for p in self.presupuestos if p.get('cliente')]))]
        self.cliente_filter['values'] = clientes_nombres


    def obtener_nombre_cliente(self, cliente_id):
        """Obtener nombre del cliente por ID"""
        for cliente in self.clientes:
            if cliente['id'] == cliente_id:
                if cliente['tipo'] == 'fisica':
                    return f"{cliente['nombre']} {cliente['apellido'] or ''}".strip()
                else:
                    return cliente['nombre']
        return "Cliente no encontrado"


    def actualizar_treeview(self):
        """Actualizar el treeview con los presupuestos"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
   
        # Llenar con datos
        for presupuesto in self.presupuestos:
            cliente_nombre = self.obtener_nombre_cliente(presupuesto.get('cliente'))
            fecha = presupuesto.get('fecha', '').split('T')[0] if presupuesto.get('fecha') else ''
           
            # Formatear montos
            subtotal_str = f"${float(presupuesto.get('subtotal', 0)):.2f}" if presupuesto.get('subtotal') else '$0.00'
            iva_str = f"${float(presupuesto.get('iva_valor', 0)):.2f}" if presupuesto.get('iva_valor') else '$0.00'
            total_str = f"${float(presupuesto.get('total', 0)):.2f}" if presupuesto.get('total') else '$0.00'
           
            # Mapear estado a español
            estado_map = {
                'borrador': 'Borrador',
                'enviado': 'Enviado',
                'aceptado': 'Aceptado',
                'rechazado': 'Rechazado',
                'anulado': '🚫 Anulado'
            }
            estado_display = estado_map.get(presupuesto.get('estado', 'borrador'), 'Borrador')
   
            self.tree.insert('', tk.END, values=(
                presupuesto['id'],
                presupuesto.get('numero', ''),
                cliente_nombre,
                fecha,
                subtotal_str,
                iva_str,
                total_str,
                estado_display
            ))
       
        # Restaurar ordenamiento si existe
        if self.sort_column:
            self.ordenar_columnas(self.sort_column)


    def seleccionar_presupuesto(self, event):
        """Manejar selección de presupuesto"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            presupuesto_id = item['values'][0]
            self.presupuesto_seleccionado = next(
                (p for p in self.presupuestos if p['id'] == presupuesto_id), None
            )


    def buscar_presupuestos(self, event=None):
        """Buscar presupuestos en tiempo real"""
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
       
        # Filtro de cliente
        cliente_seleccionado = self.cliente_filter_var.get()
        if cliente_seleccionado != "Todos":
            # Buscar ID del cliente por nombre
            for cliente in self.clientes:
                nombre_cliente = f"{cliente['nombre']} {cliente['apellido'] or ''}".strip() if cliente['tipo'] == 'fisica' else cliente['nombre']
                if nombre_cliente == cliente_seleccionado:
                    filtros['cliente'] = cliente['id']
                    break
       
        # Filtro de estado
        estado_seleccionado = self.estado_filter_var.get()
        if estado_seleccionado != "Todos":
            estado_map_inverso = {
                'Borrador': 'borrador',
                'Enviado': 'enviado',
                'Aceptado': 'aceptado',
                'Aceptado': 'aceptado',
                'Rechazado': 'rechazado',
            messagebox.showwarning("Advertencia", "Seleccione un presupuesto")
            return
       
        try:
            # Obtener datos del cliente
            cliente_id = self.presupuesto_seleccionado.get('cliente')
            cliente_data = None
            for cliente in self.clientes:
                if cliente['id'] == cliente_id:
                    cliente_data = cliente
                    break
           
            if not cliente_data:
                messagebox.showerror("Error", "No se pudo obtener información del cliente")
                return
           
            # Generar PDF
            pdf_path = generar_presupuesto_pdf(self.presupuesto_seleccionado, cliente_data)
           
            if pdf_path:
                messagebox.showinfo("Éxito", f"PDF generado:\n{pdf_path}")
            else:
                messagebox.showerror("Error", "No se pudo generar el PDF")
               
        except ImportError as e:
            messagebox.showerror("Error", f"Error al importar generador PDF: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error generando PDF: {e}")


    def ver_detalle(self):
        """Ver detalle del presupuesto seleccionado (solo lectura)"""
        if not self.presupuesto_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un presupuesto para ver el detalle")
            return
       
        FormularioPresupuesto(self.window, self, self.presupuesto_seleccionado, solo_lectura=True)


    def gestionar_adjuntos(self):
        """Abrir ventana de gestión de adjuntos"""
        if not self.presupuesto_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un presupuesto")
            return
       
        # 👈 USANDO IMPORT CORRECTO
        DialogoAdjunto(self.window, self.manager, self.presupuesto_seleccionado['id'])