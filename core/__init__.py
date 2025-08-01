"""Módulo principal do agente IA"""

from .agent import AIAgent
from .speech_to_text import SpeechToText
from .text_to_speech import HumanizedTTS
from .conversation import ConversationManager

__all__ = ['AIAgent', 'SpeechToText', 'HumanizedTTS', 'ConversationManager']
