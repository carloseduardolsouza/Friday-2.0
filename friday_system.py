# friday_system.py
import os
import time

print("🔧 Configurando SEXTA-FEIRA com sistema de conversa inteligente...")

# 1. Atualizar configurações para mudar o nome
config_update = '''# config/settings.py
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
'''

# 2. Criar sistema de gerenciamento de conversa inteligente
conversation_manager = '''# core/conversation_state.py
import time
import logging
from datetime import datetime, timedelta
from typing import Optional

class ConversationState:
    """Gerencia estado da conversa da SEXTA-FEIRA"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Estados da conversa
        self.is_in_conversation = False
        self.conversation_start_time = None
        self.last_user_input_time = None
        self.conversation_timeout = 300  # 5 minutos em segundos
        
        # Controle de ativação
        self.explicitly_activated = False  # Chamou "sexta-feira"
        self.auto_responding = False       # Está respondendo automaticamente
        
        # Histórico de interações
        self.recent_interactions = []
        
    def activate_conversation(self, activation_method="explicit"):
        """Ativa conversa (chamou pelo nome ou outro método)"""
        current_time = time.time()
        
        self.is_in_conversation = True
        self.conversation_start_time = current_time
        self.last_user_input_time = current_time
        
        if activation_method == "explicit":
            self.explicitly_activated = True
            self.auto_responding = True
            self.logger.info("Conversa ativada explicitamente (nome chamado)")
            return "🟢 SEXTA-FEIRA ativada! Estou escutando você."
        
        elif activation_method == "continuation":
            self.auto_responding = True
            self.logger.info("Conversa continuada automaticamente")
            return "🔄 Continuando nossa conversa..."
        
        return "✅ Conversa ativada"
    
    def deactivate_conversation(self, reason="timeout"):
        """Desativa conversa"""
        self.is_in_conversation = False
        self.explicitly_activated = False
        self.auto_responding = False
        self.conversation_start_time = None
        
        if reason == "explicit":
            self.logger.info("Conversa encerrada explicitamente (comando 'mudo')")
            return "🔇 SEXTA-FEIRA em modo silencioso. Chame meu nome para reativar."
        elif reason == "timeout":
            self.logger.info("Conversa encerrada por timeout")
            return "⏰ Modo de escuta seletiva ativado (5min de silêncio)"
        
        return "Conversa encerrada"
    
    def update_last_interaction(self):
        """Atualiza timestamp da última interação"""
        self.last_user_input_time = time.time()
    
    def check_conversation_timeout(self) -> bool:
        """Verifica se a conversa expirou por timeout"""
        if not self.is_in_conversation or not self.last_user_input_time:
            return False
        
        current_time = time.time()
        time_since_last = current_time - self.last_user_input_time
        
        return time_since_last > self.conversation_timeout
    
    def should_respond_to_input(self, text: str) -> tuple:
        """
        Determina se deve responder a uma entrada
        
        Returns:
            (should_respond: bool, reason: str, confidence: float)
        """
        text_lower = text.lower()
        current_time = time.time()
        
        # 1. COMANDO EXPLÍCITO DE ATIVAÇÃO
        activation_triggers = [
            "sexta-feira", "sexta feira", "friday", 
            "ei sexta", "olá sexta", "oi sexta"
        ]
        
        for trigger in activation_triggers:
            if trigger in text_lower:
                self.activate_conversation("explicit")
                return True, f"Ativação explícita detectada: '{trigger}'", 0.95
        
        # 2. COMANDO EXPLÍCITO DE DESATIVAÇÃO
        deactivation_triggers = [
            "mudo", "silêncio", "quieta", "para de escutar",
            "não fale", "modo silencioso"
        ]
        
        for trigger in deactivation_triggers:
            if trigger in text_lower:
                self.deactivate_conversation("explicit")
                return False, f"Desativação explícita: '{trigger}'", 0.0
        
        # 3. VERIFICAR TIMEOUT
        if self.check_conversation_timeout():
            self.deactivate_conversation("timeout")
            # Após timeout, só responde se for menção explícita
            return self._check_selective_response(text_lower)
        
        # 4. SE ESTÁ EM CONVERSA ATIVA
        if self.is_in_conversation and self.auto_responding:
            self.update_last_interaction()
            return True, "Conversa ativa - respondendo automaticamente", 0.9
        
        # 5. SE NÃO ESTÁ EM CONVERSA - MODO SELETIVO
        return self._check_selective_response(text_lower)
    
    def _check_selective_response(self, text_lower: str) -> tuple:
        """Verifica se deve responder em modo seletivo"""
        
        # Perguntas diretas que podem ser para a IA
        direct_questions = [
            "que horas", "que dia", "como está", "você está",
            "me ajuda", "pode ajudar", "preciso de ajuda",
            "o que é", "como faço", "onde fica"
        ]
        
        for question in direct_questions:
            if question in text_lower:
                # Perguntar se é com ela
                return True, f"Pergunta direta detectada: '{question}' - oferecendo ajuda", 0.6
        
        # Não responder - provavelmente não é com ela
        return False, "Modo seletivo - não parece ser direcionado", 0.0
    
    def get_status_message(self) -> str:
        """Retorna mensagem de status atual"""
        if self.is_in_conversation:
            time_in_conversation = time.time() - self.conversation_start_time
            minutes = int(time_in_conversation // 60)
            seconds = int(time_in_conversation % 60)
            
            return f"🟢 Em conversa ativa há {minutes}m{seconds}s"
        else:
            return "🟡 Modo seletivo - chame 'SEXTA-FEIRA' para ativar"
    
    def get_response_context(self) -> str:
        """Retorna contexto para respostas baseado no estado"""
        if self.explicitly_activated:
            return "Usuário me chamou pelo nome - responder de forma engajada"
        elif self.auto_responding:
            return "Conversa ativa - responder naturalmente"
        else:
            return "Modo seletivo - ser breve e perguntar se precisam de ajuda"
'''

