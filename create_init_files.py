# create_init_files.py
"""Script para criar arquivos __init__.py necessários"""

import os
from pathlib import Path

def create_init_files():
    """Cria arquivos __init__.py em todos os diretórios necessários"""
    
    init_files = {
        'config/__init__.py': '''"""Módulo de configurações do agente IA"""

from .settings import AgentConfig, VoiceConfig, ModelConfig, DatabaseConfig, load_config, save_config

__all__ = ['AgentConfig', 'VoiceConfig', 'ModelConfig', 'DatabaseConfig', 'load_config', 'save_config']
''',
        
        'core/__init__.py': '''"""Módulo principal do agente IA"""

from .agent import AIAgent
from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech
from .conversation import ConversationManager

__all__ = ['AIAgent', 'SpeechToText', 'TextToSpeech', 'ConversationManager']
''',
        
        'memory/__init__.py': '''"""Módulo de memória e persistência de dados"""

from .user_profile import UserProfile, UserInfo
from .database import DatabaseManager

__all__ = ['UserProfile', 'UserInfo', 'DatabaseManager']
''',
        
        'models/__init__.py': '''"""Módulo de modelos de IA"""

from .local_llm import LocalLLM

__all__ = ['LocalLLM']
''',
        
        'utils/__init__.py': '''"""Módulo de utilitários"""

# Adicione aqui quando criar os utilitários
__all__ = []
'''
    }
    
    print("🔧 Criando arquivos __init__.py...")
    
    for file_path, content in init_files.items():
        # Criar diretório se não existir
        dir_path = Path(file_path).parent
        dir_path.mkdir(exist_ok=True)
        
        # Criar arquivo __init__.py
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Criado: {file_path}")
    
    print("🎉 Todos os arquivos __init__.py foram criados!")

if __name__ == "__main__":
    create_init_files()