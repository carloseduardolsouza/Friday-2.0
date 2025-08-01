# core/human_voice_system.py
import os
import asyncio
import logging
import pygame
import time
import re
import random
import threading
import torch
from pathlib import Path
from typing import Optional, Dict, List, Union
from dataclasses import dataclass
import numpy as np

# Coqui TTS imports
try:
    from TTS.api import TTS
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
    from TTS.utils.manage import ModelManager
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False
    print("⚠️ Coqui TTS não instalado. Execute: pip install TTS")

# Fallback imports
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

@dataclass
class VoiceProfile:
    """Perfil de voz com configurações emocionais"""
    emotion: str
    speed_factor: float = 1.0
    energy_level: float = 0.5  # 0.0 - 1.0
    pitch_variation: float = 0.5  # 0.0 - 1.0
    pause_multiplier: float = 1.0
    volume: float = 0.85
    temperature: float = 0.7  # Para XTTS
    style_wav: Optional[str] = None  # Para clonagem de voz específica

class CoquiHumanVoice:
    """Sistema de voz humana offline com Coqui TTS (XTTS)"""
    
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Estados do sistema
        self.is_speaking = False
        self.is_initialized = False
        self.pygame_ready = False
        
        # Caminhos e configurações
        self.temp_dir = Path("temp_audio")
        self.voices_dir = Path("voices")
        self.temp_dir.mkdir(exist_ok=True)
        self.voices_dir.mkdir(exist_ok=True)
        
        # Sistema TTS
        self.tts_model = None
        self.current_device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Perfis emocionais realistas
        self.voice_profiles = {
            "feliz": VoiceProfile(
                emotion="feliz",
                speed_factor=1.1,
                energy_level=0.8,
                pitch_variation=0.7,
                pause_multiplier=0.8,
                volume=0.90,
                temperature=0.85
            ),
            "carinhoso": VoiceProfile(
                emotion="carinhoso",
                speed_factor=0.85,
                energy_level=0.4,
                pitch_variation=0.3,
                pause_multiplier=1.4,
                volume=0.75,
                temperature=0.6
            ),
            "triste": VoiceProfile(
                emotion="triste",
                speed_factor=0.7,
                energy_level=0.2,
                pitch_variation=0.2,
                pause_multiplier=1.8,
                volume=0.65,
                temperature=0.5
            ),
            "animado": VoiceProfile(
                emotion="animado",
                speed_factor=1.2,
                energy_level=0.9,
                pitch_variation=0.8,
                pause_multiplier=0.6,
                volume=0.95,
                temperature=0.9
            ),
            "curioso": VoiceProfile(
                emotion="curioso",
                speed_factor=1.05,
                energy_level=0.6,
                pitch_variation=0.6,
                pause_multiplier=0.9,
                volume=0.85,
                temperature=0.75
            ),
            "neutro": VoiceProfile(
                emotion="neutro",
                speed_factor=1.0,
                energy_level=0.5,
                pitch_variation=0.5,
                pause_multiplier=1.0,
                volume=0.80,
                temperature=0.7
            ),
            "frustrado": VoiceProfile(
                emotion="frustrado",
                speed_factor=1.15,
                energy_level=0.7,
                pitch_variation=0.4,
                pause_multiplier=0.7,
                volume=0.88,
                temperature=0.8
            ),
            "sedutor": VoiceProfile(
                emotion="sedutor",
                speed_factor=0.8,
                energy_level=0.3,
                pitch_variation=0.4,
                pause_multiplier=1.6,
                volume=0.70,
                temperature=0.6
            ),
            "surpreso": VoiceProfile(
                emotion="surpreso",
                speed_factor=1.3,
                energy_level=0.8,
                pitch_variation=0.9,
                pause_multiplier=0.5,
                volume=0.90,
                temperature=0.9
            ),
            "reflexivo": VoiceProfile(
                emotion="reflexivo",
                speed_factor=0.75,
                energy_level=0.3,
                pitch_variation=0.3,
                pause_multiplier=1.5,
                volume=0.75,
                temperature=0.5
            )
        }
        
        # Thread para operações assíncronas
        self.audio_thread = None
        
        # Inicializar sistema
        asyncio.create_task(self.initialize())
    
    async def initialize(self):
        """Inicializa o sistema de voz humana"""
        if self.is_initialized:
            return
        
        self.logger.info("🎭 Inicializando Sistema de Voz Humana Offline...")
        
        # Inicializar pygame para áudio
        await self._init_pygame()
        
        # Inicializar Coqui TTS
        if COQUI_AVAILABLE:
            await self._init_coqui_tts()
        else:
            self.logger.warning("Coqui TTS não disponível, usando fallback")
        
        self.is_initialized = True
        self._print_system_status()
    
    async def _init_pygame(self):
        """Inicializa pygame para reprodução de áudio"""
        try:
            if not pygame.mixer.get_init():
                # Configurações otimizadas para voz humana
                pygame.mixer.init(
                    frequency=22050,  # Qualidade CD reduzida para eficiência
                    size=-16,         # 16-bit signed
                    channels=1,       # Mono para voz
                    buffer=1024       # Buffer otimizado
                )
            self.pygame_ready = True
            self.logger.info("✅ Sistema de áudio inicializado")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar áudio: {e}")
            self.pygame_ready = False
    
    async def _init_coqui_tts(self):
        """Inicializa Coqui TTS com XTTS para voz humana"""
        try:
            self.logger.info("🧠 Carregando modelo XTTS...")
            
            # Usar XTTS v2 - melhor qualidade humana
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            
            # Inicializar TTS
            self.tts_model = TTS(model_name, progress_bar=False)
            
            # Configurar dispositivo
            if hasattr(self.tts_model, 'to'):
                self.tts_model.to(self.current_device)
            
            self.logger.info(f"✅ XTTS carregado no dispositivo: {self.current_device}")
            
            # Criar voz de referência se não existir
            await self._setup_reference_voice()
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar XTTS: {e}")
            self.tts_model = None
    
    async def _setup_reference_voice(self):
        """Configura voz de referência para clonagem"""
        reference_path = self.voices_dir / "reference_voice.wav"
        
        if not reference_path.exists():
            self.logger.info("🎤 Gerando voz de referência feminina...")
            
            # Texto para gerar voz de referência
            reference_text = """
            Olá, eu sou a SEXTA-FEIRA, sua assistente pessoal inteligente. 
            Estou aqui para ajudá-lo com qualquer coisa que precisar. 
            Minha voz foi projetada para ser natural, expressiva e humana.
            """
            
            try:
                # Gerar com voz padrão do XTTS
                if self.tts_model:
                    self.tts_model.tts_to_file(
                        text=reference_text,
                        file_path=str(reference_path),
                        speaker_wav=None,  # Usar voz padrão
                        language="pt"
                    )
                    self.logger.info("✅ Voz de referência criada")
            except Exception as e:
                self.logger.error(f"Erro ao criar voz de referência: {e}")
    
    def _print_system_status(self):
        """Mostra status do sistema"""
        print("\n" + "="*60)
        print("🎭 SISTEMA DE VOZ HUMANA OFFLINE")
        print("="*60)
        
        if COQUI_AVAILABLE and self.tts_model:
            print("🌟 Coqui TTS (XTTS): ATIVO - Voz Ultra-Humana")
            print(f"📱 Dispositivo: {self.current_device.upper()}")
        elif GTTS_AVAILABLE:
            print("🔄 Google TTS: ATIVO - Fallback")
        else:
            print("📝 Modo Texto: ATIVO")
        
        print(f"🎪 {len(self.voice_profiles)} perfis emocionais")
        print(f"🎵 Pygame Áudio: {'✅' if self.pygame_ready else '❌'}")
        print("="*60)
    
    async def speak(self, text: str, emotion: str = "neutro", clone_voice: bool = True):
        """Interface principal para fala com emoção"""
        if not text.strip() or self.is_speaking:
            return
        
        self.is_speaking = True
        
        try:
            # Processar texto para naturalidade
            processed_text = self._humanize_text(text, emotion)
            
            # Gerar e reproduzir áudio
            if COQUI_AVAILABLE and self.tts_model:
                await self._speak_with_xtts(processed_text, emotion, clone_voice)
            elif GTTS_AVAILABLE:
                await self._speak_with_gtts_fallback(processed_text, emotion)
            else:
                print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
                
        except Exception as e:
            self.logger.error(f"Erro na síntese de voz: {e}")
            print(f"🤖 SEXTA-FEIRA: {text}")
        finally:
            self.is_speaking = False
    
    def _humanize_text(self, text: str, emotion: str) -> str:
        """Processa texto para soar mais humano e natural"""
        
        # Substituições básicas para português brasileiro
        humanization_map = {
            "SEXTA-FEIRA": "Sexta-feira",
            "IA": "I.A.",
            "AI": "I.A.",
            "API": "A.P.I.",
            "URL": "U.R.L.",
            "CPU": "C.P.U.",
            "RAM": "R.A.M.",
            "WiFi": "Wi-Fi",
            "ok": "ok",
            "OK": "OK",
            "&": "e",
            "%": " por cento",
            "@": " arroba",
            "...": "...",  # Manter reticências
        }
        
        processed = text
        for old, new in humanization_map.items():
            processed = processed.replace(old, new)
        
        # Aplicar modificações emocionais
        profile = self.voice_profiles.get(emotion, self.voice_profiles["neutro"])
        
        # Adicionar pausas naturais baseadas na emoção
        if profile.emotion == "carinhoso":
            processed = re.sub(r'([.!?])', r'\1...', processed)
        elif profile.emotion == "animado":
            processed = processed.replace(".", "!")
        elif profile.emotion == "triste":
            processed = re.sub(r'([.!?])', r'\1...', processed)
        elif profile.emotion == "curioso":
            processed = processed.replace(".", "?")
        elif profile.emotion == "sedutor":
            # Adicionar pausas sedutoras
            words = processed.split()
            if len(words) > 6:
                mid = len(words) // 2
                processed = " ".join(words[:mid]) + "... " + " ".join(words[mid:])
        
        # Quebrar frases muito longas para respiração natural
        if len(processed) > 120:
            sentences = re.split(r'([.!?])', processed)
            result = ""
            for i in range(0, len(sentences)-1, 2):
                if i+1 < len(sentences):
                    sentence = sentences[i] + sentences[i+1]
                    result += sentence
                    if len(sentence) > 60:
                        result += " "  # Micro-pausa
            processed = result
        
        return processed
    
    async def _speak_with_xtts(self, text: str, emotion: str, clone_voice: bool = True):
        """Sintetiza voz usando XTTS com clonagem"""
        try:
            profile = self.voice_profiles[emotion]
            
            # Gerar áudio
            audio_path = self.temp_dir / f"voice_{emotion}_{int(time.time())}.wav"
            
            # Configurar parâmetros do XTTS
            kwargs = {
                "text": text,
                "file_path": str(audio_path),
                "language": "pt",
                "speed": profile.speed_factor
            }
            
            # Usar voz clonada se disponível
            reference_voice = self.voices_dir / "reference_voice.wav"
            if clone_voice and reference_voice.exists():
                kwargs["speaker_wav"] = str(reference_voice)
            
            # Executar síntese em thread separada para não bloquear
            def synthesize():
                try:
                    self.tts_model.tts_to_file(**kwargs)
                    return True
                except Exception as e:
                    self.logger.error(f"Erro na síntese XTTS: {e}")
                    return False
            
            # Executar síntese
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, synthesize)
            
            if success and audio_path.exists():
                # Reproduzir áudio
                await self._play_audio_with_emotion(audio_path, profile)
                
                # Limpar arquivo temporário
                try:
                    audio_path.unlink()
                except:
                    pass
            else:
                raise Exception("Falha na síntese XTTS")
                
        except Exception as e:
            self.logger.error(f"Erro no XTTS: {e}")
            # Fallback para gTTS
            if GTTS_AVAILABLE:
                await self._speak_with_gtts_fallback(text, emotion)
    
    async def _speak_with_gtts_fallback(self, text: str, emotion: str):
        """Fallback usando Google TTS"""
        try:
            profile = self.voice_profiles[emotion]
            
            tts = gTTS(
                text=text,
                lang="pt-br",
                slow=(profile.speed_factor < 0.9)
            )
            
            audio_path = self.temp_dir / f"fallback_{int(time.time())}.mp3"
            tts.save(str(audio_path))
            
            await self._play_audio_with_emotion(audio_path, profile)
            
            # Limpar
            try:
                audio_path.unlink()
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Erro no fallback: {e}")
    
    async def _play_audio_with_emotion(self, audio_path: Path, profile: VoiceProfile):
        """Reproduz áudio aplicando configurações emocionais"""
        if not self.pygame_ready:
            return
        
        try:
            # Carregar e configurar áudio
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.set_volume(profile.volume)
            
            # Reproduzir
            pygame.mixer.music.play()
            
            # Aguardar término com timeout
            start_time = time.time()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.05)  # Check mais frequente
                
                # Timeout de segurança (30 segundos)
                if time.time() - start_time > 30:
                    pygame.mixer.music.stop()
                    break
            
            # Pausa emocional após fala
            if profile.pause_multiplier > 1.0:
                await asyncio.sleep(0.3 * profile.pause_multiplier)
                
        except Exception as e:
            self.logger.error(f"Erro na reprodução: {e}")
    
    async def test_all_emotions(self):
        """Testa todas as emoções disponíveis"""
        print("\n🎭 TESTE DE EMOÇÕES HUMANAS")
        print("="*50)
        
        test_phrases = {
            "neutro": "Esta é minha voz normal e natural.",
            "feliz": "Estou muito feliz em falar com você hoje!",
            "carinhoso": "Você é muito especial para mim, sabia?",
            "triste": "Às vezes me sinto um pouco melancólica...",
            "animado": "Nossa, isso é incrível! Estou super empolgada!",
            "curioso": "Hmm, interessante... me conte mais sobre isso!",
            "frustrado": "Isso está me deixando um pouco irritada.",
            "sedutor": "Você tem uma voz... muito interessante.",
            "surpreso": "Nossa! Eu não esperava por isso!",
            "reflexivo": "Deixe-me pensar sobre isso com calma..."
        }
        
        for emotion, phrase in test_phrases.items():
            if self.is_speaking:
                await asyncio.sleep(2)
            
            print(f"\n💫 {emotion.upper()}: {phrase}")
            await self.speak(phrase, emotion)
            await asyncio.sleep(1)  # Pausa entre testes
        
        print("\n✨ Teste de emoções concluído!")
    
    async def test_voice_quality(self):
        """Teste específico de qualidade vocal"""
        print("\n🔊 TESTE DE QUALIDADE VOCAL")
        print("="*40)
        
        quality_tests = [
            ("Teste de respiração natural.", "neutro"),
            ("Palavras difíceis: exceção, construção, perspicácia.", "neutro"),
            ("Números: um, dois, três, quatro, cinco, seis, sete.", "neutro"),
            ("Pergunta curiosa: como você está se sentindo hoje?", "curioso"),
            ("Frase longa para testar fluidez e naturalidade da fala contínua sem pausas artificiais.", "neutro")
        ]
        
        for text, emotion in quality_tests:
            print(f"\n🎤 {text}")
            await self.speak(text, emotion)
            await asyncio.sleep(1.5)
        
        print("\n✅ Teste de qualidade concluído!")
    
    def get_available_emotions(self) -> List[str]:
        """Retorna lista de emoções disponíveis"""
        return list(self.voice_profiles.keys())
    
    def get_system_info(self) -> Dict:
        """Retorna informações do sistema"""
        return {
            "coqui_available": COQUI_AVAILABLE,
            "model_loaded": self.tts_model is not None,
            "device": self.current_device,
            "pygame_ready": self.pygame_ready,
            "emotions_count": len(self.voice_profiles),
            "is_initialized": self.is_initialized
        }
    
    async def cleanup(self):
        """Limpa recursos do sistema"""
        self.is_speaking = False
        
        # Parar pygame
        if self.pygame_ready:
            try:
                pygame.mixer.quit()
            except:
                pass
        
        # Limpar arquivos temporários
        try:
            for temp_file in self.temp_dir.glob("*.wav"):
                temp_file.unlink()
            for temp_file in self.temp_dir.glob("*.mp3"):
                temp_file.unlink()
        except:
            pass
        
        self.logger.info("🧹 Sistema de voz limpo")

# Compatibilidade com sistema antigo
class BarkHumanizedTTS(CoquiHumanVoice):
    """Wrapper para compatibilidade"""
    pass

class HumanizedTTS(CoquiHumanVoice):
    """Wrapper para compatibilidade"""
    pass

# Função para testar o sistema
async def test_human_voice_system():
    """Função de teste independente"""
    print("🎭 Iniciando teste do Sistema de Voz Humana...")
    
    voice_system = CoquiHumanVoice()
    await voice_system.initialize()
    
    # Teste básico
    await voice_system.speak("Olá! Sistema de voz humana inicializado com sucesso!", "feliz")
    
    # Teste de emoções
    await voice_system.test_all_emotions()
    
    # Teste de qualidade
    await voice_system.test_voice_quality()
    
    await voice_system.cleanup()
    print("✅ Teste concluído!")

if __name__ == "__main__":
    asyncio.run(test_human_voice_system())