# 3. Atualizar context_analyzer.py para usar o novo sistema
context_analyzer_update = '''# core/context_analyzer.py
import re
import logging
from typing import List, Dict, Tuple
from datetime import datetime
from core.conversation_state import ConversationState

class ContextAnalyzer:
    """Analisa contexto da fala para SEXTA-FEIRA"""
    
    def __init__(self, agent_name: str = "SEXTA-FEIRA"):
        self.agent_name = agent_name.lower()
        self.logger = logging.getLogger(__name__)
        self.conversation_state = ConversationState()
        
        # Padrões específicos para SEXTA-FEIRA
        self.direct_patterns = [
            r"\\bsexta.?feira\\b",
            r"\\bsexta\\b",
            r"\\bfriday\\b",
            r"\\bei\\s+(sexta|friday)\\b",
            r"\\b(olá|oi|hey)\\s+sexta\\b",
            
            # Comandos diretos
            r"\\b(me ajuda|ajude|responda|diga|fala)\\b",
            r"\\b(você pode|consegue|sabe)\\b",
            r"\\bqual.{0,20}(é|meu|seu|nome|hora|dia)\\b",
            r"\\bcomo.{0,20}(você|está|vai|fazer)\\b",
            r"\\bo que.{0,20}(você|é|faz|acha)\\b",
        ]
        
        # Padrões de desativação
        self.deactivation_patterns = [
            r"\\bmudo\\b",
            r"\\bsilêncio\\b",
            r"\\bquieta\\b",
            r"\\bpara\\s+de\\s+escutar\\b",
            r"\\bnão\\s+fale\\b",
            r"\\bmodo\\s+silencioso\\b"
        ]
        
        # Padrões indiretos (falando SOBRE a sexta-feira)
        self.indirect_patterns = [
            rf"\\b(essa|esta|a)\\s+sexta\\b",
            r"\\b(essa|esta|a)\\s+(ia|assistente)\\b",
            r"\\bfalando.{0,10}(da|sobre).{0,10}(sexta|assistente)\\b",
            
            # Opiniões sobre IA
            r"\\b(sexta|assistente).{0,20}(é|está|foi|fica).{0,20}(ruim|boa|legal|chata|inteligente)\\b",
            r"\\b(não gosto|odeio|amo|gosto).{0,20}(da|dessa).{0,20}(sexta|assistente)\\b",
        ]
    
    def should_respond(self, text: str, user_name: str = "") -> Tuple[bool, str, float]:
        """
        Determina se SEXTA-FEIRA deve responder
        
        Returns:
            (should_respond: bool, reason: str, confidence: float)
        """
        text_lower = text.lower()
        
        # Usar o sistema de estado de conversa
        should_respond, reason, confidence = self.conversation_state.should_respond_to_input(text)
        
        # Se não deve responder pelo estado, verificar padrões adicionais
        if not should_respond:
            # Verificar menções indiretas
            for pattern in self.indirect_patterns:
                if re.search(pattern, text_lower):
                    return True, "Menção indireta detectada", 0.7
            
            # Verificar se estão falando mal (defesa)
            negative_patterns = [
                r"\\b(sexta|assistente).{0,30}(ruim|horrível|péssima|inútil|burra)\\b",
                r"\\b(odeio|detesto).{0,20}(sexta|assistente)\\b",
            ]
            
            for pattern in negative_patterns:
                if re.search(pattern, text_lower):
                    return True, "Comentário negativo - defesa necessária", 0.8
        
        return should_respond, reason, confidence
    
    def analyze_emotional_context(self, text: str) -> Dict[str, float]:
        """Analisa contexto emocional da fala"""
        text_lower = text.lower()
        
        emotions = {
            "feliz": 0.0,
            "triste": 0.0,
            "raiva": 0.0,
            "neutro": 0.0,
            "curioso": 0.0
        }
        
        # Padrões de felicidade
        happy_words = ["feliz", "alegre", "ótimo", "excelente", "adorei", "amei", "legal", "bom"]
        emotions["feliz"] = sum(1 for word in happy_words if word in text_lower) / max(len(text_lower.split()), 1) * 10
        
        # Padrões de tristeza
        sad_words = ["triste", "chateado", "ruim", "péssimo", "horrível", "mal"]
        emotions["triste"] = sum(1 for word in sad_words if word in text_lower) / max(len(text_lower.split()), 1) * 10
        
        # Padrões de raiva
        angry_words = ["raiva", "ódio", "irritado", "furioso", "maldita", "droga"]
        emotions["raiva"] = sum(1 for word in angry_words if word in text_lower) / max(len(text_lower.split()), 1) * 10
        
        # Padrões de curiosidade
        curious_words = ["como", "por que", "quando", "onde", "qual", "?"]
        emotions["curioso"] = sum(1 for word in curious_words if word in text_lower) / max(len(text_lower.split()), 1) * 5
        
        # Se nenhuma emoção forte, é neutro
        if max(emotions.values()) < 0.1:
            emotions["neutro"] = 1.0
        
        return emotions
    
    def get_conversation_status(self) -> str:
        """Retorna status da conversa"""
        return self.conversation_state.get_status_message()
    
    def get_response_context(self) -> str:
        """Retorna contexto para respostas"""
        return self.conversation_state.get_response_context()
'''

