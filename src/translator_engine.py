from deep_translator import MyMemoryTranslator
from database.db_manager import DatabaseManager

class PortuguesTranslatorEngine:
    def __init__(self):
        self.db = DatabaseManager()

    def traducir_texto(self, texto, modo="pt_a_es"):
        if not texto or not texto.strip():
            return "", ""

        texto_limpio = texto.strip()
        
        # Códigos de idioma soportados por MyMemory
        src_lang = "pt-BR" if modo == "pt_a_es" else "es-ES"
        dest_lang = "es-ES" if modo == "pt_a_es" else "pt-BR"

        alerta_falso_amigo = ""

        # 1. Chequeo de Falsos Amigos / Falsos Cognados en la BD
        if modo == "pt_a_es":
            palabras = texto_limpio.lower().split()
            for p in palabras:
                reg = self.db.buscar_falso_amigo(p)
                if reg and reg[1] == "falso_amigo":
                    alerta_falso_amigo = f"⚠️ Nota: '{p}' es un falso cognado. En español significa '{reg[0]}'."
                    break

        # 2. Respaldo directo en BD local
        reg_bd = self.db.buscar_falso_amigo(texto_limpio.lower())
        if reg_bd and modo == "pt_a_es":
            self.db.registrar_traduccion(f"[{modo.upper()}] {texto_limpio}", reg_bd[0])
            return reg_bd[0], alerta_falso_amigo

        # 3. Traducción Neuronal con MyMemory
        try:
            translator = MyMemoryTranslator(source=src_lang, target=dest_lang)
            traduccion = translator.translate(texto_limpio)
            
            if traduccion:
                self.db.registrar_traduccion(f"[{modo.upper()}] {texto_limpio}", traduccion)
                return traduccion, alerta_falso_amigo
            else:
                return "No se pudo traducir el texto.", alerta_falso_amigo

        except Exception as e:
            print(f"Error en servidor de traducción: {e}")
            return "Error de conexión al traducir.", alerta_falso_amigo