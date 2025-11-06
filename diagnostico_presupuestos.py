import sys
import os
import tkinter as tk
from tkinter import messagebox

# Configurar path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app_escritorio')
sys.path.append(app_dir)

def ejecutar_diagnostico():
    try:
        from presupuestos_manager import PresupuestosManager
        from clientes_manager import ClientesManager
        
        print("=" * 50)
        print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA")
        print("=" * 50)
        
        # Test Presupuestos
        print("\n📊 TEST PRESUPUESTOS:")
        presupuestos_manager = PresupuestosManager()
        presupuestos = presupuestos_manager.obtener_presupuestos()
        
        print(f"Presupuestos encontrados: {len(presupuestos)}")
        
        if presupuestos:
            print("\n📋 Detalle del primer presupuesto:")
            p = presupuestos[0]
            for key, value in p.items():
                print(f"  {key}: {value} (tipo: {type(value)})")
        
        # Test Clientes
        print("\n👥 TEST CLIENTES:")
        clientes_manager = ClientesManager()
        clientes = clientes_manager.obtener_clientes()
        print(f"Clientes encontrados: {len(clientes)}")
        
        if clientes:
            print("\n📋 Detalle del primer cliente:")
            c = clientes[0]
            for key, value in c.items():
                print(f"  {key}: {value}")
        
        # Test PDF Generator
        print("\n📄 TEST PDF GENERATOR:")
        try:
            from pdf_generator import PDFGenerator
            print("✅ PDFGenerator importado correctamente")
            
            # Probar con datos de ejemplo
            ejemplo_presupuesto = {
                'numero': 'TEST-001',
                'estado': 'borrador',
                'subtotal': 1000.00,
                'iva_porcentaje': 21.0,
                'iva_valor': 210.00,
                'total': 1210.00,
                'observaciones': 'Test diagnóstico',
                'items': [
                    {
                        'codigo': 'P001',
                        'descripcion': 'Producto test',
                        'cantidad': 2,
                        'precio_unitario': 250.00
                    }
                ]
            }
            
            ejemplo_cliente = {
                'nombre': 'Cliente',
                'apellido': 'Test',
                'documento': '12345678',
                'condicion_iva': 'ri'
            }
            
            generator = PDFGenerator()
            print("✅ PDFGenerator instanciado correctamente")
            
        except Exception as e:
            print(f"❌ Error en PDFGenerator: {e}")
        
        print("\n" + "=" * 50)
        print("✅ DIAGNÓSTICO COMPLETADO")
        
        # Mostrar ventana con resultados
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Diagnóstico", f"Diagnóstico completado.\nPresupuestos: {len(presupuestos)}\nClientes: {len(clientes)}")
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ejecutar_diagnostico()