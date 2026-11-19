import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile

class AudioService:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def grabar_y_reconocer(self, duracion=5, idioma="pt-BR"):
        """Graba audio desde el micrófono usando sounddevice y lo convierte a texto"""
        fs = 44100  # Frecuencia de muestreo
        print("Grabando audio...")
        try:
            # Graba audio desde el micrófono
            recording = sd.rec(int(duracion * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()  # Espera a que termine la grabación
            
            # Guardar archivo temporal WAV
            temp_wav = os.path.join(tempfile.gettempdir(), "temp_speech.wav")
            write(temp_wav, fs, recording)

            # Reconocer texto mediante SpeechRecognition
            with sr.AudioFile(temp_wav) as source:
                audio_data = self.recognizer.record(source)
                texto = self.recognizer.recognize_google(audio_data, language=idioma)
                return texto
        except sr.UnknownValueError:
            return "No se logró entender el audio claramente."
        except Exception as e:
            return f"Error en la captura de audio: {e}"

    def reproducir_texto(self, texto, idioma="pt"):
        """Convierte texto en audio con acento natural mediante gTTS"""
        if not texto or "Error" in texto:
            return
        try:
            tts = gTTS(text=texto, lang=idioma, slow=False)
            temp_mp3 = os.path.join(tempfile.gettempdir(), "salida_audio.mp3")
            tts.save(temp_mp3)
            os.system(f'start "" "{temp_mp3}"')
        except Exception as e:
            print(f"Error reproduciendo audio: {e}")