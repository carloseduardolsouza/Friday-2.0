# fix_import_error.py
print("🔧 Corrigindo erro de importação...")

# 1. Corrigir core/__init__.py
core_init_content = '''"""Módulo principal do agente IA"""

from .agent import AIAgent
from .speech_to_text import SpeechToText
from .text_to_speech import HumanizedTTS
from .conversation import ConversationManager

__all__ = ['AIAgent', 'SpeechToText', 'HumanizedTTS', 'ConversationManager']
'''

with open("core/__init__.py", "w", encoding="utf-8") as f:
    f.write(core_init_content)

print("✅ Corrigido core/__init__.py")

# 2. Verificar se agent.py tem as importações corretas
with open("core/agent.py", "r", encoding="utf-8") as f:
    agent_content = f.read()

# Corrigir importação no agent.py se necessário
if "from core.text_to_speech import TextToSpeech" in agent_content:
    agent_content = agent_content.replace(
        "from core.text_to_speech import TextToSpeech",
        "from core.text_to_speech import HumanizedTTS"
    )
    print("✅ Corrigido import no agent.py")

if "self.tts = TextToSpeech(self.config.voice)" in agent_content:
    agent_content = agent_content.replace(
        "self.tts = TextToSpeech(self.config.voice)",
        "self.tts = HumanizedTTS(self.config.voice)"
    )
    print("✅ Corrigido inicialização do TTS no agent.py")

# Salvar agent.py corrigido
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(agent_content)

print("\n✅ Correções aplicadas!")
print("🚀 Agora execute: python main.py")
print("💡 O sistema de voz humanizada estará ativo!")