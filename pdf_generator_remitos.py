# /app_escritorio/pdf_generator_remitos.py
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
from decimal import Decimal

# Importaciones de ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image

# Importar configuración
from configuracion_manager import ConfiguracionManager


class PDFGeneratorRemitos:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Instancia del manager de configuración
        self.config_manager = ConfiguracionManager()
        
        # Cargar datos de empresa al inicializar
        self.datos_empresa = self.config_manager.obtener_datos_empresa()
        print(f"🏢 Datos empresa cargados para PDF Remitos: {self.datos_empresa.get('nombre_empresa', 'No disponible')}")
        print(f"🌐 Página web desde configuración: {self.datos_empresa.get('pagina_web', 'No disponible')}")
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados para remitos"""
        # Estilo para título principal de remito
        self.styles.add(ParagraphStyle(
            name='RemitoTitle',
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
        
        # Estilo para firmas
        self.styles.add(ParagraphStyle(
            name='Firmas',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=2,  # Derecha
            textColor=colors.black
        ))

    def _obtener_datos_empresa_pdf(self):
        """Obtener datos de empresa para usar en el PDF"""
        try:
            datos = self.datos_empresa
            
            # Obtener página web real
            pagina_web_real = datos.get('pagina_web', '')

            # Si no hay página web en la configuración, usar un valor por defecto apropiado
            if not pagina_web_real or pagina_web_real.strip() == '':
                pagina_web_real = 'https://www.panozosistemas.com.ar'
                print("⚠️ No hay página web en configuración, usando valor por defecto")
            else:
                print(f"✅ Página web obtenida de configuración: {pagina_web_real}")            

            empresa_info = {
                'nombre_empresa': datos.get('nombre_empresa', 'Servicio S.A.'),
                'cuit': datos.get('cuit', '23-14852171-9'),
                'direccion': datos.get('direccion', 'San Luis 328 - Neuquén - Neuquén'),
                'telefono': datos.get('telefono', '+542991234567'),
                'email': datos.get('email', 'servicios@gmail.com'),
                'pagina_web': pagina_web_real,
                'logo_principal_url': datos.get('logo_principal_url'),
                'logo_principal_absolute_url': datos.get('logo_principal_absolute_url')
            }
            
            print(f"📋 Datos empresa para PDF Remito: {empresa_info['nombre_empresa']}")
            print(f"🌐 Página web: {empresa_info['pagina_web']}")
            print(f"🎨 Logo URL disponible: {'Sí' if empresa_info.get('logo_principal_url') else 'No'}")
            
            return empresa_info
            
        except Exception as e:
            print(f"❌ Error obteniendo datos empresa para PDF Remito: {e}")
            return {
                'nombre_empresa': 'Servicio S.A.',
                'cuit': '23-14852171-9',
                'direccion': 'San Luis 328 - Neuquén - Neuquén',
                'telefono': '+542991234567',
                'email': 'servicios@gmail.com',
                'pagina_web': 'https://www.panozosistemas.com.ar',
                'logo_principal_url': None,
                'logo_principal_absolute_url': None
            }

    def _buscar_logo_empresa(self):
        """Buscar el logo de la empresa"""
        print("=" * 60)
        print("🔍 BÚSQUEDA DE LOGO PARA PDF REMITO")
        print("=" * 60)
        
        # Ruta exacta de producción
        ruta_exacta_produccion = r"c:/LabServicios/data/media/config/logos/logoLAB_form.jpg"
        print(f"🎯 Ruta exacta: {ruta_exacta_produccion}")
        
        if os.path.exists(ruta_exacta_produccion):
            print(f"✅ ¡LOGO ENCONTRADO EN RUTA EXACTA!")
            return ruta_exacta_produccion
        
        # Rutas alternativas
        rutas_alternativas = [
            r"C:\LabServicios\data\media\config\logos\logoLAB_form.jpg",
            r"C:\LabServicios\data\media\config\logos\logo_principal.png",
            r"C:\LabServicios\data\media\config\logos\logo_principal.jpg",
            os.path.join('data', 'media', 'config', 'logos', 'logoLAB_form.jpg'),
            os.path.join('media', 'config', 'logos', 'logoLAB_form.jpg'),
        ]
        
        print("\n🔍 Probando rutas alternativas...")
        for ruta in rutas_alternativas:
            ruta_normalizada = os.path.normpath(ruta)
            print(f"  🔎 Probando: {ruta_normalizada}")
            if os.path.exists(ruta_normalizada):
                print(f"  ✅ ¡LOGO ENCONTRADO!")
                return ruta_normalizada
        
        return None

    def _dibujar_logo_fallback(self, canvas, x, y, nombre_empresa):
        """Dibujar un logo de fallback"""
        print("🎨 Dibujando logo de fallback...")
        
        # Dibujar un rectángulo gris
        canvas.setFillColor(colors.HexColor('#F0F0F0'))
        canvas.rect(x, y, 80, 40, fill=1)
        
        # Dibujar borde
        canvas.setStrokeColor(colors.HexColor('#CCCCCC'))
        canvas.setLineWidth(1)
        canvas.rect(x, y, 80, 40)
        
        # Dibujar texto
        canvas.setFillColor(colors.HexColor('#666666'))
        canvas.setFont('Helvetica-Bold', 8)
        
        # Nombre de empresa (abreviado)
        if len(nombre_empresa) > 10:
            nombre_abreviado = nombre_empresa[:8] + '..'
        else:
            nombre_abreviado = nombre_empresa
            
        texto_width = canvas.stringWidth(nombre_abreviado, 'Helvetica-Bold', 8)
        texto_x = x + (80 - texto_width) / 2
        
        canvas.drawString(texto_x, y + 25, nombre_abreviado)
        
        # Texto "LOGO"
        canvas.setFont('Helvetica', 7)
        logo_text_width = canvas.stringWidth("LOGO", 'Helvetica', 7)
        logo_text_x = x + (80 - logo_text_width) / 2
        canvas.drawString(logo_text_x, y + 15, "LOGO")

    def _build_logo_zone(self, canvas, doc, remito_data):
        """Zona fija de 3cm con logo y datos empresa"""
        canvas.saveState()
        
        empresa_info = self._obtener_datos_empresa_pdf()
        pagina_web = empresa_info.get('pagina_web', 'https://www.labservicios.com.ar')
        
        # Logo a la izquierda
        try:
            logo_path = self._buscar_logo_empresa()
            
            if logo_path and os.path.exists(logo_path):
                logo_x = 40
                logo_y = A4[1] - 80
                
                if os.path.getsize(logo_path) > 0:
                    # Enlace clickeable
                    canvas.linkURL(
                        pagina_web,
                        (logo_x, logo_y, logo_x + 80, logo_y + 40),
                        relative=0
                    )
                    
                    try:
                        canvas.drawImage(logo_path, logo_x, logo_y, width=80, height=40, mask='auto')
                        print(f"✅ Logo dibujado exitosamente")
                    except Exception as img_error:
                        print(f"⚠️ Error dibujando logo: {img_error}")
                        try:
                            canvas.drawImage(logo_path, logo_x, logo_y, width=80, height=40)
                        except:
                            self._dibujar_logo_fallback(canvas, logo_x, logo_y, empresa_info['nombre_empresa'])
                else:
                    self._dibujar_logo_fallback(canvas, 40, A4[1] - 80, empresa_info['nombre_empresa'])
            else:
                self._dibujar_logo_fallback(canvas, 40, A4[1] - 80, empresa_info['nombre_empresa'])
                
        except Exception as e:
            print(f"❌ Error general con logo: {e}")
            self._dibujar_logo_fallback(canvas, 40, A4[1] - 80, empresa_info['nombre_empresa'])
        
        # Datos de empresa a la derecha del logo
        canvas.setFont('Helvetica', 9)
        datos_x = 140
        
        # Datos de empresa
        canvas.drawString(datos_x, A4[1] - 60, empresa_info['nombre_empresa'])
        canvas.drawString(datos_x, A4[1] - 70, f"CUIT: {empresa_info['cuit']}")
        canvas.drawString(datos_x, A4[1] - 80, empresa_info['direccion'])
        canvas.drawString(datos_x, A4[1] - 90, f"Tel: {empresa_info['telefono']}")
        canvas.drawString(datos_x, A4[1] - 100, f"Email: {empresa_info['email']}")
        
        # Línea separadora
        canvas.setStrokeColor(colors.gray)
        canvas.setLineWidth(0.5)
        canvas.line(40, A4[1] - 110, A4[0] - 40, A4[1] - 110)
        
        canvas.restoreState()

    def _build_header(self):
        """Header simplificado - espacio para zona del logo"""
        return []

    def _formatear_fecha(self, fecha_str):
        """Método auxiliar para formatear fechas"""
        if not fecha_str:
            return 'No especificada'
        
        try:
            # Limpiar si tiene hora
            if 'T' in fecha_str:
                fecha_str = fecha_str.split('T')[0]
            
            # Intentar parsear como YYYY-MM-DD
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
            return fecha_obj.strftime('%d/%m/%Y')
        except ValueError:
            # Si ya está en DD/MM/YYYY o otro formato, dejarlo
            return fecha_str
        except Exception as e:
            print(f"⚠️ Error formateando fecha: {e}")
            return fecha_str

    def _build_remito_info_section(self, remito_data, cliente_data):
        """Sección con información del remito y cliente"""
        elements = []
        
        # Espacio después de la línea divisoria
        elements.append(Spacer(1, 10))
        
        # Número de remito a la derecha
        numero_remito = remito_data.get('numero_formateado', '')
        
        # Crear tabla con 2 columnas: vacía a la izquierda, número a la derecha
        info_data = [
            ["", f"REMITO INTERNO N°: {numero_remito}"]
        ]
        
        info_table = Table(info_data, colWidths=[350, 150])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 14),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Alineado a la derecha
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 10))
        
        # 🔥 USAR MÉTODO DE FORMATEO
        fecha_emision = self._formatear_fecha(remito_data.get('fecha_emision', ''))
        
        # Sección de fechas
        fechas_data = [
            ["FECHA DE EMISIÓN:", fecha_emision]
        ]
        
        fechas_table = Table(fechas_data, colWidths=[120, 380])
        fechas_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAFC')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ]))
        
        elements.append(fechas_table)
        elements.append(Spacer(1, 10))
        
        # Sección de origen y destino
        origen = remito_data.get('origen', '')
        destino = remito_data.get('destino', '')
        
        if origen or destino:
            origen_destino_data = [
                ["ORIGEN:", origen or 'No especificado'],
                ["DESTINO:", destino or 'No especificado']
            ]
            
            origen_destino_table = Table(origen_destino_data, colWidths=[80, 420])
            origen_destino_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAFC')),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ]))
            
            elements.append(origen_destino_table)
            elements.append(Spacer(1, 10))
            
        # Sección de cliente
        cliente_title = Paragraph("DATOS DEL CLIENTE", self.styles['Heading2'])
        elements.append(cliente_title)
        elements.append(Spacer(1, 5))
        
        cliente_nombre = f"{cliente_data.get('nombre', '')} {cliente_data.get('apellido', '')}".strip()
        cliente_info = [
            ["Cliente:", cliente_nombre],
            ["CUIT:", cliente_data.get('documento', 'No especificado')],
            ["Teléfono:", cliente_data.get('telefono', 'No especificado')],
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

    def _build_referencias_section(self, remito_data):
        """Sección de referencias del remito"""
        elements = []
        
        presupuesto = remito_data.get('presupuesto_relacionado', '')
        licitacion = remito_data.get('licitacion_orden', '')
        referencia = remito_data.get('numero_referencia', '')
        
        if presupuesto or licitacion or referencia:
            
            referencias_data = []
            
            if presupuesto:
                referencias_data.append(["Presupuesto:", presupuesto])
            if licitacion:
                referencias_data.append(["Licitación/Orden:", licitacion])
            if referencia:
                referencias_data.append(["N° de Referencia:", referencia])
            
            if referencias_data:
                referencias_table = Table(referencias_data, colWidths=[120, 380])
                referencias_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAFC')),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
                ]))
                
                elements.append(referencias_table)
                elements.append(Spacer(1, 15))
        
        return elements

    def _build_items_section(self, remito_data):
        """Construir sección de items del remito - SIN TOTALES"""
        elements = []
        
        # Título de sección
        section_title = Paragraph("DETALLE DE LA ENTREGA", self.styles['Heading2'])
        elements.append(section_title)
        elements.append(Spacer(1, 5))
        
        # Encabezado de la tabla
        items_header = ['#', 'Descripción', 'Cantidad', 'Observaciones']
        items_data = [items_header]
        
        # Procesar cada item
        items = remito_data.get('items', [])
        
        for i, item in enumerate(items, 1):
            cantidad = item.get('cantidad', 0)
            observaciones = item.get('observaciones', '')
            
            items_data.append([
                str(i),
                item.get('descripcion', ''),
                f"{float(cantidad):.2f}",  # Formato con 2 decimales
                observaciones  # Observaciones completas
            ])
        
        # Crear tabla de items - ANCHO COMPLETO
        items_table = Table(items_data, colWidths=[30, 300, 80, 90])  # Descripción más ancha
        items_table.setStyle(TableStyle([
            # Estilo del encabezado
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Alineación
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Número
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Descripción (más ancho)
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),   # Cantidad
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),    # Observaciones
            
            # Bordes y grid
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Alternar colores de fila
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            
            # Alto de fila ajustable para observaciones largas
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 20))
        
        return elements

    def _build_observaciones_section(self, remito_data):
        """Construir sección de observaciones"""
        elements = []
        
        if remito_data.get('observaciones'):
            obs_title = Paragraph("OBSERVACIONES", self.styles['Heading2'])
            elements.append(obs_title)
            elements.append(Spacer(1, 5))
            
            observaciones = remito_data.get('observaciones', '').replace('\n', '<br/>')
            obs_text = Paragraph(observaciones, self.styles['Normal'])
            elements.append(obs_text)
            elements.append(Spacer(1, 15))
        
        return elements

    def _build_firmas_section(self):
        """Construir sección para firmas - MÁS SIMPLE"""
        elements = []
        
        # Espacio antes de firmas
        elements.append(Spacer(1, 60))
        
        # Firma a la izquierda
        firma_text = Paragraph(
            "RECIBIDO POR: <br/>" +
            "<br/>" +
            "<br/>" +
            "<br/>" +
            "Firma y aclaración: ",
            ParagraphStyle(
                name='FirmaSimple',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=0,  # Izquierda
                textColor=colors.black,
                spaceAfter=10
            )
        )
        
        elements.append(firma_text)

        return elements

    def _build_footer(self, canvas, doc):
        """Construir pie de página"""
        canvas.saveState()
        
        empresa_info = self._obtener_datos_empresa_pdf()
        
        # Texto del footer
        footer_text = f"{empresa_info['nombre_empresa']} - {empresa_info['pagina_web']} - Tel: {empresa_info['telefono']}"
        
        # Configurar el pie de página
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.gray)
        
        # Centrar el texto
        page_width = A4[0]
        text_width = canvas.stringWidth(footer_text, 'Helvetica', 8)
        x_position = (page_width - text_width) / 2
        
        # Dibujar el pie de página
        canvas.drawString(x_position, 30, footer_text)
        
        # Número de página
        #page_num = f"Página {doc.page}"
        #canvas.drawRightString(page_width - 40, 30, page_num)
        
        canvas.restoreState()

    def _get_save_path(self, remito_data, cliente_data):
        """Obtener ruta para guardar el archivo"""
        root = tk.Tk()
        root.withdraw()
        
        numero = remito_data.get('numero_formateado', '').replace('/', '_')
        cliente_nombre = cliente_data.get('nombre', '').replace(' ', '_')
        fecha = datetime.now().strftime('%Y%m%d_%H%M')
        
        default_name = f"Remito_{numero}_{cliente_nombre}_{fecha}.pdf"
        
        return filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
            initialfile=default_name,
            title="Guardar remito como PDF"
        )

    def _abrir_pdf(self, pdf_path):
        """Abrir el PDF automáticamente"""
        try:
            if os.name == 'nt':
                os.startfile(pdf_path)
            else:
                import subprocess
                subprocess.call(['open', pdf_path] if os.name == 'posix' else ['xdg-open', pdf_path])
        except Exception as e:
            print(f"No se pudo abrir el PDF automáticamente: {e}")

    def generar_remito(self, remito_data, cliente_data):
        """Generar PDF del remito"""
        try:
            # Actualizar datos de empresa
            self.datos_empresa = self.config_manager.obtener_datos_empresa()
            
            # Pedir ubicación para guardar
            output_path = self._get_save_path(remito_data, cliente_data)
            if not output_path:
                return None

            # Crear documento
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                topMargin=115,        # Más espacio para el logo más grande
                bottomMargin=60,
                leftMargin=40,
                rightMargin=40
            )
            
            story = []
            
            # 1. HEADER (vacío - el logo va en zona fija)
            story.extend(self._build_header())
            
            # 2. INFORMACIÓN DEL REMITO Y CLIENTE
            story.extend(self._build_remito_info_section(remito_data, cliente_data))
            
            # 3. REFERENCIAS
            story.extend(self._build_referencias_section(remito_data))
            
            # 4. ITEMS DEL REMITO
            story.extend(self._build_items_section(remito_data))
            
            # 5. OBSERVACIONES
            story.extend(self._build_observaciones_section(remito_data))
            
            # 6. FIRMAS Y CONFORMIDAD
            story.extend(self._build_firmas_section())
            
            # Generar PDF con zona de logo fija
            def first_page(canvas, doc):
                self._build_logo_zone(canvas, doc, remito_data)
                self._build_footer(canvas, doc)
            
            def other_pages(canvas, doc):
                self._build_logo_zone(canvas, doc, remito_data)
                self._build_footer(canvas, doc)
            
            doc.build(story, onFirstPage=first_page, onLaterPages=other_pages)
            
            # Mostrar mensaje de éxito
            empresa_info = self._obtener_datos_empresa_pdf()
            messagebox.showinfo(
                "PDF Generado",
                f"✅ Remito guardado como PDF:\n\n"
                f"📄 Archivo: {os.path.basename(output_path)}\n"
                f"🏢 Empresa: {empresa_info['nombre_empresa']}\n"
                f"📋 Remito N°: {remito_data.get('numero_formateado', '')}"
            )
            
            # Abrir el PDF automáticamente
            self._abrir_pdf(output_path)
            
            return output_path
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Error al generar PDF",
                f"❌ No se pudo generar el PDF del remito:\n{str(e)}"
            )
            return None


# Función de conveniencia para uso rápido
def generar_remito_pdf(remito_data, cliente_data):
    """Función simple para generar PDF desde otros módulos"""
    generator = PDFGeneratorRemitos()
    return generator.generar_remito(remito_data, cliente_data)

# Prueba del módulo
if __name__ == "__main__":
    print("🧪 Probando generador de PDF para remitos...")
    
    # Datos de ejemplo para remito
    ejemplo_remito = {
        'numero': 123,
        'numero_formateado': 'REMI-000123',
        'estado': 'pendiente',
        'fecha_emision': '2024-01-15T10:30:00Z',
        'fecha_entrega': '2024-01-18T14:00:00Z',
        'origen': 'Depósito Central - Neuquén',
        'destino': 'Obra Sitio 5 - Plottier',
        'presupuesto_relacionado': 'PRES-2024-001',
        'licitacion_orden': 'LIC-2023-456',
        'numero_referencia': 'REF-789',
        'observaciones': 'Entrega con inspección previa. Verificar estado de materiales al recibir.',
        'items': [
            {
                'codigo': 'TERM-001',
                'descripcion': 'Termotanque Instalado Longvie 1.00 Color Blanco',
                'cantidad': 1,
                'unidad_medida': 'UNIDAD',
                'observaciones': 'Color blanco'
            },
            {
                'codigo': 'TUB-50',
                'descripcion': 'Tubo PVC 50mm x 6m',
                'cantidad': 25,
                'unidad_medida': 'UNIDAD',
                'observaciones': 'Color gris'
            },
            {
                'codigo': 'CON-50',
                'descripcion': 'Codo PVC 50mm 90°',
                'cantidad': 50,
                'unidad_medida': 'UNIDAD',
                'observaciones': 'Sellado hermético'
            },
                        {
                'codigo': 'inst',
                'descripcion': 'Instalación y puesta en funcionamiento',
                'cantidad': 1,
                'unidad_medida': 'UNIDAD',
                'observaciones': 'Con prueba'
            }
        ]
    }
    
    ejemplo_cliente = {
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'documento': '20-12345678-9',
        'condicion_iva': 'ri',
        'telefono': '299-555-1234',
        'email': 'juan.perez@empresa.com',
        'direccion': 'Av. Argentina 1234, Neuquén Capital'
    }
    
    # Probar generación
    resultado = generar_remito_pdf(ejemplo_remito, ejemplo_cliente)
    if resultado:
        print(f"✅ PDF de remito generado exitosamente: {resultado}")
    else:
        print("❌ No se pudo generar el PDF del remito")