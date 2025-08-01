# core/brazilian_voice_system.py - Sistema de voz brasileiro
import asyncio
import logging
import time
import json
from pathlib import Path

class BrazilianVoiceSystem:
    """Sistema de voz otimizado para português brasileiro"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tts = None
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Configuração carregada
        self.config = self.load_voice_config()
        
        # Emoções em português brasileiro
        self.emotions_ptbr = {
            "neutro": {"text_prefix": "", "text_suffix": ""},
            "feliz": {"text_prefix": "", "text_suffix": "!"},
            "carinhoso": {"text_prefix": "", "text_suffix": "..."},
            "triste": {"text_prefix": "", "text_suffix": "..."},
            "curioso": {"text_prefix": "", "text_suffix": "?"},
            "animado": {"text_prefix": "Nossa! ", "text_suffix": "!"},
            "frustrado": {"text_prefix": "", "text_suffix": "."},
            "surpreso": {"text_prefix": "Uau! ", "text_suffix": "!"},
            "reflexivo": {"text_prefix": "Bem... ", "text_suffix": "..."},
            "sedutor": {"text_prefix": "", "text_suffix": "..."}
        }
        
        self.initialize_tts()
    
    def load_voice_config(self):
        """Carrega configuração da voz brasileira"""
        try:
            config_file = Path("config/brazilian_voice_config.json")
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao carregar config: {e}")
        
        # Configuração padrão
        return {
            "model_name": "tts_models/pt/cv/vits",
            "model_type": "vits",
            "language": "pt"
        }
    
    def initialize_tts(self):
        """Inicializa TTS brasileiro"""
        try:
            # Patch MeCab
            self.patch_mecab()
            
            from TTS.api import TTS
            
            model_name = self.config["model_name"]
            print(f"🇧🇷 Carregando voz brasileira: {model_name}")
            
            self.tts = TTS(model_name=model_name, progress_bar=True)
            
            print("✅ Voz brasileira carregada com sucesso!")
            print(f"🎭 Tipo: {self.config.get('description', 'Voz brasileira')}")
            
        except Exception as e:
            print(f"❌ Erro ao carregar voz brasileira: {e}")
            self.tts = None
    
    def patch_mecab(self):
        """Patch MeCab para evitar erros"""
        import sys
        class FakeMeCab:
            class Tagger:
                def __init__(self, *args, **kwargs): pass
                def parse(self, text): return text
        sys.modules['MeCab'] = FakeMeCab()
    
    async def speak(self, text, emotion="neutro"):
        """Fala em português brasileiro com emoção"""
        if not self.tts:
            print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
            return
        
        try:
            # Processar texto para português brasileiro
            processed_text = self.process_brazilian_text(text, emotion)
            
            # Gerar áudio
            audio_file = self.temp_dir / f"ptbr_{emotion}_{int(time.time())}.wav"
            
            # Diferentes métodos baseados no modelo
            if self.config["model_type"] == "xtts_v2":
                self.tts.tts_to_file(
                    text=processed_text,
                    file_path=str(audio_file),
                    language="pt",
                    speaker_wav=None  # Pode usar voz customizada aqui
                )
            else:
                self.tts.tts_to_file(
                    text=processed_text,
                    file_path=str(audio_file)
                )
            
            print(f"🇧🇷 SEXTA-FEIRA (PT-BR {emotion}): {text}")
            print(f"🔊 Áudio brasileiro: {audio_file.name}")
            
            # Reproduzir
            await self.play_audio(audio_file)
            
            # Limpar
            try:
                audio_file.unlink()
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Erro na fala brasileira: {e}")
            print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
    
    def process_brazilian_text(self, text, emotion):
        """Processa texto para soar mais brasileiro"""
        # Substituições brasileiras
        brazilian_replacements = {
            "SEXTA-FEIRA": "Sexta-feira",
            "IA": "inteligência artificial",
            "você": "você",
            "está": "tá" if emotion in ["feliz", "animado"] else "está",
            "muito": "muito",
            "legal": "legal",
            "bacana": "bacana"
        }
        
        processed = text
        for old, new in brazilian_replacements.items():
            processed = processed.replace(old, new)
        
        # Adicionar modificações emocionais
        emotion_config = self.emotions_ptbr.get(emotion, self.emotions_ptbr["neutro"])
        
        processed = emotion_config["text_prefix"] + processed + emotion_config["text_suffix"]
        
        return processed
    
    async def play_audio(self, audio_file):
        """Reproduz áudio"""
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            pygame.mixer.music.load(str(audio_file))
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
        except ImportError:
            print("🔊 Instale pygame para reprodução automática")
        except Exception as e:
            print(f"⚠️ Erro na reprodução: {e}")
    
    async def test_brazilian_emotions(self):
        """Testa emoções em português brasileiro"""
        print("\n🇧🇷 TESTE DE EMOÇÕES BRASILEIRAS")
        print("="*38)
        
        brazilian_tests = [
            ("Oi, tudo bem? Eu sou a Sexta-feira!", "neutro"),
            ("Que legal! Estou super animada hoje!", "feliz"),
            ("Você é muito querido, sabia?", "carinhoso"),
            ("Puxa, que triste essa notícia...", "triste"),
            ("Hmmm, que interessante isso!", "curioso"),
            ("Nossa! Que demais! Adorei!", "animado"),
            ("Poxa, isso me deixa chateada.", "frustrado"),
            ("Caramba! Não acredito!", "surpreso"),
            ("Bem... deixa eu pensar sobre isso.", "reflexivo"),
            ("Você tem uma voz muito... interessante.", "sedutor")
        ]
        
        for text, emotion in brazilian_tests:
            print(f"\n💫 {emotion.upper()}: {text}")
            await self.speak(text, emotion)
            await asyncio.sleep(2)
        
        print("\n✅ Teste brasileiro concluído!")
    
    def get_current_system(self):
        """Sistema atual"""
        if self.tts:
            return f"🇧🇷 Voz Brasileira ({self.config['model_type'].upper()})"
        return "📝 Modo Texto"
    
    def get_available_emotions(self):
        """Emoções disponíveis"""
        return list(self.emotions_ptbr.keys())
    
    def get_voice_info(self):
        """Informações da voz"""
        return {
            "model": self.config.get("model_name", "Desconhecido"),
            "type": self.config.get("model_type", "Desconhecido"),
            "quality": self.config.get("quality", "Desconhecido"),
            "language": "Português Brasileiro",
            "emotions": len(self.emotions_ptbr),
            "features": self.config.get("features", [])
        }

# Compatibilidade
HumanizedTTS = BrazilianVoiceSystem
BarkHumanizedTTS = BrazilianVoiceSystem
CoquiHumanVoice = BrazilianVoiceSystem
SuperiorFeminineVoice = BrazilianVoiceSystem
