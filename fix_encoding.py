# Script para arreglar el encoding en presupuestos_formulario.py
import re

# Leer el archivo
with open('presupuestos_formulario.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Agregar encoding declaration al principio si no existe
if not content.startswith('# -*- coding:'):
    content = '# -*- coding: utf-8 -*-\n' + content

# Reemplazar los print statements con emojis
replacements = [
    ('print("✅ tkcalendar disponible - Usando calendario gráfico")', 
     'print("tkcalendar disponible - Usando calendario grafico")'),
    ('print("⚠️ tkcalendar no disponible. Usando campo de texto para fechas.")',
     'print("tkcalendar no disponible. Usando campo de texto para fechas.")'),
]

for old, new in replacements:
    content = content.replace(old, new)

# Escribir el archivo
with open('presupuestos_formulario.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Archivo corregido exitosamente")
