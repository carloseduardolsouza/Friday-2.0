# create_humanized_voice.py
print("🎭 Criando sistema de voz humanizada para SEXTA-FEIRA...")

# 1. Novo TTS humanizado usando multiple engines + Azure/Google TTS
humanized_tts_code = '''# core/text_to_speech.py
import asyncio
import logging
import pyttsx3
import threading
import random
import time
import requests
import tempfile
import os
from pathlib import Path
from typing import Optional
from config.settings import VoiceConfig

try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("⚠️ gTTS não disponível. Instale com: pip install gtts pygame")

class HumanizedTTS:
    """Sistema de TTS humanizado com múltiplas opções"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Preferências de voz (ordem de prioridade)
        self.voice_engines = {
            "azure": self._speak_azure,      # Melhor qualidade (se disponível)
            "gtts": self._speak_gtts,        # Google TTS (online)
            "pyttsx3": self._speak_pyttsx3,  # Sistema local (fallback)
        }
        
        # Configurações de humanização
        self.humanization_settings = {
            "pause_factor": 1.2,      # Pausas mais naturais
            "speed_variation": 0.15,  # Variação de velocidade
            "emotion_intensity": 0.8, # Intensidade das emoções
            "breath_pauses": True,    # Pausas para "respirar"
        }
        
        # Inicializar pygame para reprodução
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.pygame_available = True
        except:
            self.pygame_available = False
            self.logger.warning("Pygame não disponível")
        
        # Configurações de emoção mais sofisticadas
        self.emotion_configs = {
            "feliz": {
                "rate": 210, "volume": 0.95, "pitch": "+20Hz",
                "pause_multiplier": 0.8, "excitement": 0.9
            },
            "triste": {
                "rate": 160, "volume": 0.75, "pitch": "-15Hz",
                "pause_multiplier": 1.4, "melancholy": 0.8
            },
            "curioso": {
                "rate": 190, "volume": 0.88, "pitch": "+10Hz",
                "pause_multiplier": 1.1, "inquisitive": 0.7
            },
            "neutro": {
                "rate": 180, "volume": 0.85, "pitch": "0Hz",
                "pause_multiplier": 1.0, "neutral": 1.0
            },
            "frustrado": {
                "rate": 200, "volume": 0.9, "pitch": "+5Hz",
                "pause_multiplier": 0.9, "tension": 0.8
            },
            "carinhoso": {
                "rate": 170, "volume": 0.82, "pitch": "-5Hz",
                "pause_multiplier": 1.2, "warmth": 0.9
            }
        }
        
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
    
    async def speak(self, text: str, emotion: str = "neutro"):
        """Interface principal para fala humanizada"""
        if not text.strip():
            return
        
        # Processar texto para humanização
        processed_text = self._humanize_text(text, emotion)
        
        # Tentar engines em ordem de prioridade
        success = False
        for engine_name, engine_func in self.voice_engines.items():
            try:
                if engine_name == "azure" and not self._azure_available():
                    continue
                if engine_name == "gtts" and not GTTS_AVAILABLE:
                    continue
                
                print(f"🎤 Usando engine: {engine_name}")
                await engine_func(processed_text, emotion)
                success = True
                break
                
            except Exception as e:
                self.logger.warning(f"Engine {engine_name} falhou: {e}")
                continue
        
        if not success:
            print(f"🔇 [TODAS AS ENGINES FALHARAM] {text}")
    
    def _humanize_text(self, text: str, emotion: str) -> str:
        """Processa texto para soar mais humano"""
        
        # Substituições para pronúncia mais natural
        replacements = {
            "SEXTA-FEIRA": "Sexta feira",
            "IA": "Inteligência Artificial",
            "AI": "A I",
            "TTS": "T T S",
            "API": "A P I",
            "URL": "U R L",
            "CPU": "C P U",
            "RAM": "R A M",
            "SSD": "S S D",
            "USB": "U S B",
            "WiFi": "Wi Fi",
            "Bluetooth": "Blu tu",
            "&": "e",
            "%": "por cento",
            "@": "arroba",
            "#": "hashtag",
            "°C": "graus Celsius",
            "km/h": "quilômetros por hora",
            "Dr.": "Doutor",
            "Dra.": "Doutora",
            "Sr.": "Senhor",
            "Sra.": "Senhora",
            "etc.": "etcetera",
        }
        
        processed = text
        for old, new in replacements.items():
            processed = processed.replace(old, new)
        
        # Adicionar pausas naturais baseadas na emoção
        emotion_config = self.emotion_configs.get(emotion, self.emotion_configs["neutro"])
        pause_multiplier = emotion_config["pause_multiplier"]
        
        # Pausas mais longas para emoções específicas
        if emotion in ["triste", "carinhoso"]:
            processed = processed.replace(".", "... ")
            processed = processed.replace(",", ", ")
        elif emotion == "feliz":
            processed = processed.replace("!", "! ")
            processed = processed.replace("?", "? ")
        
        # Adicionar "respiração" em frases longas
        if len(processed) > 100:
            sentences = processed.split(". ")
            if len(sentences) > 1:
                processed = ". ".join(sentences[:2]) + "... " + ". ".join(sentences[2:])
        
        return processed
    
    async def _speak_gtts(self, text: str, emotion: str):
        """Google TTS - Mais natural"""
        try:
            # Configurar idioma com variante regional
            lang_variants = {
                "neutro": "pt-br",
                "feliz": "pt-br", 
                "carinhoso": "pt-br",
                "triste": "pt-br",
                "curioso": "pt-br",
                "frustrado": "pt-br"
            }
            
            lang = lang_variants.get(emotion, "pt-br")
            
            # Criar arquivo temporário
            temp_file = self.temp_dir / f"gtts_{int(time.time())}.mp3"
            
            # Gerar áudio
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(str(temp_file))
            
            # Reproduzir com pygame
            if self.pygame_available:
                pygame.mixer.music.load(str(temp_file))
                pygame.mixer.music.play()
                
                # Aguardar terminar
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
            
            # Limpar arquivo temporário
            if temp_file.exists():
                temp_file.unlink()
                
        except Exception as e:
            self.logger.error(f"Erro no Google TTS: {e}")
            raise
    
    async def _speak_pyttsx3(self, text: str, emotion: str):
        """Sistema TTS local humanizado"""
        emotion_config = self.emotion_configs.get(emotion, self.emotion_configs["neutro"])
        
        def speak_sync():
            try:
                engine = pyttsx3.init()
                
                # Configurar velocidade com variação natural
                base_rate = emotion_config["rate"]
                rate_variation = random.randint(-15, 15)
                engine.setProperty('rate', base_rate + rate_variation)
                
                # Volume
                engine.setProperty('volume', emotion_config["volume"])
                
                # Buscar voz feminina em português
                voices = engine.getProperty('voices')
                female_voice = None
                
                for voice in voices:
                    voice_name = voice.name.lower()
                    # Priorizar vozes femininas em português
                    if any(keyword in voice_name for keyword in ['maria', 'helena', 'ana', 'julia', 'fernanda']):
                        female_voice = voice.id
                        break
                    elif any(keyword in voice_name for keyword in ['portuguese', 'brasil', 'pt']):
                        if any(fem in voice_name for fem in ['female', 'woman', 'mulher']):
                            female_voice = voice.id
                            break
                
                if female_voice:
                    engine.setProperty('voice', female_voice)
                    self.logger.info("Usando voz feminina em português")
                
                # Falar com pausas naturais
                sentences = text.split('. ')
                for i, sentence in enumerate(sentences):
                    if sentence.strip():
                        engine.say(sentence)
                        engine.runAndWait()
                        
                        # Pausa entre frases (mais humano)
                        if i < len(sentences) - 1:
                            time.sleep(0.3 * emotion_config["pause_multiplier"])
                
                engine.stop()
                
            except Exception as e:
                self.logger.error(f"Erro no pyttsx3: {e}")
                raise
        
        # Executar em thread separada
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, speak_sync)
    
    async def _speak_azure(self, text: str, emotion: str):
        """Azure Cognitive Services TTS (se configurado)"""
        # Implementação futura para Azure TTS
        # Requires: pip install azure-cognitiveservices-speech
        raise NotImplementedError("Azure TTS não implementado ainda")
    
    def _azure_available(self) -> bool:
        """Verifica se Azure TTS está disponível"""
        return False  # Por enquanto
    
    def test_voice_quality(self):
        """Testa qualidade de diferentes engines"""
        test_text = "Olá! Sou a Sexta-feira, sua assistente pessoal inteligente."
        
        print("🎭 Testando qualidade das vozes disponíveis...")
        
        for engine_name in self.voice_engines.keys():
            if engine_name == "azure" and not self._azure_available():
                continue
            if engine_name == "gtts" and not GTTS_AVAILABLE:
                continue
                
            print(f"\\n🔊 Testando: {engine_name}")
            try:
                asyncio.run(self.voice_engines[engine_name](test_text, "neutro"))
                print(f"✅ {engine_name}: Funcionando")
            except Exception as e:
                print(f"❌ {engine_name}: {e}")
    
    def get_available_engines(self) -> list:
        """Retorna engines disponíveis"""
        available = []
        
        if GTTS_AVAILABLE:
            available.append("gtts (Google TTS - Online)")
        
        available.append("pyttsx3 (Sistema Local)")
        
        if self._azure_available():
            available.append("azure (Azure Cognitive Services)")
        
        return available
'''

