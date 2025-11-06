# app_escritorio/pdf_generator.py
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from decimal import Decimal

# Importaciones de ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
   
    def _setup_custom_styles(self):
        """Configurar estilos personalizados"""
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='PresupuestoTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1,  # Centrado
            textColor=colors.navy
        ))
       
        # Estilo para información de empresa
        self.styles.add(ParagraphStyle(
            name='EmpresaInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.darkblue
        ))

    def _sanitizar_datos_presupuesto(self, presupuesto_data):
        """Sanitizar y convertir tipos de datos del presupuesto"""
        try:
            # Crear copia para no modificar el original
            sanitized = presupuesto_data.copy()
           
            # Convertir items
            if 'items' in sanitized:
                for item in sanitized['items']:
                    # Convertir cantidad a entero
                    if 'cantidad' in item:
                        if isinstance(item['cantidad'], str):
                            item['cantidad'] = int(float(item['cantidad']))
                        elif isinstance(item['cantidad'], float):
                            item['cantidad'] = int(item['cantidad'])
                   
                    # Convertir precio a float
                    if 'precio_unitario' in item:
                        if isinstance(item['precio_unitario'], str):
                            item['precio_unitario'] = float(item['precio_unitario'])
           
            # Asegurar que los totales sean números
            numeric_fields = ['subtotal', 'iva_valor', 'total', 'iva_porcentaje']
            for field in numeric_fields:
                if field in sanitized and isinstance(sanitized[field], str):
                    try:
                        sanitized[field] = float(sanitized[field])
                    except (ValueError, TypeError):
                        sanitized[field] = 0.0
           
            return sanitized
           
        except Exception as e:
            print(f"⚠️ Error sanitizando datos: {e}")
            return presupuesto_data

    def generar_presupuesto(self, presupuesto_data, cliente_data):
        """Generar PDF del presupuesto"""
        try:
            # SANITIZAR DATOS ANTES DE USAR
            presupuesto_data = self._sanitizar_datos_presupuesto(presupuesto_data)
           
            # Pedir ubicación para guardar
            output_path = self._get_save_path(presupuesto_data, cliente_data)
            if not output_path:
                return None  # Usuario canceló
            
                    # Función para crear el pie de página en cada página
            def add_footer(canvas, doc):
                canvas.saveState()
                
                # Configurar el pie de página
                footer_text = "LAB SERVICIOS SAS - Tel: +54 2995576550 - Email: info@labservicios.com"
                
                # Posicionar en la parte inferior
                canvas.setFont('Helvetica', 8)
                canvas.setFillColor(colors.gray)
                
                # Centrar el texto en la parte inferior
                page_width = A4[0]
                text_width = canvas.stringWidth(footer_text, 'Helvetica', 8)
                x_position = (page_width - text_width) / 2
                
                # Dibujar el pie de página
                canvas.drawString(x_position, 30, footer_text)
                
                canvas.restoreState()
           
            # Crear documento
            doc = SimpleDocTemplate(
                output_path, 
                pagesize=A4, 
                topMargin=40, 
                bottomMargin=60, 
                leftMargin=40, 
                rightMargin=40
            )
            
            story = []
           
            # 1. ENCABEZADO
            story.extend(self._build_header(presupuesto_data))
           
            # 2. INFORMACIÓN DEL CLIENTE
            story.extend(self._build_cliente_section(cliente_data, presupuesto_data))
           
            # 3. ITEMS DEL PRESUPUESTO
            story.extend(self._build_items_section(presupuesto_data))
           
            # 4. TOTALES
            story.extend(self._build_totales_section(presupuesto_data))
           
            # 5. OBSERVACIONES Y CONDICIONES
            story.extend(self._build_observaciones_section(presupuesto_data))
           
            # 6. PIE DE PÁGINA
            #story.extend(self._build_footer())
           
            # Generar PDF CON FOOTER EN CADA PÁGINA
            doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
           
            # Mostrar mensaje de éxito
            messagebox.showinfo(
                "PDF Generado",
                f"Presupuesto guardado como PDF:\n{os.path.basename(output_path)}"
            )
           
            # Abrir el PDF automáticamente
            self._abrir_pdf(output_path)
           
            return output_path
           
        except Exception as e:
            messagebox.showerror(
                "Error al generar PDF",
                f"No se pudo generar el PDF:\n{str(e)}"
            )
            return None
    def _build_footer(self):
        """Método vacío ya que el footer se maneja en cada página"""
        return []  # 🔥 DEVOLVER LISTA VACÍA

    def _get_save_path(self, presupuesto_data, cliente_data):
        """Obtener ruta para guardar el archivo"""
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
       
        numero = presupuesto_data.get('numero', '')
        cliente_nombre = cliente_data.get('nombre', '').replace(' ', '_')
        fecha = datetime.now().strftime('%Y%m%d_%H%M')
       
        default_name = f"Presupuesto_{numero}_{cliente_nombre}_{fecha}.pdf"
       
        return filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
            initialfile=default_name,
            title="Guardar presupuesto como PDF"
        )

    def _build_header(self, presupuesto_data):
        """Construir encabezado con número de presupuesto destacado"""
        elements = []
        
        try:
            from reportlab.platypus import Image
            logo_path = "logoLAB_form.jpg"
            logo = Image(logo_path, width=80, height=40)
        except Exception as e:
            print(f"⚠️ Logo no encontrado: {e}")
            logo = "LAB SERVICIOS"
        
        # 🔥 FORMATEAR NÚMERO CON 5 DÍGITOS - VERSIÓN SEGURA
        numero_presupuesto = presupuesto_data.get('numero', '')
        
        try:
            # Intentar convertir a número y formatear
            if numero_presupuesto:
                numero_int = int(numero_presupuesto)
                numero_formateado = f"{numero_int:05d}"
            else:
                numero_formateado = "00000"
        except (ValueError, TypeError):
            # Si hay error, usar el valor original
            numero_formateado = str(numero_presupuesto) if numero_presupuesto else "00000"
            print(f"⚠️ No se pudo formatear número de presupuesto: {numero_presupuesto}")
        
        header_data = [
            [
                logo,
                "\nLAB SERVICIOS SAS\nCUIT: 20-12345678-9",
                # 🔥 TEXTO MÁS GRANDE Y DESTACADO
                f"PRESUPUESTO N° {numero_formateado}\nFecha: {datetime.now().strftime('%d/%m/%Y')}"
            ]
        ]
        
        header_table = Table(header_data, colWidths=[80, 280, 140])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTSIZE', (2, 0), (2, 0), 12),           # 🔥 TEXTO MÁS GRANDE
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),  # 🔥 NEGRITA
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        return elements
    def _build_cliente_section(self, cliente_data, presupuesto_data):
        """Construir sección de información del cliente"""
        elements = []
       
        # Título de sección
        section_title = Paragraph("DATOS DEL CLIENTE", self.styles['Heading2'])
        elements.append(section_title)
        elements.append(Spacer(1, 8))
       
        # Información del cliente
        cliente_nombre = f"{cliente_data.get('nombre', '')} {cliente_data.get('apellido', '')}".strip()
        cliente_info = [
            ["Cliente:", cliente_nombre],
            ["CUIT:", cliente_data.get('documento', 'No especificado')],
            ["Condición IVA:", self._get_condicion_iva_display(cliente_data.get('condicion_iva', ''))],
            ["Teléfono:", cliente_data.get('telefono', 'No especificado')],
            ["Email:", cliente_data.get('email', 'No especificado') or 'No especificado'],
            ["Dirección:", cliente_data.get('direccion', 'No especificado')],
        ]
       
        cliente_table = Table(cliente_info, colWidths=[100, 400])
        cliente_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAFC')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        elements.append(cliente_table)
        elements.append(Spacer(1, 15))
       
        return elements

    def _build_items_section(self, presupuesto_data):
        """Construir sección de items del presupuesto"""
        elements = []
       
        # Título de sección
        section_title = Paragraph("DETALLE DEL PRESUPUESTO", self.styles['Heading2'])
        elements.append(section_title)
        elements.append(Spacer(1, 8))
       
        # Encabezado de la tabla
        items_header = ['Código', 'Descripción', 'Cant.', 'Precio Unit.', 'Subtotal']
        items_data = [items_header]
       
        # Procesar cada item
        for item in presupuesto_data.get('items', []):
            cantidad = item.get('cantidad', 0)
            precio_unitario = Decimal(str(item.get('precio_unitario', 0)))
            subtotal = cantidad * precio_unitario
           
            items_data.append([
                item.get('codigo', ''),
                item.get('descripcion', ''),
                str(cantidad),
                f"${precio_unitario:,.2f}",
                f"${subtotal:,.2f}"
            ])
       
        # Crear tabla de items
        items_table = Table(items_data, colWidths=[70, 240, 40, 80, 80])
        items_table.setStyle(TableStyle([
            # Estilo del encabezado
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # 🔥 CENTRAR ENCABEZADOS
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
           
            # Alineación
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),   # 🔥 Código centrado
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),   # 🔥 Cantidad centrada
           
            # Bordes y grid
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
           
            # Alternar colores de fila para mejor lectura
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 15))
       
        return elements

    def _build_totales_section(self, presupuesto_data):
        """Construir sección de totales - VERSIÓN MEJORADA"""
        elements = []
    
        subtotal = Decimal(str(presupuesto_data.get('subtotal', 0)))
        iva_porcentaje = Decimal(str(presupuesto_data.get('iva_porcentaje', 21)))
        iva_valor = Decimal(str(presupuesto_data.get('iva_valor', 0)))
        total = Decimal(str(presupuesto_data.get('total', 0)))
    
        totales_data = [
            ["", ""],  # Espacio en blanco para separación
            ["SUBTOTAL:", f"${subtotal:,.2f}"],
            [f"IVA ({iva_porcentaje}%):", f"${iva_valor:,.2f}"],
            ["TOTAL:", f"${total:,.2f}"]
        ]
    
        totales_table = Table(totales_data, colWidths=[250, 150])  # 🔥 MÁS ANCHO
        totales_table.setStyle(TableStyle([
            # Primera fila (espacio en blanco)
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            
            # Etiquetas (columna izquierda)
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 12),
            ('ALIGN', (0, 1), (0, -1), 'RIGHT'),  # 🔥 ETIQUETAS a la DERECHA
            ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
            
            # Valores (columna derecha)
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 1), (1, -1), 12),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # 🔥 VALORES a la DERECHA
            ('VALIGN', (1, 1), (1, -1), 'MIDDLE'),
            
            # Total (última fila)
            ('FONTSIZE', (-1, -1), (-1, -1), 14),
            ('BACKGROUND', (-1, -1), (-1, -1), colors.HexColor('#10B981')),
            ('TEXTCOLOR', (-1, -1), (-1, -1), colors.white),
            ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(totales_table)
        elements.append(Spacer(1, 20))
    
        return elements

    def _build_observaciones_section(self, presupuesto_data):
        """Construir sección de observaciones y condiciones"""
        elements = []
        
        # Observaciones (se mantiene igual)
        if presupuesto_data.get('observaciones'):
            obs_title = Paragraph("OBSERVACIONES", self.styles['Heading2'])
            elements.append(obs_title)
            elements.append(Spacer(1, 5))
            
            observaciones = presupuesto_data.get('observaciones', '').replace('\n', '<br/>')
            obs_text = Paragraph(observaciones, self.styles['Normal'])
            elements.append(obs_text)
            elements.append(Spacer(1, 10))
        
        # 🔥 OBTENER FECHA DE VALIDEZ PARA REEMPLAZAR "Mantenimiento de oferta"
        valido_hasta = presupuesto_data.get('valido_hasta')
        validez_texto = "15 días"  # 🔥 Mantener el texto por defecto del formulario
        
        if valido_hasta:
            try:
                # La fecha viene en formato YYYY-MM-DD desde la API
                if 'T' in str(valido_hasta):
                    valido_hasta = str(valido_hasta).split('T')[0]
                
                # Convertir de YYYY-MM-DD a DD/MM/YYYY
                fecha_obj = datetime.strptime(str(valido_hasta), '%Y-%m-%d')
                validez_texto = f"hasta el {fecha_obj.strftime('%d/%m/%Y')}"
            except (ValueError, TypeError) as e:
                print(f"⚠️ Error formateando fecha en condiciones: {e}")
                validez_texto = str(valido_hasta)
        
        # 🔥 CONDICIONES COMERCIALES - MANTENER LAS DEL FORMULARIO
        if presupuesto_data.get('condiciones_comerciales'):
            cond_title = Paragraph("CONDICIONES COMERCIALES", self.styles['Heading2'])
            elements.append(cond_title)
            elements.append(Spacer(1, 5))
            
            condiciones_base = presupuesto_data.get('condiciones_comerciales', '')
            
            # 🔥 REEMPLAZAR "Mantenimiento de oferta: 15 días" por la fecha específica
            # Buscar y reemplazar la línea completa
            lineas = condiciones_base.split('\n')
            lineas_actualizadas = []
            
            for linea in lineas:
                if 'Mantenimiento de oferta' in linea:
                    # 🔥 REEMPLAZAR con la validez específica
                    linea_actualizada = f"Validez de oferta: {validez_texto}"
                    lineas_actualizadas.append(linea_actualizada)
                else:
                    # 🔥 MANTENER las demás líneas tal cual vienen del formulario
                    lineas_actualizadas.append(linea)
            
            # Si no encontró "Mantenimiento de oferta", agregar la línea de validez
            if 'Mantenimiento de oferta' not in condiciones_base:
                lineas_actualizadas.append(f"Validez de oferta: {validez_texto}")
            
            condiciones_texto = '<br/>'.join(lineas_actualizadas)
            cond_text = Paragraph(condiciones_texto, self.styles['Normal'])
            elements.append(cond_text)
            elements.append(Spacer(1, 15))
        
        return elements

    def _build_footer(self):
        """Construir pie de página"""
        elements = []
        # Agregar espacio flexible para empujar el footer hacia abajo
        elements.append(Spacer(1, 20))
       
        footer_text = """
        <para alignment="center">
        <font color="gray" size="8">
        LAB SERVICIOS SAS - Tel: +54 2995576550 - Email: info@labservicios.com<br/>
        </font>
        </para>
        """
       
        footer = Paragraph(footer_text, self.styles['Normal'])
        elements.append(footer)
       
        return elements

    def _abrir_pdf(self, pdf_path):
        """Abrir el PDF automáticamente"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(pdf_path)
            else:  # macOS y Linux
                import subprocess
                subprocess.call(['open', pdf_path] if os.name == 'posix' else ['xdg-open', pdf_path])
        except Exception as e:
            print(f"No se pudo abrir el PDF automáticamente: {e}")

    def _get_condicion_iva_display(self, condicion_iva):
        """Convertir código de condición IVA a texto legible"""
        condiciones = {
            'ri': 'Responsable Inscripto',
            'mono': 'Monotributista',
            'exento': 'Exento',
            'cf': 'Consumidor Final',
            'noresidente': 'No Residente'
        }
        return condiciones.get(condicion_iva, condicion_iva)

    # NOTA: Ya no se usa _get_estado_display en el PDF, pero lo dejamos por si acaso
    def _get_estado_display(self, estado):
        """Convertir código de estado a texto legible"""
        estados = {
            'borrador': 'Borrador',
            'enviado': 'Enviado',
            'aceptado': 'Aceptado',
            'rechazado': 'Rechazado'
        }
        return estados.get(estado, estado)

# Función de conveniencia para uso rápido
def generar_presupuesto_pdf(presupuesto_data, cliente_data):
    """Función simple para generar PDF desde otros módulos"""
    generator = PDFGenerator()
    return generator.generar_presupuesto(presupuesto_data, cliente_data)

# Prueba del módulo
if __name__ == "__main__":
    print("🧪 Probando generador de PDF...")
   
    # Datos de ejemplo
    ejemplo_presupuesto = {
        'numero': '999',
        'estado': 'enviado',  # Esto ya no aparece en el PDF
        'valido_hasta': '30/12/2024',
        'subtotal': 1000.00,
        'iva_porcentaje': 21.0,
        'iva_valor': 210.00,
        'total': 1210.00,
        'observaciones': 'Material de primera calidad. Garantía 6 meses.',
        'condiciones_comerciales': 'Precios válidos por 30 días.\nPago: 50% al pedido, 50% al entregar.',
        'items': [
            {
                'codigo': 'P001',
                'descripcion': 'Producto de ejemplo de alta calidad',
                'cantidad': 2,
                'precio_unitario': 250.00
            },
            {
                'codigo': 'S001',
                'descripcion': 'Servicio especializado de instalación',
                'cantidad': 1,
                'precio_unitario': 500.00
            }
        ]
    }
   
    ejemplo_cliente = {
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'documento': '20123456789',
        'condicion_iva': 'ri',
        'telefono': '299-1234567',
        'email': 'juan.perez@empresa.com',
        'direccion': 'Av. Siempre Viva 123, Neuquén'
    }
   
    # Probar generación
    resultado = generar_presupuesto_pdf(ejemplo_presupuesto, ejemplo_cliente)
    if resultado:
        print(f"✅ PDF generado exitosamente: {resultado}")
    else:
        print("❌ No se pudo generar el PDF")