# fix_agent.py
import os

# 1. Primeiro, vamos mudar para um modelo menor
print("🔧 Corrigindo configurações...")

settings_code = '''# config/settings.py
import os
import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class VoiceConfig:
    """Configurações de voz"""
    tts_engine: str = "pyttsx3"  # ou "gtts"
    voice_rate: int = 200
    voice_volume: float = 0.9
    voice_language: str = "pt-BR"
    recognition_language: str = "pt-BR"
    wake_word: str = "assistente"
    
@dataclass
class ModelConfig:
    """Configurações do modelo de IA"""
    model_name: str = "llama3.2:1b"  # MODELO MENOR - 1B em vez de 3B
    model_path: str = "models/"
    max_tokens: int = 1024  # REDUZIDO
    temperature: float = 0.7
    context_length: int = 2048  # REDUZIDO

@dataclass
class DatabaseConfig:
    """Configurações do banco de dados"""
    user_data_path: str = "data/user_data.json"
    conversations_db: str = "data/conversations.db"
    knowledge_db: str = "data/knowledge.db"

@dataclass
class AgentConfig:
    """Configuração geral do agente"""
    name: str = "ARIA"  # Nome do seu assistente
    personality: str = "amigável, prestativo e inteligente"
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # Configurações de comportamento
    auto_save_interval: int = 30  # segundos
    max_conversation_history: int = 100
    enable_learning: bool = True
    debug_mode: bool = False

def load_config() -> AgentConfig:
    """Carrega configurações do arquivo ou cria padrão"""
    config_file = Path("config/config.json")
    
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        # Aqui você pode implementar a lógica para carregar do JSON
        # Por simplicidade, retornamos a configuração padrão
    
    # Criar diretórios necessários
    for directory in ["data", "logs", "models"]:
        Path(directory).mkdir(exist_ok=True)
    
    config = AgentConfig()
    
    # Salvar configuração padrão se não existir
    if not config_file.exists():
        save_config(config)
    
    return config

def save_config(config: AgentConfig):
    """Salva configurações em arquivo"""
    config_file = Path("config/config.json")
    config_file.parent.mkdir(exist_ok=True)
    
    # Converter para dicionário (simplificado)
    config_dict = {
        "name": config.name,
        "personality": config.personality,
        "voice": {
            "tts_engine": config.voice.tts_engine,
            "voice_rate": config.voice.voice_rate,
            "voice_volume": config.voice.voice_volume,
            "voice_language": config.voice.voice_language,
            "recognition_language": config.voice.recognition_language,
            "wake_word": config.voice.wake_word
        },
        "model": {
            "model_name": config.model.model_name,
            "max_tokens": config.model.max_tokens,
            "temperature": config.model.temperature,
            "context_length": config.model.context_length
        }
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)
'''

