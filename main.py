# app_escritorio/main.py
from login_window import LoginWindow
from main_app import MainApp

def main():
    def on_login_success():
        # Cuando el login es exitoso, abrir la aplicación principal
        app = MainApp()
        app.run()
    
    # Mostrar ventana de login
    login_window = LoginWindow(on_login_success)
    login_window.run()

if __name__ == "__main__":
    main()