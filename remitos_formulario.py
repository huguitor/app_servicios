# /app_escritorio/remitos_formulario.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from configuracion_manager import ConfiguracionManager
from remitos_manager import RemitosManager
from clientes_manager import ClientesManager
import os
from datetime import datetime
from styles import Styles


# 🔥 IMPORTAR CALENDARIO
try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
    print("✅ tkcalendar disponible - Usando calendario gráfico para remitos")
except ImportError:
    CALENDAR_AVAILABLE = False
    print("⚠️ tkcalendar no disponible. Usando campo de texto para fechas.")


class DialogoEditarItemRemito:
    """Diálogo para editar un item de remito"""
    def __init__(self, parent, item_data=None):
        self.parent = parent
        self.item_data = item_data or {}
        self.resultado = None
       
    def mostrar(self):
        self.dialogo = tk.Toplevel(self.parent)
        self.dialogo.title("Editar Ítem de Remito" if self.item_data else "Nuevo Ítem de Remito")
        self.dialogo.geometry("450x250")
        self.dialogo.transient(self.parent)
        self.dialogo.grab_set()
       
        self.center_window()
       
        # Variables
        self.codigo_var = tk.StringVar(value=self.item_data.get('codigo', ''))
        self.descripcion_var = tk.StringVar(value=self.item_data.get('descripcion', ''))
        self.cantidad_var = tk.StringVar(value=str(self.item_data.get('cantidad', 1)))
        self.unidad_var = tk.StringVar(value=self.item_data.get('unidad_medida', 'UNIDAD'))
        self.observaciones_var = tk.StringVar(value=self.item_data.get('observaciones', ''))
       
        # Frame principal
        main_frame = ttk.Frame(self.dialogo, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
       
        # Grid layout
        main_frame.columnconfigure(1, weight=1)
       
        # Campos del formulario
        ttk.Label(main_frame, text="Código:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        ttk.Entry(main_frame, textvariable=self.codigo_var, width=20).grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=(0, 0))
       
        ttk.Label(main_frame, text="Descripción:*").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        ttk.Entry(main_frame, textvariable=self.descripcion_var, width=40).grid(row=1, column=1, sticky=tk.W+tk.E, pady=5, padx=(0, 0))
       
        ttk.Label(main_frame, text="Cantidad:*").grid(row=2, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        ttk.Entry(main_frame, textvariable=self.cantidad_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5, padx=(0, 0))
       
        ttk.Label(main_frame, text="Unidad:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=(0, 5))
        unidad_combo = ttk.Combobox(main_frame, textvariable=self.unidad_var, width=15)
        unidad_combo['values'] = ['UNIDAD', 'KG', 'LITRO', 'M', 'M2', 'M3', 'PAR', 'JUEGO', 'SET', 'OTRO']
        unidad_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(0, 0))
       
        ttk.Label(main_frame, text="Observaciones:").grid(row=4, column=0, sticky=tk.W+tk.N, pady=5, padx=(0, 5))
        self.observaciones_text = tk.Text(main_frame, width=40, height=3)
        self.observaciones_text.grid(row=4, column=1, sticky=tk.W+tk.E, pady=5, padx=(0, 0))
        if self.observaciones_var.get():
            self.observaciones_text.insert('1.0', self.observaciones_var.get())
       
        # Scrollbar para observaciones
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.observaciones_text.yview)
        self.observaciones_text.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=4, column=2, sticky=tk.NS)
       
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=15)
       
        ttk.Button(button_frame, text="✅ Aceptar", command=self.aceptar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancelar", command=self.cancelar).pack(side=tk.LEFT, padx=5)
       
        self.dialogo.wait_window()
        return self.resultado
   
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.dialogo.update_idletasks()
        width = self.dialogo.winfo_width()
        height = self.dialogo.winfo_height()
        screen_width = self.dialogo.winfo_screenwidth()
        screen_height = self.dialogo.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.dialogo.geometry(f"+{x}+{y}")
   
    def aceptar(self):
        try:
            descripcion = self.descripcion_var.get().strip()
            if not descripcion:
                messagebox.showwarning("Advertencia", "La descripción es obligatoria")
                return
           
            cantidad_str = self.cantidad_var.get().strip()
            if not cantidad_str:
                messagebox.showwarning("Advertencia", "La cantidad es obligatoria")
                return
           
            try:
                cantidad = float(cantidad_str)
                if cantidad <= 0:
                    messagebox.showwarning("Advertencia", "La cantidad debe ser mayor a cero")
                    return
            except ValueError:
                messagebox.showwarning("Advertencia", "La cantidad debe ser un número válido")
                return
           
            self.resultado = {
                'codigo': self.codigo_var.get().strip(),
                'descripcion': descripcion,
                'cantidad': cantidad,
                'unidad_medida': self.unidad_var.get(),
                'observaciones': self.observaciones_text.get('1.0', tk.END).strip(),
                'orden': self.item_data.get('orden', 0)
            }
           
            self.dialogo.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar datos: {e}")
   
    def cancelar(self):
        self.dialogo.destroy()


class FormularioRemito:
    def __init__(self, parent, remitos_window, remito_data, solo_lectura=False):
        print(f"🚀 INICIANDO FORMULARIO REMITO - Modo: {'SOLO LECTURA' if solo_lectura else 'EDICIÓN'}")
       
        self.parent = parent
        self.remitos_window = remitos_window
        self.remito_data = remito_data
        self.es_nuevo = remito_data is None
        self.solo_lectura = solo_lectura
       
        # 🔥 DETECTAR SI ES UN REMITO ANULADO
        self.es_anulado = False
        if not self.es_nuevo and remito_data:
            self.es_anulado = remito_data.get('estado') == 'anulado'
            if self.es_anulado:
                print("⚠️ REMITO ANULADO - Modo solo lectura forzado")
                self.solo_lectura = True
       
        # ✅ INICIALIZAR MANAGERS
        self.manager = RemitosManager()
        self.clientes_manager = ClientesManager()
        self.config_manager = ConfiguracionManager()
       
        self.clientes = []
        self.comprobantes = []
        self.items_remito = []
       
        # ✅ CREAR VENTANA
        self.window = tk.Toplevel(parent)
       
        # 🔥 TÍTULO ESPECIAL PARA REMITOS ANULADOS
        if self.es_anulado:
            self.window.title("📋 Remito Anulado - Solo Lectura")
        elif solo_lectura:
            self.window.title("📋 Ver Remito")
        elif self.es_nuevo:
            self.window.title("🆕 Nuevo Remito")
        else:
            self.window.title("✏️ Editar Remito")
           
        # Color coding
        module_color = Styles.get_module_style("presupuestos")  # Mismo color que presupuestos
        self.header_strip = tk.Frame(self.window, bg=module_color, height=5)
        self.header_strip.pack(fill=tk.X, side=tk.TOP)
           
        self.window.geometry("900x700")
        self.window.transient(parent)
        self.window.grab_set()
       
        # 🔥 COLOR DE FONDO ESPECIAL PARA ANULADOS
        if self.es_anulado:
            self.window.configure(bg='#f8f9fa')
       
        self.center_window(900, 700)
       
        # ✅ OBTENER DATOS PARA COMBOS
        self.cargar_datos_combobox()
       
        # ✅ INICIALIZAR VARIABLES
        self.cliente_var = tk.StringVar(self.window)
        self.comprobante_var = tk.StringVar(self.window)
        self.origen_var = tk.StringVar(self.window, value="")
        self.destino_var = tk.StringVar(self.window, value="")
        self.presupuesto_var = tk.StringVar(self.window, value="")
        self.licitacion_var = tk.StringVar(self.window, value="")
        self.referencia_var = tk.StringVar(self.window, value="")
        self.observaciones_var = tk.StringVar(self.window, value="")
        self.estado_var = tk.StringVar(self.window, value="borrador")
       
        # Variables para fechas
        self.fecha_emision_var = tk.StringVar(self.window, value=datetime.now().strftime('%d/%m/%Y'))
        self.fecha_entrega_var = tk.StringVar(self.window, value="")
       
        self.create_widgets()
       
        # ✅ CARGAR DATOS EXISTENTES SI NO ES NUEVO
        if not self.es_nuevo:
            print("📝 Cargando datos existentes del remito...")
            self.cargar_datos()
        else:
            print("🆕 Configurando nuevo remito...")
            # Intentar obtener próximo número disponible
            self.obtener_proximo_numero()
   
    def obtener_nombre_cliente(self, cliente):
        """Obtener nombre completo del cliente según su tipo"""
        if not cliente:
            return "Cliente no disponible"
       
        if cliente.get('tipo') == 'fisica':
            return f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}".strip()
        else:
            return cliente.get('nombre', 'Cliente sin nombre')
   
    def obtener_proximo_numero(self):
        """Obtener próximo número disponible desde la API"""
        try:
            print("🔄 Obteniendo próximo número para remito...")
            data, error = self.manager.obtener_proximo_numero()
           
            if data:
                proximo_numero = data.get('proximo_numero')
                serie = data.get('serie', 'REMI')
                comprobante_id = data.get('comprobante_id')
               
                if proximo_numero and comprobante_id:
                    print(f"✅ Próximo número: {serie}-{proximo_numero:06d}")
                   
                    # Buscar el comprobante correspondiente en la lista
                    for comprobante in self.comprobantes:
                        if comprobante['id'] == comprobante_id:
                            self.comprobante_var.set(f"{comprobante['serie']} - {comprobante['tipo']}")
                            break
            else:
                print("⚠️ No se pudo obtener próximo número automáticamente")
               
        except Exception as e:
            print(f"❌ Error obteniendo próximo número: {e}")
   
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
            self.comprobantes = self.manager.obtener_comprobantes_remitos()
           
            # Filtrar solo activos
            self.clientes = [c for c in self.clientes if c.get('activo', True)]
           
            print(f"✅ Clientes cargados: {len(self.clientes)}")
            print(f"✅ Comprobantes cargados: {len(self.comprobantes)}")
           
        except Exception as e:
            print(f"❌ Error cargando datos para combobox: {e}")
            self.clientes = []
            self.comprobantes = []
   
    def create_widgets(self):
        """Crear interfaz gráfica - VERSIÓN PARA REMITOS"""
        print("🎨 Creando interfaz gráfica para remitos...")
       
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
   
        # Cabecera del remito
        titulo_frame = "📋 Información del Remito"
        if self.es_anulado:
            titulo_frame = "❌ REMITO ANULADO - SOLO LECTURA"
        elif not self.es_nuevo and self.remito_data:
            numero_formateado = self.remito_data.get('numero_formateado', '')
            if numero_formateado:
                titulo_frame += f" N° {numero_formateado}"
               
        header_frame = ttk.LabelFrame(main_frame, text=titulo_frame, padding="10")
       
        # 🔥 ESTILO ESPECIAL PARA ANULADOS
        if self.es_anulado:
            header_frame.configure(style='Anulado.TLabelframe')
       
        header_frame.pack(fill=tk.X, pady=(0, 10))
   
        # Fila 0: Cliente y Comprobante
        ttk.Label(header_frame, text="Cliente:*").grid(row=0, column=0, sticky=tk.W, pady=5)
       
        # Combobox de clientes
        self.cliente_combo = ttk.Combobox(header_frame, textvariable=self.cliente_var, width=40,
                                         state="readonly" if not self.solo_lectura else "disabled")
        nombres_clientes = [self.obtener_nombre_cliente(c) for c in self.clientes]
        self.cliente_combo['values'] = nombres_clientes
        print(f"🔧 Combobox clientes cargado con {len(nombres_clientes)} opciones")        
        self.cliente_combo.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5, padx=(10, 0))
       
        # Comprobante
        ttk.Label(header_frame, text="Comprobante:*").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.comprobante_combo = ttk.Combobox(header_frame, textvariable=self.comprobante_var, width=20,
                                             state="readonly" if not self.solo_lectura else "disabled")
        comprobante_values = [f"{c['serie']} - {c['tipo']}" for c in self.comprobantes]
        self.comprobante_combo['values'] = comprobante_values
        if comprobante_values:
            self.comprobante_combo.current(0)
        self.comprobante_combo.grid(row=0, column=3, sticky=tk.W, pady=5, padx=(10, 0))
   
        # Fila 1: Fechas
        ttk.Label(header_frame, text="Fecha Emisión:*").grid(row=1, column=0, sticky=tk.W, pady=5)
       
        if CALENDAR_AVAILABLE:
            self.fecha_emision_calendar = DateEntry(
                header_frame,
                width=12,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/mm/yyyy',
                state="readonly" if self.solo_lectura else "normal"
            )
            self.fecha_emision_calendar.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
            print("✅ Calendario de fecha emisión configurado")
        else:
            self.fecha_emision_entry = ttk.Entry(header_frame, textvariable=self.fecha_emision_var, width=12,
                                               state="readonly" if self.solo_lectura else "normal")
            self.fecha_emision_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
            ttk.Label(header_frame, text="(DD/MM/AAAA)", font=("Arial", 7)).grid(row=1, column=2, sticky=tk.W, pady=5, padx=(5, 0))
       
        ttk.Label(header_frame, text="Fecha Entrega:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20, 0))
       
        if CALENDAR_AVAILABLE:
            self.fecha_entrega_calendar = DateEntry(
                header_frame,
                width=12,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/mm/yyyy',
                state="readonly" if self.solo_lectura else "normal"
            )
            self.fecha_entrega_calendar.grid(row=1, column=3, sticky=tk.W, pady=5, padx=(10, 0))
        else:
            self.fecha_entrega_entry = ttk.Entry(header_frame, textvariable=self.fecha_entrega_var, width=12,
                                               state="readonly" if self.solo_lectura else "normal")
            self.fecha_entrega_entry.grid(row=1, column=3, sticky=tk.W, pady=5, padx=(10, 0))
   
        # Fila 2: Origen y Destino
        ttk.Label(header_frame, text="Origen:").grid(row=2, column=0, sticky=tk.W, pady=5)
        origen_entry = ttk.Entry(header_frame, textvariable=self.origen_var, width=40,
                               state="readonly" if self.solo_lectura else "normal")
        origen_entry.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5, padx=(10, 0))
       
        ttk.Label(header_frame, text="Destino:").grid(row=2, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        destino_entry = ttk.Entry(header_frame, textvariable=self.destino_var, width=20,
                                state="readonly" if self.solo_lectura else "normal")
        destino_entry.grid(row=2, column=3, sticky=tk.W+tk.E, pady=5, padx=(10, 0))
   
        # Fila 3: Referencias
        ttk.Label(header_frame, text="Presupuesto:").grid(row=3, column=0, sticky=tk.W, pady=5)
        presupuesto_entry = ttk.Entry(header_frame, textvariable=self.presupuesto_var, width=18,
                                     state="readonly" if self.solo_lectura else "normal")
        presupuesto_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
       
        ttk.Label(header_frame, text="Licitación/Orden:").grid(row=3, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        licitacion_entry = ttk.Entry(header_frame, textvariable=self.licitacion_var, width=18,
                                    state="readonly" if self.solo_lectura else "normal")
        licitacion_entry.grid(row=3, column=3, sticky=tk.W, pady=5, padx=(10, 0))
   
        ttk.Label(header_frame, text="Referencia:").grid(row=4, column=0, sticky=tk.W, pady=5)
        referencia_entry = ttk.Entry(header_frame, textvariable=self.referencia_var, width=40,
                                   state="readonly" if self.solo_lectura else "normal")
        referencia_entry.grid(row=4, column=1, sticky=tk.W+tk.E, pady=5, padx=(10, 0), columnspan=3)
   
        # Fila 5: Estado (solo para edición)
        if not self.es_nuevo:
            ttk.Label(header_frame, text="Estado:").grid(row=5, column=0, sticky=tk.W, pady=5)
            self.estado_combo = ttk.Combobox(header_frame, textvariable=self.estado_var, width=15,
                                          state="readonly" if not self.solo_lectura else "disabled")
           
            # 🔥 AGREGAR ESTADO "ANULADO" AL COMBOBOX
            if self.es_anulado:
                self.estado_combo['values'] = ['anulado']
            else:
                self.estado_combo['values'] = ['borrador', 'pendiente', 'entregado', 'anulado']
               
            self.estado_combo.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
           
            print("✅ Selector de estado configurado")
   
        header_frame.columnconfigure(1, weight=1)
        header_frame.columnconfigure(3, weight=1)
   
        # Frame para items
        items_frame = ttk.LabelFrame(main_frame, text="📦 Ítems del Remito", padding="10")
        items_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
   
        # Toolbar para items
        items_toolbar = ttk.Frame(items_frame)
        items_toolbar.pack(fill=tk.X, pady=(0, 10))
   
        if not self.solo_lectura:
            ttk.Button(items_toolbar, text="➕ Agregar Ítem",
                      command=self.agregar_item).pack(side=tk.LEFT, padx=5)
            ttk.Button(items_toolbar, text="✏️ Editar Ítem",
                      command=self.editar_item).pack(side=tk.LEFT, padx=5)
            ttk.Button(items_toolbar, text="🗑️ Eliminar Ítem",
                      command=self.eliminar_item).pack(side=tk.LEFT, padx=5)
            ttk.Button(items_toolbar, text="⬆️ Subir",
                      command=self.subir_item).pack(side=tk.LEFT, padx=5)
            ttk.Button(items_toolbar, text="⬇️ Bajar",
                      command=self.bajar_item).pack(side=tk.LEFT, padx=5)
            print("✅ Botones de items configurados")
        else:
            # 🔥 MOSTRAR INDICADOR DE SOLO LECTURA PARA ANULADOS
            if self.es_anulado:
                ttk.Label(items_toolbar, text="📋 REMITO ANULADO - SOLO LECTURA",
                         foreground="red", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
   
        # Treeview para items
        columns = ('orden', 'codigo', 'descripcion', 'cantidad', 'unidad', 'observaciones')
        self.tree_items = ttk.Treeview(items_frame, columns=columns, show='headings', height=8)
   
        # Configurar columnas
        self.tree_items.heading('orden', text='#', anchor='center')
        self.tree_items.heading('codigo', text='Código', anchor='center')
        self.tree_items.heading('descripcion', text='Descripción', anchor='center')
        self.tree_items.heading('cantidad', text='Cantidad', anchor='center')
        self.tree_items.heading('unidad', text='Unidad', anchor='center')
        self.tree_items.heading('observaciones', text='Observaciones', anchor='center')
   
        self.tree_items.column('orden', width=30, anchor='center')
        self.tree_items.column('codigo', width=100, anchor='center')
        self.tree_items.column('descripcion', width=250)
        self.tree_items.column('cantidad', width=70, anchor='center')
        self.tree_items.column('unidad', width=70, anchor='center')
        self.tree_items.column('observaciones', width=150)
   
        # Scrollbar
        scrollbar_items = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.tree_items.yview)
        self.tree_items.configure(yscroll=scrollbar_items.set)
        scrollbar_items.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
   
        if not self.solo_lectura:
            self.tree_items.bind('<Double-1>', lambda e: self.editar_item())
   
        # Frame para observaciones
        obs_frame = ttk.LabelFrame(main_frame, text="📝 Observaciones Generales", padding="5")
        obs_frame.pack(fill=tk.X, pady=(0, 10))
       
        self.observaciones_text = tk.Text(obs_frame, width=40, height=4,
                                        state="normal" if not self.solo_lectura else "disabled")
        self.observaciones_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
   
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
   
        if self.solo_lectura:
            ttk.Button(button_frame, text="⬅️ Volver",
                      command=self.window.destroy).pack(side=tk.LEFT, padx=5)
           
            # 🔥 BOTÓN ESPECIAL PARA REMITOS ANULADOS
            if self.es_anulado:
                # Mostrar información de anulación si está disponible
                if self.remito_data.get('fecha_anulacion') or self.remito_data.get('motivo_anulacion'):
                    ttk.Button(button_frame, text="📋 Ver Detalles de Anulación",
                              command=self.mostrar_detalles_anulacion).pack(side=tk.LEFT, padx=5)
           
            print("✅ Modo solo lectura - Botón volver configurado")
        else:
            ttk.Button(button_frame, text="💾 Guardar Borrador",
                      command=lambda: self.guardar('borrador')).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="📤 Generar Remito",
                      command=lambda: self.guardar('pendiente')).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="📎 Adjuntos",
                      command=self.gestionar_adjuntos).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="🖨️ Imprimir",
                      command=self.imprimir).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="❌ Cancelar",
                      command=self.window.destroy).pack(side=tk.LEFT, padx=5)
            print("✅ Botones de acción configurados")
   
        # 🔥 CONFIGURAR ESTILOS PARA ANULADOS
        self.configurar_estilos()
       
        print("🎉 INTERFAZ GRÁFICA PARA REMITOS CREADA EXITOSAMENTE")
   
    # Los demás métodos (agregar_item, editar_item, eliminar_item, etc.) siguen
    # similares a los de presupuestos pero adaptados para remitos
   
    def agregar_item(self):
        """Abrir diálogo para agregar item"""
        if not self.cliente_var.get():
            messagebox.showwarning("Advertencia", "Primero seleccione un cliente")
            return
       
        # 🔥 VERIFICAR SI ESTÁ ANULADO
        if self.es_anulado:
            messagebox.showinfo("Remito Anulado", "No se pueden modificar items de un remito anulado.")
            return
       
        print("📝 Abriendo diálogo para agregar item...")
        dialogo = DialogoEditarItemRemito(self.window)
        resultado = dialogo.mostrar()
       
        if resultado:
            # Asignar número de orden
            resultado['orden'] = len(self.items_remito) + 1
            self.items_remito.append(resultado)
            self.agregar_item_a_treeview(resultado)
            print(f"✅ Ítem agregado: {resultado['descripcion']} x{resultado['cantidad']}")
   
    def editar_item(self):
        """Editar ítem seleccionado"""
        # 🔥 VERIFICAR SI ESTÁ ANULADO
        if self.es_anulado:
            messagebox.showinfo("Remito Anulado", "No se pueden editar items de un remito anulado.")
            return
           
        selection = self.tree_items.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un ítem para editar")
            return
       
        item_index = self.tree_items.index(selection[0])
        item = self.items_remito[item_index]
       
        print(f"✏️ Editando ítem: {item['descripcion']}")
        dialogo = DialogoEditarItemRemito(self.window, item)
        resultado = dialogo.mostrar()
       
        if resultado:
            self.items_remito[item_index] = resultado
            # Actualizar treeview
            self.tree_items.delete(selection[0])
            self.agregar_item_a_treeview(resultado)
            print(f"✅ Ítem actualizado: {resultado['descripcion']} x{resultado['cantidad']}")
   
    def eliminar_item(self):
        """Eliminar ítem seleccionado"""
        # 🔥 VERIFICAR SI ESTÁ ANULADO
        if self.es_anulado:
            messagebox.showinfo("Remito Anulado", "No se pueden eliminar items de un remito anulado.")
            return
           
        selection = self.tree_items.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un ítem para eliminar")
            return
       
        item_index = self.tree_items.index(selection[0])
        item_descripcion = self.items_remito[item_index]['descripcion']
        self.tree_items.delete(selection[0])
        self.items_remito.pop(item_index)
        # Recalcular órdenes
        self.recalcular_ordenes()
        print(f"🗑️ Ítem eliminado: {item_descripcion}")
   
    def subir_item(self):
        """Subir item en la lista"""
        selection = self.tree_items.selection()
        if not selection or len(selection) != 1:
            return
       
        item_index = self.tree_items.index(selection[0])
        if item_index > 0:
            # Intercambiar items en la lista
            self.items_remito[item_index], self.items_remito[item_index - 1] = \
                self.items_remito[item_index - 1], self.items_remito[item_index]
           
            # Actualizar treeview
            self.actualizar_treeview_items()
   
    def bajar_item(self):
        """Bajar item en la lista"""
        selection = self.tree_items.selection()
        if not selection or len(selection) != 1:
            return
       
        item_index = self.tree_items.index(selection[0])
        if item_index < len(self.items_remito) - 1:
            # Intercambiar items en la lista
            self.items_remito[item_index], self.items_remito[item_index + 1] = \
                self.items_remito[item_index + 1], self.items_remito[item_index]
           
            # Actualizar treeview
            self.actualizar_treeview_items()
   
    def agregar_item_a_treeview(self, item):
        """Agregar un ítem al treeview"""
        self.tree_items.insert('', tk.END, values=(
            item.get('orden', 0),
            item.get('codigo', ''),
            item.get('descripcion', ''),
            item.get('cantidad', 1),
            item.get('unidad_medida', 'UNIDAD'),
            item.get('observaciones', '')[:30] + '...' if len(item.get('observaciones', '')) > 30 else item.get('observaciones', '')
        ))
   
    def actualizar_treeview_items(self):
        """Actualizar todo el treeview de items"""
        # Limpiar treeview
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)
       
        # Recalcular órdenes
        self.recalcular_ordenes()
       
        # Agregar items
        for item in self.items_remito:
            self.agregar_item_a_treeview(item)
   
    def recalcular_ordenes(self):
        """Recalcular números de orden"""
        for i, item in enumerate(self.items_remito):
            item['orden'] = i + 1
   
    def obtener_fecha(self, fecha_var, calendar_widget=None):
        """Obtener fecha en formato YYYY-MM-DD para la API"""
        try:
            if CALENDAR_AVAILABLE and calendar_widget:
                # Obtener fecha del calendario
                fecha_obj = calendar_widget.get_date()
                return fecha_obj.strftime('%Y-%m-%d')
            else:
                # Convertir de DD/MM/YYYY a YYYY-MM-DD
                fecha_str = fecha_var.get()
                if fecha_str:
                    fecha_obj = datetime.strptime(fecha_str, '%d/%m/%Y')
                    return fecha_obj.strftime('%Y-%m-%d')
                return None
        except Exception as e:
            print(f"❌ Error obteniendo fecha: {e}")
            return None
   
    def validar_formulario(self):
        """Validar datos del formulario"""
        if not self.cliente_var.get():
            messagebox.showerror("Error", "Debe seleccionar un cliente")
            return False
       
        if not self.comprobante_var.get():
            messagebox.showerror("Error", "Debe seleccionar un comprobante")
            return False
       
        if not self.items_remito:
            messagebox.showerror("Error", "El remito debe tener al menos un ítem")
            return False
       
        # Validar fecha de emisión
        try:
            fecha_emision = self.obtener_fecha(self.fecha_emision_var, 
                                             self.fecha_emision_calendar if CALENDAR_AVAILABLE else None)
            if not fecha_emision:
                messagebox.showerror("Error", "La fecha de emisión es obligatoria")
                return False
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha de emisión inválido. Use DD/MM/YYYY")
            return False
       
        # Validar fecha de entrega si se especificó
        if self.fecha_entrega_var.get():
            try:
                fecha_entrega = self.obtener_fecha(self.fecha_entrega_var,
                                                 self.fecha_entrega_calendar if CALENDAR_AVAILABLE else None)
                if fecha_entrega:
                    fecha_emision_obj = datetime.strptime(fecha_emision, '%Y-%m-%d')
                    fecha_entrega_obj = datetime.strptime(fecha_entrega, '%Y-%m-%d')
                    if fecha_entrega_obj < fecha_emision_obj:
                        messagebox.showerror("Error", "La fecha de entrega no puede ser anterior a la fecha de emisión")
                        return False
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha de entrega inválido. Use DD/MM/YYYY")
                return False
       
        return True
   
    def cargar_datos(self):
        """Cargar datos del remito en el formulario - VERSIÓN PARA REMITOS"""
        if not self.remito_data:
            return
       
        print("🔍 Cargando datos del remito existente...")
       
        # Cargar cliente
        cliente_id = self.remito_data.get('cliente')
        cliente_encontrado = False
        for cliente in self.clientes:
            if cliente['id'] == cliente_id:
                self.cliente_var.set(self.obtener_nombre_cliente(cliente))
                cliente_encontrado = True
                print(f"✅ Cliente cargado: {self.obtener_nombre_cliente(cliente)}")
                break
       
        if not cliente_encontrado:
            print("⚠️ Cliente no encontrado en la lista local")
       
        # Cargar comprobante
        comprobante_id = self.remito_data.get('comprobante')
        for comprobante in self.comprobantes:
            if comprobante['id'] == comprobante_id:
                self.comprobante_var.set(f"{comprobante['serie']} - {comprobante['tipo']}")
                print(f"✅ Comprobante cargado: {comprobante['serie']}")
                break
       
        # Cargar fechas
        fecha_emision = self.remito_data.get('fecha_emision')
        if fecha_emision:
            try:
                if 'T' in fecha_emision:
                    fecha_emision = fecha_emision.split('T')[0]
                fecha_obj = datetime.strptime(fecha_emision, '%Y-%m-%d')
                fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
               
                if CALENDAR_AVAILABLE:
                    self.fecha_emision_calendar.set_date(fecha_obj)
                else:
                    self.fecha_emision_var.set(fecha_formateada)
                print(f"✅ Fecha emisión cargada: {fecha_formateada}")
            except ValueError as e:
                print(f"⚠️ Error convirtiendo fecha emisión: {e}")
       
        fecha_entrega = self.remito_data.get('fecha_entrega')
        if fecha_entrega:
            try:
                if 'T' in fecha_entrega:
                    fecha_entrega = fecha_entrega.split('T')[0]
                fecha_obj = datetime.strptime(fecha_entrega, '%Y-%m-%d')
                fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
               
                if CALENDAR_AVAILABLE:
                    self.fecha_entrega_calendar.set_date(fecha_obj)
                else:
                    self.fecha_entrega_var.set(fecha_formateada)
                print(f"✅ Fecha entrega cargada: {fecha_formateada}")
            except ValueError as e:
                print(f"⚠️ Error convirtiendo fecha entrega: {e}")
       
        # Cargar otros campos
        self.origen_var.set(self.remito_data.get('origen', ''))
        self.destino_var.set(self.remito_data.get('destino', ''))
        self.presupuesto_var.set(self.remito_data.get('presupuesto_relacionado', ''))
        self.licitacion_var.set(self.remito_data.get('licitacion_orden', ''))
        self.referencia_var.set(self.remito_data.get('numero_referencia', ''))
       
        # Cargar estado
        estado = self.remito_data.get('estado', 'borrador')
        self.estado_var.set(estado)
        print(f"✅ Estado cargado: {estado}")
       
        # Cargar observaciones
        observaciones = self.remito_data.get('observaciones', '')
        self.observaciones_text.delete('1.0', tk.END)
        self.observaciones_text.insert('1.0', observaciones)
        print(f"✅ Observaciones cargadas: '{observaciones}'")
       
        # Cargar items
        self.items_remito = []
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)
       
        if 'items' in self.remito_data:
            items_data = self.remito_data['items']
            print(f"📋 Items encontrados: {len(items_data)}")
           
            for i, item in enumerate(items_data):
                print(f"   Ítem {i}: {item.get('descripcion', 'Sin descripción')}")
               
                item_data = item.copy()
                # Asegurar tipos de datos
                if 'cantidad' in item_data:
                    try:
                        item_data['cantidad'] = float(item_data['cantidad'])
                    except (ValueError, TypeError):
                        item_data['cantidad'] = 1.0
               
                # Asegurar que todos los campos existan
                item_data.setdefault('codigo', '')
                item_data.setdefault('descripcion', '')
                item_data.setdefault('cantidad', 1.0)
                item_data.setdefault('unidad_medida', 'UNIDAD')
                item_data.setdefault('observaciones', '')
                item_data.setdefault('orden', i + 1)
               
                self.items_remito.append(item_data)
                self.agregar_item_a_treeview(item_data)
        else:
            print("ℹ️ No hay items en el remito")
       
        print("✅ Datos del remito cargados exitosamente")
   
    def guardar(self, estado=None):
        """Guardar remito"""
        # 🔥 VERIFICAR SI ESTÁ ANULADO
        if self.es_anulado:
            messagebox.showinfo("Remito Anulado",
                              "No se puede guardar un remito anulado.\n\n"
                              "Los remitos anulados son de solo lectura para auditoría.")
            return
           
        print("💾 Iniciando proceso de guardado de remito...")
       
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
       
        # Obtener ID del comprobante
        comprobante_texto = self.comprobante_var.get()
        comprobante_id = None
        for comprobante in self.comprobantes:
            comprobante_str = f"{comprobante['serie']} - {comprobante['tipo']}"
            if comprobante_str == comprobante_texto:
                comprobante_id = comprobante['id']
                break
       
        if not comprobante_id:
            messagebox.showwarning("Advertencia", "Seleccione un comprobante válido")
            return
       
        # Preparar items
        items_para_guardar = []
        for item in self.items_remito:
            item_data = item.copy()
           
            # Si es una edición (no nuevo) y el item tiene ID, preservarlo
            if not self.es_nuevo:
                # Buscar el ID original del item en los datos del remito
                if 'items' in self.remito_data:
                    for original_item in self.remito_data['items']:
                        # Comparar por descripción y orden para encontrar el match
                        if (original_item.get('descripcion') == item.get('descripcion') and
                            original_item.get('orden') == item.get('orden')):
                            item_data['id'] = original_item['id']
                            print(f"🔗 Preservando ID {original_item['id']} para item: {item['descripcion']}")
                            break
           
            items_para_guardar.append(item_data)
       
        print(f"📦 Items para guardar ({len(items_para_guardar)}):")
        for i, item in enumerate(items_para_guardar):
            print(f"   {i+1}. ID: {item.get('id', 'NUEVO')}, Desc: {item['descripcion']}, Cant: {item['cantidad']}")
       
        # Determinar estado
        if estado:
            estado_guardar = estado
        else:
            estado_guardar = self.estado_var.get()
       
        # Preparar datos
        datos = {
            'cliente': cliente_id,
            'comprobante': comprobante_id,
            'fecha_emision': self.obtener_fecha(self.fecha_emision_var,
                                               self.fecha_emision_calendar if CALENDAR_AVAILABLE else None),
            'fecha_entrega': self.obtener_fecha(self.fecha_entrega_var,
                                              self.fecha_entrega_calendar if CALENDAR_AVAILABLE else None) or None,
            'origen': self.origen_var.get().strip(),
            'destino': self.destino_var.get().strip(),
            'presupuesto_relacionado': self.presupuesto_var.get().strip(),
            'licitacion_orden': self.licitacion_var.get().strip(),
            'numero_referencia': self.referencia_var.get().strip(),
            'observaciones': self.observaciones_text.get('1.0', tk.END).strip(),
            'estado': estado_guardar,
            'items': items_para_guardar
        }
       
        print(f"📦 Datos a guardar:")
        print(f"   Tipo: {'NUEVO' if self.es_nuevo else 'EXISTENTE'}")
        print(f"   Estado: {estado_guardar}")
        print(f"   Items: {len(items_para_guardar)} items")
       
        # Llamar al manager
        try:
            if self.es_nuevo:
                print("🆕 Creando nuevo remito...")
                resultado = self.manager.crear_remito(datos)
            else:
                print(f"📝 Actualizando remito ID: {self.remito_data['id']}")
                resultado = self.manager.actualizar_remito(self.remito_data['id'], datos)
           
            if resultado:
                print("✅ Remito guardado exitosamente")
                if hasattr(self.remitos_window, 'cargar_remitos'):
                    self.remitos_window.cargar_remitos()
                self.window.destroy()
            else:
                print("❌ Error al guardar remito")
                messagebox.showerror("Error", "No se pudo guardar el remito")
               
        except Exception as e:
            print(f"💥 Error crítico al guardar: {e}")
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
   
    def gestionar_adjuntos(self):
        """Abrir gestión de adjuntos desde el formulario"""
        # 🔥 VERIFICAR SI ESTÁ ANULADO
        if self.es_anulado:
            messagebox.showinfo("Remito Anulado",
                              "No se pueden gestionar adjuntos de un remito anulado.\n\n"
                              "Los remitos anulados son de solo lectura para auditoría.")
            return
           
        from dialogo_adjunto import DialogoAdjunto
        remito_id = self.remito_data['id'] if self.remito_data else None
        if remito_id:
            print(f"🔧 Abriendo diálogo de adjuntos para remito ID: {remito_id}")
            # Crear un manager adaptado para remitos
            dialogo = DialogoAdjunto(self.window, self.manager, remito_id, titulo="Remito")
        else:
            messagebox.showwarning("Advertencia", "Guarde el remito primero para agregar adjuntos")
   
    # En remitos_formulario.py, modifica el método imprimir:
    def imprimir(self):
        """Generar PDF del remito"""
        # 🔥 VERIFICAR SI ESTÁ ANULADO
        if self.es_anulado:
            messagebox.showinfo("Remito Anulado",
                            "No se puede generar PDF de un remito anulado.")
            return
        
        if self.es_nuevo:
            messagebox.showwarning("Advertencia", "Debe guardar el remito antes de generar PDF")
            return
        
        print(f"🖨️ Generando PDF para remito ID: {self.remito_data['id']}")
        
        # Importar el generador de PDF
        from pdf_generator_remitos import generar_remito_pdf
        
        try:
            # Obtener datos del cliente
            cliente_id = self.remito_data.get('cliente')
            cliente_data = None
            
            # Buscar el cliente en la lista
            for cliente in self.clientes:
                if cliente['id'] == cliente_id:
                    cliente_data = cliente
                    break
            
            if not cliente_data:
                messagebox.showerror("Error", "No se pudo encontrar la información del cliente")
                return
            
            # Generar PDF
            resultado = generar_remito_pdf(self.remito_data, cliente_data)
            
            if resultado:
                print(f"✅ PDF generado exitosamente")
            else:
                print("❌ No se pudo generar el PDF")
                
        except Exception as e:
            print(f"❌ Error generando PDF: {e}")
            messagebox.showerror("Error", f"No se pudo generar el PDF: {str(e)}")
   
    def configurar_estilos(self):
        """Configurar estilos visuales para remitos anulados"""
        style = ttk.Style()
       
        # Estilo para label frame de anulados
        style.configure('Anulado.TLabelframe',
                       background='#f8f9fa',
                       bordercolor='#95a5a6')
        style.configure('Anulado.TLabelframe.Label',
                       foreground='#d63031',
                       background='#f8f9fa',
                       font=('Arial', 10, 'bold'))
   
    def mostrar_detalles_anulacion(self):
        """Mostrar detalles de la anulación del remito"""
        detalles = []
       
        if self.remito_data.get('fecha_anulacion'):
            fecha_anulacion = self.remito_data['fecha_anulacion']
            detalles.append(f"🗓️ Fecha de anulación: {fecha_anulacion}")
       
        if self.remito_data.get('motivo_anulacion'):
            motivo = self.remito_data['motivo_anulacion']
            detalles.append(f"📝 Motivo: {motivo}")
       
        if self.remito_data.get('anulado_por'):
            detalles.append(f"👤 Anulado por: Usuario ID {self.remito_data['anulado_por']}")
       
        if detalles:
            messagebox.showinfo("📋 Detalles de Anulación", "\n\n".join(detalles))
        else:
            messagebox.showinfo("📋 Detalles de Anulación",
                              "No hay información adicional disponible sobre la anulación.")