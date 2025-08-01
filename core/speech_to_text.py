# core/speech_to_text.py
import asyncio
import logging
import speech_recognition as sr
import threading
import time
from typing import Optional, Callable
from config.settings import VoiceConfig

class SpeechToText:
    """Classe para reconhecimento de voz com escuta contínua"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Inicializar reconhecedor
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Estado da escuta contínua
        self.is_listening_continuously = False
        self.continuous_thread = None
        self.callback_function = None
        
        # Configurar microfone
        self.setup_microphone()
    
    def setup_microphone(self):
        """Configura o microfone"""
        try:
            with self.microphone as source:
                self.logger.info("Calibrando microfone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                # Ajustar para escuta contínua
                self.recognizer.energy_threshold = 4000
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 1.0
                self.logger.info("Microfone calibrado para escuta contínua!")
        except Exception as e:
            self.logger.error(f"Erro ao configurar microfone: {e}")
    
    async def listen(self, timeout: int = 5) -> Optional[str]:
        """Escuta uma única vez (modo manual)"""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._listen_once, timeout)
        except Exception as e:
            self.logger.error(f"Erro no reconhecimento de voz: {e}")
            return None
    
    def _listen_once(self, timeout: int) -> Optional[str]:
        """Método para escuta única"""
        try:
            print("🎤 Escutando... (fale agora)")
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            print("🔄 Processando...")
            
            try:
                text = self.recognizer.recognize_google(
                    audio, 
                    language=self.config.recognition_language
                )
                return text.strip()
            except sr.UnknownValueError:
                print("❌ Não consegui entender")
                return None
            except sr.RequestError as e:
                print("❌ Erro no serviço de reconhecimento")
                return None
                
        except sr.WaitTimeoutError:
            print("⏰ Timeout")
            return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def start_continuous_listening(self, callback: Callable[[str], None]):
        """Inicia escuta contínua em background"""
        if self.is_listening_continuously:
            return
        
        self.callback_function = callback
        self.is_listening_continuously = True
        
        # Iniciar thread de escuta contínua
        self.continuous_thread = threading.Thread(
            target=self._continuous_listen_worker,
            daemon=True
        )
        self.continuous_thread.start()
        
        print("👂 MODO ESCUTA CONTÍNUA ATIVADO")
        print("💡 Agora estou sempre escutando... fale naturalmente!")
    
    def stop_continuous_listening(self):
        """Para escuta contínua"""
        self.is_listening_continuously = False
        if self.continuous_thread:
            self.continuous_thread.join(timeout=2)
        print("🔇 Escuta contínua desativada")
    
    def _continuous_listen_worker(self):
        """Worker thread para escuta contínua"""
        self.logger.info("Iniciando escuta contínua...")
        
        while self.is_listening_continuously:
            try:
                with self.microphone as source:
                    # Escutar com timeout curto para não bloquear
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=8)
                
                # Processar áudio em background
                try:
                    text = self.recognizer.recognize_google(
                        audio, 
                        language=self.config.recognition_language
                    )
                    
                    if text and text.strip():
                        # Chamar callback com o texto reconhecido
                        if self.callback_function:
                            self.callback_function(text.strip())
                            
                except sr.UnknownValueError:
                    # Ignorar silenciosamente quando não entender
                    pass
                except sr.RequestError:
                    # Pausar um pouco se houver erro de rede
                    time.sleep(2)
                    
            except sr.WaitTimeoutError:
                # Timeout normal, continuar escutando
                pass
            except Exception as e:
                self.logger.error(f"Erro na escuta contínua: {e}")
                time.sleep(1)
        
        self.logger.info("Escuta contínua finalizada")
