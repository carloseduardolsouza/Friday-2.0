# core/text_to_speech.py - Atualizado para sistema mínimo
import asyncio
import logging
from typing import List
from config.settings import VoiceConfig

# Import do sistema mínimo (sempre funciona)
try:
    from core.minimal_voice_system import MinimalVoiceSystem
    MINIMAL_AVAILABLE = True
except ImportError:
    MINIMAL_AVAILABLE = False

class SuperiorFeminineVoice:
    """Sistema de voz com fallback garantido"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.voice_system = None
        self.is_initialized = False
        
        # Inicializar automaticamente
        asyncio.create_task(self._initialize_system())
    
    async def _initialize_system(self):
        """Inicializa sistema mínimo"""
        if self.is_initialized:
            return
        
        try:
            if MINIMAL_AVAILABLE:
                self.voice_system = MinimalVoiceSystem(self.config)
                self.current_system = "minimal"
                self.logger.info("✅ Sistema mínimo ativado")
            else:
                self.current_system = "text_only"
                self.logger.warning("📝 Apenas texto disponível")
            
            self.is_initialized = True
            self._print_status()
            
        except Exception as e:
            self.logger.error(f"Erro: {e}")
            self.current_system = "text_only"
            self.is_initialized = True
    
    def _print_status(self):
        """Status do sistema"""
        print("\n" + "="*50)
        print("🎭 SISTEMA DE VOZ SEXTA-FEIRA")
        print("="*50)
        
        if self.current_system == "minimal" and self.voice_system:
            system_name = self.voice_system.get_current_system()
            print(f"✅ {system_name}")
            info = self.voice_system.get_system_info()
            print(f"🎪 {info['emotions_count']} emoções disponíveis")
        else:
            print("📝 Modo Texto Apenas")
        
        print("="*50)
    
    async def speak(self, text: str, emotion: str = "neutro"):
        """Interface principal"""
        if not self.is_initialized:
            await self._initialize_system()
        
        if self.voice_system:
            await self.voice_system.speak(text, emotion)
        else:
            print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
    
    async def test_voice_emotions(self):
        """Teste de emoções"""
        if not self.is_initialized:
            await self._initialize_system()
        
        if self.voice_system:
            await self.voice_system.test_all_emotions()
        else:
            print("📝 Teste no modo texto:")
            print("🤖 Esta é minha voz (texto)")
    
    async def test_voice_quality(self):
        """Teste de qualidade"""
        await self.speak("Teste de qualidade de voz.", "neutro")
    
    def get_available_emotions(self) -> List[str]:
        """Emoções disponíveis"""
        if self.voice_system:
            return self.voice_system.get_available_emotions()
        return ["neutro", "feliz", "triste", "curioso"]
    
    def get_current_system(self) -> str:
        """Sistema atual"""
        if self.voice_system:
            return self.voice_system.get_current_system()
        return "📝 Modo Texto"
    
    def test_audio_system(self) -> bool:
        """Testa áudio"""
        return self.voice_system is not None
    
    def reset_audio_system(self):
        """Reset áudio"""
        if self.voice_system:
            try:
                import pygame
                pygame.mixer.quit()
                pygame.mixer.init()
            except:
                pass
    
    async def cleanup(self):
        """Limpeza"""
        if self.voice_system:
            await self.voice_system.cleanup()

# Compatibilidade
HumanizedTTS = SuperiorFeminineVoice
BarkHumanizedTTS = SuperiorFeminineVoice
