# config/settings.py
import os
import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class VoiceConfig:
    """Configurações de voz"""
    tts_engine: str = "pyttsx3"
    voice_rate: int = 200
    voice_volume: float = 0.9
    voice_language: str = "pt-BR"
    recognition_language: str = "pt-BR"
    wake_word: str = "sexta-feira"  # MUDANÇA AQUI
    
@dataclass
class ModelConfig:
    """Configurações do modelo de IA"""
    model_name: str = "llama3.2:1b"
    model_path: str = "models/"
    max_tokens: int = 1024
    temperature: float = 0.7
    context_length: int = 2048

@dataclass
class DatabaseConfig:
    """Configurações do banco de dados"""
    user_data_path: str = "data/user_data.json"
    conversations_db: str = "data/conversations.db"
    knowledge_db: str = "data/knowledge.db"

@dataclass
class AgentConfig:
    """Configuração geral do agente"""
    name: str = "SEXTA-FEIRA"  # MUDANÇA AQUI
    personality: str = "amigável, prestativo e inteligente como a IA do Homem de Ferro"
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # Configurações de comportamento
    auto_save_interval: int = 30
    max_conversation_history: int = 100
    enable_learning: bool = True
    debug_mode: bool = False

def load_config() -> AgentConfig:
    """Carrega configurações do arquivo ou cria padrão"""
    config_file = Path("config/config.json")
    
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    
    for directory in ["data", "logs", "models"]:
        Path(directory).mkdir(exist_ok=True)
    
    config = AgentConfig()
    
    if not config_file.exists():
        save_config(config)
    
    return config

def save_config(config: AgentConfig):
    """Salva configurações em arquivo"""
    config_file = Path("config/config.json")
    config_file.parent.mkdir(exist_ok=True)
    
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
