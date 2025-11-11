# /app_escritorio/presupuestos_formulario.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
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
except ImportError:
    CALENDAR_AVAILABLE = False
    print("⚠️ tkcalendar no disponible. Usando campo de texto para fechas.")


class FormularioPresupuesto:
    def __init__(self, parent, presupuestos_window, presupuesto_data, solo_lectura=False):
        self.parent = parent
        self.presupuestos_window = presupuestos_window
        self.presupuesto_data = presupuesto_data
        self.es_nuevo = presupuesto_data is None
        self.solo_lectura = solo_lectura
       
        self.manager = PresupuestosManager()
        self.clientes_manager = ClientesManager()
        self.productos_manager = ProductosManager()
        self.servicios_manager = ServiciosManager()
       
        self.clientes = []
        self.productos = []
        self.servicios = []
        self.items_presupuesto = []
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Ver Presupuesto" if solo_lectura else
                         "Nuevo Presupuesto" if self.es_nuevo else "Editar Presupuesto")
        self.window.geometry("900x700")
        self.window.transient(parent)
        self.window.grab_set()
       
        self.center_window(900, 700)
       
        # INICIALIZAR VARIABLES
        self.cliente_var = tk.StringVar(self.window)
        self.observaciones_var = tk.StringVar(self.window)
        self.condiciones_var = tk.StringVar(self.window)
        self.iva_var = tk.StringVar(self.window, value="21.00")
        self.estado_var = tk.StringVar(self.window, value="borrador")
       
        # Variables para totales
        self.subtotal_var = tk.StringVar(self.window, value="$0.00")
        self.iva_valor_var = tk.StringVar(self.window, value="$0.00")
        self.total_var = tk.StringVar(self.window, value="$0.00")
       
        # 🔥 ORDEN CORREGIDO: Cargar datos PRIMERO
        self.cargar_datos_combobox()
        self.create_widgets()
       
        if not self.es_nuevo:
            self.cargar_datos()
        else:
            # Para nuevo presupuesto, cargar condiciones por defecto
            default_condiciones = (
                "Precios: Expresados en Pesos Argentinos\n"
                "Plazo de entrega: Inmediata\n"
                "Forma de Pago: 30 días\n"
            )
            try:
                self.condiciones_text.insert('1.0', default_condiciones)
            except Exception as e:
                print(f"Error cargando condiciones por defecto: {e}")


    def center_window(self, width, height):
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
        # Frame principal con scroll
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
        # Cabecera del presupuesto
        header_frame = ttk.LabelFrame(main_frame, text="📋 Información del Presupuesto", padding="10")
        header_frame.pack(fill=tk.X, pady=(0, 10))
    
        # Fila 0: Cliente y Fecha de validez
        ttk.Label(header_frame, text="Cliente:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Crear el combobox y GUARDARLO como atributo
        self.cliente_combo = ttk.Combobox(header_frame, textvariable=self.cliente_var, width=50, state="readonly")
        
        # 🔥 CARGAR VALORES después de crear el combobox
        nombres_clientes = [self.obtener_nombre_cliente(c) for c in self.clientes]
        self.cliente_combo['values'] = nombres_clientes
        print(f"🔧 Combobox clientes cargado con {len(nombres_clientes)} opciones")        
        self.cliente_combo.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=(10, 0))
        
        # 🔥 NUEVO: Fecha de validez - CORREGIR POSICIÓN
        ttk.Label(header_frame, text="Válido hasta:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        
        if CALENDAR_AVAILABLE:
            # Usar DateEntry con calendario
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
        else:
            # Usar Entry simple si no hay tkcalendar
            self.valido_hasta_var = tk.StringVar(self.window)
            fecha_default = (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')
            self.valido_hasta_var.set(fecha_default)
            self.valido_hasta_entry = ttk.Entry(header_frame, textvariable=self.valido_hasta_var, width=12)
            self.valido_hasta_entry.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(10, 0))
            ttk.Label(header_frame, text="(DD/MM/AAAA)", font=("Arial", 7)).grid(row=0, column=4, sticky=tk.W, pady=5, padx=(5, 0))

        # Fila 1: IVA y Estado (solo para edición)
        ttk.Label(header_frame, text="% IVA:").grid(row=1, column=0, sticky=tk.W, pady=5)
        iva_entry = ttk.Entry(header_frame, textvariable=self.iva_var, width=10)
        iva_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # 🔥 CORREGIR: Estado en la misma fila que IVA
        if not self.es_nuevo:
            ttk.Label(header_frame, text="Estado:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20, 0))
            estado_combo = ttk.Combobox(header_frame, textvariable=self.estado_var, width=15, state="readonly")
            estado_combo['values'] = ['borrador', 'enviado', 'aceptado', 'rechazado']
            estado_combo.grid(row=1, column=3, sticky=tk.W, pady=5, padx=(10, 0))
    
        # Configurar grid weights para mejor distribución
        header_frame.columnconfigure(1, weight=1)
    
        # Frame para items del presupuesto
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
    
        # Scrollbar para items
        scrollbar_items = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.tree_items.yview)
        self.tree_items.configure(yscroll=scrollbar_items.set)
        scrollbar_items.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        # Bind eventos para items
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
    
        # Botones - CORREGIDO: SIN DUPLICACIÓN Y SIN CÓDIGO SUELTO
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
    
        if self.solo_lectura:
            ttk.Button(button_frame, text="⬅️ Volver",
                    command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        else:
            ttk.Button(button_frame, text="💾 Guardar Presupuesto",
                    command=self.guardar).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="📎 Adjuntos",
                    command=self.gestionar_adjuntos).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="❌ Cancelar",
                    command=self.window.destroy).pack(side=tk.LEFT, padx=5)
    
        # Configurar grid weights
        header_frame.columnconfigure(1, weight=1)
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.columnconfigure(1, weight=1)

    def gestionar_adjuntos(self):
        """Abrir gestión de adjuntos desde el formulario"""
        from dialogo_adjunto import DialogoAdjunto
        presupuesto_id = self.presupuesto_data['id'] if self.presupuesto_data else None
        if presupuesto_id:
            print(f"🔧 Abriendo diálogo de adjuntos para presupuesto ID: {presupuesto_id}")
            dialogo = DialogoAdjunto(self.window, self.manager, presupuesto_id)
            # El diálogo se maneja automáticamente, no necesitamos hacer nada más
        else:
            messagebox.showwarning("Advertencia", "Guarde el presupuesto primero para agregar adjuntos")

    def obtener_nombre_cliente(self, cliente):
        """Obtener nombre completo del cliente"""
        if not cliente:
            return "Cliente no disponible"
        if cliente['tipo'] == 'fisica':
            return f"{cliente['nombre']} {cliente['apellido'] or ''}".strip()
        else:
            return cliente['nombre']


    def cargar_datos(self):
        """Cargar datos del presupuesto en el formulario"""
        if not self.presupuesto_data:
            return
        
        print("🔍 DEBUG - CARGANDO DATOS DEL PRESUPUESTO EXISTENTE:")
        print(f"Presupuesto ID: {self.presupuesto_data.get('id')}")
        print(f"Estado: {self.presupuesto_data.get('estado')}")
        print(f"IVA: {self.presupuesto_data.get('iva_porcentaje')}")
        
        # Cargar cliente
        cliente_id = self.presupuesto_data.get('cliente')
        for cliente in self.clientes:
            if cliente['id'] == cliente_id:
                self.cliente_var.set(self.obtener_nombre_cliente(cliente))
                break
        
        # 🔥 CARGAR FECHA DE VALIDEZ - CONVERSIÓN DE FORMATO
        valido_hasta = self.presupuesto_data.get('valido_hasta')
        if valido_hasta:
            try:
                # Convertir de YYYY-MM-DD a DD/MM/YYYY
                if 'T' in valido_hasta:
                    valido_hasta = valido_hasta.split('T')[0]
                
                fecha_obj = datetime.strptime(valido_hasta, '%Y-%m-%d')
                fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
                
                if CALENDAR_AVAILABLE:
                    self.valido_hasta_calendar.set_date(fecha_obj)
                else:
                    self.valido_hasta_var.set(fecha_formateada)
                    
            except ValueError as e:
                print(f"⚠️ Error convirtiendo fecha: {e}")
                if not CALENDAR_AVAILABLE:
                    self.valido_hasta_var.set(valido_hasta)

        # Cargar estado
        self.estado_var.set(self.presupuesto_data.get('estado', 'borrador'))
        
        # Cargar IVA
        self.iva_var.set(str(self.presupuesto_data.get('iva_porcentaje', '21.00')))
        
        # Cargar observaciones y condiciones
        self.observaciones_text.delete('1.0', tk.END)
        self.observaciones_text.insert('1.0', self.presupuesto_data.get('observaciones', ''))
        
        self.condiciones_text.delete('1.0', tk.END)
        self.condiciones_text.insert('1.0', self.presupuesto_data.get('condiciones_comerciales', ''))
        
        # 🔥 LIMPIAR DATOS EXISTENTES
        self.items_presupuesto = []
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)
        
        # Cargar items - CON CONVERSIÓN DE TIPOS
        if 'items' in self.presupuesto_data:
            print(f"📋 Items encontrados: {len(self.presupuesto_data['items'])}")
            for i, item in enumerate(self.presupuesto_data['items']):
                print(f"   Ítem {i}: precio={item.get('precio_unitario')}, tipo={type(item.get('precio_unitario'))}")
                
                # 🔥 CONVERTIR PRECIOS A FLOAT
                item_data = item.copy()
                if 'precio_unitario' in item_data:
                    precio = item_data['precio_unitario']
                    if isinstance(precio, str):
                        try:
                            item_data['precio_unitario'] = float(precio)
                        except (ValueError, TypeError):
                            item_data['precio_unitario'] = 0.0
                            print(f"   ⚠️  Precio convertido a 0.0: {precio}")
                
                self.items_presupuesto.append(item_data)
                self.agregar_item_a_treeview(item_data)
        
        # Actualizar totales
        self.actualizar_totales()


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


    def agregar_producto(self):
        """Abrir diálogo para agregar producto"""
        if not self.cliente_var.get():
            messagebox.showwarning("Advertencia", "Primero seleccione un cliente")
            return
       
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


    def agregar_servicio(self):
        """Abrir diálogo para agregar servicio"""
        if not self.cliente_var.get():
            messagebox.showwarning("Advertencia", "Primero seleccione un cliente")
            return
       
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


    def eliminar_item(self):
        """Eliminar ítem seleccionado"""
        selection = self.tree_items.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un ítem para eliminar")
            return
       
        item_index = self.tree_items.index(selection[0])
        self.tree_items.delete(selection[0])
        self.items_presupuesto.pop(item_index)
        self.actualizar_totales()


    def editar_item(self, event):
        """Editar ítem seleccionado (cambiar cantidad)"""
        selection = self.tree_items.selection()
        if not selection:
            return
       
        item_index = self.tree_items.index(selection[0])
        item = self.items_presupuesto[item_index]
       
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


    def obtener_fecha_validez(self):
        """Obtener fecha de validez en formato YYYY-MM-DD para la API"""
        try:
            if CALENDAR_AVAILABLE:
                # Obtener fecha del calendario y convertir a YYYY-MM-DD
                fecha_obj = self.valido_hasta_calendar.get_date()
                return fecha_obj.strftime('%Y-%m-%d')
            else:
                # Convertir de DD/MM/YYYY a YYYY-MM-DD
                fecha_str = self.valido_hasta_var.get()
                fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
                return fecha_obj.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"⚠️ Error obteniendo fecha de validez: {e}")
            return None


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


    def guardar(self):
        """Guardar presupuesto"""
        if not self.validar_formulario():
            return
        
        # Obtener ID del cliente seleccionado
        cliente_nombre = self.cliente_var.get()
        cliente_id = None
        for cliente in self.clientes:
            nombre_completo = self.obtener_nombre_cliente(cliente)
            if nombre_completo == cliente_nombre:
                cliente_id = cliente['id']
                break
        
        if not cliente_id:
            messagebox.showerror("Error", "Cliente no válido")
            return
        
        # Preparar datos
        datos = {
            'cliente': cliente_id,
            'valido_hasta': self.obtener_fecha_validez(),
            'observaciones': self.observaciones_text.get('1.0', tk.END).strip(),
            'condiciones_comerciales': self.condiciones_text.get('1.0', tk.END).strip(),
            'iva_porcentaje': float(self.iva_var.get()),
            'estado': self.estado_var.get(),
            'items': self.items_presupuesto
        }
        
        # Llamar al manager
        if self.es_nuevo:
            resultado = self.manager.crear_presupuesto(datos)
        else:
            resultado = self.manager.actualizar_presupuesto(self.presupuesto_data['id'], datos)
        
        if resultado:
            self.presupuestos_window.cargar_presupuestos()
            self.window.destroy()


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