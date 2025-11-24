
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import APIClient, Endpoints

def check_comprobantes():
    client = APIClient()
    print(f"Consultando {Endpoints.COMPROBANTES}...")
    data, error = client.get(Endpoints.COMPROBANTES)
    
    if error:
        print(f"Error: {error}")
    else:
        print("Datos recibidos:")
        import json
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    check_comprobantes()
