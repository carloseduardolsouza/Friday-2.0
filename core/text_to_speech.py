# core/text_to_speech.py
import asyncio
import logging
import pyttsx3
import threading
from typing import Optional
from config.settings import VoiceConfig

class TextToSpeech:
    """Classe para síntese de voz"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Engine de TTS (criar novo para cada uso)
        self.engine_lock = threading.Lock()
        
    def _get_engine(self):
        """Cria um novo engine TTS"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.config.voice_rate)
            engine.setProperty('volume', self.config.voice_volume)
            
            # Tentar definir voz em português
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'portuguese' in voice.name.lower() or 'pt' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            return engine
        except Exception as e:
            self.logger.error(f"Erro ao criar engine TTS: {e}")
            return None
    
    async def speak(self, text: str):
        """Converte texto em fala"""
        if not text.strip():
            return
        
        try:
            # Executar TTS em thread separada com engine próprio
            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.run_in_executor(None, self._speak_sync, text),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            self.logger.warning("TTS timeout")
            print("[Áudio indisponível]")
        except Exception as e:
            self.logger.error(f"Erro na síntese de voz: {e}")
            print(f"[TTS Error: {e}]")
    
    def _speak_sync(self, text: str):
        """Método síncrono para TTS"""
        with self.engine_lock:
            try:
                # Criar novo engine para cada fala
                engine = self._get_engine()
                if engine:
                    engine.say(text)
                    engine.runAndWait()
                    # Limpar engine
                    engine.stop()
                    del engine
                else:
                    print(f"[FALA] {text}")
            except Exception as e:
                self.logger.error(f"Erro no TTS sync: {e}")
                print(f"[FALA] {text}")
