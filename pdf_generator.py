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

# 🔥 NUEVA IMPORTACIÓN
from configuracion_manager import ConfiguracionManager


class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # 🔥 NUEVO: Instancia del manager de configuración
        self.config_manager = ConfiguracionManager()
        
        # 🔥 NUEVO: Cargar datos de empresa al inicializar
        self.datos_empresa = self.config_manager.obtener_datos_empresa()
        print(f"🏢 Datos empresa cargados para PDF: {self.datos_empresa.get('nombre_empresa', 'No disponible')}")
        print(f"🌐 Página web desde configuración: {self.datos_empresa.get('pagina_web', 'No disponible')}")
    
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

    def _obtener_datos_empresa_pdf(self):
        """Obtener datos de empresa para usar en el PDF - VERSIÓN CORREGIDA"""
        try:
            # 🔥 USAR DATOS REALES DE LA CONFIGURACIÓN
            datos = self.datos_empresa
            
            # 🔥 IMPORTANTE: Obtener PÁGINA WEB REAL de la configuración
            pagina_web_real = datos.get('pagina_web', '')
            
            # Si no hay página web en la configuración, usar un valor por defecto apropiado
            if not pagina_web_real or pagina_web_real.strip() == '':
                pagina_web_real = 'https://www.labservicios.com.ar'
                print("⚠️ No hay página web en configuración, usando valor por defecto")
            else:
                print(f"✅ Página web obtenida de configuración: {pagina_web_real}")
            
            empresa_info = {
                'nombre_empresa': datos.get('nombre_empresa', 'LAB Servicios'),
                'cuit': datos.get('cuit', '23-14852171-9'),
                'direccion': datos.get('direccion', 'Río Neuquén 4100 - Plottier - Neuquén'),
                'telefono': datos.get('telefono', '+542995576550'),
                'email': datos.get('email', 'labservicios@outlook.com'),
                'pagina_web': pagina_web_real,  # 🔥 USAR VALOR REAL
                'condiciones_comerciales': datos.get('condiciones_comerciales', ''),
                'logo_principal_url': datos.get('logo_principal_url'),  # 🔥 PARA BUSCAR LOGO
                'logo_principal_absolute_url': datos.get('logo_principal_absolute_url')
            }
            
            print(f"📋 Datos empresa para PDF: {empresa_info['nombre_empresa']}")
            print(f"🌐 Página web para PDF: {empresa_info['pagina_web']}")
            print(f"🎨 Logo URL disponible: {'Sí' if empresa_info.get('logo_principal_url') else 'No'}")
            
            return empresa_info
            
        except Exception as e:
            print(f"❌ Error obteniendo datos empresa para PDF: {e}")
            # 🔥 FALLBACK POR DEFECTO CON LOGOS
            return {
                'nombre_empresa': 'LAB Servicios',
                'cuit': '23-14852171-9',
                'direccion': 'Río Neuquén 4100 - Plottier - Neuquén',
                'telefono': '+542995576550',
                'email': 'labservicios@outlook.com',
                'pagina_web': 'https://www.labservicios.com.ar',
                'condiciones_comerciales': 'Precios expresados en pesos Argentinos\nPlazo de entrega: Inmediata\nForma de Pago: 30 días',
                'logo_principal_url': None,
                'logo_principal_absolute_url': None
            }

    def _buscar_logo_empresa(self):
        """Buscar el logo de la empresa en las rutas posibles - VERSIÓN ESPECÍFICA PARA PRODUCCIÓN"""
        print("=" * 60)
        print("🔍 BÚSQUEDA DE LOGO PARA PDF - MODO PRODUCCIÓN")
        print("=" * 60)
        
        # 🔥 RUTA EXACTA DE PRODUCCIÓN (según lo que me dijiste)
        ruta_exacta_produccion = r"c:/LabServicios/data/media/config/logos/logoLAB_form.jpg"
        print(f"🎯 Ruta exacta de producción: {ruta_exacta_produccion}")
        
        # 🔥 PRIMERO: Verificar la ruta exacta de producción
        if os.path.exists(ruta_exacta_produccion):
            print(f"✅ ¡LOGO ENCONTRADO EN RUTA EXACTA!: {ruta_exacta_produccion}")
            return ruta_exacta_produccion
        
        # 🔥 SEGUNDO: Rutas alternativas (por si cambia la ubicación)
        rutas_alternativas = [
            # Rutas absolutas
            r"C:\LabServicios\data\media\config\logos\logoLAB_form.jpg",
            r"C:\LabServicios\data\media\config\logos\logo_principal.png",
            r"C:\LabServicios\data\media\config\logos\logo_principal.jpg",
            r"C:\LabServicios\data\media\config\logos\logo.png",
            r"C:\LabServicios\data\media\config\logos\logo.jpg",
            
            # Rutas relativas (para .exe en producción)
            os.path.join('data', 'media', 'config', 'logos', 'logoLAB_form.jpg'),
            os.path.join('data', 'media', 'config', 'logos', 'logo_principal.png'),
            os.path.join('data', 'media', 'config', 'logos', 'logo_principal.jpg'),
            os.path.join('data', 'media', 'config', 'logos', 'logo.png'),
            os.path.join('data', 'media', 'config', 'logos', 'logo.jpg'),
            
            # Rutas desde directorio actual
            os.path.join('..', 'data', 'media', 'config', 'logos', 'logoLAB_form.jpg'),
            os.path.join('..', '..', 'data', 'media', 'config', 'logos', 'logoLAB_form.jpg'),
            
            # Rutas de desarrollo
            os.path.join('media', 'config', 'logos', 'logoLAB_form.jpg'),
            os.path.join('..', 'media', 'config', 'logos', 'logoLAB_form.jpg'),
            os.path.join('..', '..', 'media', 'config', 'logos', 'logoLAB_form.jpg'),
        ]
        
        print("\n🔍 Probando rutas alternativas...")
        for ruta in rutas_alternativas:
            # Normalizar ruta para diferentes sistemas operativos
            ruta_normalizada = os.path.normpath(ruta)
            print(f"  🔎 Probando: {ruta_normalizada}")
            if os.path.exists(ruta_normalizada):
                print(f"  ✅ ¡LOGO ENCONTRADO!: {ruta_normalizada}")
                return ruta_normalizada
            else:
                print(f"  ❌ No existe")
        
        # 🔥 TERCERO: Intentar obtener logo de configuración Django (URL)
        try:
            if self.datos_empresa and 'logo_principal_url' in self.datos_empresa:
                logo_url = self.datos_empresa.get('logo_principal_url')
                if logo_url and logo_url.startswith('/media/'):
                    # Convertir URL Django a ruta local
                    relative_path = logo_url[7:]  # Quita "/media/"
                    rutas_django = [
                        os.path.join('data', 'media', relative_path),
                        os.path.join('..', 'data', 'media', relative_path),
                        os.path.join('..', '..', 'data', 'media', relative_path),
                        os.path.join('media', relative_path),
                        os.path.join('..', 'media', relative_path),
                    ]
                    
                    print("\n🔍 Probando rutas Django...")
                    for ruta in rutas_django:
                        ruta_normalizada = os.path.normpath(ruta)
                        print(f"  🔎 Probando: {ruta_normalizada}")
                        if os.path.exists(ruta_normalizada):
                            print(f"  ✅ ¡LOGO ENCONTRADO!: {ruta_normalizada}")
                            return ruta_normalizada
        except Exception as e:
            print(f"⚠️ Error buscando logo de Django: {e}")
        
        print("\n❌ Logo no encontrado en ninguna ubicación conocida")
        return None

    def _dibujar_logo_fallback(self, canvas, x, y, nombre_empresa):
        """Dibujar un logo de fallback cuando no se encuentra la imagen"""
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

    def _build_logo_zone(self, canvas, doc, presupuesto_data):
        """Zona fija de 3cm solo con logo y datos empresa - SIN presupuesto"""
        canvas.saveState()
        
        empresa_info = self._obtener_datos_empresa_pdf()
        pagina_web = empresa_info.get('pagina_web', 'https://www.labservicios.com.ar')
        
        # 🔥 LOGO A LA IZQUIERDA
        try:
            # Buscar logo en las rutas correctas
            logo_path = self._buscar_logo_empresa()
            
            if logo_path and os.path.exists(logo_path):
                logo_x = 40
                logo_y = A4[1] - 80  # Parte superior
                
                # Verificar que el archivo sea válido
                if os.path.getsize(logo_path) > 0:
                    # Enlace clickeable a la página web REAL de la configuración
                    canvas.linkURL(
                        pagina_web,
                        (logo_x, logo_y, logo_x + 80, logo_y + 40),
                        relative=0
                    )
                    
                    # Dibujar logo con manejo de errores
                    try:
                        canvas.drawImage(logo_path, logo_x, logo_y, width=80, height=40, mask='auto')
                        print(f"✅ Logo dibujado exitosamente: {os.path.basename(logo_path)}")
                        print(f"📏 Tamaño del archivo: {os.path.getsize(logo_path)} bytes")
                        print(f"🔗 Enlace del logo: {pagina_web}")
                    except Exception as img_error:
                        print(f"⚠️ Error dibujando logo (ReportLab): {img_error}")
                        # Intentar con formato diferente
                        try:
                            canvas.drawImage(logo_path, logo_x, logo_y, width=80, height=40)
                            print(f"✅ Logo dibujado (segundo intento)")
                        except:
                            print(f"❌ Error crítico con logo, usando fallback")
                            self._dibujar_logo_fallback(canvas, logo_x, logo_y, empresa_info['nombre_empresa'])
                else:
                    print(f"⚠️ Archivo de logo vacío o corrupto: {logo_path}")
                    self._dibujar_logo_fallback(canvas, 40, A4[1] - 80, empresa_info['nombre_empresa'])
            else:
                # Logo no encontrado, usar fallback
                print("⚠️ Logo no encontrado en ninguna ruta, usando versión de fallback")
                self._dibujar_logo_fallback(canvas, 40, A4[1] - 80, empresa_info['nombre_empresa'])
                
        except Exception as e:
            print(f"❌ Error general con logo: {e}")
            import traceback
            traceback.print_exc()
            self._dibujar_logo_fallback(canvas, 40, A4[1] - 80, empresa_info['nombre_empresa'])
        
        # 🔥 DATOS DE EMPRESA A LA DERECHA DEL LOGO (alineados)
        canvas.setFont('Helvetica', 9)
        datos_x = 140  # Más a la derecha del logo para mejor alineación
        
        canvas.drawString(datos_x, A4[1] - 45, empresa_info['nombre_empresa'])
        canvas.drawString(datos_x, A4[1] - 55, f"CUIT: {empresa_info['cuit']}")
        canvas.drawString(datos_x, A4[1] - 65, empresa_info['direccion'])
        canvas.drawString(datos_x, A4[1] - 75, f"Tel: {empresa_info['telefono']}")
        canvas.drawString(datos_x, A4[1] - 85, f"Email: {empresa_info['email']}")
        
        # 🔥 LÍNEA SEPARADORA DE LA ZONA
        canvas.setStrokeColor(colors.gray)
        canvas.setLineWidth(0.5)
        canvas.line(40, A4[1] - 95, A4[0] - 40, A4[1] - 95)
        
        canvas.restoreState()

    def _build_header(self, presupuesto_data):
        """Header simplificado - solo espacio para la zona del logo"""
        elements = []
        
        # 🔥 NO necesitamos agregar espacio aquí porque ya tenemos margen superior
        # El contenido automáticamente empieza después de los 3cm
        
        return elements  # 🔥 Devuelve lista vacía

    def _build_header_for_other_pages(self, canvas, doc):
        """Header para páginas posteriores (sin logo)"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(40, A4[1] - 20, "LAB Servicios - Presupuesto")
        canvas.restoreState()

    def _build_cliente_section(self, cliente_data, presupuesto_data):
        """Sección cliente con Presupuesto N° y Fecha a la derecha"""
        elements = []
        
        # 🔥 AGREGAR ESPACIO DESPUÉS DE LA LÍNEA DIVISORIA
        elements.append(Spacer(1, 15))  # 🔥 15 puntos de espacio después de la línea
        
        # 🔥 CREAR TABLA CON 2 COLUMNAS: Cliente a la izquierda, Presupuesto a la derecha
        numero_presupuesto = presupuesto_data.get('numero', '')
        try:
            if numero_presupuesto:
                numero_int = int(numero_presupuesto)
                numero_formateado = f"{numero_int:05d}"
            else:
                numero_formateado = "00000"
        except:
            numero_formateado = str(numero_presupuesto) if numero_presupuesto else "00000"
        
        # Tabla con cliente izquierda / presupuesto derecha
        header_data = [
            [
                "",  # 🔥 CELDA VACÍA en lugar de "DATOS DEL CLIENTE"
                f"PRESUPUESTO N° {numero_formateado}\n\nFecha: {datetime.now().strftime('%d/%m/%Y')}"
            ]
        ]
        
        header_table = Table(header_data, colWidths=[360, 140])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 11),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 3))  # 5🔥 MENOS ESPACIO aquí
        
        # 🔥 AGREGAR "DATOS DEL CLIENTE" COMO TÍTULO SEPARADO
        section_title = Paragraph("DATOS DEL CLIENTE", self.styles['Heading2'])
        elements.append(section_title)
        elements.append(Spacer(1, 5))
        
        # 🔥 INFORMACIÓN DETALLADA DEL CLIENTE (tabla normal)
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
        elements.append(Spacer(1, 3))
        
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
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Alineación
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            
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
        """Construir sección de totales"""
        elements = []

        subtotal = Decimal(str(presupuesto_data.get('subtotal', 0)))
        iva_porcentaje = Decimal(str(presupuesto_data.get('iva_porcentaje', 21)))
        iva_valor = Decimal(str(presupuesto_data.get('iva_valor', 0)))
        total = Decimal(str(presupuesto_data.get('total', 0)))

        totales_data = [
            ["", ""],
            ["SUBTOTAL:", f"${subtotal:,.2f}"],
            [f"IVA ({iva_porcentaje}%):", f"${iva_valor:,.2f}"],
            ["TOTAL:", f"${total:,.2f}"]
        ]

        totales_table = Table(totales_data, colWidths=[250, 150])
        totales_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 12),
            ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 1), (1, -1), 12),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('VALIGN', (1, 1), (1, -1), 'MIDDLE'),
            ('FONTSIZE', (-1, -1), (-1, -1), 14),
            ('BACKGROUND', (-1, -1), (-1, -1), colors.HexColor('#10B981')),
            ('TEXTCOLOR', (-1, -1), (-1, -1), colors.white),
            ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(totales_table)
        elements.append(Spacer(1, 20))

        return elements

    def _build_observaciones_section(self, presupuesto_data):
        """Construir sección de observaciones y condiciones con datos reales"""
        elements = []
        
        # 🔥 OBTENER CONDICIONES COMERCIALES DE LA CONFIGURACIÓN
        empresa_info = self._obtener_datos_empresa_pdf()
        condiciones_por_defecto = empresa_info.get('condiciones_comerciales', '')
        
        # Observaciones específicas del presupuesto
        if presupuesto_data.get('observaciones'):
            obs_title = Paragraph("OBSERVACIONES", self.styles['Heading2'])
            elements.append(obs_title)
            elements.append(Spacer(1, 5))
            
            observaciones = presupuesto_data.get('observaciones', '').replace('\n', '<br/>')
            obs_text = Paragraph(observaciones, self.styles['Normal'])
            elements.append(obs_text)
            elements.append(Spacer(1, 10))
        
        # 🔥 CONDICIONES COMERCIALES - USAR LAS DE LA CONFIGURACIÓN SI NO HAY ESPECÍFICAS
        condiciones_presupuesto = presupuesto_data.get('condiciones_comerciales', condiciones_por_defecto)
        
        if condiciones_presupuesto:
            cond_title = Paragraph("CONDICIONES COMERCIALES", self.styles['Heading2'])
            elements.append(cond_title)
            elements.append(Spacer(1, 5))
            
            # 🔥 OBTENER FECHA DE VALIDEZ
            valido_hasta = presupuesto_data.get('valido_hasta')
            validez_texto = "15 días"
            
            if valido_hasta:
                try:
                    if 'T' in str(valido_hasta):
                        valido_hasta = str(valido_hasta).split('T')[0]
                    
                    fecha_obj = datetime.strptime(str(valido_hasta), '%Y-%m-%d')
                    validez_texto = f"hasta el {fecha_obj.strftime('%d/%m/%Y')}"
                except (ValueError, TypeError) as e:
                    print(f"⚠️ Error formateando fecha en condiciones: {e}")
                    validez_texto = str(valido_hasta)
            
            # 🔥 PROCESAR CONDICIONES
            condiciones_base = condiciones_presupuesto
            
            # Reemplazar o agregar línea de validez
            lineas = condiciones_base.split('\n')
            lineas_actualizadas = []
            
            validez_encontrada = False
            for linea in lineas:
                if any(term in linea.lower() for term in ['mantenimiento', 'validez', 'vigencia']):
                    linea_actualizada = f"Validez de oferta: {validez_texto}"
                    lineas_actualizadas.append(linea_actualizada)
                    validez_encontrada = True
                else:
                    lineas_actualizadas.append(linea)
            
            # Si no encontró línea de validez, agregarla
            if not validez_encontrada:
                lineas_actualizadas.append(f"Validez de oferta: {validez_texto}")
            
            condiciones_texto = '<br/>'.join(lineas_actualizadas)
            cond_text = Paragraph(condiciones_texto, self.styles['Normal'])
            elements.append(cond_text)
            elements.append(Spacer(1, 15))
        
        return elements

    def _build_footer(self, canvas, doc):
        """Construir pie de página con datos reales de la empresa"""
        canvas.saveState()
        
        # 🔥 OBTENER DATOS REALES PARA EL FOOTER (con página web real)
        empresa_info = self._obtener_datos_empresa_pdf()
        
        # Construir texto del footer con página web real
        if empresa_info['pagina_web'] and empresa_info['pagina_web'] != 'https://www.labservicios.com.ar':
            footer_text = f"{empresa_info['nombre_empresa']} - {empresa_info['pagina_web']} - Tel: {empresa_info['telefono']}"
        else:
            footer_text = f"{empresa_info['nombre_empresa']} - Tel: {empresa_info['telefono']} - Email: {empresa_info['email']}"
        
        # Configurar el pie de página
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.gray)
        
        # Centrar el texto en la parte inferior
        page_width = A4[0]
        text_width = canvas.stringWidth(footer_text, 'Helvetica', 8)
        x_position = (page_width - text_width) / 2
        
        # Dibujar el pie de página
        canvas.drawString(x_position, 30, footer_text)
        
        canvas.restoreState()

    def _get_save_path(self, presupuesto_data, cliente_data):
        """Obtener ruta para guardar el archivo"""
        root = tk.Tk()
        root.withdraw()
        
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

    def _get_estado_display(self, estado):
        """Convertir código de estado a texto legible"""
        estados = {
            'borrador': 'Borrador',
            'enviado': 'Enviado',
            'aceptado': 'Aceptado',
            'rechazado': 'Rechazado'
        }
        return estados.get(estado, estado)

    def generar_presupuesto(self, presupuesto_data, cliente_data):
        """Generar PDF del presupuesto con zona fija de 3cm"""
        try:
            # SANITIZAR DATOS ANTES DE USAR
            presupuesto_data = self._sanitizar_datos_presupuesto(presupuesto_data)
            
            # 🔥 ACTUALIZAR DATOS DE EMPRESA (por si cambiaron)
            self.datos_empresa = self.config_manager.obtener_datos_empresa()
            
            # Pedir ubicación para guardar
            output_path = self._get_save_path(presupuesto_data, cliente_data)
            if not output_path:
                return None

            # 🔥 CREAR DOCUMENTO CON ZONA DE 3CM ARRIBA
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                topMargin=85,        # 🔥 3 CM = 85 PUNTOS
                bottomMargin=60,
                leftMargin=40,
                rightMargin=40
            )
            
            story = []
            
            # 1. HEADER (vacío - el logo va en zona fija)
            story.extend(self._build_header(presupuesto_data))
            
            # 2. INFORMACIÓN DEL CLIENTE (con Presupuesto N° y Fecha)
            story.extend(self._build_cliente_section(cliente_data, presupuesto_data))
            
            # 3. ITEMS DEL PRESUPUESTO
            story.extend(self._build_items_section(presupuesto_data))
            
            # 4. TOTALES
            story.extend(self._build_totales_section(presupuesto_data))
            
            # 5. OBSERVACIONES Y CONDICIONES
            story.extend(self._build_observaciones_section(presupuesto_data))
            
            # 🔥 GENERAR PDF CON ZONA DE LOGO FIJA
            def first_page(canvas, doc):
                self._build_logo_zone(canvas, doc, presupuesto_data)  # 🔥 ZONA DE 3CM
                self._build_footer(canvas, doc)
            
            def other_pages(canvas, doc):
                self._build_logo_zone(canvas, doc, presupuesto_data)  # 🔥 ZONA EN TODAS LAS PÁGINAS
                self._build_footer(canvas, doc)
            
            doc.build(story, onFirstPage=first_page, onLaterPages=other_pages)
            
            # Mostrar mensaje de éxito
            empresa_info = self._obtener_datos_empresa_pdf()
            messagebox.showinfo(
                "PDF Generado",
                f"✅ Presupuesto guardado como PDF:\n\n"
                f"📄 Archivo: {os.path.basename(output_path)}\n"
                f"🏢 Empresa: {empresa_info['nombre_empresa']}\n"
                f"🌐 Página web en logo: {empresa_info['pagina_web']}"
            )
            
            # Abrir el PDF automáticamente
            self._abrir_pdf(output_path)
            
            return output_path
            
        except Exception as e:
            messagebox.showerror(
                "Error al generar PDF",
                f"❌ No se pudo generar el PDF:\n{str(e)}"
            )
            return None


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
        'estado': 'enviado',
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