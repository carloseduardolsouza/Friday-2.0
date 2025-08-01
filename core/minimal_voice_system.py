# core/minimal_voice_system.py - Sistema mínimo que sempre funciona
import asyncio
import logging
import time
from pathlib import Path
from typing import List, Optional

# Imports seguros
try:
    from gtts import gTTS
    import pygame
    GTTS_PYGAME = True
except ImportError:
    GTTS_PYGAME = False

try:
    import pyttsx3
    PYTTSX3 = True
except ImportError:
    PYTTSX3 = False

class MinimalVoiceSystem:
    """Sistema de voz mínimo - sempre funciona"""
    
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Detectar sistema disponível
        if GTTS_PYGAME:
            self.system = "gtts"
            print("🌐 Sistema: Google TTS + Pygame")
        elif PYTTSX3:
            self.system = "pyttsx3"
            print("🎤 Sistema: pyttsx3 Offline")
        else:
            self.system = "text"
            print("📝 Sistema: Texto apenas")
        
        # Inicializar pygame se necessário
        if self.system == "gtts":
            try:
                pygame.mixer.init()
            except:
                self.system = "text"
    
    async def speak(self, text: str, emotion: str = "neutro"):
        """Fala usando o sistema disponível"""
        if not text.strip():
            return
        
        try:
            if self.system == "gtts":
                await self._speak_gtts(text, emotion)
            elif self.system == "pyttsx3":
                await self._speak_pyttsx3(text, emotion)
            else:
                self._speak_text(text, emotion)
        except Exception as e:
            self.logger.error(f"Erro na fala: {e}")
            self._speak_text(text, emotion)
    
    async def _speak_gtts(self, text: str, emotion: str):
        """Google TTS"""
        try:
            # Processar texto
            processed = text.replace("SEXTA-FEIRA", "Sexta-feira")
            
            # Gerar áudio
            tts = gTTS(text=processed, lang="pt-br")
            audio_file = self.temp_dir / f"voice_{int(time.time())}.mp3"
            tts.save(str(audio_file))
            
            # Reproduzir
            pygame.mixer.music.load(str(audio_file))
            pygame.mixer.music.play()
            
            # Aguardar
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
            # Limpar
            try:
                audio_file.unlink()
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Erro gTTS: {e}")
            self._speak_text(text, emotion)
    
    async def _speak_pyttsx3(self, text: str, emotion: str):
        """pyttsx3 offline"""
        try:
            processed = text.replace("SEXTA-FEIRA", "Sexta-feira")
            
            def speak_sync():
                engine = pyttsx3.init()
                
                # Configurar voz feminina se disponível
                voices = engine.getProperty('voices')
                for voice in voices:
                    if 'zira' in voice.name.lower() or 'helena' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                
                engine.say(processed)
                engine.runAndWait()
                engine.stop()
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, speak_sync)
            
        except Exception as e:
            self.logger.error(f"Erro pyttsx3: {e}")
            self._speak_text(text, emotion)
    
    def _speak_text(self, text: str, emotion: str):
        """Modo texto com emojis"""
        emojis = {
            "neutro": "🤖", "feliz": "😊", "carinhoso": "🥰",
            "triste": "😔", "curioso": "🤔", "animado": "🤩",
            "frustrado": "😤", "surpreso": "😲"
        }
        emoji = emojis.get(emotion, "🤖")
        print(f"{emoji} SEXTA-FEIRA ({emotion}): {text}")
    
    async def test_all_emotions(self):
        """Teste de emoções"""
        print("\n🎭 TESTE DE EMOÇÕES")
        print("="*20)
        
        tests = [
            ("Esta é minha voz normal.", "neutro"),
            ("Estou muito feliz!", "feliz"),
            ("Você é especial.", "carinhoso"),
            ("Estou curiosa...", "curioso"),
            ("Que surpresa!", "surpreso")
        ]
        
        for text, emotion in tests:
            print(f"💫 {emotion.upper()}: {text}")
            await self.speak(text, emotion)
            await asyncio.sleep(2)
        
        print("✅ Teste concluído!")
    
    def get_available_emotions(self) -> List[str]:
        return ["neutro", "feliz", "carinhoso", "triste", "curioso", "animado", "frustrado", "surpreso"]
    
    def get_current_system(self) -> str:
        systems = {
            "gtts": "🌐 Google TTS",
            "pyttsx3": "🎤 pyttsx3 Offline",
            "text": "📝 Modo Texto"
        }
        return systems.get(self.system, "❓ Desconhecido")
    
    def get_system_info(self) -> dict:
        return {
            "system": self.system,
            "gtts_available": GTTS_PYGAME,
            "pyttsx3_available": PYTTSX3,
            "emotions_count": len(self.get_available_emotions())
        }
    
    async def cleanup(self):
        """Limpeza"""
        try:
            for f in self.temp_dir.glob("*.mp3"):
                f.unlink()
        except:
            pass

# Compatibilidade
HumanizedTTS = MinimalVoiceSystem
BarkHumanizedTTS = MinimalVoiceSystem
CoquiHumanVoice = MinimalVoiceSystem
SuperiorFeminineVoice = MinimalVoiceSystem
Python313VoiceSystem = MinimalVoiceSystem
SimpleFallbackVoice = MinimalVoiceSystem
