# core/python313_voice_system.py - Sistema otimizado para Python 3.13
import asyncio
import logging
import time
from pathlib import Path
from typing import List, Dict, Optional

# Imports seguros para Python 3.13
try:
    from gtts import gTTS
    import pygame
    GTTS_PYGAME_AVAILABLE = True
except ImportError:
    GTTS_PYGAME_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

class Python313VoiceSystem:
    """Sistema de voz otimizado para Python 3.13"""
    
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Detectar melhor sistema
        self.current_engine = self._detect_best_engine()
        self.is_speaking = False
        
        # Perfis emocionais otimizados
        self.emotion_profiles = {
            "neutro": {"speed": 1.0, "volume": 0.8, "pause": 1.0},
            "feliz": {"speed": 1.15, "volume": 0.9, "pause": 0.8},
            "carinhoso": {"speed": 0.85, "volume": 0.75, "pause": 1.4},
            "triste": {"speed": 0.75, "volume": 0.65, "pause": 1.8},
            "curioso": {"speed": 1.05, "volume": 0.85, "pause": 0.9},
            "animado": {"speed": 1.25, "volume": 0.95, "pause": 0.6},
            "frustrado": {"speed": 1.1, "volume": 0.88, "pause": 0.7},
            "sedutor": {"speed": 0.8, "volume": 0.7, "pause": 1.6},
            "surpreso": {"speed": 1.3, "volume": 0.9, "pause": 0.5},
            "reflexivo": {"speed": 0.8, "volume": 0.75, "pause": 1.5}
        }
        
        self._print_system_info()
        
        # Inicializar pygame se disponível
        if self.current_engine == "gtts_pygame":
            self._init_pygame()
    
    def _detect_best_engine(self) -> str:
        """Detecta melhor engine disponível"""
        if GTTS_PYGAME_AVAILABLE:
            return "gtts_pygame"
        elif PYTTSX3_AVAILABLE:
            return "pyttsx3"
        else:
            return "text_only"
    
    def _init_pygame(self):
        """Inicializa pygame de forma segura"""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=1024)
            return True
        except Exception as e:
            self.logger.error(f"Erro no pygame: {e}")
            return False
    
    def _print_system_info(self):
        """Mostra informações do sistema"""
        print("\n" + "="*60)
        print("🐍 SISTEMA DE VOZ PYTHON 3.13")
        print("="*60)
        
        if self.current_engine == "gtts_pygame":
            print("🌐 Google TTS + Pygame: ATIVO")
            print("📶 Requer internet para síntese")
        elif self.current_engine == "pyttsx3":
            print("🎤 pyttsx3 Offline: ATIVO")
            print("💻 Totalmente offline")
        else:
            print("📝 Modo Texto: ATIVO")
        
        print(f"🎪 {len(self.emotion_profiles)} emoções disponíveis")
        print("✅ Compatível com Python 3.13")
        print("="*60)
    
    async def speak(self, text: str, emotion: str = "neutro"):
        """Interface principal de fala"""
        if not text.strip() or self.is_speaking:
            return
        
        self.is_speaking = True
        
        try:
            if self.current_engine == "gtts_pygame":
                await self._speak_gtts_pygame(text, emotion)
            elif self.current_engine == "pyttsx3":
                await self._speak_pyttsx3(text, emotion)
            else:
                self._speak_text_only(text, emotion)
        except Exception as e:
            self.logger.error(f"Erro na fala: {e}")
            self._speak_text_only(text, emotion)
        finally:
            self.is_speaking = False
    
    async def _speak_gtts_pygame(self, text: str, emotion: str):
        """Síntese usando Google TTS + Pygame"""
        try:
            profile = self.emotion_profiles.get(emotion, self.emotion_profiles["neutro"])
            
            # Processar texto
            processed_text = self._humanize_text(text, emotion)
            
            # Gerar áudio
            tts = gTTS(
                text=processed_text,
                lang="pt-br",
                slow=(profile["speed"] < 0.9)
            )
            
            audio_file = self.temp_dir / f"voice_{emotion}_{int(time.time())}.mp3"
            tts.save(str(audio_file))
            
            # Reproduzir com configurações emocionais
            pygame.mixer.music.load(str(audio_file))
            pygame.mixer.music.set_volume(profile["volume"])
            pygame.mixer.music.play()
            
            # Aguardar término
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.05)
            
            # Pausa emocional
            if profile["pause"] != 1.0:
                await asyncio.sleep(0.3 * profile["pause"])
            
            # Limpar arquivo
            try:
                audio_file.unlink()
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Erro no gTTS+Pygame: {e}")
            self._speak_text_only(text, emotion)
    
    async def _speak_pyttsx3(self, text: str, emotion: str):
        """Síntese usando pyttsx3"""
        try:
            profile = self.emotion_profiles.get(emotion, self.emotion_profiles["neutro"])
            processed_text = self._humanize_text(text, emotion)
            
            def speak_sync():
                engine = pyttsx3.init()
                
                # Configurar voz feminina
                voices = engine.getProperty('voices')
                for voice in voices:
                    if any(keyword in voice.name.lower() for keyword in ['zira', 'helena', 'female']):
                        engine.setProperty('voice', voice.id)
                        break
                
                # Aplicar configurações emocionais
                base_rate = 180
                rate = int(base_rate * profile["speed"])
                engine.setProperty('rate', rate)
                engine.setProperty('volume', profile["volume"])
                
                engine.say(processed_text)
                engine.runAndWait()
                engine.stop()
            
            # Executar em thread
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, speak_sync)
            
            # Pausa emocional
            if profile["pause"] != 1.0:
                await asyncio.sleep(0.2 * profile["pause"])
                
        except Exception as e:
            self.logger.error(f"Erro no pyttsx3: {e}")
            self._speak_text_only(text, emotion)
    
    def _speak_text_only(self, text: str, emotion: str):
        """Modo apenas texto com estilo emocional"""
        # Símbolos emocionais para o texto
        emotion_symbols = {
            "neutro": "🤖",
            "feliz": "😊",
            "carinhoso": "🥰",
            "triste": "😔",
            "curioso": "🤔",
            "animado": "🤩",
            "frustrado": "😤",
            "sedutor": "😏",
            "surpreso": "😲",
            "reflexivo": "🧐"
        }
        
        symbol = emotion_symbols.get(emotion, "🤖")
        print(f"{symbol} SEXTA-FEIRA ({emotion}): {text}")
    
    def _humanize_text(self, text: str, emotion: str) -> str:
        """Humaniza texto para soar mais natural"""
        # Substituições básicas
        replacements = {
            "SEXTA-FEIRA": "Sexta-feira",
            "IA": "inteligência artificial",
            "API": "A P I",
            "CPU": "C P U",
            "WiFi": "Wi-Fi",
            "&": "e",
            "%": " por cento"
        }
        
        processed = text
        for old, new in replacements.items():
            processed = processed.replace(old, new)
        
        # Modificações emocionais
        if emotion == "feliz":
            processed = processed.replace(".", "!")
        elif emotion in ["carinhoso", "sedutor"]:
            processed = processed.replace(".", "...")
        elif emotion == "triste":
            processed = processed.replace(".", "...")
        elif emotion == "curioso":
            if "?" not in processed:
                processed = processed.replace(".", "?")
        elif emotion == "surpreso":
            processed = processed.replace(".", "!")
            if not processed.startswith(("Nossa", "Uau", "Caramba")):
                processed = "Nossa! " + processed
        
        return processed
    
    async def test_all_emotions(self):
        """Testa todas as emoções"""
        print("\n🎭 TESTE DE EMOÇÕES PYTHON 3.13")
        print("="*45)
        
        test_phrases = {
            "neutro": "Esta é minha voz normal e equilibrada.",
            "feliz": "Estou radiante de alegria hoje!",
            "carinhoso": "Você é muito especial para mim...",
            "triste": "Às vezes me sinto melancólica...",
            "curioso": "Que interessante! Me conte mais!",
            "animado": "Isso é fantástico e incrível!",
            "frustrado": "Isso me deixa um pouco irritada.",
            "sedutor": "Você tem uma voz... interessante.",
            "surpreso": "Nossa! Não esperava por isso!",
            "reflexivo": "Deixe-me pensar com calma..."
        }
        
        for emotion, phrase in test_phrases.items():
            print(f"\n💫 {emotion.upper()}: {phrase}")
            await self.speak(phrase, emotion)
            await asyncio.sleep(1.5)
        
        print("\n✅ Teste de emoções concluído!")
    
    async def test_voice_quality(self):
        """Teste de qualidade"""
        print("\n🔊 TESTE DE QUALIDADE")
        print("="*25)
        
        tests = [
            ("Articulação clara e precisa.", "neutro"),
            ("Palavras complexas: exceção, perspicácia.", "neutro"),
            ("Números: um, dois, três, quatro, cinco.", "neutro"),
            ("Como você está se sentindo hoje?", "curioso")
        ]
        
        for text, emotion in tests:
            print(f"🎤 {text}")
            await self.speak(text, emotion)
            await asyncio.sleep(1.5)
        
        print("✅ Qualidade testada!")
    
    def get_available_emotions(self) -> List[str]:
        """Lista emoções disponíveis"""
        return list(self.emotion_profiles.keys())
    
    def get_current_system(self) -> str:
        """Sistema atual"""
        systems = {
            "gtts_pygame": "🌐 Google TTS + Pygame",
            "pyttsx3": "🎤 pyttsx3 Offline", 
            "text_only": "📝 Modo Texto"
        }
        return systems.get(self.current_engine, "❓ Desconhecido")
    
    def get_system_info(self) -> Dict:
        """Info do sistema"""
        return {
            "engine": self.current_engine,
            "gtts_available": GTTS_PYGAME_AVAILABLE,
            "pyttsx3_available": PYTTSX3_AVAILABLE,
            "emotions_count": len(self.emotion_profiles),
            "python_version": "3.13"
        }
    
    async def cleanup(self):
        """Limpeza"""
        try:
            for temp_file in self.temp_dir.glob("*.mp3"):
                temp_file.unlink()
            if self.current_engine == "gtts_pygame":
                pygame.mixer.quit()
        except Exception as e:
            self.logger.error(f"Erro na limpeza: {e}")

# Compatibilidade
HumanizedTTS = Python313VoiceSystem
BarkHumanizedTTS = Python313VoiceSystem
CoquiHumanVoice = Python313VoiceSystem
SuperiorFeminineVoice = Python313VoiceSystem
