# core/text_to_speech.py - Sistema principal simples
import asyncio
import logging
from typing import List
from config.settings import VoiceConfig

# Sistema brasileiro simples
try:
    import sys
    from pathlib import Path
    
    # Aplicar patch PyTorch
    if Path("pytorch_fix.py").exists():
        exec(open("pytorch_fix.py").read())
    
    # Importar sistema brasileiro
    from brazilian_tts_simple import SimpleBrazilianTTS
    BRAZILIAN_AVAILABLE = True
except ImportError as e:
    print(f"Sistema brasileiro não disponível: {e}")
    BRAZILIAN_AVAILABLE = False

class SuperiorFeminineVoice:
    """Sistema principal com TTS brasileiro"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.brazilian_tts = None
        self.is_initialized = False
        
        asyncio.create_task(self._initialize_system())
    
    async def _initialize_system(self):
        if self.is_initialized:
            return
        
        print("\n🇧🇷 INICIALIZANDO TTS BRASILEIRO")
        print("="*35)
        
        if BRAZILIAN_AVAILABLE:
            try:
                self.brazilian_tts = SimpleBrazilianTTS()
                self.current_system = "brazilian"
                print("✅ TTS brasileiro ativo!")
            except Exception as e:
                print(f"❌ Erro TTS: {e}")
                self.current_system = "text_only"
        else:
            self.current_system = "text_only"
            print("📝 Modo texto")
        
        self.is_initialized = True
    
    async def speak(self, text: str, emotion: str = "neutro"):
        if not self.is_initialized:
            await self._initialize_system()
        
        if self.brazilian_tts:
            await self.brazilian_tts.speak(text, emotion)
        else:
            print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
    
    async def test_voice_emotions(self):
        if not self.is_initialized:
            await self._initialize_system()
        
        if self.brazilian_tts:
            await self.brazilian_tts.test_emotions()
        else:
            print("📝 Teste no modo texto")
    
    def get_current_system(self):
        if self.brazilian_tts:
            return self.brazilian_tts.get_system_info()
        return "📝 Modo Texto"
    
    def get_available_emotions(self):
        if self.brazilian_tts:
            return list(self.brazilian_tts.emotions.keys())
        return ["neutro", "feliz", "triste"]

# Compatibilidade
HumanizedTTS = SuperiorFeminineVoice
BarkHumanizedTTS = SuperiorFeminineVoice
