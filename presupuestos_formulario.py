# /app_escritorio/presupuestos_formulario.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from configuracion_manager import ConfiguracionManager
from presupuestos_manager import PresupuestosManager
from clientes_manager import ClientesManager
from productos_manager import ProductosManager
from servicios_manager import ServiciosManager
import os
from decimal import Decimal
from datetime import datetime, timedelta

# 🔥 IMPORTAR CALENDARIO
try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
    print("✅ tkcalendar disponible - Usando calendario gráfico")
except ImportError:
    CALENDAR_AVAILABLE = False
    print("⚠️ tkcalendar no disponible. Usando campo de texto para fechas.")


class DialogoSeleccionProducto:
    """Diálogo para seleccionar producto y cantidad"""
    def __init__(self, parent, productos):
        self.parent = parent
        self.productos = productos
        self.resultado = None
       
    def mostrar(self):
        self.dialogo = tk.Toplevel(self.parent)
        self.dialogo.title("Seleccionar Producto")
        self.dialogo.geometry("400x200")
        self.dialogo.transient(self.parent)
        self.dialogo.grab_set()
       
        # Variables
        self.producto_var = tk.StringVar()
        self.cantidad_var = tk.StringVar(value="1")
       
        # Widgets
        ttk.Label(self.dialogo, text="Producto:").pack(pady=5)
        producto_combo = ttk.Combobox(self.dialogo, textvariable=self.producto_var, width=50)
        producto_combo['values'] = [f"{p['sku'] or 'NO-SKU'} - {p['nombre']}" for p in self.productos]
        producto_combo.pack(pady=5)
       
        ttk.Label(self.dialogo, text="Cantidad:").pack(pady=5)
        ttk.Entry(self.dialogo, textvariable=self.cantidad_var, width=10).pack(pady=5)
       
        button_frame = ttk.Frame(self.dialogo)
        button_frame.pack(pady=10)
       
        ttk.Button(button_frame, text="Aceptar", command=self.aceptar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.cancelar).pack(side=tk.LEFT, padx=5)
       
        self.dialogo.wait_window()
        return self.resultado
   
    def aceptar(self):
        try:
            producto_texto = self.producto_var.get()
            cantidad = int(self.cantidad_var.get())
           
            if not producto_texto or cantidad <= 0:
                messagebox.showwarning("Advertencia", "Seleccione un producto y cantidad válida")
                return
           
            # Buscar producto
            for producto in self.productos:
                producto_str = f"{producto['sku'] or 'NO-SKU'} - {producto['nombre']}"
                if producto_str == producto_texto:
                    self.resultado = (producto, cantidad)
                    break
           
            self.dialogo.destroy()
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero")
   
    def cancelar(self):
        self.dialogo.destroy()


class DialogoSeleccionServicio:
    """Diálogo para seleccionar servicio y cantidad"""
    def __init__(self, parent, servicios):
        self.parent = parent
        self.servicios = servicios
        self.resultado = None
       
    def mostrar(self):
        self.dialogo = tk.Toplevel(self.parent)
        self.dialogo.title("Seleccionar Servicio")
        self.dialogo.geometry("400x200")
        self.dialogo.transient(self.parent)
        self.dialogo.grab_set()
       
        # Variables
        self.servicio_var = tk.StringVar()
        self.cantidad_var = tk.StringVar(value="1")
       
        # Widgets
        ttk.Label(self.dialogo, text="Servicio:").pack(pady=5)
        servicio_combo = ttk.Combobox(self.dialogo, textvariable=self.servicio_var, width=50)
        servicio_combo['values'] = [f"{s['codigo_interno'] or 'NO-CODE'} - {s['nombre']}" for s in self.servicios]
        servicio_combo.pack(pady=5)
       
        ttk.Label(self.dialogo, text="Cantidad:").pack(pady=5)
        ttk.Entry(self.dialogo, textvariable=self.cantidad_var, width=10).pack(pady=5)
       
        button_frame = ttk.Frame(self.dialogo)
        button_frame.pack(pady=10)
       
        ttk.Button(button_frame, text="Aceptar", command=self.aceptar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.cancelar).pack(side=tk.LEFT, padx=5)
       
        self.dialogo.wait_window()
        return self.resultado
   
    def aceptar(self):
        try:
            servicio_texto = self.servicio_var.get()
            cantidad = int(self.cantidad_var.get())
           
            if not servicio_texto or cantidad <= 0:
                messagebox.showwarning("Advertencia", "Seleccione un servicio y cantidad válida")
                return
           
            # Buscar servicio
            for servicio in self.servicios:
                servicio_str = f"{servicio['codigo_interno'] or 'NO-CODE'} - {servicio['nombre']}"
                if servicio_str == servicio_texto:
                    self.resultado = (servicio, cantidad)
                    break
           
            self.dialogo.destroy()
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero")
   
    def cancelar(self):
        self.dialogo.destroy()


