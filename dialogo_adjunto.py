# dialogo_adjunto.py - VERSIÓN CON BOTONES MÁS ANCHOS
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime
import webbrowser

class DialogoAdjunto(tk.Toplevel):
    def __init__(self, parent, presupuestos_manager, presupuesto_id, adjunto_existente=None):
        super().__init__(parent)
        self.presupuestos_manager = presupuestos_manager
        self.presupuesto_id = presupuesto_id
        self.adjunto_existente = adjunto_existente
        self.archivo_seleccionado = None
        self.archivo_path = None
        self.adjuntos_existentes = []
       
        self.title("📎 Gestión de Adjuntos - Presupuesto #{}".format(presupuesto_id))
        
        self.geometry("900x600")
        self.minsize(850, 550)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        self.center_window(900, 600)
       
        self.crear_widgets()
        self.cargar_tipos()
        self.cargar_adjuntos_existentes()
       
        if adjunto_existente:
            self.cargar_datos_existentes()

    def center_window(self, width, height):
        """Centrar la ventana en la pantalla"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
   
    def crear_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
       
        # Título principal
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="📎 Gestión de Archivos Adjuntos", 
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        ttk.Label(title_frame, text=f"Presupuesto #{self.presupuesto_id}", 
                 font=('Arial', 10), foreground="gray").pack(side=tk.RIGHT)
        
        # SECCIÓN DE ARCHIVOS EXISTENTES
        lista_frame = ttk.LabelFrame(main_frame, text="📂 Archivos Adjuntos Existentes", padding="10")
        lista_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Frame para el contador y botones de acción
        header_frame = ttk.Frame(lista_frame)
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.contador_label = ttk.Label(header_frame, text="Cargando...", 
                                       font=('Arial', 9, 'bold'))
        self.contador_label.pack(side=tk.LEFT)
        
        action_buttons = ttk.Frame(header_frame)
        action_buttons.pack(side=tk.RIGHT)
        
        # 👇 BOTONES MÁS ANCHOS
        ttk.Button(action_buttons, text="👁️ Ver Detalles", 
                  command=self.ver_archivo_seleccionado, width=20).pack(side=tk.LEFT, padx=(0, 8)) # width=14
        ttk.Button(action_buttons, text="🗑️ Eliminar", 
                  command=self.eliminar_archivo_seleccionado, width=18).pack(side=tk.LEFT, padx=(0, 8)) # width=12
        ttk.Button(action_buttons, text="🔄 Actualizar", 
                  command=self.cargar_adjuntos_existentes, width=18).pack(side=tk.LEFT) # width=12
        
        # Treeview para lista de adjuntos
        self.crear_treeview_adjuntos(lista_frame)
       
        # SECCIÓN: Agregar nuevo archivo
        nuevo_frame = ttk.LabelFrame(main_frame, text="➕ Agregar Nuevo Archivo", padding="10")
        nuevo_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grid para mejor alineación
        nuevo_frame.columnconfigure(1, weight=1)
        
        # Selección de archivo
        ttk.Label(nuevo_frame, text="Archivo:*", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=6, padx=(0, 8))
        
        file_selection_frame = ttk.Frame(nuevo_frame)
        file_selection_frame.grid(row=0, column=1, sticky=tk.W+tk.E, pady=6)
        file_selection_frame.columnconfigure(0, weight=1)
        
        self.archivo_label = ttk.Label(file_selection_frame, text="Ningún archivo seleccionado", 
                                     foreground="gray", font=('Arial', 8))
        self.archivo_label.grid(row=0, column=0, sticky=tk.W+tk.E)
        
        ttk.Button(file_selection_frame, text="📁 Seleccionar...",
                  command=self.seleccionar_archivo, width=14).grid(row=0, column=1, padx=(8, 0))
       
        # Tipo de adjunto
        ttk.Label(nuevo_frame, text="Tipo:*", font=('Arial', 9, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=6, padx=(0, 8))
        
        self.tipo_var = tk.StringVar()
        self.tipo_combo = ttk.Combobox(nuevo_frame, textvariable=self.tipo_var, 
                                      state="readonly", font=('Arial', 9))
        self.tipo_combo.grid(row=1, column=1, sticky=tk.W+tk.E, pady=6)
       
        # Descripción
        ttk.Label(nuevo_frame, text="Descripción:", font=('Arial', 9, 'bold')).grid(
            row=2, column=0, sticky=tk.NW, pady=6, padx=(0, 8))
        
        desc_frame = ttk.Frame(nuevo_frame)
        desc_frame.grid(row=2, column=1, sticky=tk.W+tk.E, pady=6)
        desc_frame.columnconfigure(0, weight=1)
        
        self.descripcion_text = tk.Text(desc_frame, height=3, width=50, font=('Arial', 9))
        self.descripcion_text.grid(row=0, column=0, sticky=tk.NSEW)
        
        # Scrollbar para descripción
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=self.descripcion_text.yview)
        self.descripcion_text.configure(yscrollcommand=desc_scrollbar.set)
        desc_scrollbar.grid(row=0, column=1, sticky=tk.NS)
       
        # BOTONES PRINCIPALES - TAMBIÉN MÁS ANCHOS
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
       
        if not self.adjunto_existente:
            ttk.Button(left_buttons, text="📤 Subir Archivo", style="Accent.TButton",
                      command=self.guardar, width=20).pack(side=tk.LEFT, padx=(0, 10)) # width=16
        else:
            ttk.Button(left_buttons, text="🔄 Actualizar",
                      command=self.actualizar_adjunto, width=14).pack(side=tk.LEFT, padx=(0, 8))
            ttk.Button(left_buttons, text="🗑️ Eliminar",
                      command=self.eliminar_adjunto, width=14).pack(side=tk.LEFT, padx=(0, 8))
           
        ttk.Button(right_buttons, text="❌ Cerrar",
                  command=self.destroy, width=14).pack(side=tk.RIGHT)
        
        # Configurar estilo para botón principal
        style = ttk.Style()
        style.configure("Accent.TButton", font=('Arial', 9, 'bold'))

    def crear_treeview_adjuntos(self, parent):
        """Crear treeview para mostrar archivos adjuntos"""
        # Frame para treeview y scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid para mejor control
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('nombre', 'tipo', 'tamaño', 'fecha', 'descripcion')
        self.tree_adjuntos = ttk.Treeview(tree_frame, columns=columns, show='headings', height=6)
        
        # Configurar columnas
        self.tree_adjuntos.heading('nombre', text='📄 Nombre del Archivo')
        self.tree_adjuntos.heading('tipo', text='📋 Tipo')
        self.tree_adjuntos.heading('tamaño', text='📏 Tamaño')
        self.tree_adjuntos.heading('fecha', text='📅 Fecha Subida')
        self.tree_adjuntos.heading('descripcion', text='📝 Descripción')
        
        # Columnas
        self.tree_adjuntos.column('nombre', width=200, minwidth=150)
        self.tree_adjuntos.column('tipo', width=100, minwidth=80)
        self.tree_adjuntos.column('tamaño', width=80, minwidth=60)
        self.tree_adjuntos.column('fecha', width=120, minwidth=100)
        self.tree_adjuntos.column('descripcion', width=150, minwidth=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_adjuntos.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree_adjuntos.xview)
        self.tree_adjuntos.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree_adjuntos.grid(row=0, column=0, sticky=tk.NSEW)
        v_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        h_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        
        # Bind double click para ver archivo
        self.tree_adjuntos.bind('<Double-1>', lambda e: self.ver_archivo_seleccionado())

    # Los demás métodos se mantienen igual...
    def cargar_adjuntos_existentes(self):
        """Cargar lista de archivos adjuntos existentes"""
        try:
            print(f"🔄 Cargando adjuntos para presupuesto {self.presupuesto_id}...")
            self.adjuntos_existentes = self.presupuestos_manager.obtener_adjuntos(self.presupuesto_id)
           
            # Limpiar treeview
            for item in self.tree_adjuntos.get_children():
                self.tree_adjuntos.delete(item)
           
            # Llenar con datos
            for adjunto in self.adjuntos_existentes:
                descripcion = adjunto.get('descripcion', '')
                if descripcion and len(descripcion) > 40:
                    descripcion = descripcion[:40] + '...'
                
                self.tree_adjuntos.insert('', tk.END, values=(
                    adjunto.get('nombre_original', 'N/A'),
                    adjunto.get('tipo', 'N/A'),
                    adjunto.get('tamaño_formateado', 'N/A'),
                    adjunto.get('fecha_subida', 'N/A'),
                    descripcion
                ))
           
            # Actualizar contador
            total_archivos = len(self.adjuntos_existentes)
            tamaño_total = sum(adjunto.get('tamaño', 0) for adjunto in self.adjuntos_existentes)
            tamaño_mb = tamaño_total / (1024 * 1024)
            
            self.contador_label.config(
                text=f"📊 {total_archivos} archivo(s) - {tamaño_mb:.1f} MB total"
            )
           
            print(f"✅ Cargados {total_archivos} archivos adjuntos ({tamaño_mb:.1f} MB)")
           
        except Exception as e:
            print(f"❌ Error cargando adjuntos: {e}")
            self.contador_label.config(text="❌ Error al cargar archivos")

    def cargar_tipos(self):
        """Cargar tipos de adjuntos disponibles"""
        try:
            tipos_data = self.presupuestos_manager.obtener_tipos_adjunto()
            
            if not tipos_data:
                # Valores por defecto si la API no responde
                tipos_data = [
                    {'codigo': 'factura', 'label': '📄 Factura'},
                    {'codigo': 'contrato', 'label': '📝 Contrato'},
                    {'codigo': 'especificacion', 'label': '📋 Especificación Técnica'},
                    {'codigo': 'diagrama', 'label': '📐 Diagrama'},
                    {'codigo': 'imagen', 'label': '🖼️ Imagen'},
                    {'codigo': 'otro', 'label': '📎 Otro'}
                ]
            
            # Extraer solo las etiquetas para el combobox
            valores = [tipo['label'] for tipo in tipos_data]
            self.tipo_combo['values'] = valores
            
            if valores:
                self.tipo_var.set(valores[0])
                
            print(f"✅ Tipos cargados: {len(valores)} tipos disponibles")
            
        except Exception as e:
            print(f"❌ Error cargando tipos: {e}")
            # En caso de error, cargar valores por defecto
            valores_default = ['📄 Factura', '📝 Contrato', '📋 Especificación', '📐 Diagrama', '🖼️ Imagen', '📎 Otro']
            self.tipo_combo['values'] = valores_default
            if valores_default:
                self.tipo_var.set(valores_default[0])
   
    def cargar_datos_existentes(self):
        """Cargar datos del adjunto existente"""
        if self.adjunto_existente:
            # Para adjuntos existentes, mostrar información pero no permitir cambiar archivo
            nombre_archivo = self.adjunto_existente.get('nombre_original', 'N/A')
            self.archivo_label.config(text=nombre_archivo, foreground="black")
            
            # Cargar tipo y descripción
            tipo_actual = self.adjunto_existente.get('tipo', '')
            # Buscar el label correspondiente al tipo
            tipos_data = self.presupuestos_manager.obtener_tipos_adjunto()
            for tipo in tipos_data:
                if tipo['codigo'] == tipo_actual:
                    self.tipo_var.set(tipo['label'])
                    break
            
            self.descripcion_text.insert('1.0', self.adjunto_existente.get('descripcion', ''))
   
    def seleccionar_archivo(self):
        """Seleccionar archivo del sistema"""
        if self.adjunto_existente:
            messagebox.showinfo("Información", "No se puede cambiar el archivo de un adjunto existente")
            return
       
        archivo_path = filedialog.askopenfilename(
            title="Seleccionar archivo para adjuntar",
            filetypes=[
                ("Todos los archivos", "*.*"),
                ("Documentos PDF", "*.pdf"),
                ("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Documentos Word", "*.doc *.docx"),
                ("Documentos Excel", "*.xls *.xlsx"),
                ("Archivos DWG", "*.dwg"),
                ("Archivos de texto", "*.txt"),
            ]
        )
       
        if archivo_path:
            self.archivo_path = archivo_path
            nombre_archivo = os.path.basename(archivo_path)
            tamaño = os.path.getsize(archivo_path) / 1024  # Tamaño en KB
            
            self.archivo_label.config(
                text=f"{nombre_archivo} ({tamaño:.1f} KB)", 
                foreground="black"
            )
            print(f"✅ Archivo seleccionado: {nombre_archivo} ({tamaño:.1f} KB)")

    def obtener_codigo_tipo(self, tipo_label):
        """Obtener el código del tipo a partir del label - DEBUG COMPLETO"""
        try:
            print(f"🔍 DEBUG OBTENER_CODIGO_TIPO INICIO:")
            print(f"   tipo_label recibido: '{tipo_label}'")
            print(f"   tipo_label tipo: {type(tipo_label)}")
            
            # Obtener tipos de la API
            tipos_data = self.presupuestos_manager.obtener_tipos_adjunto()
            print(f"   Tipos disponibles desde API ({len(tipos_data)}):")
            for i, tipo in enumerate(tipos_data):
                print(f"     {i+1}. codigo='{tipo.get('codigo')}', label='{tipo.get('label')}'")
            
            # Buscar coincidencia exacta
            encontrado = False
            for tipo in tipos_data:
                if tipo.get('label') == tipo_label:
                    codigo = tipo.get('valor')
                    print(f"   ✅ COINCIDENCIA EXACTA: '{tipo_label}' -> '{codigo}'")
                    encontrado = True
                    return codigo
            
            if not encontrado:
                print(f"   ❌ NO HAY COINCIDENCIA EXACTA para: '{tipo_label}'")
                print(f"   🔍 Buscando coincidencia parcial...")
                
                # Buscar por contenido
                for tipo in tipos_data:
                    if tipo_label in tipo.get('label', '') or tipo.get('label', '') in tipo_label:
                        codigo = tipo.get('codigo')
                        print(f"   ✅ COINCIDENCIA PARCIAL: '{tipo_label}' en '{tipo.get('label')}' -> '{codigo}'")
                        return codigo
                
                print(f"   ❌ NO HAY COINCIDENCIA PARCIAL")
                print(f"   🎯 Asignando 'otro' por defecto")
                return 'otro'
                
        except Exception as e:
            print(f"❌ Error en obtener_codigo_tipo: {e}")
            return 'otro'

    def ver_archivo_seleccionado(self):
        """Ver el archivo adjunto seleccionado en la lista"""
        selection = self.tree_adjuntos.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un archivo para ver")
            return
        
        item_index = self.tree_adjuntos.index(selection[0])
        if item_index < len(self.adjuntos_existentes):
            adjunto = self.adjuntos_existentes[item_index]
            
            # Crear ventana de detalles
            detalles_window = tk.Toplevel(self)
            detalles_window.title("Detalles del Archivo")
            detalles_window.geometry("500x400")
            detalles_window.transient(self)
            detalles_window.grab_set()
            
            # Frame principal
            main_frame = ttk.Frame(detalles_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="📄 Detalles del Archivo", 
                     font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=(0, 15))
            
            # Información en formato de lista
            info_text = f"""
