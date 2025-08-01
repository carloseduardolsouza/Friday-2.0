# config/settings.py
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
