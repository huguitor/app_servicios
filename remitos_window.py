# /app_escritorio/remitos_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from remitos_manager import RemitosManager
from clientes_manager import ClientesManager
import os
from PIL import Image, ImageTk
from remitos_formulario import FormularioRemito
from dialogo_adjunto import DialogoAdjunto
from styles import Styles




class RemitosWindow:
    def __init__(self, parent):
        self.parent = parent
        self.manager = RemitosManager()
        self.clientes_manager = ClientesManager()
       
        self.remitos = []
        self.clientes = []
        self.remito_seleccionado = None
       
        # Variables para ordenamiento
        self.sort_column = None
        self.sort_reverse = False
       
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Remitos - Lab Servicios")
       
        # Color coding
        module_color = Styles.get_module_style("presupuestos")  # Mismo color que presupuestos
        self.header_strip = tk.Frame(self.window, bg=module_color, height=5)
        self.header_strip.pack(fill=tk.X, side=tk.TOP)
       
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
        self.cargar_remitos()
   
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
            # Filtrar solo activos
            self.clientes = [c for c in self.clientes if c.get('activo', True)]
            print(f"✅ Clientes cargados para filtros: {len(self.clientes)}")
           
            # Actualizar combobox
            nombres_clientes = []
            for cliente in self.clientes:
                if cliente.get('tipo') == 'fisica':
                    nombre = f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}".strip()
                else:
                    nombre = cliente.get('nombre', 'Cliente sin nombre')
                nombres_clientes.append(nombre)
           
            self.cliente_filter['values'] = ['Todos'] + nombres_clientes
            self.cliente_filter.set('Todos')
           
        except Exception as e:
            print(f"Error cargando datos para combobox: {e}")
            self.clientes = []
   
    def obtener_nombre_cliente(self, cliente):
        """Obtener nombre completo del cliente según su tipo"""
        if not cliente:
            return "Cliente no disponible"
       
        if cliente.get('tipo') == 'fisica':
            return f"{cliente.get('nombre', '')} {cliente.get('apellido', '')}".strip()
        else:
            return cliente.get('nombre', 'Cliente sin nombre')
   
    def create_widgets(self):
        """Crear todos los widgets de la ventana"""
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
        self.search_entry.bind('<KeyRelease>', self.buscar_remitos)
       
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
            values=["Todos", "Borrador", "Pendiente", "Entregado", "Anulado"],
            state="readonly",
            width=12
        )
        self.estado_filter.set("Todos")
        self.estado_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.estado_filter.bind('<<ComboboxSelected>>', self.aplicar_filtros)
       
        # Botones
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(side=tk.RIGHT)
       
        ttk.Button(button_frame, text="➕ Nuevo Remito",
                  command=self.nuevo_remito).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="✏️ Editar",
                  command=self.editar_remito).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="👁️ Ver",
                  command=self.ver_remito).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📎 Adjuntos",
                  command=self.gestionar_adjuntos).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🖨️ Imprimir",
                  command=self.imprimir_remito).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="❌ Anular",
                  command=self.anular_remito).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🔄 Recargar",
                  command=self.cargar_remitos).pack(side=tk.LEFT, padx=2)
       
        # Treeview para lista de remitos
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
       
        columns = ('id', 'numero', 'cliente', 'fecha_emision', 'origen_destino', 'estado', 'items_count')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
       
        # Configurar columnas con bindings para ordenamiento
        column_configs = [
            ('id', 'ID', 50),
            ('numero', 'Número', 100),
            ('cliente', 'Cliente', 200),
            ('fecha_emision', 'Fecha Emisión', 100),
            ('origen_destino', 'Origen → Destino', 200),
            ('estado', 'Estado', 90),
            ('items_count', 'Ítems', 60)
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
        self.tree.bind('<<TreeviewSelect>>', self.seleccionar_remito)
        self.tree.bind('<Double-1>', lambda e: self.ver_remito())
   
    def ordenar_columnas(self, col):
        """Ordenar columnas al hacer clic en el encabezado"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
       
        # Obtener todos los elementos del treeview
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
       
        # Ordenar según el tipo de dato
        try:
            # Intentar ordenar como número
            items.sort(key=lambda t: float(t[0]) if t[0] else 0, reverse=self.sort_reverse)
        except ValueError:
            # Ordenar como texto
            items.sort(key=lambda t: t[0], reverse=self.sort_reverse)
       
        # Reorganizar elementos en el treeview
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)
       
        # Actualizar encabezados para mostrar dirección de ordenamiento
        self.actualizar_encabezados()
   
    def actualizar_encabezados(self):
        """Actualizar encabezados para mostrar dirección de ordenamiento"""
        for col in self.tree['columns']:
            heading = self.tree.heading(col)['text']
            # Remover flechas existentes
            if heading.endswith(' ↑') or heading.endswith(' ↓'):
                heading = heading[:-2]
           
            # Agregar flecha si es la columna ordenada
            if col == self.sort_column:
                arrow = ' ↑' if not self.sort_reverse else ' ↓'
                heading += arrow
           
            self.tree.heading(col, text=heading)
   
    def seleccionar_remito(self, event):
        """Manejar selección de remito en el treeview"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            remito_id = item['values'][0]
           
            # Buscar el remito en la lista
            for remito in self.remitos:
                if remito['id'] == remito_id:
                    self.remito_seleccionado = remito
                    break
        else:
            self.remito_seleccionado = None
   
    def cargar_remitos(self, filtros=None):
        """Cargar lista de remitos"""
        print("🔄 Cargando lista de remitos...")
       
        try:
            self.remitos = self.manager.obtener_remitos(filtros)
            print(f"✅ {len(self.remitos)} remitos cargados")
           
            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
           
            # Agregar remitos al treeview
            for remito in self.remitos:
                # Buscar nombre del cliente
                cliente_nombre = "Cliente no encontrado"
                for cliente in self.clientes:
                    if cliente['id'] == remito.get('cliente'):
                        cliente_nombre = self.obtener_nombre_cliente(cliente)
                        break
               
                # Formatear fecha
                fecha_emision = remito.get('fecha_emision', '')
                if fecha_emision and 'T' in fecha_emision:
                    fecha_emision = fecha_emision.split('T')[0]
               
                # Origen y destino
                origen = remito.get('origen', '')[:30]
                destino = remito.get('destino', '')[:30]
                origen_destino = f"{origen} → {destino}" if origen or destino else ""
               
                # Estado con color
                estado = remito.get('estado', 'borrador').capitalize()
               
                # Número de items
                items_count = len(remito.get('items', []))
               
                # Insertar en treeview
                values = (
                    remito['id'],
                    remito.get('numero_formateado', ''),
                    cliente_nombre[:50],
                    fecha_emision,
                    origen_destino,
                    estado,
                    items_count
                )
               
                item_id = self.tree.insert('', tk.END, values=values)
               
                # Colorear según estado
                estado_lower = remito.get('estado', 'borrador')
                if estado_lower == 'anulado':
                    self.tree.item(item_id, tags=('anulado',))
                elif estado_lower == 'entregado':
                    self.tree.item(item_id, tags=('entregado',))
                elif estado_lower == 'pendiente':
                    self.tree.item(item_id, tags=('pendiente',))
                else:  # borrador
                    self.tree.item(item_id, tags=('borrador',))
           
            # Configurar tags para colores
            self.tree.tag_configure('anulado', foreground='#d63031')
            self.tree.tag_configure('entregado', foreground='#27ae60')
            self.tree.tag_configure('pendiente', foreground='#f39c12')
            self.tree.tag_configure('borrador', foreground='#7f8c8d')
           
        except Exception as e:
            print(f"❌ Error cargando remitos: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los remitos: {str(e)}")
   
    def buscar_remitos(self, event=None):
        """Buscar remitos según texto ingresado"""
        search_text = self.search_var.get().lower().strip()
        cliente_filter = self.cliente_filter_var.get()
        estado_filter = self.estado_filter_var.get()
       
        # Construir filtros
        filtros = {}
       
        if search_text:
            filtros['search'] = search_text
       
        if estado_filter and estado_filter != "Todos":
            filtros['estado'] = estado_filter.lower()
       
        # Aplicar filtros
        self.cargar_remitos(filtros if filtros else None)
   
    def aplicar_filtros(self, event=None):
        """Aplicar filtros seleccionados"""
        self.buscar_remitos()
   
    def nuevo_remito(self):
        """Abrir formulario para nuevo remito"""
        print("➕ Abriendo formulario para nuevo remito...")
        FormularioRemito(self.window, self, None, solo_lectura=False)
   
    def editar_remito(self):
        """Editar remito seleccionado"""
        if not self.remito_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un remito para editar")
            return
       
        # Verificar si está anulado
        if self.remito_seleccionado.get('estado') == 'anulado':
            messagebox.showinfo("Remito Anulado",
                              "No se puede editar un remito anulado.\n\n"
                              "Los remitos anulados son de solo lectura para auditoría.")
            return
       
        print(f"✏️ Editando remito ID: {self.remito_seleccionado['id']}")
        FormularioRemito(self.window, self, self.remito_seleccionado, solo_lectura=False)
   
    def ver_remito(self):
        """Ver remito seleccionado en modo solo lectura"""
        if not self.remito_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un remito para ver")
            return
       
        print(f"👁️ Viendo remito ID: {self.remito_seleccionado['id']}")
        FormularioRemito(self.window, self, self.remito_seleccionado, solo_lectura=True)
   
    def gestionar_adjuntos(self):
        """Abrir gestión de adjuntos del remito seleccionado"""
        if not self.remito_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un remito para gestionar adjuntos")
            return
       
        remito_id = self.remito_seleccionado['id']
        print(f"📎 Abriendo gestión de adjuntos para remito ID: {remito_id}")
       
        try:
            dialogo = DialogoAdjunto(self.window, self.manager, remito_id, titulo="Remito")
        except Exception as e:
            print(f"❌ Error abriendo diálogo de adjuntos: {e}")
            messagebox.showerror("Error", f"No se pudo abrir la gestión de adjuntos: {str(e)}")
   
    # En remitos_window.py, modifica el método imprimir_remito:
    def imprimir_remito(self):
        """Generar PDF del remito seleccionado"""
        if not self.remito_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un remito para generar PDF")
            return
        
        print(f"🖨️ Generando PDF para remito ID: {self.remito_seleccionado['id']}")
        
        # Importar el generador de PDF
        from pdf_generator_remitos import generar_remito_pdf
        
        try:
            # Obtener datos del cliente
            cliente_id = self.remito_seleccionado.get('cliente')
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
            resultado = generar_remito_pdf(self.remito_seleccionado, cliente_data)
            
            if resultado:
                print(f"✅ PDF generado exitosamente: {resultado}")
            else:
                print("❌ No se pudo generar el PDF")
                
        except Exception as e:
            print(f"❌ Error generando PDF: {e}")
            messagebox.showerror("Error", f"No se pudo generar el PDF: {str(e)}")
        
    def anular_remito(self):
        """Anular remito seleccionado"""
        if not self.remito_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un remito para anular")
            return
       
        remito_id = self.remito_seleccionado['id']
        remito_numero = self.remito_seleccionado.get('numero_formateado', 'N/A')
       
        # Verificar si ya está anulado
        if self.remito_seleccionado.get('estado') == 'anulado':
            messagebox.showinfo("Información", "Este remito ya está anulado")
            return
       
        # Verificar si puede ser anulado
        puede_anular, mensaje = self.manager.puede_anular_remito(self.remito_seleccionado)
        if not puede_anular:
            messagebox.showwarning("No se puede anular", mensaje)
            return
       
        # Confirmar anulación
        confirmacion = messagebox.askyesno(
            "Confirmar Anulación",
            f"¿Está seguro que desea ANULAR el remito {remito_numero}?\n\n"
            f"Cliente: {self.obtener_nombre_cliente(self.remito_seleccionado.get('cliente_info', {}))}\n\n"
            f"⚠️ Esta acción NO se puede deshacer.\n"
            f"El remito quedará marcado como ANULADO y será de solo lectura."
        )
       
        if not confirmacion:
            return
       
        # Pedir motivo de anulación
        motivo = simpledialog.askstring(
            "Motivo de anulación",
            "Ingrese el motivo de la anulación (opcional):",
            parent=self.window
        )
       
        try:
            print(f"❌ Anulando remito ID: {remito_id}")
            resultado = self.manager.anular_remito(remito_id, motivo or "")
           
            if resultado:
                messagebox.showinfo("Éxito", f"Remito {remito_numero} anulado correctamente")
                # Recargar lista
                self.cargar_remitos()
            else:
                messagebox.showerror("Error", "No se pudo anular el remito")
               
        except Exception as e:
            print(f"❌ Error anulando remito: {e}")
            messagebox.showerror("Error", f"No se pudo anular el remito: {str(e)}")
   
    def actualizar_lista(self):
        """Actualizar la lista de remitos (alias para recargar)"""
        self.cargar_remitos()
   
    def destroy(self):
        """Cerrar ventana"""
        self.window.destroy()