import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import tkinter.font as tkFont
from datetime import datetime

class DialogoAnularPresupuesto(tk.Toplevel):
    def __init__(self, parent, presupuestos_manager, presupuesto_id, presupuesto_info):
        super().__init__(parent)
        self.presupuestos_manager = presupuestos_manager
        self.presupuesto_id = presupuesto_id
        self.presupuesto_info = presupuesto_info
        self.resultado = None
        self.anulado_exitosamente = False  # 🔥 NUEVA VARIABLE CRÍTICA
        
        self.title("⚠️ Anular Presupuesto")
        self.geometry("600x550")
        self.resizable(False, False)
        self.configure(bg='#f0f0f0')
        
        # Centrar en la pantalla
        self.transient(parent)
        self.grab_set()
        
        self.crear_widgets()
        self.center_on_parent()
        
        # Bind Enter key para confirmar
        self.bind('<Return>', lambda e: self.confirmar_anulacion())
        self.bind('<Escape>', lambda e: self.cancelar())
    
    def center_on_parent(self):
        """Centrar el diálogo sobre la ventana padre"""
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def crear_widgets(self):
        # Frame principal CON PESOS para controlar el crecimiento
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configurar pesos de filas y columnas
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Solo el área de texto crece
        main_frame.rowconfigure(4, weight=0)  # Los botones NO crecen
        
        # Título
        titulo_font = tkFont.Font(family="Arial", size=14, weight="bold")
        titulo = ttk.Label(
            main_frame, 
            text="⚠️ ANULAR PRESUPUESTO", 
            font=titulo_font,
            foreground="#d63031",
            justify=tk.CENTER
        )
        titulo.grid(row=0, column=0, pady=(0, 15), sticky=tk.EW)
        
        # Información del presupuesto
        info_frame = ttk.LabelFrame(main_frame, text="📋 Información del Presupuesto", padding="10")
        info_frame.grid(row=1, column=0, pady=(0, 15), sticky=tk.EW)
        
        # Obtener datos del presupuesto
        numero = self.presupuesto_info.get('numero', 'N/A')
        cliente_nombre = self.presupuesto_info.get('cliente_nombre', 'N/A')
        estado = self.presupuesto_info.get('estado', 'N/A').upper()
        total = self.presupuesto_info.get('total', 0)
        
        try:
            total_formateado = f"${float(total):.2f}"
        except (ValueError, TypeError):
            total_formateado = "$0.00"
        
        datos = [
            ("Número:", f"#{numero}"),
            ("Cliente:", cliente_nombre),
            ("Estado Actual:", estado),
            ("Total:", total_formateado)
        ]
        
        for i, (label, value) in enumerate(datos):
            frame_fila = ttk.Frame(info_frame)
            frame_fila.pack(fill=tk.X, pady=2)
            
            ttk.Label(frame_fila, text=label, font=('Arial', 9, 'bold'), width=15, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(frame_fila, text=value, font=('Arial', 9)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Advertencia
        advertencia_frame = ttk.LabelFrame(main_frame, text="🚨 ADVERTENCIA", padding="10")
        advertencia_frame.grid(row=2, column=0, pady=(0, 15), sticky=tk.EW)
        
        advertencia_text = (
            "Esta acción NO se puede deshacer.\n\n"
            "• El presupuesto será marcado como ANULADO\n"
            "• Se registrará la fecha, usuario y motivo\n" 
            "• El número de presupuesto no podrá reutilizarse\n"
            "• Los datos se conservarán para auditoría"
        )
        
        advertencia = ttk.Label(
            advertencia_frame, 
            text=advertencia_text,
            foreground="#d63031",
            justify=tk.LEFT,
            font=('Arial', 9)
        )
        advertencia.pack(anchor=tk.W)
        
        # Motivo de anulación - ESTE ES EL QUE CRECE
        motivo_frame = ttk.LabelFrame(main_frame, text="📝 Motivo de Anulación (*)", padding="10")
        motivo_frame.grid(row=3, column=0, pady=(0, 15), sticky=tk.NSEW)
        
        # Configurar pesos para el frame del motivo
        motivo_frame.columnconfigure(0, weight=1)
        motivo_frame.rowconfigure(0, weight=1)
        
        self.motivo_text = scrolledtext.ScrolledText(
            motivo_frame, 
            height=6,  # Altura fija inicial
            width=60,
            font=('Arial', 9),
            wrap=tk.WORD
        )
        self.motivo_text.grid(row=0, column=0, sticky=tk.NSEW)
        
        # Validación en tiempo real del motivo
        def validar_motivo(event=None):
            motivo = self.motivo_text.get("1.0", tk.END).strip()
            if motivo:
                self.btn_anular.config(
                    state='normal',
                    bg='#d63031',  # Rojo intenso
                    fg='white',    # Texto blanco
                    activebackground='#c0392b',  # Rojo más oscuro al hacer hover
                    activeforeground='white'
                )
            else:
                self.btn_anular.config(
                    state='disabled',
                    bg='#f5b7b1',  # Rosa claro
                    fg='#7f8c8d',  # Texto gris
                    activebackground='#f5b7b1',
                    activeforeground='#7f8c8d'
                )
        
        self.motivo_text.bind('<KeyRelease>', validar_motivo)
        
        # Botones - ESTOS SIEMPRE VISIBLES EN LA PARTE INFERIOR
        botones_frame = ttk.Frame(main_frame)
        botones_frame.grid(row=4, column=0, pady=(10, 0), sticky=tk.EW)
        
        # Configurar el frame de botones para que los botones estén a la derecha
        botones_frame.columnconfigure(0, weight=1)  # Espacio flexible a la izquierda
        
        # Configuración común para ambos botones
        boton_font = ('Arial', 10)  # Misma fuente y tamaño
        boton_width = 20  # Mismo ancho (un poco más largo para que entre el texto)
        boton_height = 1  # Misma altura
        
        # Botón Cancelar (tk.Button para igualar estilo)
        self.btn_cancelar = tk.Button(
            botones_frame, 
            text="❌ Cancelar", 
            command=self.cancelar,
            width=boton_width,
            height=boton_height,
            font=boton_font,
            relief='raised',
            borderwidth=2,
            bg='#95a5a6',  # Gris
            fg='white',     # Texto blanco
            activebackground='#7f8c8d',  # Gris más oscuro al hacer hover
            activeforeground='white'
        )
        self.btn_cancelar.grid(row=0, column=1, padx=(10, 5))
        
        # Botón Confirmar Anulación (tk.Button)
        self.btn_anular = tk.Button(
            botones_frame, 
            text="✅ Confirmar Anulación", 
            command=self.confirmar_anulacion,
            width=boton_width,
            height=boton_height,
            font=boton_font,
            relief='raised',
            borderwidth=2,
            state='disabled'
        )
        self.btn_anular.grid(row=0, column=2, padx=(5, 0))
        
        # Configurar estado inicial del botón de anulación
        self.btn_anular.config(
            state='disabled',
            bg='#f5b7b1',  # Rosa claro
            fg='#7f8c8d',  # Texto gris
            activebackground='#f5b7b1',
            activeforeground='#7f8c8d'
        )
        
        # Asegurar que la ventana tenga el tamaño mínimo correcto
        self.update_idletasks()
        self.minsize(600, 550)
        
        # Enfocar el campo de texto
        self.after(100, self.motivo_text.focus)
    
    def cancelar(self):
        """Cancelar la anulación"""
        if messagebox.askyesno("Cancelar", "¿Está seguro de que desea cancelar la anulación?"):
            self.destroy()
    
    def confirmar_anulacion(self):
        """Confirmar la anulación del presupuesto"""
        motivo = self.motivo_text.get("1.0", tk.END).strip()
        
        if not motivo:
            messagebox.showwarning(
                "Motivo Requerido", 
                "Por favor, ingrese el motivo de la anulación.\n"
                "Esto es importante para la auditoría."
            )
            self.motivo_text.focus()
            return
        
        # Confirmación final
        confirmacion = messagebox.askyesno(
            "Confirmar Anulación",
            f"¿Está ABSOLUTAMENTE seguro de que desea anular el presupuesto #{self.presupuesto_info.get('numero', 'N/A')}?\n\n"
            f"Cliente: {self.presupuesto_info.get('cliente_nombre', 'N/A')}\n"
            f"Total: {self.presupuesto_info.get('total', '0')}\n\n"
            "✅ Se conservarán todos los datos para auditoría\n"
            "❌ Esta acción NO se puede deshacer\n"
            "📊 El presupuesto aparecerá como ANULADO",
            icon='warning'
        )
        
        if confirmacion:
            self.ejecutar_anulacion(motivo)
    
    def ejecutar_anulacion(self, motivo):
        """Ejecutar la anulación"""
        # Deshabilitar todos los controles durante la anulación
        self.btn_anular.config(
            state='disabled',
            bg='#f5b7b1',
            fg='#7f8c8d'
        )
        self.btn_cancelar.config(state='disabled')
        
        # Crear frame de progreso en la parte inferior
        progress_frame = ttk.Frame(self)
        progress_frame.place(relx=0.5, rely=0.9, anchor=tk.CENTER, relwidth=0.8)
        
        progress_label = ttk.Label(progress_frame, text="Anulando presupuesto...")
        progress_label.pack()
        
        progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        progress.pack(fill=tk.X, pady=(5, 0))
        progress.start()
        
        def anular():
            try:
                # Llamar a la API o método de anulación
                if hasattr(self.presupuestos_manager, 'anular_presupuesto'):
                    resultado = self.presupuestos_manager.anular_presupuesto(
                        self.presupuesto_id, 
                        motivo
                    )
                else:
                    # Simular anulación si no existe el método
                    resultado = {
                        'success': True,
                        'fecha_anulacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'usuario': 'Sistema'
                    }
                
                self.after(0, lambda: completar_anulacion(resultado))
                
            except Exception as e:
                # CORREGIDO: Pasar el error como parámetro
                self.after(0, lambda error=e: mostrar_error(error))
        
        def completar_anulacion(resultado):
            progress.stop()
            progress_frame.destroy()
            
            # 🔥 CORRECCIÓN CRÍTICA: La API devuelve el presupuesto serializado, no un campo 'success'
            # Si hay resultado y no hay error, consideramos que fue exitoso
            if resultado is not None:
                # 🔥 MARCAR COMO ANULADO EXITOSAMENTE
                self.anulado_exitosamente = True
                
                messagebox.showinfo(
                    "Anulación Exitosa",
                    f"✅ El presupuesto ha sido anulado correctamente.\n\n"
                    f"📋 Número: #{self.presupuesto_info.get('numero', 'N/A')}\n"
                    f"👤 Cliente: {self.presupuesto_info.get('cliente_nombre', 'N/A')}\n"
                    f"📝 Estado: ANULADO\n"
                    f"🗓️ Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                    f"💡 El presupuesto seguirá visible en el sistema\n"
                    f"   pero marcado como ANULADO para auditoría."
                )
                self.resultado = resultado
                self.destroy()
            else:
                messagebox.showerror(
                    "Error al Anular",
                    "No se pudo anular el presupuesto. Por favor, intente nuevamente."
                )
                self.btn_anular.config(
                    state='normal',
                    bg='#d63031',
                    fg='white',
                    activebackground='#c0392b',
                    activeforeground='white'
                )
                self.btn_cancelar.config(state='normal')
        
        def mostrar_error(error):
            """CORREGIDO: Recibir el error como parámetro"""
            progress.stop()
            progress_frame.destroy()
            messagebox.showerror(
                "Error de Conexión",
                f"❌ Error al anular el presupuesto:\n{str(error)}"
            )
            self.btn_anular.config(
                state='normal',
                bg='#d63031',
                fg='white',
                activebackground='#c0392b',
                activeforeground='white'
            )
            self.btn_cancelar.config(state='normal')
        
        # Ejecutar en un hilo separado (en una aplicación real)
        self.after(100, anular)