# 2. Atualizar agent.py para usar o novo sistema
agent_voice_update = '''
# Adicionar ao core/agent.py - no método __init__
# Substituir a linha: self.tts = TextToSpeech(self.config.voice)
# Por: self.tts = HumanizedTTS(self.config.voice)

# E adicionar import no topo:
# from core.text_to_speech import HumanizedTTS
'''

# 3. Script de instalação de dependências de voz
install_voice_deps = '''# install_voice_dependencies.py
import subprocess
import sys

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except:
        return False

print("📦 Instalando dependências para voz humanizada...")

packages = [
    "gtts",           # Google Text-to-Speech
    "pygame",         # Para reprodução de áudio
    "pydub",          # Processamento de áudio
    "requests",       # Para APIs de voz
]

for package in packages:
    print(f"Instalando {package}...")
    if install_package(package):
        print(f"✅ {package} instalado")
    else:
        print(f"❌ Falha ao instalar {package}")

print("\\n🎭 Dependências instaladas!")
print("Execute: python update_voice_system.py")
'''

# 4. Script para atualizar o sistema de voz
update_voice_script = '''# update_voice_system.py
print("🎭 Atualizando sistema de voz da SEXTA-FEIRA...")

# Ler agent.py
with open("core/agent.py", "r", encoding="utf-8") as f:
    content = f.read()

# Atualizar import
if "from core.text_to_speech import HumanizedTTS" not in content:
    # Adicionar import
    import_line = "from core.text_to_speech import TextToSpeech"
    if import_line in content:
        content = content.replace(import_line, "from core.text_to_speech import HumanizedTTS")
        print("✅ Import atualizado")

# Atualizar inicialização do TTS
old_tts_init = "self.tts = TextToSpeech(self.config.voice)"
new_tts_init = "self.tts = HumanizedTTS(self.config.voice)"

if old_tts_init in content:
    content = content.replace(old_tts_init, new_tts_init)
    print("✅ Inicialização do TTS atualizada")

# Adicionar método de teste de voz melhorado
voice_test_method = """
    async def test_voice_quality(self):
        \"\"\"Testa qualidade das vozes disponíveis\"\"\"
        print("🎭 Testando qualidade das vozes...")
        
        # Mostrar engines disponíveis
        available_engines = self.tts.get_available_engines()
        print("🔊 Engines disponíveis:")
        for engine in available_engines:
            print(f"   • {engine}")
        
        # Testar qualidade
        self.tts.test_voice_quality()
        
        print("\\n✅ Teste de qualidade concluído!")
"""

# Inserir método se não existir
if "test_voice_quality" not in content:
    insert_point = content.find("    async def test_voice_emotions(self):")
    if insert_point != -1:
        content = content[:insert_point] + voice_test_method + "\\n" + content[insert_point:]
        print("✅ Método de teste de qualidade adicionado")

# Salvar arquivo atualizado
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\\n✅ Sistema de voz atualizado!")
print("\\n🎯 MELHORIAS IMPLEMENTADAS:")
print("• 🎤 Google TTS (mais natural)")
print("• 🎭 Voz feminina otimizada") 
print("• 🔊 Qualidade de áudio melhorada")
print("• ⏸️ Pausas naturais e respiração")
print("• 🎪 Variação emocional sofisticada")
print("• 🔄 Sistema de fallback robusto")
print("\\n🚀 Execute: python main.py")
print("💡 Teste com: 'teste sua voz' ou 'como você está'")
'''

