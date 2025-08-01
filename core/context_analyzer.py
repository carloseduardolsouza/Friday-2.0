# core/context_analyzer.py
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
        
        # Padrões MUITO ESPECÍFICOS para SEXTA-FEIRA
        self.friday_name_patterns = [
            # Variações de "sexta-feira"
            r"\bsexta.feira\b",
            r"\bsexta\s+feira\b", 
            r"\bsextafeira\b",
            r"\bsexta\b(?!.*feira\s+que)",  # "sexta" mas não "sexta-feira que vem"
            
            # Variações em inglês
            r"\bfriday\b",
            
            # Com saudações
            r"\b(ei|oi|olá|hey)\s+(sexta|friday)\b",
            r"\b(oi|olá)\s+sexta.feira\b",
            
            # Com títulos
            r"\b(assistente|ia)\s+sexta\b",
            r"\bminha\s+sexta\b",
            
            # Formas carinhosas
            r"\bsextinha\b",
            r"\bfri\b",
        ]
        
        # Padrões para quando ela SABE que é sobre ela
        self.self_reference_patterns = [
            # Quando perguntam sobre ela especificamente
            r"\b(qual|como)\s+(é\s+)?o\s+seu\s+nome\b",
            r"\b(quem|o\s+que)\s+(é\s+)?você\b",
            r"\bcomo\s+você\s+se\s+chama\b",
            r"\bvocê\s+é\s+(a\s+)?sexta\b",
            r"\bseu\s+nome\s+é\s+sexta\b",
            
            # Referências diretas a ela
            r"\bvocê\s+(é|está|pode|consegue|sabe)\b",
            r"\bme\s+(ajuda|diga|fala|conte)\b",
            r"\b(pode|consegue)\s+me\s+ajudar\b",
            
            # Comandos diretos
            r"\b(responda|diga|fale|conte|explique)\b",
            r"\b(qual|como|quando|onde|por\s+que)\b.*\?",
        ]
        
        # Padrões que NÃO são sobre sexta-feira (contexto temporal)
        self.temporal_friday_patterns = [
            r"\bsexta.feira\s+(passada|que\s+vem|próxima|retrasada)\b",
            r"\bna\s+sexta\b",
            r"\bessa\s+sexta\s+(feira\s+)?(vai|vou|tem)\b",
            r"\bnesta\s+sexta\b",
            r"\bsexta.feira\s+à\s+(noite|tarde|manhã)\b",
            r"\btoda\s+sexta\b",
        ]
        
        # Padrões de desativação
        self.deactivation_patterns = [
            r"\bmudo\b",
            r"\bsilêncio\b",
            r"\bquieta\b",
            r"\bpara\s+de\s+(escutar|falar|responder)\b",
            r"\bnão\s+(fale|responda|escute)\b",
            r"\bmodo\s+silencioso\b",
            r"\bfique\s+(quieta|calada)\b",
            r"\bchega\s+(de\s+)?conversa\b",
        ]
        
        # Padrões indiretos (falando SOBRE a sexta-feira)
        self.indirect_patterns = [
            rf"\b(essa|esta|a)\s+(sexta|assistente|ia)\b",
            r"\bfalando.{0,15}(da|sobre|com).{0,15}(sexta|assistente)\b",
            
            # Opiniões sobre ela
            r"\b(sexta|assistente).{0,30}(é|está|foi|fica).{0,30}(ruim|boa|legal|chata|inteligente|útil)\b",
            r"\b(gosto|não\s+gosto|amo|odeio).{0,20}(da|dessa).{0,20}(sexta|assistente)\b",
            r"\ba\s+(sexta|assistente).{0,20}(me\s+)?(ajuda|entende|sabe)\b",
        ]
    
    def should_respond(self, text: str, user_name: str = "") -> Tuple[bool, str, float]:
        """
        Determina se SEXTA-FEIRA deve responder
        """
        text_lower = text.lower()
        
        # 1. VERIFICAR SE É CONTEXTO TEMPORAL (sexta-feira do calendário)
        for pattern in self.temporal_friday_patterns:
            if re.search(pattern, text_lower):
                return False, "Contexto temporal detectado - não é sobre mim", 0.0
        
        # 2. VERIFICAR MENÇÃO DIRETA DO NOME SEXTA-FEIRA
        for pattern in self.friday_name_patterns:
            if re.search(pattern, text_lower):
                self.conversation_state.activate_conversation("explicit")
                return True, f"Nome SEXTA-FEIRA detectado explicitamente", 0.98
        
        # 3. VERIFICAR COMANDOS DE DESATIVAÇÃO
        for pattern in self.deactivation_patterns:
            if re.search(pattern, text_lower):
                self.conversation_state.deactivate_conversation("explicit")
                return False, f"Comando de desativação detectado", 0.0
        
        # 4. USAR SISTEMA DE ESTADO DE CONVERSA
        should_respond, reason, confidence = self.conversation_state.should_respond_to_input(text)
        
        # 5. SE JÁ DISSE QUE DEVE RESPONDER, VERIFICAR PADRÕES ADICIONAIS
        if should_respond:
            return should_respond, reason, confidence
        
        # 6. VERIFICAR REFERÊNCIAS A ELA MESMO SEM NOME
        for pattern in self.self_reference_patterns:
            if re.search(pattern, text_lower):
                return True, "Referência direta detectada (sem nome)", 0.85
        
        # 7. VERIFICAR MENÇÕES INDIRETAS
        for pattern in self.indirect_patterns:
            if re.search(pattern, text_lower):
                return True, "Menção indireta detectada", 0.7
        
        # 8. VERIFICAR DEFESA (falando mal)
        negative_patterns = [
            r"\b(sexta|assistente|ia).{0,30}(ruim|horrível|péssima|inútil|burra|idiota)\b",
            r"\b(odeio|detesto|não\s+gosto).{0,20}(da|dessa).{0,20}(sexta|assistente)\b",
            r"\b(sexta|assistente).{0,20}(não|nunca).{0,20}(funciona|entende|ajuda|serve)\b",
        ]
        
        for pattern in negative_patterns:
            if re.search(pattern, text_lower):
                return True, "Comentário negativo detectado - defesa necessária", 0.9
        
        return False, "Não parece ser direcionado à SEXTA-FEIRA", 0.0
    
    def analyze_emotional_context(self, text: str) -> Dict[str, float]:
        """Analisa contexto emocional da fala"""
        text_lower = text.lower()
        
        emotions = {
            "feliz": 0.0,
            "triste": 0.0,
            "raiva": 0.0,
            "neutro": 0.0,
            "curioso": 0.0,
            "frustrado": 0.0
        }
        
        # Palavras de cada emoção
        emotion_words = {
            "feliz": ["feliz", "alegre", "ótimo", "excelente", "adorei", "amei", "legal", "bom", "maravilhoso", "perfeito"],
            "triste": ["triste", "chateado", "ruim", "péssimo", "horrível", "mal", "deprimido", "desanimado"],
            "raiva": ["raiva", "ódio", "irritado", "furioso", "puto", "bravo", "nervoso", "maldito"],
            "curioso": ["como", "por que", "quando", "onde", "qual", "o que", "me explique", "não entendi"],
            "frustrado": ["não funciona", "não entende", "burra", "inútil", "não serve", "problemática"]
        }
        
        words = text_lower.split()
        total_words = max(len(words), 1)
        
        for emotion, word_list in emotion_words.items():
            count = sum(1 for word in word_list if word in text_lower)
            emotions[emotion] = count / total_words * 10
        
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
    
    def is_talking_about_friday_calendar(self, text: str) -> bool:
        """Verifica se está falando sobre sexta-feira do calendário"""
        text_lower = text.lower()
        for pattern in self.temporal_friday_patterns:
            if re.search(pattern, text_lower):
                return True
        return False
