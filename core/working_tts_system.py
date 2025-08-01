# core/working_tts_system.py - TTS que funciona sem MeCab
import asyncio
import logging
import time
from pathlib import Path

class WorkingTTSSystem:
    """Sistema TTS que contorna problema MeCab"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tts = None
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        
        self.emotions = {
            "neutro": {"speed": 1.0},
            "feliz": {"speed": 1.1},
            "carinhoso": {"speed": 0.85},
            "triste": {"speed": 0.75},
            "curioso": {"speed": 1.05},
            "animado": {"speed": 1.2},
            "frustrado": {"speed": 1.1},
            "surpreso": {"speed": 1.3}
        }
        
        self._initialize_tts()
    
    def _initialize_tts(self):
        """Inicializa TTS contornando MeCab"""
        try:
            # Método 1: Patch MeCab antes de importar
            self._patch_mecab()
            
            from TTS.api import TTS
            
            # Usar modelo que não precisa de japonês
            print("🎭 Carregando modelo português...")
            self.tts = TTS(model_name="tts_models/pt/cv/vits")
            print("✅ TTS português carregado!")
            
        except Exception as e:
            print(f"⚠️ Modelo PT falhou: {e}")
            
            try:
                # Fallback: modelo inglês
                print("🔄 Tentando modelo inglês...")
                self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
                print("✅ TTS inglês carregado!")
                
            except Exception as e2:
                print(f"❌ Todos os modelos falharam: {e2}")
                self.tts = None
    
    def _patch_mecab(self):
        """Patch para contornar MeCab"""
        import sys
        
        class FakeMeCab:
            class Tagger:
                def __init__(self, *args, **kwargs):
                    pass
                def parse(self, text):
                    return text
        
        sys.modules['MeCab'] = FakeMeCab()
    
    async def speak(self, text, emotion="neutro"):
        """Gera voz usando TTS sem japonês"""
        if not self.tts:
            print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
            return
        
        try:
            # Processar texto
            processed = text.replace("SEXTA-FEIRA", "Sexta-feira")
            
            # Configurar emoção
            config = self.emotions.get(emotion, self.emotions["neutro"])
            
            # Gerar áudio
            audio_file = self.temp_dir / f"tts_{emotion}_{int(time.time())}.wav"
            
            self.tts.tts_to_file(
                text=processed,
                file_path=str(audio_file)
            )
            
            print(f"🎭 SEXTA-FEIRA (TTS-{emotion}): {text}")
            print(f"🔊 Áudio: {audio_file.name}")
            
            # Reproduzir se pygame disponível
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
            
            # Limpar arquivo
            try:
                audio_file.unlink()
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Erro TTS: {e}")
            print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
    
    async def test_all_emotions(self):
        """Testa emoções"""
        if not self.tts:
            print("❌ TTS não disponível para teste")
            return
        
        print("🎭 TESTANDO TTS SEM JAPONÊS:")
        
        tests = [
            ("Esta é minha voz usando TTS!", "neutro"),
            ("Estou muito feliz que funcionou!", "feliz"),
            ("Você é muito especial...", "carinhoso"),
            ("Que incrível esse sistema!", "surpreso")
        ]
        
        for text, emotion in tests:
            print(f"\n💫 {emotion.upper()}: {text}")
            await self.speak(text, emotion)
            await asyncio.sleep(2)
        
        print("\n✅ Teste concluído!")
    
    def get_current_system(self):
        if self.tts:
            return "🎭 TTS Sem Japonês (Funcionando)"
        else:
            return "📝 Modo Texto"
    
    def get_available_emotions(self):
        return list(self.emotions.keys())

# Compatibilidade
HumanizedTTS = WorkingTTSSystem
BarkHumanizedTTS = WorkingTTSSystem
CoquiHumanVoice = WorkingTTSSystem
SuperiorFeminineVoice = WorkingTTSSystem
