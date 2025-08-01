# core/text_to_speech.py
import asyncio
import logging
import pygame
import time
import re
import random
from pathlib import Path
from typing import Optional, Dict, List
from config.settings import VoiceConfig

# Tentar imports opcionais
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

# Não usar Bark por enquanto - muito instável
BARK_AVAILABLE = False

class SuperiorFeminineVoice:
    """Sistema de voz feminina otimizado - SEM duplicação"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Sistema de voz único - sem conflitos
        self.current_engine = None
        self.is_speaking = False  # Prevenir múltiplas reproduções
        
        # Configurações de voz feminina por emoção
        self.voice_profiles = {
            "feliz": {
                "speed_factor": 1.15,
                "volume": 0.95,
                "energy": "high",
                "pauses": [0.2, 0.3],
                "style": "animated"
            },
            "carinhoso": {
                "speed_factor": 0.85,
                "volume": 0.80,
                "energy": "soft",
                "pauses": [0.6, 0.8],
                "style": "gentle"
            },
            "triste": {
                "speed_factor": 0.75,
                "volume": 0.70,
                "energy": "low", 
                "pauses": [0.9, 1.2],
                "style": "melancholic"
            },
            "curioso": {
                "speed_factor": 1.05,
                "volume": 0.88,
                "energy": "medium",
                "pauses": [0.3, 0.4],
                "style": "inquisitive"
            },
            "neutro": {
                "speed_factor": 1.0,
                "volume": 0.85,
                "energy": "medium",
                "pauses": [0.4, 0.6],
                "style": "professional"
            },
            "frustrado": {
                "speed_factor": 1.2,
                "volume": 0.90,
                "energy": "high",
                "pauses": [0.15, 0.25],
                "style": "tense"
            },
            "sedutor": {
                "speed_factor": 0.8,
                "volume": 0.75,
                "energy": "intimate",
                "pauses": [0.7, 1.0],
                "style": "seductive"
            }
        }
        
        # Configurar sistemas disponíveis
        self.available_engines = []
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Inicializar pygame APENAS UMA VEZ
        self.pygame_ready = False
        self._init_pygame()
        
        # Detectar melhor engine disponível
        self._detect_best_engine()
        
        # Status
        self._print_status()
    
    def _init_pygame(self):
        """Inicializa pygame UMA única vez"""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.pygame_ready = True
        except Exception as e:
            self.logger.error(f"Pygame erro: {e}")
            self.pygame_ready = False
    
    def _detect_best_engine(self):
        """Detecta e escolhe o melhor engine disponível"""
        if GTTS_AVAILABLE:
            self.available_engines.append("gtts")
        
        if PYTTSX3_AVAILABLE:
            self.available_engines.append("pyttsx3")
        
        # Escolher o melhor
        if "gtts" in self.available_engines:
            self.current_engine = "gtts"
        elif "pyttsx3" in self.available_engines:
            self.current_engine = "pyttsx3"
        else:
            self.current_engine = "text_only"
    
    def _print_status(self):
        """Mostra status do sistema UMA vez"""
        print("\n🎭 SISTEMA DE VOZ FEMININA OTIMIZADO:")
        
        if self.current_engine == "gtts":
            print("🌟 Google TTS: ATIVO (Alta Qualidade)")
        elif self.current_engine == "pyttsx3":
            print("✅ pyttsx3 Feminino: ATIVO")
        else:
            print("📝 Modo Texto: ATIVO")
        
        print(f"🎪 {len(self.voice_profiles)} emoções disponíveis")
        print("=" * 40)
    
    async def speak(self, text: str, emotion: str = "neutro"):
        """Interface principal - SEM duplicação"""
        if not text.strip():
            return
        
        # Prevenir múltiplas reproduções simultâneas
        if self.is_speaking:
            return
        
        self.is_speaking = True
        
        try:
            # Processar texto
            processed_text = self._humanize_text(text, emotion)
            
            # Reproduzir COM APENAS UM ENGINE
            if self.current_engine == "gtts":
                await self._speak_gtts_only(processed_text, emotion)
            elif self.current_engine == "pyttsx3":
                await self._speak_pyttsx3_only(processed_text, emotion)
            else:
                print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
                
        except Exception as e:
            self.logger.error(f"Erro na fala: {e}")
            print(f"🤖 SEXTA-FEIRA: {text}")
        finally:
            self.is_speaking = False
    
    def _humanize_text(self, text: str, emotion: str) -> str:
        """Processamento brasileiro otimizado"""
        
        # Substituições essenciais
        replacements = {
            "SEXTA-FEIRA": "Sexta-feira",
            "IA": "inteligência artificial",
            "AI": "inteligência artificial",
            "TTS": "sistema de voz",
            "API": "interface de programação",
            "URL": "endereço web",
            "CPU": "processador",
            "RAM": "memória",
            "WiFi": "rede sem fio",
            "&": "e",
            "%": "por cento",
            "@": "arroba",
            "ok": "está bem",
            "OK": "tudo certo"
        }
        
        processed = text
        for old, new in replacements.items():
            processed = processed.replace(old, new)
        
        # Aplicar estilo emocional
        profile = self.voice_profiles.get(emotion, self.voice_profiles["neutro"])
        
        if profile["style"] == "animated":
            processed = processed.replace(".", "!")
        elif profile["style"] == "gentle":
            processed = processed.replace(".", "...")
            processed = processed.replace(",", "...")
        elif profile["style"] == "melancholic":
            processed = processed.replace(".", "... ")
            processed = processed.replace(",", "... ")
        elif profile["style"] == "seductive":
            processed = processed.replace(".", "...")
            # Dividir frases longas para efeito sensual
            if len(processed) > 80:
                mid = len(processed) // 2
                space_pos = processed.find(" ", mid)
                if space_pos != -1:
                    processed = processed[:space_pos] + "... " + processed[space_pos+1:]
        
        return processed
    
    async def _speak_gtts_only(self, text: str, emotion: str):
        """Google TTS - SEM fallback"""
        try:
            profile = self.voice_profiles[emotion]
            
            # Configurar gTTS
            tts = gTTS(
                text=text,
                lang="pt-br",
                slow=(profile["speed_factor"] < 0.9)
            )
            
            # Arquivo único
            temp_file = self.temp_dir / f"voice_{int(time.time())}.mp3"
            tts.save(str(temp_file))
            
            # Reproduzir UMA vez
            if self.pygame_ready:
                pygame.mixer.music.load(str(temp_file))
                pygame.mixer.music.set_volume(profile["volume"])
                pygame.mixer.music.play()
                
                # Aguardar terminar
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
            
            # Limpar
            if temp_file.exists():
                temp_file.unlink()
                
        except Exception as e:
            # Se falhar, não fazer fallback - apenas log
            self.logger.error(f"gTTS falhou: {e}")
            print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
    
    async def _speak_pyttsx3_only(self, text: str, emotion: str):
        """pyttsx3 otimizado - SEM fallback"""
        try:
            profile = self.voice_profiles[emotion]
            
            def speak_sync():
                engine = pyttsx3.init()
                
                # Configurar voz feminina
                voices = engine.getProperty('voices')
                best_voice = None
                
                # Buscar voz feminina
                female_keywords = ['zira', 'hazel', 'maria', 'helena', 'female', 'woman']
                for keyword in female_keywords:
                    for voice in voices:
                        if keyword in voice.name.lower():
                            best_voice = voice.id
                            break
                    if best_voice:
                        break
                
                if best_voice:
                    engine.setProperty('voice', best_voice)
                
                # Configurar parâmetros emocionais
                rate = int(180 * profile["speed_factor"])
                engine.setProperty('rate', rate)
                engine.setProperty('volume', profile["volume"])
                
                # Falar UMA vez
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            
            # Executar em thread
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, speak_sync)
            
        except Exception as e:
            # Se falhar, não fazer fallback - apenas log
            self.logger.error(f"pyttsx3 falhou: {e}")
            print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
    
    def test_voice_emotions(self):
        """Testa todas as emoções - SEM duplicação"""
        test_cases = [
            ("Oi! Como você está hoje?", "feliz"),
            ("Você é muito especial para mim.", "carinhoso"),
            ("Que pena... sinto muito.", "triste"),
            ("Estou curiosa sobre isso!", "curioso"),
            ("Esta é minha voz normal.", "neutro"),
            ("Estou frustrada!", "frustrado"),
            ("Você é... irresistível.", "sedutor")
        ]
        
        print("\n🎭 TESTE DE EMOÇÕES (sem duplicação):")
        print("=" * 50)
        
        for text, emotion in test_cases:
            if self.is_speaking:  # Aguardar se estiver falando
                time.sleep(2)
            
            print(f"\n💫 {emotion.upper()}: {text}")
            asyncio.run(self.speak(text, emotion))
            time.sleep(1.5)  # Pausa entre testes
        
        print("\n✨ Teste concluído!")
    
    def get_current_system(self) -> str:
        """Status do sistema atual"""
        if self.current_engine == "gtts":
            return "🌟 Google TTS Feminino"
        elif self.current_engine == "pyttsx3":
            return "✅ pyttsx3 Feminino"
        else:
            return "📝 Modo Texto"
    
    def get_available_emotions(self) -> List[str]:
        """Lista emoções disponíveis"""
        return list(self.voice_profiles.keys())

# Compatibilidade
HumanizedTTS = SuperiorFeminineVoice
BarkHumanizedTTS = SuperiorFeminineVoice