# 2. Corrigir o agente principal para incluir loop de escuta
agent_code = '''# core/agent.py
import asyncio
import logging
import threading
from datetime import datetime
from typing import Optional, Dict, Any

from core.speech_to_text import SpeechToText
from core.text_to_speech import TextToSpeech
from core.conversation import ConversationManager
from memory.user_profile import UserProfile
from memory.database import DatabaseManager
from models.local_llm import LocalLLM
from config.settings import AgentConfig

class AIAgent:
    """Classe principal do agente de IA"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Componentes principais
        self.stt: Optional[SpeechToText] = None
        self.tts: Optional[TextToSpeech] = None
        self.llm: Optional[LocalLLM] = None
        self.conversation_manager: Optional[ConversationManager] = None
        self.user_profile: Optional[UserProfile] = None
        self.database: Optional[DatabaseManager] = None
        
        # Estado do agente
        self.is_listening = False
        self.is_speaking = False
        self.is_running = False
        
    async def initialize(self):
        """Inicializa todos os componentes do agente"""
        self.logger.info("Inicializando componentes do agente...")
        
        try:
            # Inicializar banco de dados
            self.database = DatabaseManager(self.config.database)
            await self.database.initialize()
            
            # Inicializar perfil do usuário
            self.user_profile = UserProfile(self.database)
            await self.user_profile.load_profile()
            
            # Inicializar modelo de IA
            self.llm = LocalLLM(self.config.model)
            await self.llm.initialize()
            
            # Inicializar componentes de voz
            self.stt = SpeechToText(self.config.voice)
            self.tts = TextToSpeech(self.config.voice)
            
            # Inicializar gerenciador de conversas
            self.conversation_manager = ConversationManager(
                self.database, 
                self.user_profile,
                self.config
            )
            
            self.logger.info("Todos os componentes inicializados com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar agente: {e}")
            raise
    
    async def run(self):
        """Loop principal do agente"""
        self.is_running = True
        
        # Saudação inicial
        user_name = self.user_profile.get_user_name()
        greeting = f"Olá {user_name}! Sou a {self.config.name}, sua assistente pessoal. Como posso ajudá-lo hoje?"
        await self.speak(greeting)
        
        print("\\n🎤 AGENTE ATIVO - Pode começar a falar!")
        print("💡 Dica: Fale claramente e aguarde o processamento")
        print("❌ Para sair, diga 'sair' ou pressione Ctrl+C\\n")
        
        try:
            while self.is_running:
                # Escutar comando do usuário
                user_input = await self.listen()
                
                if user_input:
                    # Verificar comandos especiais
                    if self.check_exit_command(user_input):
                        break
                    
                    # Processar entrada do usuário
                    response = await self.process_input(user_input)
                    
                    # Responder ao usuário
                    if response:
                        await self.speak(response)
                else:
                    # Pequena pausa se não houve entrada
                    await asyncio.sleep(0.5)
                
        except KeyboardInterrupt:
            self.logger.info("Interrupção detectada pelo usuário")
        finally:
            await self.shutdown()
    
    async def listen(self) -> Optional[str]:
        """Escuta entrada do usuário"""
        if self.is_speaking or self.is_listening:
            return None
            
        self.is_listening = True
        try:
            # Usar reconhecimento de voz
            text = await self.stt.listen()
            if text:
                self.logger.info(f"Usuário disse: {text}")
                print(f"👤 Você: {text}")
                # Salvar na conversa
                await self.conversation_manager.add_message("user", text)
            return text
        except Exception as e:
            self.logger.error(f"Erro no reconhecimento de voz: {e}")
            print(f"❌ Erro no reconhecimento: {e}")
            return None
        finally:
            self.is_listening = False
    
    async def speak(self, text: str):
        """Fala o texto fornecido"""
        if self.is_speaking:
            return
            
        self.is_speaking = True
        try:
            self.logger.info(f"Assistente: {text}")
            print(f"🤖 ARIA: {text}")
            await self.tts.speak(text)
            # Salvar na conversa
            await self.conversation_manager.add_message("assistant", text)
        except Exception as e:
            self.logger.error(f"Erro na síntese de voz: {e}")
            print(f"❌ Erro na fala: {e}")
        finally:
            self.is_speaking = False
    
    async def process_input(self, user_input: str) -> Optional[str]:
        """Processa a entrada do usuário e gera resposta"""
        try:
            print("🧠 Processando...")
            
            # Extrair informações pessoais do usuário
            await self.user_profile.extract_and_update_info(user_input)
            
            # Obter contexto da conversa
            context = await self.conversation_manager.get_context()
            
            # Criar prompt personalizado
            prompt = self.create_personalized_prompt(user_input, context)
            
            # Gerar resposta usando o modelo local
            response = await self.llm.generate_response(prompt)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao processar entrada: {e}")
            return "Desculpe, houve um erro interno. Pode repetir por favor?"
    
    def create_personalized_prompt(self, user_input: str, context: str) -> str:
        """Cria prompt personalizado baseado no perfil do usuário"""
        user_info = self.user_profile.get_summary()
        
        prompt = f"""Você é {self.config.name}, uma assistente pessoal IA {self.config.personality}.

INFORMAÇÕES DO USUÁRIO:
{user_info}

CONTEXTO DA CONVERSA:
{context}

ENTRADA ATUAL DO USUÁRIO: {user_input}

Responda de forma natural, amigável e personalizada, considerando as informações que você conhece sobre o usuário. 
Seja concisa mas útil. Se o usuário compartilhar novas informações pessoais, reconheça e lembre-se delas para conversas futuras.

RESPOSTA:"""
        
        return prompt
    
    def check_exit_command(self, text: str) -> bool:
        """Verifica se o usuário quer sair"""
        exit_commands = ["sair", "tchau", "até logo", "encerrar", "parar", "quit", "exit"]
        return any(cmd in text.lower() for cmd in exit_commands)
    
    async def shutdown(self):
        """Encerra o agente de forma limpa"""
        self.logger.info("Encerrando agente...")
        self.is_running = False
        
        print("\\n🔄 Salvando dados...")
        
        # Salvar dados do usuário
        if self.user_profile:
            await self.user_profile.save_profile()
        
        # Fechar conexões
        if self.database:
            await self.database.close()
        
        # Despedida
        if self.tts:
            await self.speak("Até logo! Foi um prazer ajudá-lo.")
        
        print("👋 Agente encerrado com sucesso!")
        self.logger.info("Agente encerrado com sucesso!")
'''

# Salvar arquivos corrigidos
print("📝 Atualizando config/settings.py...")
with open("config/settings.py", "w", encoding="utf-8") as f:
    f.write(settings_code)

print("📝 Atualizando core/agent.py...")
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(agent_code)

print("✅ Correções aplicadas!")
print("")
print("🎯 MUDANÇAS FEITAS:")
print("• Modelo alterado para llama3.2:1b (menos RAM)")
print("• Tokens reduzidos para 1024")
print("• Sistema de escuta melhorado")
print("• Interface mais clara")
print("")
print("🚀 Execute: python main.py")
print("💡 Agora o agente vai escutar continuamente!")