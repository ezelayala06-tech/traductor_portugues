import customtkinter as ctk
import os
from src.translator_engine import PortuguesTranslatorEngine
from src.audio_service import AudioService
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configuración visual de la interfaz
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AppTraductor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Traductor Inteligente Portugués <-> Español")
        self.geometry("750x600")

        self.engine = PortuguesTranslatorEngine()
        self.audio = AudioService()

        # Selección de dirección
        self.modo_var = ctk.StringVar(value="pt_a_es")

        self._crear_widgets()

    def _crear_widgets(self):
        # Título principal
        lbl_titulo = ctk.CTkLabel(
            self, 
            text="Traductor Portugués - Español", 
            font=("Arial", 22, "bold")
        )
        lbl_titulo.pack(pady=15)

        # Marco para selección de idioma
        frame_modo = ctk.CTkFrame(self)
        frame_modo.pack(pady=5, padx=20, fill="x")

        rb1 = ctk.CTkRadioButton(
            frame_modo, 
            text="Portugués ➔ Español", 
            variable=self.modo_var, 
            value="pt_a_es"
        )
        rb1.pack(side="left", padx=20, pady=10)

        rb2 = ctk.CTkRadioButton(
            frame_modo, 
            text="Español ➔ Portugués", 
            variable=self.modo_var, 
            value="es_a_pt"
        )
        rb2.pack(side="left", padx=20, pady=10)

        # Entrada de Texto
        self.txt_entrada = ctk.CTkTextbox(self, height=120)
        self.txt_entrada.pack(pady=10, padx=20, fill="x")
        self.txt_entrada.insert("1.0", "Escribe o graba un texto aquí...")

        # Botones de Acción
        frame_botones = ctk.CTkFrame(self)
        frame_botones.pack(pady=5, padx=20, fill="x")

        btn_traducir = ctk.CTkButton(
            frame_botones, 
            text="Traducir", 
            command=self.ejecutar_traduccion
        )
        btn_traducir.pack(side="left", padx=10, pady=10)

        btn_mic = ctk.CTkButton(
            frame_botones, 
            text="🎤 Grabar Voz", 
            fg_color="green", 
            command=self.grabar_voz
        )
        btn_mic.pack(side="left", padx=10, pady=10)

        btn_pdf = ctk.CTkButton(
            frame_botones, 
            text="📄 Exportar PDF", 
            fg_color="orange", 
            command=self.exportar_pdf
        )
        btn_pdf.pack(side="right", padx=10, pady=10)

        # Salida de Texto
        self.txt_salida = ctk.CTkTextbox(self, height=120)
        self.txt_salida.pack(pady=10, padx=20, fill="x")

        # Botón para escuchar traducción
        btn_audio = ctk.CTkButton(
            self, 
            text="🔊 Escuchar Traducción", 
            command=self.escuchar_traduccion
        )
        btn_audio.pack(pady=5)

        # Etiqueta de Alerta para Falsos Cognados / Falsos Amigos
        self.lbl_alerta = ctk.CTkLabel(
            self, 
            text="", 
            text_color="darkorange", 
            font=("Arial", 12, "italic")
        )
        self.lbl_alerta.pack(pady=10)

    def ejecutar_traduccion(self):
        texto = texto = self.txt_entrada.get("1.0", "end").strip()
        modo = self.modo_var.get()

        traduccion, alerta = self.engine.traducir_texto(texto, modo=modo)
        
        self.txt_salida.delete("1.0", "end")
        self.txt_salida.insert("1.0", traduccion)

        self.lbl_alerta.configure(text=alerta)

    def grabar_voz(self):
        self.lbl_alerta.configure(text="Grabando audio por 5 segundos...")
        self.update()

        idioma_mic = "pt-BR" if self.modo_var.get() == "pt_a_es" else "es-ES"
        texto_reconocido = self.audio.grabar_y_reconocer(duracion=5, idioma=idioma_mic)

        self.txt_entrada.delete("1.0", "end")
        self.txt_entrada.insert("1.0", texto_reconocido)
        
        self.ejecutar_traduccion()

    def escuchar_traduccion(self):
        texto = self.txt_salida.get("1.0", "end").strip()
        idioma_audio = "es" if self.modo_var.get() == "pt_a_es" else "pt"
        self.audio.reproducir_texto(texto, idioma=idioma_audio)

    def exportar_pdf(self):
        historial = self.engine.db.obtener_historial()
        pdf_path = "historial_traducciones.pdf"

        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "Historial de Traducciones (Portugués - Español)")
        
        c.setFont("Helvetica", 10)
        y = 710

        for reg in historial:
            origen, destino, fecha = reg
            linea = f"[{fecha}] {origen} -> {destino}"
            c.drawString(50, y, linea[:90])
            y -= 20
            if y < 50:
                c.showPage()
                y = 750

        c.save()
        self.lbl_alerta.configure(text=f"PDF generado con éxito: {os.path.abspath(pdf_path)}")

if __name__ == "__main__":
    app = AppTraductor()
    app.mainloop()