class FormularioPresupuesto:
    def __init__(self, parent, presupuestos_window, presupuesto_data, solo_lectura=False):
        print(f"🚀 INICIANDO FORMULARIO PRESUPUESTO - Modo: {'SOLO LECTURA' if solo_lectura else 'EDICIÓN'}")
        
        self.parent = parent
        self.presupuestos_window = presupuestos_window
        self.presupuesto_data = presupuesto_data
        self.es_nuevo = presupuesto_data is None
        self.solo_lectura = solo_lectura
       
        # ✅ INICIALIZAR MANAGERS
        self.manager = PresupuestosManager()
        self.clientes_manager = ClientesManager()
        self.productos_manager = ProductosManager()
        self.servicios_manager = ServiciosManager()
        self.config_manager = ConfiguracionManager()
       
        self.clientes = []
        self.productos = []
        self.servicios = []
        self.items_presupuesto = []
       
        # ✅ CREAR VENTANA
        self.window = tk.Toplevel(parent)
        self.window.title("Ver Presupuesto" if solo_lectura else
                         "Nuevo Presupuesto" if self.es_nuevo else "Editar Presupuesto")
        self.window.geometry("900x700")
        self.window.transient(parent)
        self.window.grab_set()
       
        self.center_window(900, 700)
        
        # ✅ OBTENER CONFIGURACIÓN GLOBAL PRIMERO
        print("🔄 Obteniendo configuración global desde Django...")
        self.config_presupuestos = self.config_manager.obtener_config_presupuestos()
        print(f"✅ Configuración obtenida: {self.config_presupuestos}")
       
        # ✅ INICIALIZAR VARIABLES CON CONFIGURACIÓN GLOBAL
        self.cliente_var = tk.StringVar(self.window)
        self.observaciones_var = tk.StringVar(self.window)
        self.condiciones_var = tk.StringVar(self.window)
        
        # 🔥 USAR IVA DE CONFIGURACIÓN O VALOR POR DEFECTO
        iva_default = str(self.config_presupuestos.get('iva_por_defecto', 21.0))
        self.iva_var = tk.StringVar(self.window, value=iva_default)
        self.estado_var = tk.StringVar(self.window, value="borrador")
       
        # Variables para totales
        self.subtotal_var = tk.StringVar(self.window, value="$0.00")
        self.iva_valor_var = tk.StringVar(self.window, value="$0.00")
        self.total_var = tk.StringVar(self.window, value="$0.00")
       
        # 🔥 ORDEN CORREGIDO: Cargar datos PRIMERO
        self.cargar_datos_combobox()
        self.create_widgets()
       
        # ✅ CORRECCIÓN: CARGAR CONDICIONES POR DEFECTO PARA NUEVOS PRESUPUESTOS
        if self.es_nuevo:
            print("🆕 Configurando nuevo presupuesto con condiciones por defecto...")
            self.cargar_configuracion_por_defecto()
        else:
            print("📝 Cargando datos existentes del presupuesto...")
            self.cargar_datos()

    def obtener_nombre_cliente(self, cliente):
        """Obtener nombre completo del cliente según su tipo"""
        if not cliente:
            return "Cliente no disponible"
        
        if cliente.get('tipo') == 'fisica':
            # Persona física: Nombre + Apellido
            return f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}".strip()
        else:
            # Persona jurídica: Solo nombre (razón social)
            return cliente.get('nombre', 'Cliente sin nombre')

    def cargar_configuracion_por_defecto(self):
        """Cargar configuración por defecto desde Django - SOLO PARA NUEVOS"""
        try:
            if not self.es_nuevo:
                print("ℹ️ Presupuesto existente - No se carga configuración por defecto")
                return
                
            print("🔄 Aplicando configuración por defecto desde Django...")
            
            # Solo cargar fecha de validez para nuevos presupuestos
            dias_validez = self.config_presupuestos.get('dias_validez', 30)
            fecha_validez = datetime.now() + timedelta(days=dias_validez)

            print(f"📅 Configurando validez: {dias_validez} días desde hoy")

            if CALENDAR_AVAILABLE:
                self.valido_hasta_calendar.set_date(fecha_validez)
                print("✅ Fecha configurada en calendario")
            else:
                fecha_formateada = fecha_validez.strftime('%d/%m/%Y')
                self.valido_hasta_var.set(fecha_formateada)
                print(f"✅ Fecha configurada en campo: {fecha_formateada}")
            # ✅ CONDICIONES COMERCIALES DESDE CONFIGURACIÓN - PARA NUEVOS PRESUPUESTOS
            condiciones_default = self.config_presupuestos.get('condiciones_comerciales', '')
            
            print(f"📄 Condiciones por defecto a cargar: '{condiciones_default}'")
            
            if condiciones_default and condiciones_default.strip():
                self.condiciones_text.delete('1.0', tk.END)
                
                # Formatear correctamente para Tkinter
                condiciones_formateadas = condiciones_default.replace('\r\n', '\n')
                self.condiciones_text.insert('1.0', condiciones_formateadas)
                
                # DEBUG: Verificar qué se cargó
                contenido_cargado = self.condiciones_text.get('1.0', tk.END).strip()
                print(f"✅ Condiciones cargadas desde configuración: '{contenido_cargado}'")
            else:
                print("✅ Campo de condiciones dejado en blanco (no hay configuración)")
                
            print(f"🎯 Configuración aplicada: IVA {self.iva_var.get()}%, {dias_validez} días validez")
            
        except Exception as e:
            print(f"❌ Error cargando configuración por defecto: {e}")

    def center_window(self, width, height):
        """Centrar ventana en pantalla"""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def cargar_datos_combobox(self):
        """Cargar datos para los combobox"""
        try:
            print("🔄 Cargando datos para combobox...")
            self.clientes = self.clientes_manager.obtener_clientes()
            self.productos = self.productos_manager.obtener_productos()
            self.servicios = self.servicios_manager.obtener_servicios()
           
            # Filtrar solo activos
            self.clientes = [c for c in self.clientes if c.get('activo', True)]
            self.productos = [p for p in self.productos if p.get('activo', True)]
            self.servicios = [s for s in self.servicios if s.get('activo', True)]
           
            print(f"✅ Clientes cargados: {len(self.clientes)}")
            print(f"✅ Productos cargados: {len(self.productos)}") 
            print(f"✅ Servicios cargados: {len(self.servicios)}")
           
        except Exception as e:
            print(f"❌ Error cargando datos para combobox: {e}")
            self.clientes = []
            self.productos = []
            self.servicios = []

    def create_widgets(self):
        """Crear interfaz gráfica - VERSIÓN COMPLETA"""
        print("🎨 Creando interfaz gráfica...")
        
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
        # Cabecera del presupuesto
        header_frame = ttk.LabelFrame(main_frame, text="📋 Información del Presupuesto", padding="10")
        header_frame.pack(fill=tk.X, pady=(0, 10))
    
        # Fila 0: Cliente y Fecha de validez
        ttk.Label(header_frame, text="Cliente:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Combobox de clientes
        self.cliente_combo = ttk.Combobox(header_frame, textvariable=self.cliente_var, width=50, state="readonly")
        nombres_clientes = [self.obtener_nombre_cliente(c) for c in self.clientes]
        self.cliente_combo['values'] = nombres_clientes
        print(f"🔧 Combobox clientes cargado con {len(nombres_clientes)} opciones")        
        self.cliente_combo.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=(10, 0))
        
        # Fecha de validez
        ttk.Label(header_frame, text="Válido hasta:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        
        if CALENDAR_AVAILABLE:
            fecha_default = datetime.now() + timedelta(days=30)
            self.valido_hasta_calendar = DateEntry(
                header_frame,
                width=12,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/mm/yyyy',
                mindate=datetime.now(),
                year=fecha_default.year,
                month=fecha_default.month,
                day=fecha_default.day
            )
            self.valido_hasta_calendar.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(10, 0))
            print("✅ Calendario de fecha configurado")
        else:
            self.valido_hasta_var = tk.StringVar(self.window)
            fecha_default = (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')
            self.valido_hasta_var.set(fecha_default)
            self.valido_hasta_entry = ttk.Entry(header_frame, textvariable=self.valido_hasta_var, width=12)
            self.valido_hasta_entry.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(10, 0))
            ttk.Label(header_frame, text="(DD/MM/AAAA)", font=("Arial", 7)).grid(row=0, column=4, sticky=tk.W, pady=5, padx=(5, 0))
            print(f"✅ Campo de fecha configurado: {fecha_default}")

        # Fila 1: IVA y Estado
        ttk.Label(header_frame, text="% IVA:").grid(row=1, column=0, sticky=tk.W, pady=5)
        iva_entry = ttk.Entry(header_frame, textvariable=self.iva_var, width=10)
        iva_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        print(f"💰 Campo IVA configurado: {self.iva_var.get()}%")
        
        if not self.es_nuevo:
            ttk.Label(header_frame, text="Estado:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20, 0))
            estado_combo = ttk.Combobox(header_frame, textvariable=self.estado_var, width=15, state="readonly")
            estado_combo['values'] = ['borrador', 'enviado', 'aceptado', 'rechazado']
            estado_combo.grid(row=1, column=3, sticky=tk.W, pady=5, padx=(10, 0))
            print("✅ Selector de estado configurado")
    
        header_frame.columnconfigure(1, weight=1)
    
        # Frame para items
        items_frame = ttk.LabelFrame(main_frame, text="🛒 Ítems del Presupuesto", padding="10")
        items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
        # Toolbar para items
        items_toolbar = ttk.Frame(items_frame)
        items_toolbar.pack(fill=tk.X, pady=(0, 10))
    
        if not self.solo_lectura:
            ttk.Button(items_toolbar, text="➕ Agregar Producto",
                    command=self.agregar_producto).pack(side=tk.LEFT, padx=5)
            ttk.Button(items_toolbar, text="➕ Agregar Servicio",
                    command=self.agregar_servicio).pack(side=tk.LEFT, padx=5)
            ttk.Button(items_toolbar, text="🗑️ Eliminar Ítem",
                    command=self.eliminar_item).pack(side=tk.LEFT, padx=5)
            print("✅ Botones de items configurados")
    
        # Treeview para items
        columns = ('codigo', 'descripcion', 'cantidad', 'precio', 'subtotal')
        self.tree_items = ttk.Treeview(items_frame, columns=columns, show='headings', height=8)
    
        # Configurar columnas
        self.tree_items.heading('codigo', text='Código', anchor='center')
        self.tree_items.heading('descripcion', text='Descripción', anchor='center')
        self.tree_items.heading('cantidad', text='Cantidad', anchor='center')
        self.tree_items.heading('precio', text='Precio Unit.', anchor='center')
        self.tree_items.heading('subtotal', text='Subtotal', anchor='center')
    
        self.tree_items.column('codigo', width=100, anchor='center')
        self.tree_items.column('descripcion', width=250)
        self.tree_items.column('cantidad', width=70, anchor='center')
        self.tree_items.column('precio', width=90, anchor='e')
        self.tree_items.column('subtotal', width=90, anchor='e')
    
        # Scrollbar
        scrollbar_items = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.tree_items.yview)
        self.tree_items.configure(yscroll=scrollbar_items.set)
        scrollbar_items.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        if not self.solo_lectura:
            self.tree_items.bind('<Double-1>', self.editar_item)
    
        # Frame para observaciones y condiciones
        notes_frame = ttk.Frame(main_frame)
        notes_frame.pack(fill=tk.X, pady=(0, 10))
    
        # Observaciones
        obs_frame = ttk.LabelFrame(notes_frame, text="📝 Observaciones", padding="5")
        obs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.observaciones_text = tk.Text(obs_frame, width=40, height=4)
        self.observaciones_text.pack(fill=tk.BOTH, expand=True)
    
        # Condiciones comerciales
        cond_frame = ttk.LabelFrame(notes_frame, text="📄 Condiciones Comerciales", padding="5")
        cond_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self.condiciones_text = tk.Text(cond_frame, width=40, height=4)
        self.condiciones_text.pack(fill=tk.BOTH, expand=True)
        print("✅ Campos de texto configurados")
    
        # Frame para totales
        totals_frame = ttk.LabelFrame(main_frame, text="💰 Totales", padding="10")
        totals_frame.pack(fill=tk.X, pady=(0, 10))
    
        ttk.Label(totals_frame, text="Subtotal:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(totals_frame, textvariable=self.subtotal_var,
                font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W)
    
        ttk.Label(totals_frame, text="IVA:").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        ttk.Label(totals_frame, textvariable=self.iva_valor_var,
                font=("Arial", 10, "bold")).grid(row=0, column=3, sticky=tk.W)
    
        ttk.Label(totals_frame, text="TOTAL:").grid(row=0, column=4, sticky=tk.W, padx=(20, 10))
        ttk.Label(totals_frame, textvariable=self.total_var,
                font=("Arial", 12, "bold"), foreground="red").grid(row=0, column=5, sticky=tk.W)
        print("✅ Sección de totales configurada")
    
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
    
        if self.solo_lectura:
            ttk.Button(button_frame, text="⬅️ Volver",
                    command=self.window.destroy).pack(side=tk.LEFT, padx=5)
            print("✅ Modo solo lectura - Botón volver configurado")
        else:
            ttk.Button(button_frame, text="💾 Guardar Presupuesto",
                    command=self.guardar).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="📎 Adjuntos",
                    command=self.gestionar_adjuntos).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="❌ Cancelar",
                    command=self.window.destroy).pack(side=tk.LEFT, padx=5)
            print("✅ Botones de acción configurados")
    
        header_frame.columnconfigure(1, weight=1)
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.columnconfigure(1, weight=1)
        
        print("🎉 INTERFAZ GRÁFICA CREADA EXITOSAMENTE")

    def agregar_producto(self):
        """Abrir diálogo para agregar producto"""
        if not self.cliente_var.get():
            messagebox.showwarning("Advertencia", "Primero seleccione un cliente")
            return
       
        print("🛍️ Abriendo diálogo para agregar producto...")
        dialogo = DialogoSeleccionProducto(self.window, self.productos)
        resultado = dialogo.mostrar()
       
        if resultado:
            producto, cantidad = resultado
            item = {
                'producto': producto['id'],
                'servicio': None,
                'codigo': producto.get('sku', ''),
                'descripcion': producto['nombre'],
                'cantidad': cantidad,
                'precio_unitario': float(producto.get('precio_venta', 0))
            }
            self.items_presupuesto.append(item)
            self.agregar_item_a_treeview(item)
            self.actualizar_totales()
            print(f"✅ Producto agregado: {producto['nombre']} x{cantidad}")

    def agregar_servicio(self):
        """Abrir diálogo para agregar servicio"""
        if not self.cliente_var.get():
            messagebox.showwarning("Advertencia", "Primero seleccione un cliente")
            return
       
        print("🔧 Abriendo diálogo para agregar servicio...")
        dialogo = DialogoSeleccionServicio(self.window, self.servicios)
        resultado = dialogo.mostrar()
       
        if resultado:
            servicio, cantidad = resultado
            item = {
                'producto': None,
                'servicio': servicio['id'],
                'codigo': servicio.get('codigo_interno', ''),
                'descripcion': servicio['nombre'],
                'cantidad': cantidad,
                'precio_unitario': float(servicio.get('precio_base', 0))
            }
            self.items_presupuesto.append(item)
            self.agregar_item_a_treeview(item)
            self.actualizar_totales()
            print(f"✅ Servicio agregado: {servicio['nombre']} x{cantidad}")

    def eliminar_item(self):
        """Eliminar ítem seleccionado"""
        selection = self.tree_items.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un ítem para eliminar")
            return
       
        item_index = self.tree_items.index(selection[0])
        item_descripcion = self.items_presupuesto[item_index]['descripcion']
        self.tree_items.delete(selection[0])
        self.items_presupuesto.pop(item_index)
        self.actualizar_totales()
        print(f"🗑️ Ítem eliminado: {item_descripcion}")

    def editar_item(self, event):
        """Editar ítem seleccionado (cambiar cantidad o precio unitario)"""
        selection = self.tree_items.selection()
        if not selection:
            return
        
        item_index = self.tree_items.index(selection[0])
        item = self.items_presupuesto[item_index]
        
        # Determinar qué columna se hizo clic
        column = self.tree_items.identify_column(event.x)
        col_index = int(column.replace('#', '')) - 1
        
        print(f"✏️ Editando ítem: {item['descripcion']} - Columna: {col_index}")
        
        if col_index == 2:  # Columna de Cantidad (índice 2)
            print(f"📦 Editando cantidad del ítem: {item['descripcion']}")
            nueva_cantidad = simpledialog.askinteger(
                "Editar Cantidad",
                f"Ingrese la nueva cantidad para:\n{item['descripcion']}",
                initialvalue=item['cantidad'],
                minvalue=1
            )
            
            if nueva_cantidad and nueva_cantidad != item['cantidad']:
                item['cantidad'] = nueva_cantidad
                # Actualizar treeview
                self.tree_items.delete(selection[0])
                self.agregar_item_a_treeview(item)
                self.actualizar_totales()
                print(f"✅ Cantidad actualizada: {item['descripcion']} x{nueva_cantidad}")
        
        elif col_index == 3:  # Columna de Precio Unitario (índice 3)
            print(f"💰 Editando precio unitario del ítem: {item['descripcion']}")
            nuevo_precio = simpledialog.askfloat(
                "Editar Precio Unitario",
                f"Ingrese el nuevo precio unitario para:\n{item['descripcion']}",
                initialvalue=item['precio_unitario'],
                minvalue=0.0
            )
            
            if nuevo_precio is not None and nuevo_precio != item['precio_unitario']:
                item['precio_unitario'] = nuevo_precio
                # Actualizar treeview
                self.tree_items.delete(selection[0])
                self.agregar_item_a_treeview(item)
                self.actualizar_totales()
                print(f"✅ Precio actualizado: {item['descripcion']} - ${nuevo_precio:.2f}")
                
    def agregar_item_a_treeview(self, item):
        """Agregar un ítem al treeview"""
        codigo = item.get('codigo', '')
        descripcion = item.get('descripcion', '')
        
        # 🔥 MANEJO ROBUSTO DE CANTIDAD
        cantidad = item.get('cantidad', 1)
        if isinstance(cantidad, str):
            try:
                cantidad = int(cantidad)
            except (ValueError, TypeError):
                cantidad = 1
        
        # 🔥 MANEJO ROBUSTO DE PRECIO
        precio_unitario = item.get('precio_unitario', 0)
        if isinstance(precio_unitario, str):
            try:
                precio_unitario = float(precio_unitario)
            except (ValueError, TypeError):
                precio_unitario = 0.0
        
        subtotal = cantidad * precio_unitario
        
        self.tree_items.insert('', tk.END, values=(
            codigo,
            descripcion,
            cantidad,
            f"${precio_unitario:.2f}",
            f"${subtotal:.2f}"
        ))

    def actualizar_totales(self):
        """Calcular y actualizar totales"""
        subtotal = 0.0
        
        for item in self.items_presupuesto:
            # 🔥 MANEJO ROBUSTO DE TIPOS DE DATOS
            precio_unitario = item.get('precio_unitario', 0)
            cantidad = item.get('cantidad', 1)
            
            # Convertir a float si es string
            if isinstance(precio_unitario, str):
                try:
                    precio_unitario = float(precio_unitario)
                except (ValueError, TypeError):
                    precio_unitario = 0.0
            
            # Asegurar que cantidad sea entero
            if isinstance(cantidad, str):
                try:
                    cantidad = int(cantidad)
                except (ValueError, TypeError):
                    cantidad = 1
            
            subtotal += cantidad * precio_unitario
        
        # Calcular IVA y total
        try:
            iva_porcentaje = float(self.iva_var.get())
        except (ValueError, TypeError):
            iva_porcentaje = 21.0
        
        iva_valor = subtotal * (iva_porcentaje / 100)
        total = subtotal + iva_valor
        
        # Actualizar variables
        self.subtotal_var.set(f"${subtotal:.2f}")
        self.iva_valor_var.set(f"${iva_valor:.2f}")
        self.total_var.set(f"${total:.2f}")
        
        print(f"💰 Totales actualizados: Subtotal=${subtotal:.2f}, IVA=${iva_valor:.2f}, Total=${total:.2f}")

    def obtener_fecha_validez(self):
        """Obtener fecha de validez en formato YYYY-MM-DD para la API"""
        try:
            if CALENDAR_AVAILABLE:
                # Obtener fecha del calendario y convertir a YYYY-MM-DD
                fecha_obj = self.valido_hasta_calendar.get_date()
                fecha_api = fecha_obj.strftime('%Y-%m-%d')
                print(f"📅 Fecha para API (calendario): {fecha_api}")
                return fecha_api
            else:
                # Convertir de DD/MM/YYYY a YYYY-MM-DD
                fecha_str = self.valido_hasta_var.get()
                fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
                fecha_api = fecha_obj.strftime('%Y-%m-%d')
                print(f"📅 Fecha para API (texto): {fecha_api}")
                return fecha_api
        except Exception as e:
            print(f"❌ Error obteniendo fecha de validez: {e}")
            # Fecha por defecto: 30 días desde hoy
            fecha_default = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            return fecha_default

    def validar_fecha_validez(self):
        """Validar que la fecha de validez sea correcta"""
        try:
            if CALENDAR_AVAILABLE:
                # El calendario ya valida la fecha
                fecha_obj = self.valido_hasta_calendar.get_date()
                if fecha_obj < datetime.now().date():
                    messagebox.showerror("Error", "La fecha de validez no puede ser anterior a hoy")
                    return False
                return True
            else:
                # Validar formato DD/MM/YYYY
                fecha_str = self.valido_hasta_var.get()
                fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
                if fecha_obj.date() < datetime.now().date():
                    messagebox.showerror("Error", "La fecha de validez no puede ser anterior a hoy")
                    return False
                return True
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/YYYY")
            return False
        except Exception as e:
            print(f"Error validando fecha: {e}")
            return False

    def validar_formulario(self):
        """Validar datos del formulario"""
        if not self.cliente_var.get():
            messagebox.showerror("Error", "Debe seleccionar un cliente")
            return False
        
        if not self.items_presupuesto:
            messagebox.showerror("Error", "El presupuesto debe tener al menos un ítem")
            return False
        
        # Validar fecha de validez
        if not self.validar_fecha_validez():
            return False
        
        try:
            iva = float(self.iva_var.get())
            if iva < 0:
                messagebox.showerror("Error", "El IVA no puede ser negativo")
                return False
        except ValueError:
            messagebox.showerror("Error", "El IVA debe ser un número válido")
            return False
        
        return True

    def cargar_datos(self):
        """Cargar datos del presupuesto en el formulario - VERSIÓN CORREGIDA"""
        if not self.presupuesto_data:
            return
        
        print("🔍 Cargando datos del presupuesto existente...")
        
        # ✅ DEBUG: Verificar todos los campos disponibles
        print("🔍 CAMPOS DISPONIBLES en presupuesto_data:")
        for key, value in self.presupuesto_data.items():
            print(f"   {key}: {value}")
        
        # Cargar cliente
        cliente_id = self.presupuesto_data.get('cliente')
        cliente_encontrado = False
        for cliente in self.clientes:
            if cliente['id'] == cliente_id:
                self.cliente_var.set(self.obtener_nombre_cliente(cliente))
                cliente_encontrado = True
                print(f"✅ Cliente cargado: {self.obtener_nombre_cliente(cliente)}")
                break
        
        if not cliente_encontrado:
            print("⚠️ Cliente no encontrado en la lista local")
        
        # Cargar fecha de validez
        valido_hasta = self.presupuesto_data.get('valido_hasta')
        if valido_hasta:
            try:
                if 'T' in valido_hasta:
                    valido_hasta = valido_hasta.split('T')[0]
                
                fecha_obj = datetime.strptime(valido_hasta, '%Y-%m-%d')
                fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
                
                if CALENDAR_AVAILABLE:
                    self.valido_hasta_calendar.set_date(fecha_obj)
                    print(f"✅ Fecha configurada en calendario: {fecha_formateada}")
                else:
                    self.valido_hasta_var.set(fecha_formateada)
                    print(f"✅ Fecha configurada en campo: {fecha_formateada}")
                    
            except ValueError as e:
                print(f"⚠️ Error convirtiendo fecha: {e}")
                if not CALENDAR_AVAILABLE:
                    self.valido_hasta_var.set(valido_hasta)
        else:
            print("ℹ️ No hay fecha de validez definida")

        # Cargar estado
        estado = self.presupuesto_data.get('estado', 'borrador')
        self.estado_var.set(estado)
        print(f"✅ Estado cargado: {estado}")
        
        # Cargar observaciones
        observaciones = self.presupuesto_data.get('observaciones', '')
        self.observaciones_text.delete('1.0', tk.END)
        self.observaciones_text.insert('1.0', observaciones)
        print(f"✅ Observaciones cargadas: '{observaciones}'")
        
        # ✅ LÓGICA CORRECTA PARA CONDICIONES COMERCIALES - SOLO PARA PRESUPUESTOS EXISTENTES
        print("📄 CARGANDO CONDICIONES COMERCIALES:")
        print("   📝 Presupuesto EXISTENTE - Usando condiciones guardadas en BD")
        
        # Siempre usar las condiciones del presupuesto (aunque estén vacías)
        condiciones = self.presupuesto_data.get('condiciones_comerciales', '')
        print(f"   Valor en BD: '{condiciones}'")
        print(f"   Longitud: {len(condiciones)} caracteres")
        
        # DEBUG: Comparar con configuración global para verificar diferencia
        condiciones_config = self.config_presupuestos.get('condiciones_comerciales', '')
        print(f"   Valor en configuración global: '{condiciones_config}'")
        print(f"   ¿Son diferentes?: {condiciones != condiciones_config}")
        
        # Limpiar y cargar el widget
        self.condiciones_text.delete('1.0', tk.END)
        
        if condiciones and condiciones.strip():
            condiciones_formateadas = condiciones.replace('\r\n', '\n')
            self.condiciones_text.insert('1.0', condiciones_formateadas)
            print(f"   ✅ Cargadas {len(condiciones)} caracteres desde BD")
        else:
            print("   ✅ Campo dejado vacío (sin condiciones en BD o están vacías)")
        
        # DEBUG final
        contenido_cargado = self.condiciones_text.get('1.0', tk.END).strip()
        print(f"   📄 Contenido final en widget: '{contenido_cargado}'")

        # Cargar items
        self.items_presupuesto = []
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)
        
        if 'items' in self.presupuesto_data:
            items_data = self.presupuesto_data['items']
            print(f"📋 Items encontrados: {len(items_data)}")
            
            for i, item in enumerate(items_data):
                print(f"   Ítem {i}: {item.get('descripcion', 'Sin descripción')}")
                
                # CONVERTIR PRECIOS A FLOAT
                item_data = item.copy()
                if 'precio_unitario' in item_data:
                    precio = item_data['precio_unitario']
                    if isinstance(precio, str):
                        try:
                            item_data['precio_unitario'] = float(precio)
                            print(f"      Precio convertido a float: {item_data['precio_unitario']}")
                        except (ValueError, TypeError) as e:
                            item_data['precio_unitario'] = 0.0
                            print(f"      ⚠️  Precio convertido a 0.0 por error: {e}")
                    else:
                        print(f"      Precio ya es numérico: {precio}")
                
                # Asegurar que cantidad sea entero
                if 'cantidad' in item_data:
                    cantidad = item_data['cantidad']
                    if isinstance(cantidad, str):
                        try:
                            item_data['cantidad'] = int(cantidad)
                        except (ValueError, TypeError):
                            item_data['cantidad'] = 1
                
                self.items_presupuesto.append(item_data)
                self.agregar_item_a_treeview(item_data)
        else:
            print("ℹ️ No hay items en el presupuesto")
        
        # Actualizar totales
        self.actualizar_totales()
        print("✅ Datos cargados exitosamente")
            

    def gestionar_adjuntos(self):
        """Abrir gestión de adjuntos desde el formulario"""
        from dialogo_adjunto import DialogoAdjunto
        presupuesto_id = self.presupuesto_data['id'] if self.presupuesto_data else None
        if presupuesto_id:
            print(f"🔧 Abriendo diálogo de adjuntos para presupuesto ID: {presupuesto_id}")
            dialogo = DialogoAdjunto(self.window, self.manager, presupuesto_id)
        else:
            messagebox.showwarning("Advertencia", "Guarde el presupuesto primero para agregar adjuntos")

    def guardar(self):
        """Guardar presupuesto - VERSIÓN CORREGIDA CON IDs PRESERVADOS"""
        print("💾 Iniciando proceso de guardado...")
        
        if not self.validar_formulario():
            print("❌ Validación de formulario falló")
            return
        
        # Obtener ID del cliente
        cliente_nombre = self.cliente_var.get()
        cliente_id = None
        for cliente in self.clientes:
            nombre_completo = self.obtener_nombre_cliente(cliente)
            if nombre_completo == cliente_nombre:
                cliente_id = cliente['id']
                break
        
        if not cliente_id:
            messagebox.showwarning("Advertencia", "Seleccione un cliente válido")
            return
        
        # ✅ OBTENER CONDICIONES EXACTAMENTE COMO ESTÁN EN EL WIDGET
        condiciones = self.condiciones_text.get('1.0', tk.END).strip()
        print(f"📄 Condiciones a guardar: '{condiciones}'")
        print(f"   Longitud: {len(condiciones)} caracteres")
        
        # 🔥🔥🔥 CORRECCIÓN CRÍTICA: PRESERVAR LOS IDs DE LOS ITEMS EXISTENTES
        items_para_guardar = []
        for item in self.items_presupuesto:
            item_data = item.copy()
            
            # Si es una edición (no nuevo) y el item tiene ID, preservarlo
            if not self.es_nuevo:
                # Buscar el ID original del item en los datos del presupuesto
                if 'items' in self.presupuesto_data:
                    for original_item in self.presupuesto_data['items']:
                        # Comparar por descripción y cantidad para encontrar el match
                        if (original_item.get('descripcion') == item.get('descripcion') and
                            original_item.get('cantidad') == item.get('cantidad')):
                            item_data['id'] = original_item['id']
                            print(f"🔗 Preservando ID {original_item['id']} para item: {item['descripcion']}")
                            break
            
            items_para_guardar.append(item_data)
        
        print(f"📦 Items para guardar ({len(items_para_guardar)}):")
        for i, item in enumerate(items_para_guardar):
            print(f"   {i+1}. ID: {item.get('id', 'NUEVO')}, Desc: {item['descripcion']}, Precio: ${item['precio_unitario']:.2f}")
        
        # Preparar datos - ENVIAR EXACTAMENTE LO QUE ESTÁ EN EL FORMULARIO
        datos = {
            'cliente': cliente_id,
            'valido_hasta': self.obtener_fecha_validez(),
            'observaciones': self.observaciones_text.get('1.0', tk.END).strip(),
            'condiciones_comerciales': condiciones,
            'iva_porcentaje': float(self.iva_var.get()),
            'estado': self.estado_var.get(),
            'items': items_para_guardar  # 🔥 USAR LA LISTA CORREGIDA CON IDs
        }
        
        print(f"📦 Datos a guardar:")
        print(f"   Tipo: {'NUEVO' if self.es_nuevo else 'EXISTENTE'}")
        print(f"   Items: {len(items_para_guardar)} items con IDs preservados")
        
        # Llamar al manager
        try:
            if self.es_nuevo:
                print("🆕 Creando nuevo presupuesto...")
                resultado = self.manager.crear_presupuesto(datos)
            else:
                print(f"📝 Actualizando presupuesto ID: {self.presupuesto_data['id']}")
                resultado = self.manager.actualizar_presupuesto(self.presupuesto_data['id'], datos)
            
            if resultado:
                print("✅ Presupuesto guardado exitosamente")
                if hasattr(self.presupuestos_window, 'cargar_presupuestos'):
                    self.presupuestos_window.cargar_presupuestos()
                self.window.destroy()
            else:
                print("❌ Error al guardar presupuesto")
                messagebox.showerror("Error", "No se pudo guardar el presupuesto")
                
        except Exception as e:
            print(f"💥 Error crítico al guardar: {e}")
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")