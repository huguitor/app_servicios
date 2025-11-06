# test_simple.py
import sys
print("Python path:", sys.executable)

try:
    import reportlab
    print("✅ reportlab importado")
    print("Versión:", reportlab.Version)
except ImportError as e:
    print("❌ Error importando reportlab:", e)

try:
    from reportlab.lib.pagesizes import A4
    print("✅ A4 importado")
except ImportError as e:
    print("❌ Error importando A4:", e)