# Salvar todos os arquivos
print("📝 Criando sistema de voz humanizada...")
with open("core/text_to_speech.py", "w", encoding="utf-8") as f:
    f.write(humanized_tts_code)

print("📝 Criando instalador de dependências...")
with open("install_voice_dependencies.py", "w", encoding="utf-8") as f:
    f.write(install_voice_deps)

print("📝 Criando script de atualização...")
with open("update_voice_system.py", "w", encoding="utf-8") as f:
    f.write(update_voice_script)

print("✅ Sistema de voz humanizada criado!")
print("")
print("🎯 FUNCIONALIDADES DA NOVA VOZ:")
print("• 🎤 Google TTS (qualidade similar ao ChatGPT)")
print("• 👩 Voz feminina otimizada e natural")
print("• 🎭 Emoções mais expressivas e humanas")
print("• ⏸️ Pausas naturais e 'respiração'")
print("• 🔊 Múltiplos engines com fallback automático")
print("• 🎪 Variação de velocidade e tom")
print("• 🌊 Processamento de texto humanizado")
print("")
print("🚀 PARA ATIVAR A NOVA VOZ:")
print("1. pip install gtts pygame pydub")
print("2. python update_voice_system.py")
print("3. python main.py")
print("")
print("💡 COMANDOS PARA TESTAR:")
print("• 'teste sua voz' → Demonstra emoções")
print("• 'como você está' → Voz natural")
print("• 'fale algo carinhoso' → Tom afetuoso")
print("")
print("🎉 A SEXTA-FEIRA terá uma voz muito mais humana e feminina!")