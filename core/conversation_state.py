# core/conversation_state.py
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