📋 Información del Archivo:

📄 Nombre: {adjunto.get('nombre_original', 'N/A')}
🔧 Tipo: {adjunto.get('tipo', 'N/A')}
📏 Tamaño: {adjunto.get('tamaño_formateado', 'N/A')}
📅 Fecha de subida: {adjunto.get('fecha_subida', 'N/A')}
👤 Subido por: {adjunto.get('subido_por_nombre', 'N/A')}

📝 Descripción:
{adjunto.get('descripcion', 'Sin descripción')}

🔗 URL: {adjunto.get('archivo', 'No disponible')}
            """.strip()
            
            text_widget = tk.Text(main_frame, height=15, width=60, font=('Arial', 10))
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert('1.0', info_text)
            text_widget.config(state=tk.DISABLED)
            
            # Botones
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(15, 0))
            
            ttk.Button(button_frame, text="🔗 Abrir en Navegador",
                      command=lambda: self.abrir_en_navegador(adjunto.get('archivo'))).pack(side=tk.LEFT)
            ttk.Button(button_frame, text="❌ Cerrar",
                      command=detalles_window.destroy).pack(side=tk.RIGHT)

    def abrir_en_navegador(self, url):
        """Abrir URL en navegador"""
        if url and url.startswith('http'):
            webbrowser.open(url)
        else:
            messagebox.showinfo("Información", "URL no disponible para este archivo")

    def eliminar_archivo_seleccionado(self):
        """Eliminar el archivo adjunto seleccionado en la lista"""
        selection = self.tree_adjuntos.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un archivo para eliminar")
            return
        
        item_index = self.tree_adjuntos.index(selection[0])
        if item_index < len(self.adjuntos_existentes):
            adjunto = self.adjuntos_existentes[item_index]
            
            confirmacion = messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Está seguro de que desea eliminar el archivo:\n"
                f"'{adjunto.get('nombre_original', 'N/A')}'?\n\n"
                f"📏 Tamaño: {adjunto.get('tamaño_formateado', 'N/A')}\n"
                f"📅 Subido: {adjunto.get('fecha_subida', 'N/A')}\n\n"
                f"⚠️  Esta acción no se puede deshacer."
            )
           
            if confirmacion:
                try:
                    adjunto_id = adjunto.get('id')
                    if adjunto_id:
                        print(f"🗑️ Intentando eliminar adjunto ID: {adjunto_id} del presupuesto: {self.presupuesto_id}")
                        self.presupuestos_manager.eliminar_adjunto(adjunto_id, self.presupuesto_id)
                        messagebox.showinfo("Éxito", "✅ Archivo eliminado correctamente")
                        self.cargar_adjuntos_existentes()
                    else:
                        messagebox.showerror("Error", "No se pudo obtener el ID del adjunto")
                except Exception as e:
                    error_msg = str(e)
                    print(f"❌ Error eliminando adjunto: {error_msg}")
                    messagebox.showerror("Error", f"No se pudo eliminar el archivo:\n{error_msg}")
   
    def guardar(self):
        """Subir nuevo archivo adjunto"""
        try:
            # Validaciones
            if not self.archivo_path:
                messagebox.showerror("Error", "Debe seleccionar un archivo")
                return
               
            if not os.path.exists(self.archivo_path):
                messagebox.showerror("Error", "El archivo seleccionado no existe")
                return
           
            tipo_label = self.tipo_var.get()
            if not tipo_label:
                messagebox.showerror("Error", "Debe seleccionar un tipo de archivo")
                return
            
            # Obtener código del tipo
            tipo_codigo = self.obtener_codigo_tipo(tipo_label)
            descripcion = self.descripcion_text.get('1.0', tk.END).strip()
            
            print(f"📤 Subiendo archivo: {self.archivo_path}")
            print(f"📋 Tipo: {tipo_codigo}")
            print(f"📝 Descripción: {descripcion}")
            
            # Subir archivo
            resultado = self.presupuestos_manager.agregar_adjunto(
                self.presupuesto_id,
                self.archivo_path,
                tipo_codigo,
                descripcion
            )
            
            if resultado:
                messagebox.showinfo("Éxito", f"✅ Archivo subido correctamente:\n{os.path.basename(self.archivo_path)}")
                # Limpiar formulario y recargar lista
                self.archivo_path = None
                self.archivo_label.config(text="Ningún archivo seleccionado", foreground="gray")
                self.descripcion_text.delete('1.0', tk.END)
                self.cargar_adjuntos_existentes()
            else:
                messagebox.showerror("Error", "❌ No se pudo subir el archivo")
           
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al subir archivo:\n{str(e)}")
            print(f"❌ Error en guardar: {e}")
   
    def actualizar_adjunto(self):
        """Actualizar adjunto existente (solo descripción y tipo)"""
        try:
            tipo_label = self.tipo_var.get()
            if not tipo_label:
                messagebox.showerror("Error", "Debe seleccionar un tipo")
                return
            
            tipo_codigo = self.obtener_codigo_tipo(tipo_label)
            descripcion = self.descripcion_text.get('1.0', tk.END).strip()
            
            # Aquí deberías implementar la actualización si tu API lo permite
            messagebox.showinfo("Información", 
                              "La edición de adjuntos existentes requiere funcionalidad adicional en la API.\n\n"
                              "Para cambiar el archivo, elimine este adjunto y agregue uno nuevo.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {e}")
   
    def eliminar_adjunto(self):
        """Eliminar adjunto existente"""
        if not self.adjunto_existente:
            return
            
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar el archivo:\n"
            f"'{self.adjunto_existente.get('nombre_original', 'N/A')}'?\n\n"
            f"⚠️  Esta acción no se puede deshacer."
        )
       
        if confirmacion:
            try:
                adjunto_id = self.adjunto_existente.get('id')
                if adjunto_id:
                    self.presupuestos_manager.eliminar_adjunto(adjunto_id, self.presupuesto_id)
                    messagebox.showinfo("Éxito", "Archivo eliminado correctamente")
                    self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el archivo: {e}")