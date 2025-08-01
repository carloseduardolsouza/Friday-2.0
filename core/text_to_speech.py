# core/text_to_speech.py - VERSÃO CORRIGIDA
import asyncio
import logging
from typing import List
from config.settings import VoiceConfig

# Tentar importar sistema ultra-realista
try:
    from core.ultra_realistic_voice import UltraRealisticVoice
    ULTRA_AVAILABLE = True
    print("🌟 Sistema ultra-realista disponível!")
except ImportError as e:
    print(f"⚠️ Sistema ultra-realista não disponível: {e}")
    ULTRA_AVAILABLE = False

class SuperiorFeminineVoice:
    """Sistema principal da SEXTA-FEIRA - ERRO MECAB CORRIGIDO"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.voice_system = None
        self.current_system = "initializing"
        self.is_initialized = False
        
        # Auto-inicializar
        asyncio.create_task(self._smart_initialize())
    
    async def _smart_initialize(self):
        """Inicialização inteligente e robusta"""
        if self.is_initialized:
            return
        
        print("\n🎭 INICIANDO SISTEMA DE VOZ SEXTA-FEIRA")
        print("="*50)
        
        if ULTRA_AVAILABLE:
            try:
                print("🌟 Carregando sistema ultra-realista...")
                self.voice_system = UltraRealisticVoice()
                
                # Aguardar inicialização (com timeout)
                max_wait = 60  # 1 minuto
                wait_time = 0
                
                while wait_time < max_wait:
                    if hasattr(self.voice_system, 'is_initialized') and self.voice_system.is_initialized:
                        break
                    await asyncio.sleep(2)
                    wait_time += 2
                    if wait_time % 10 == 0:
                        print(f"⏳ Aguardando... ({wait_time}s)")
                
                if hasattr(self.voice_system, 'is_initialized') and self.voice_system.is_initialized:
                    self.current_system = "ultra_realistic"
                    print("\n" + "🎉" * 20)
                    print("✅ VOZ ULTRA-REALISTA ATIVA!")
                    print("🌟 SEXTA-FEIRA agora fala como ChatGPT!")
                    print("🎉" * 20)
                else:
                    print("⚠️ Timeout na inicialização (usando modo texto)")
                    self.current_system = "text_fallback"
                    
            except Exception as e:
                print(f"⚠️ Erro no ultra-realista: {e}")
                self.current_system = "text_fallback"
        else:
            print("📝 Sistema ultra-realista não disponível")
            self.current_system = "text_fallback"
        
        self.is_initialized = True
        print(f"✅ Sistema inicializado: {self.get_current_system()}")
    
    async def speak(self, text: str, emotion: str = "neutro"):
        """Interface principal de fala"""
        # Aguardar inicialização se necessário
        if not self.is_initialized:
            await self._smart_initialize()
        
        # Se sistema ultra-realista disponível
        if self.current_system == "ultra_realistic" and self.voice_system:
            await self.voice_system.speak(text, emotion)
        else:
            # Fallback: modo texto com emojis
            emojis = {
                "neutro": "🤖", "feliz": "😊", "carinhoso": "🥰",
                "triste": "😔", "animado": "🤩", "curioso": "🤔",
                "sedutor": "😏", "surpreso": "😲"
            }
            emoji = emojis.get(emotion, "🤖")
            print(f"{emoji} SEXTA-FEIRA ({emotion}): {text}")
    
    async def test_voice_emotions(self):
        """Teste de emoções"""
        if not self.is_initialized:
            await self._smart_initialize()
        
        if self.current_system == "ultra_realistic" and self.voice_system:
            print("🎭 Testando sistema ultra-realista...")
            await self.voice_system.test_ultra_realistic_emotions()
        else:
            print("📝 Testando sistema de texto...")
            emotions = ["neutro", "feliz", "carinhoso", "triste", "animado"]
            for emotion in emotions:
                await self.speak(f"Esta é minha emoção {emotion}.", emotion)
                await asyncio.sleep(1)
    
    def get_current_system(self):
        """Sistema atual em uso"""
        if self.current_system == "ultra_realistic":
            return "🌟 Voz Ultra-Realista (Estilo ChatGPT)"
        elif self.current_system == "text_fallback":
            return "📝 Modo Texto (Fallback)"
        else:
            return "⏳ Inicializando..."
    
    def get_available_emotions(self):
        """Emoções disponíveis"""
        if self.voice_system and hasattr(self.voice_system, 'get_available_emotions'):
            return self.voice_system.get_available_emotions()
        return ["neutro", "feliz", "carinhoso", "triste", "animado", "curioso", "sedutor", "surpreso"]
    
    def get_voice_info(self):
        """Informações do sistema"""
        if self.voice_system and hasattr(self.voice_system, 'get_voice_info'):
            return self.voice_system.get_voice_info()
        return {
            "system": self.current_system,
            "quality": "text_only",
            "status": "fallback"
        }

# Compatibilidade com nomes antigos
HumanizedTTS = SuperiorFeminineVoice
BarkHumanizedTTS = SuperiorFeminineVoice
