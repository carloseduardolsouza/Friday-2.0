# core/conversation.py
import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from memory.database import DatabaseManager
from memory.user_profile import UserProfile
from config.settings import AgentConfig

class ConversationManager:
    """Gerencia contexto e histórico de conversas"""
    
    def __init__(self, database: DatabaseManager, user_profile: UserProfile, config: AgentConfig):
        self.database = database
        self.user_profile = user_profile
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # ID da sessão atual
        self.current_session_id = str(uuid.uuid4())
        
        # Cache do contexto atual
        self.current_context: List[Dict[str, Any]] = []
        self.context_window_size = 20  # Número de mensagens no contexto
        
        # Estatísticas da conversa
        self.conversation_stats = {
            'messages_today': 0,
            'session_start': datetime.now(),
            'total_interactions': 0
        }
    
    async def add_message(self, role: str, content: str, metadata: Dict = None):
        """Adiciona mensagem à conversa"""
        try:
            # Salvar no banco
            await self.database.save_conversation_message(
                self.current_session_id,
                role, 
                content, 
                metadata
            )
            
            # Adicionar ao contexto atual
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
            
            if metadata:
                message['metadata'] = metadata
            
            self.current_context.append(message)
            
            # Manter tamanho do contexto
            if len(self.current_context) > self.context_window_size:
                self.current_context = self.current_context[-self.context_window_size:]
            
            # Atualizar estatísticas
            self.conversation_stats['total_interactions'] += 1
            if role == 'user':
                self.conversation_stats['messages_today'] += 1
            
            self.logger.debug(f"Mensagem adicionada: {role} - {content[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar mensagem: {e}")
    
    async def get_context(self, max_messages: int = None) -> str:
        """Obtém contexto atual da conversa formatado"""
        try:
            # Definir número máximo de mensagens
            if max_messages is None:
                max_messages = self.context_window_size
            
            # Obter mensagens do contexto
            context_messages = self.current_context[-max_messages:]
            
            if not context_messages:
                return "Nenhuma conversa anterior na sessão atual."
            
            # Formatar contexto
            formatted_context = []
            for msg in context_messages:
                role_name = "Usuário" if msg['role'] == 'user' else "Assistente"
                timestamp = msg.get('timestamp', '')
                
                # Formato: [Timestamp] Role: Content
                if timestamp:
                    # Simplificar timestamp
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime("%H:%M")
                        formatted_context.append(f"[{time_str}] {role_name}: {msg['content']}")
                    except:
                        formatted_context.append(f"{role_name}: {msg['content']}")
                else:
                    formatted_context.append(f"{role_name}: {msg['content']}")
            
            return "\n".join(formatted_context)
            
        except Exception as e:
            self.logger.error(f"Erro ao obter contexto: {e}")
            return "Erro ao recuperar contexto da conversa."
    
    async def get_full_history(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Obtém histórico completo das conversas"""
        try:
            return await self.database.get_conversation_history(
                self.current_session_id,
                limit=100
            )
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico: {e}")
            return []
    
    async def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Busca nas conversas anteriores"""
        try:
            # Implementação simples - pode ser melhorada com busca semântica
            history = await self.get_full_history(days_back=30)
            
            results = []
            query_lower = query.lower()
            
            for msg in history:
                if query_lower in msg['content'].lower():
                    results.append(msg)
                    if len(results) >= limit:
                        break
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca: {e}")
            return []
    
    async def summarize_conversation(self) -> str:
        """Cria resumo da conversa atual"""
        try:
            if not self.current_context:
                return "Nenhuma conversa para resumir."
            
            # Contar mensagens por tipo
            user_messages = len([m for m in self.current_context if m['role'] == 'user'])
            assistant_messages = len([m for m in self.current_context if m['role'] == 'assistant'])
            
            # Identificar tópicos principais (simplificado)
            all_content = " ".join([m['content'] for m in self.current_context])
            
            # Palavras mais comuns (filtradas)
            words = all_content.lower().split()
            common_words = {'o', 'a', 'de', 'que', 'e', 'do', 'da', 'em', 'um', 'uma', 'para', 'é', 'com', 'não', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'eu', 'sua', 'no', 'pelo', 'pela'}
            filtered_words = [w for w in words if w not in common_words and len(w) > 3]
            
            # Resumo básico
            duration = datetime.now() - self.conversation_stats['session_start']
            
            summary = f"""
Resumo da Conversa:
- Duração: {duration.seconds // 60} minutos
- Mensagens do usuário: {user_messages}
- Respostas do assistente: {assistant_messages}
- Sessão iniciada: {self.conversation_stats['session_start'].strftime('%H:%M')}
"""
            
            if filtered_words:
                from collections import Counter
                top_words = Counter(filtered_words).most_common(5)
                keywords = ", ".join([word for word, count in top_words])
                summary += f"- Palavras-chave: {keywords}"
            
            return summary.strip()
            
        except Exception as e:
            self.logger.error(f"Erro no resumo: {e}")
            return "Erro ao criar resumo da conversa."
    
    async def analyze_conversation_patterns(self) -> Dict[str, Any]:
        """Analisa padrões na conversa"""
        try:
            analysis = {
                'session_info': {
                    'session_id': self.current_session_id,
                    'start_time': self.conversation_stats['session_start'].isoformat(),
                    'duration_minutes': (datetime.now() - self.conversation_stats['session_start']).seconds // 60,
                    'message_count': len(self.current_context)
                },
                'interaction_patterns': {
                    'avg_user_message_length': 0,
                    'avg_assistant_message_length': 0,
                    'question_count': 0,
                    'topics_mentioned': []
                },
                'user_engagement': {
                    'messages_per_minute': 0,
                    'session_activity': 'baixa'  # baixa, média, alta
                }
            }
            
            if self.current_context:
                user_messages = [m for m in self.current_context if m['role'] == 'user']
                assistant_messages = [m for m in self.current_context if m['role'] == 'assistant']
                
                # Calcular médias de tamanho
                if user_messages:
                    analysis['interaction_patterns']['avg_user_message_length'] = \
                        sum(len(m['content']) for m in user_messages) // len(user_messages)
                
                if assistant_messages:
                    analysis['interaction_patterns']['avg_assistant_message_length'] = \
                        sum(len(m['content']) for m in assistant_messages) // len(assistant_messages)
                
                # Contar perguntas
                analysis['interaction_patterns']['question_count'] = \
                    sum(1 for m in user_messages if '?' in m['content'])
                
                # Calcular engajamento
                duration_minutes = (datetime.now() - self.conversation_stats['session_start']).seconds // 60
                if duration_minutes > 0:
                    messages_per_minute = len(user_messages) / duration_minutes
                    analysis['user_engagement']['messages_per_minute'] = round(messages_per_minute, 2)
                    
                    if messages_per_minute > 2:
                        analysis['user_engagement']['session_activity'] = 'alta'
                    elif messages_per_minute > 0.5:
                        analysis['user_engagement']['session_activity'] = 'média'
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erro na análise: {e}")
            return {}
    
    async def start_new_session(self):
        """Inicia nova sessão de conversa"""
        try:
            # Salvar análise da sessão anterior
            if self.current_context:
                analysis = await self.analyze_conversation_patterns()
                await self.database.add_knowledge(
                    f"session_{self.current_session_id}",
                    f"Análise da sessão: {analysis}",
                    "conversation_analysis"
                )
            
            # Nova sessão
            self.current_session_id = str(uuid.uuid4())
            self.current_context = []
            self.conversation_stats = {
                'messages_today': 0,
                'session_start': datetime.now(),
                'total_interactions': 0
            }
            
            self.logger.info(f"Nova sessão iniciada: {self.current_session_id}")
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar nova sessão: {e}")
    
    async def get_conversation_suggestions(self) -> List[str]:
        """Sugere tópicos de conversa baseados no histórico"""
        try:
            suggestions = []
            
            # Sugestões baseadas no perfil do usuário
            user_info = self.user_profile.user_info
            
            if user_info.hobbies:
                suggestions.append(f"Como foram seus hobbies recentemente? ({', '.join(user_info.hobbies[:2])})")
            
            if user_info.occupation:
                suggestions.append(f"Como está o trabalho como {user_info.occupation}?")
            
            # Sugestões baseadas em eventos próximos
            upcoming_events = await self.database.get_upcoming_events(7)
            if upcoming_events:
                event = upcoming_events[0]
                suggestions.append(f"Você está preparado para {event['name']} em {event['date']}?")
            
            # Sugestões gerais
            general_suggestions = [
                "O que você gostaria de aprender hoje?",
                "Há algo específico em que posso ajudá-lo?",
                "Como posso tornar seu dia mais produtivo?"
            ]
            
            suggestions.extend(general_suggestions[:2])
            
            return suggestions[:5]  # Máximo 5 sugestões
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar sugestões: {e}")
            return ["Como posso ajudá-lo hoje?"]