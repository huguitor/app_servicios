# /app_escritorio/clientes_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
from clientes_manager import ClientesManager
from styles import Styles


class ClientesWindow:
    def __init__(self, parent):
        self.parent = parent
        self.manager = ClientesManager()
        self.clientes = []
        self.cliente_seleccionado = None
        
        # Variables para ordenamiento
        self.sort_column = None
        self.sort_reverse = False
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Clientes - Lab Servicios")
       
        # USAR 80% DEL ANCHO DE PANTALLA
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        self.window.geometry(f"{window_width}x{window_height}")
       
        self.window.transient(parent)
        self.window.grab_set()
       
        # Configurar icono - MÉTODO MEJORADO
        self.set_icon()
       
        self.center_window(window_width, window_height)
       
        # INICIALIZAR VARIABLES CON LA VENTANA COMO MASTER
        self.search_var = tk.StringVar(self.window)
        self.tipo_filter_var = tk.StringVar(self.window)
        self.estado_filter_var = tk.StringVar(self.window)
       
        self.create_widgets()
        self.cargar_clientes()


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
                        from PIL import Image, ImageTk
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
        self.search_entry.bind('<KeyRelease>', self.buscar_clientes)
       
        # Filtros
        ttk.Label(search_frame, text="Tipo:").pack(side=tk.LEFT, padx=(20, 5))
        self.tipo_filter = ttk.Combobox(
            search_frame,
            textvariable=self.tipo_filter_var,
            values=["Todos", "Persona Física", "Persona Jurídica"],
            state="readonly",
            width=15
        )
        self.tipo_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.tipo_filter.bind('<<ComboboxSelected>>', self.aplicar_filtros)
       
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
       
        ttk.Button(button_frame, text="➕ Nuevo Cliente", command=self.nuevo_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Editar", command=self.editar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Eliminar", command=self.eliminar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Recargar", command=self.cargar_clientes).pack(side=tk.LEFT, padx=5)
       
        # Treeview para lista de clientes
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
       
        columns = ('id', 'nombre', 'documento', 'tipo', 'condicion_iva', 'telefono', 'email', 'activo')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
       
        # Configurar columnas con bindings para ordenamiento
        column_configs = [
            ('id', 'ID', 50),
            ('nombre', 'Nombre/Razón Social', 200),
            ('documento', 'Documento', 100),
            ('tipo', 'Tipo', 120),
            ('condicion_iva', 'Condición IVA', 120),
            ('telefono', 'Teléfono', 100),
            ('email', 'Email', 150),
            ('activo', 'Estado', 80)
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
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_cliente)
        self.tree.bind('<Double-1>', lambda e: self.editar_cliente())
    
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
        elif column in ['documento', 'telefono']:
            # Ordenar como texto numérico (puede contener números y guiones)
            items.sort(key=lambda x: x[0], reverse=self.sort_reverse)
        elif column == 'activo':
            # Ordenar por estado (Activo/Inactivo)
            items.sort(key=lambda x: x[0] == 'Activo', reverse=self.sort_reverse)
        else:
            # Ordenar como texto (nombre, tipo, condición_iva, email)
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
   
    def cargar_clientes(self, filtros=None):
        """Cargar lista de clientes"""
        self.clientes = self.manager.obtener_clientes(filtros)
        self.actualizar_treeview()
   
    def actualizar_treeview(self):
        """Actualizar el treeview con los clientes"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)


        # Mapeo para condiciones IVA legibles
        condicion_iva_map = {
            "ri": "Resp. Inscripto",
            "mono": "Monotributo",
            "exento": "Exento",
            "cf": "Cons. Final",
            "noresidente": "No Residente"
        }
       
        # Llenar con datos
        for cliente in self.clientes:
            tipo_display = "Persona Física" if cliente['tipo'] == 'fisica' else "Persona Jurídica"
            estado_display = "Activo" if cliente['activo'] else "Inactivo"
            # CORREGIDO: Usar nombre/apellido o razón social en lugar de display_name
            if cliente['tipo'] == 'fisica':
                nombre_display = f"{cliente['nombre']} {cliente['apellido'] or ''}".strip()  
            else:
                nombre_display = cliente['nombre']
            # CORREGIDO: Usar condición IVA legible
            condicion_iva_display = condicion_iva_map.get(
                cliente['condicion_iva'],
                cliente['condicion_iva']
            )      
            self.tree.insert('', tk.END, values=(
                cliente['id'],
                nombre_display,
                cliente['documento'] or '',
                tipo_display,
                condicion_iva_display,  # <-- Condición IVA legible
                cliente['telefono'] or '',
                cliente['email'] or '',
                estado_display
            ))
        
        # Restaurar ordenamiento si existe
        if self.sort_column:
            self.ordenar_columnas(self.sort_column)
   
    def seleccionar_cliente(self, event):
        """Manejar selección de cliente"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            cliente_id = item['values'][0]
            self.cliente_seleccionado = next(
                (c for c in self.clientes if c['id'] == cliente_id), None
            )
   
    def buscar_clientes(self, event=None):
        """Buscar clientes en tiempo real"""
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
        if tipo_seleccionado == "Persona Física":
            filtros['tipo'] = 'fisica'
        elif tipo_seleccionado == "Persona Jurídica":
            filtros['tipo'] = 'juridica'
       
        # Filtro de estado
        estado_seleccionado = self.estado_filter_var.get()
        if estado_seleccionado == "Activos":
            filtros['activo'] = 'true'
        elif estado_seleccionado == "Inactivos":
            filtros['activo'] = 'false'
       
        self.cargar_clientes(filtros)
   
    def nuevo_cliente(self):
        """Abrir formulario para nuevo cliente"""
        FormularioCliente(self.window, self, None)
   
    def editar_cliente(self):
        """Abrir formulario para editar cliente seleccionado"""
        if not self.cliente_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un cliente para editar")
            return
       
        FormularioCliente(self.window, self, self.cliente_seleccionado)
   
    def eliminar_cliente(self):
        """Eliminar cliente seleccionado"""
        if not self.cliente_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor seleccione un cliente para eliminar")
            return
       
        # Obtener nombre del cliente para el mensaje de confirmación
        if self.cliente_seleccionado['tipo'] == 'fisica':
            nombre_cliente = f"{self.cliente_seleccionado['nombre']} {self.cliente_seleccionado['apellido'] or ''}".strip()
        else:
            nombre_cliente = self.cliente_seleccionado['nombre']
       
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar al cliente:\n{nombre_cliente}?"
        )
       
        if confirmacion:
            if self.manager.eliminar_cliente(self.cliente_seleccionado['id']):
                self.cargar_clientes()