# Salvar arquivos
print("📝 Atualizando config/settings.py...")
with open("config/settings.py", "w", encoding="utf-8") as f:
    f.write(config_update)

print("📝 Criando core/conversation_state.py...")
with open("core/conversation_state.py", "w", encoding="utf-8") as f:
    f.write(conversation_manager)

print("📝 Atualizando core/context_analyzer.py...")
with open("core/context_analyzer.py", "w", encoding="utf-8") as f:
    f.write(context_analyzer_update)

print("✅ Sistema SEXTA-FEIRA configurado!")
print("")
print("🎯 FUNCIONALIDADES IMPLEMENTADAS:")
print("• 🤖 Nome alterado para 'SEXTA-FEIRA'")
print("• 🎯 Ativação: Diga 'Sexta-feira' para começar conversa")
print("• 💬 Auto-resposta: Após ativar, responde automaticamente")
print("• ⏰ Timeout: 5min de silêncio = modo seletivo")
print("• 🔇 Desativação: Diga 'mudo' para parar")
print("• 🧠 Estado inteligente de conversa")
print("")
print("🚀 Execute: python main.py")
print("")
print("💡 EXEMPLO DE USO:")
print("1. 'Sexta-feira' → Ativa conversa")
print("2. 'Como você está?' → Responde (conversa ativa)")
print("3. 'Qual meu nome?' → Responde (conversa ativa)")
print("4. [5min silêncio] → Modo seletivo")
print("5. 'mudo' → Para de responder")
print("6. 'Sexta-feira' → Ativa novamente")