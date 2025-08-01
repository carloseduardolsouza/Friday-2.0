# core/context_analyzer.py
import re
import logging
from typing import List, Dict, Tuple
from datetime import datetime

class ContextAnalyzer:
    """Analisa contexto da fala para decidir quando a IA deve responder"""
    
    def __init__(self, agent_name: str = "ARIA"):
        self.agent_name = agent_name.lower()
        self.logger = logging.getLogger(__name__)
        
        # Padrões que indicam que é direcionado à IA
        self.direct_patterns = [
            # Menções diretas
            rf"\b{self.agent_name}\b",
            r"\baria\b",
            r"\bassistente\b",
            r"\bia\b",
            r"\brobô\b",
            r"\bbot\b",
            
            # Palavras de comando
            r"\b(ei|hey|olá|oi)\s+(aria|assistente|ia)\b",
            r"\b(me ajuda|ajude|responda|diga|fala)\b",
            r"\b(você pode|consegue|sabe)\b",
            r"\bqual.{0,20}(é|meu|seu|nome|hora|dia)\b",
            r"\bcomo.{0,20}(você|está|vai|fazer)\b",
            r"\bo que.{0,20}(você|é|faz|acha)\b",
        ]
        
        # Padrões que sugerem menção indireta mas relevante
        self.indirect_patterns = [
            # Falando SOBRE a IA
            rf"\b(essa|esta|a)\s+{self.agent_name}\b",
            r"\b(essa|esta|a)\s+(ia|assistente)\b",
            r"\bfalando.{0,10}(da|sobre).{0,10}(ia|assistente|aria)\b",
            
            # Opiniões sobre IA
            r"\b(ia|assistente|aria).{0,20}(é|está|foi|fica).{0,20}(ruim|boa|legal|chata|inteligente|burra)\b",
            r"\b(não gosto|odeio|amo|gosto).{0,20}(da|dessa).{0,20}(ia|assistente|aria)\b",
            r"\b(ia|assistente|aria).{0,20}(não|nunca).{0,20}(funciona|entende|responde|ajuda)\b",
            
            # Comparações
            r"\b(melhor|pior).{0,20}que.{0,20}(ia|assistente|aria)\b",
            r"\b(ia|assistente|aria).{0,20}(melhor|pior).{0,20}que\b",
        ]
        
        # Padrões que sugerem que NÃO é para a IA
        self.ignore_patterns = [
            r"\b(não|nem).{0,10}(fala|responde|liga).{0,10}(aria|ia|assistente)\b",
            r"\b(cala|silêncio|quieta).{0,10}(aria|ia|assistente)\b",
            r"\bestou falando com\b",
            r"\bnão é com você\b",
        ]
        
    def should_respond(self, text: str, user_name: str = "") -> Tuple[bool, str, float]:
        """
        Analisa se a IA deve responder
        
        Returns:
            (should_respond: bool, reason: str, confidence: float)
        """
        text_lower = text.lower()
        
        # 1. Verificar padrões de ignorar (prioridade máxima)
        for pattern in self.ignore_patterns:
            if re.search(pattern, text_lower):
                return False, "Usuário pediu para não responder", 0.0
        
        # 2. Verificar menções diretas (alta prioridade)
        for pattern in self.direct_patterns:
            if re.search(pattern, text_lower):
                confidence = 0.9
                # Aumentar confiança se mencionar nome do usuário
                if user_name and user_name.lower() in text_lower:
                    confidence = 0.95
                return True, "Menção direta detectada", confidence
        
        # 3. Verificar menções indiretas (média prioridade)
        for pattern in self.indirect_patterns:
            if re.search(pattern, text_lower):
                return True, "Menção indireta detectada", 0.7
        
        # 4. Verificar perguntas gerais que podem ser para a IA
        question_patterns = [
            r"\b(que horas|que dia|que data)\b",
            r"\b(como está|como vai|tudo bem)\b",
            r"\b(você|vocês).{0,20}(está|estão|vai|vão)\b",
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, text_lower):
                # Só responder se não houver outras pessoas sendo mencionadas
                if not re.search(r"\b(ele|ela|joão|maria|pedro|ana|fulano)\b", text_lower):
                    return True, "Pergunta geral possivelmente direcionada", 0.5
        
        # 5. Detectar se estão falando mal da IA (para defesa)
        negative_patterns = [
            r"\b(ia|assistente|aria).{0,30}(ruim|horrível|péssima|inútil|burra)\b",
            r"\b(odeio|detesto).{0,20}(ia|assistente|aria)\b",
            r"\b(ia|assistente|aria).{0,20}não.{0,20}(serve|funciona|presta)\b",
        ]
        
        for pattern in negative_patterns:
            if re.search(pattern, text_lower):
                return True, "Comentário negativo sobre a IA - defesa necessária", 0.8
        
        return False, "Não parece ser direcionado à IA", 0.0
    
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
        emotions["feliz"] = sum(1 for word in happy_words if word in text_lower) / len(text_lower.split()) * 10
        
        # Padrões de tristeza
        sad_words = ["triste", "chateado", "ruim", "péssimo", "horrível", "mal"]
        emotions["triste"] = sum(1 for word in sad_words if word in text_lower) / len(text_lower.split()) * 10
        
        # Padrões de raiva
        angry_words = ["raiva", "ódio", "irritado", "furioso", "maldita", "droga"]
        emotions["raiva"] = sum(1 for word in angry_words if word in text_lower) / len(text_lower.split()) * 10
        
        # Padrões de curiosidade
        curious_words = ["como", "por que", "quando", "onde", "qual", "?"]
        emotions["curioso"] = sum(1 for word in curious_words if word in text_lower) / len(text_lower.split()) * 5
        
        # Se nenhuma emoção forte, é neutro
        if max(emotions.values()) < 0.1:
            emotions["neutro"] = 1.0
        
        return emotions
