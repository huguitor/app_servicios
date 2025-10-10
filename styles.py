# app_escritorio/styles.py
from config import Config

class Styles:
    # Tema de Tkinter
    THEME = "clam"  # <-- AGREGAR ESTA LÍNEA
    
    # Fuentes
    FONT_PRIMARY = ("Arial", 10)
    FONT_SECONDARY = ("Arial", 9)
    FONT_TITLE = ("Arial", 12, "bold")
    
    # Colores
    BG_PRIMARY = Config.PRIMARY_COLOR
    BG_SECONDARY = "white"
    TEXT_PRIMARY = "white"
    TEXT_SECONDARY = "black"
    
    # Estilos para widgets
    @classmethod
    def get_button_style(cls, style="primary"):
        styles = {
            "primary": {
                "bg": Config.SECONDARY_COLOR,
                "fg": "white",
                "font": cls.FONT_PRIMARY,
                "relief": "flat",
                "bd": 0,
                "padx": 20,
                "pady": 8
            },
            "success": {
                "bg": Config.SUCCESS_COLOR,
                "fg": "white",
                "font": cls.FONT_PRIMARY
            },
            "danger": {
                "bg": Config.DANGER_COLOR,
                "fg": "white",
                "font": cls.FONT_PRIMARY
            }
        }
        return styles.get(style, styles["primary"])
    
    @classmethod
    def get_entry_style(cls):
        return {
            "font": cls.FONT_PRIMARY,
            "relief": "solid",
            "bd": 1,
            "bg": "white"
        }
    
    @classmethod
    def get_label_style(cls):
        return {
            "font": cls.FONT_PRIMARY,
            "bg": cls.BG_SECONDARY,
            "fg": cls.TEXT_SECONDARY
        }