class FormularioCliente:
    def __init__(self, parent, clientes_window, cliente_data):
        self.parent = parent
        self.clientes_window = clientes_window
        self.cliente_data = cliente_data
        self.es_nuevo = cliente_data is None
       
        # Mapeo de condición IVA: display -> valor real
        self.condicion_iva_map = {
            "Responsable Inscripto": "ri",
            "Monotributista": "mono",
            "Exento": "exento",
            "Consumidor Final": "cf",
            "No Residente": "noresidente"
        }
       
        # Mapeo inverso para cargar datos
        self.condicion_iva_reverse_map = {
            "ri": "Responsable Inscripto",
            "mono": "Monotributista",
            "exento": "Exento",
            "cf": "Consumidor Final",
            "noresidente": "No Residente"
        }
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Nuevo Cliente" if self.es_nuevo else "Editar Cliente")
        self.window.geometry("500x600")
        self.window.transient(parent)
        self.window.grab_set()
       
        # Configurar icono también para el formulario
        self.set_icon()
       
        self.center_window(500, 600)
       
        # INICIALIZAR VARIABLES CON LA VENTANA COMO MASTER
        self.tipo_var = tk.StringVar(self.window, value="fisica")
        self.nombre_var = tk.StringVar(self.window)
        self.apellido_var = tk.StringVar(self.window)
        self.documento_var = tk.StringVar(self.window)
        self.condicion_iva_var = tk.StringVar(self.window, value="Consumidor Final")  # Valor display
        self.telefono_var = tk.StringVar(self.window)
        self.email_var = tk.StringVar(self.window)
        self.direccion_var = tk.StringVar(self.window)
        self.ciudad_var = tk.StringVar(self.window)
        self.provincia_var = tk.StringVar(self.window)
        self.activo_var = tk.BooleanVar(self.window, value=True)
       
        self.create_widgets()
        if not self.es_nuevo:
            self.cargar_datos()
        else:
            self.actualizar_campos()  # Para nuevo cliente también


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
                        from PIL import Image, ImageTk
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
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
       
        # Tipo de persona
        ttk.Label(main_frame, text="Tipo de Persona:*").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Radiobutton(main_frame, text="Persona Física", variable=self.tipo_var, value="fisica", command=self.actualizar_campos).grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="Persona Jurídica", variable=self.tipo_var, value="juridica", command=self.actualizar_campos).grid(row=0, column=2, sticky=tk.W)
       
        # Nombre
        ttk.Label(main_frame, text="Nombre/Razón Social:*").grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        self.nombre_entry = ttk.Entry(main_frame, textvariable=self.nombre_var, width=40)
        self.nombre_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(10, 5))
       
        # Apellido (solo para persona física)
        ttk.Label(main_frame, text="Apellido:*").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.apellido_entry = ttk.Entry(main_frame, textvariable=self.apellido_var, width=40)
        self.apellido_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(0, 5))
       
        # Documento - VERSIÓN SIMPLIFICADA (sin placeholders complejos)
        ttk.Label(main_frame, text="Documento:").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        self.documento_entry = ttk.Entry(main_frame, textvariable=self.documento_var, width=40)
        self.documento_entry.grid(row=3, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(10, 5))
       
        # Condición IVA - CORREGIDO
        ttk.Label(main_frame, text="Condición IVA:*").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        condicion_iva_combo = ttk.Combobox(main_frame, textvariable=self.condicion_iva_var, state="readonly", width=37)
        condicion_iva_combo['values'] = list(self.condicion_iva_map.keys())  # Usar las claves del mapa
        condicion_iva_combo.grid(row=4, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(10, 5))
       
        # Contacto
        ttk.Label(main_frame, text="Teléfono:").grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        ttk.Entry(main_frame, textvariable=self.telefono_var, width=40).grid(row=5, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(10, 5))
       
        ttk.Label(main_frame, text="Email:").grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.email_var, width=40).grid(row=6, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(0, 5))
       
        # Dirección
        ttk.Label(main_frame, text="Dirección:").grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        ttk.Entry(main_frame, textvariable=self.direccion_var, width=40).grid(row=7, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(10, 5))
       
        ttk.Label(main_frame, text="Ciudad:").grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.ciudad_var, width=40).grid(row=8, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(0, 5))
       
        ttk.Label(main_frame, text="Provincia:").grid(row=9, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.provincia_var, width=40).grid(row=9, column=1, columnspan=2, sticky=tk.W+tk.E, pady=(0, 5))
       
        # Estado
        ttk.Label(main_frame, text="Estado:*").grid(row=10, column=0, sticky=tk.W, pady=(10, 5))
        ttk.Checkbutton(main_frame, text="Activo", variable=self.activo_var).grid(row=10, column=1, sticky=tk.W)
       
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=3, pady=20)
       
        ttk.Button(button_frame, text="💾 Guardar", command=self.guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
       
        # Configurar grid weights
        main_frame.columnconfigure(1, weight=1)
   
    def actualizar_campos(self):
        """Actualizar campos según tipo de persona - VERSIÓN SIMPLIFICADA"""
        if self.tipo_var.get() == "juridica":
            # Persona jurídica: deshabilitar apellido y limpiar
            self.apellido_entry.config(state="disabled")
            self.apellido_var.set("")
        else:
            # Persona física: habilitar apellido
            self.apellido_entry.config(state="normal")
   
    def cargar_datos(self):
        """Cargar datos del cliente en el formulario - VERSIÓN CORREGIDA"""
        if not self.cliente_data:
            return
       
        print("DEBUG - Datos del cliente:")
        print(f"Tipo: {self.cliente_data['tipo']}")
        print(f"Documento: {self.cliente_data['documento']}")
        print(f"Apellido: {self.cliente_data['apellido']}")
        print(f"Condición IVA original: {self.cliente_data['condicion_iva']}")
       
        # Cargar datos
        self.tipo_var.set(self.cliente_data['tipo'])
        self.nombre_var.set(self.cliente_data['nombre'])
        self.apellido_var.set(self.cliente_data['apellido'] or '')
        self.documento_var.set(self.cliente_data['documento'] or '')
       
        # Mapear condición IVA del backend al display
        condicion_iva_display = self.condicion_iva_reverse_map.get(
            self.cliente_data['condicion_iva'],
            "Consumidor Final"
        )
        self.condicion_iva_var.set(condicion_iva_display)
       
        self.telefono_var.set(self.cliente_data['telefono'] or '')
        self.email_var.set(self.cliente_data['email'] or '')
        self.direccion_var.set(self.cliente_data['direccion'] or '')
        self.ciudad_var.set(self.cliente_data['ciudad'] or '')
        self.provincia_var.set(self.cliente_data['provincia'] or '')
        self.activo_var.set(self.cliente_data['activo'])
       
        self.actualizar_campos()
   
    def validar_formulario(self):
        """Validar datos del formulario - VERSIÓN MEJORADA CON DEBUG"""
        # Validar nombre
        if not self.nombre_var.get().strip():
            messagebox.showerror("Error", "El nombre/razón social es obligatorio")
            return False
       
        # Validar apellido solo para persona física
        if self.tipo_var.get() == "fisica":
            if not self.apellido_var.get().strip():
                messagebox.showerror("Error", "El apellido es obligatorio para Persona Física")
                return False
        else:
            # Para persona jurídica, asegurarse de que apellido esté vacío
            if self.apellido_var.get().strip():
                messagebox.showerror("Error", "El apellido no debe completarse para Persona Jurídica")
                return False
       
        # Validar documento
        documento = self.documento_var.get().strip()
        print(f"DEBUG - Validando documento: '{documento}' para tipo: {self.tipo_var.get()}")
       
        if documento:  # Solo validar si hay documento ingresado
            if not documento.isdigit():
                messagebox.showerror("Error", "El documento debe contener solo números")
                return False
           
            if self.tipo_var.get() == "fisica":
                # Persona física: puede tener DNI (8) o CUIT (11)
                if len(documento) not in [8, 11]:
                    messagebox.showerror("Error", f"Para Persona Física, el documento debe tener 8 (DNI) o 11 (CUIT) dígitos. Actual: {len(documento)}")
                    return False
            else:  # Persona jurídica
                # Persona jurídica: solo CUIT (11)
                if len(documento) != 11:
                    messagebox.showerror("Error", f"Para Persona Jurídica, el CUIT debe tener 11 dígitos. Actual: {len(documento)}")
                    return False
       
        print("DEBUG - Validación exitosa")
        return True
   
    def guardar(self):
        """Guardar cliente - VERSIÓN CORREGIDA"""
        print("DEBUG - Iniciando guardado...")
       
        if not self.validar_formulario():
            print("DEBUG - Validación falló")
            return
       
        # Convertir condición IVA de display a valor backend
        condicion_iva_backend = self.condicion_iva_map.get(
            self.condicion_iva_var.get(),
            "cf"  # Valor por defecto
        )
        print(f"DEBUG - Condición IVA (display): {self.condicion_iva_var.get()} -> (backend): {condicion_iva_backend}")
       
        # Preparar datos
        datos = {
            'tipo': self.tipo_var.get(),
            'nombre': self.nombre_var.get().strip(),
            'apellido': self.apellido_var.get().strip() if self.tipo_var.get() == 'fisica' else '',
            'documento': self.documento_var.get().strip() or None,
            'condicion_iva': condicion_iva_backend,  # Usar valor convertido
            'telefono': self.telefono_var.get().strip() or None,
            'email': self.email_var.get().strip() or None,
            'direccion': self.direccion_var.get().strip() or None,
            'ciudad': self.ciudad_var.get().strip() or None,
            'provincia': self.provincia_var.get().strip() or None,
            'pais': 'Argentina',
            'activo': self.activo_var.get()
        }
       
        print(f"DEBUG - Datos a enviar: {datos}")
       
        manager = ClientesManager()
        if self.es_nuevo:
            print("DEBUG - Creando nuevo cliente")
            resultado = manager.crear_cliente(datos)
        else:
            print(f"DEBUG - Actualizando cliente ID: {self.cliente_data['id']}")
            resultado = manager.actualizar_cliente(self.cliente_data['id'], datos)
       
        if resultado:
            print("DEBUG - Guardado exitoso")
            self.clientes_window.cargar_clientes()
            self.window.destroy()
        else:
            print("DEBUG - Error en guardado")