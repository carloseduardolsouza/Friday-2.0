# fix_complete.py
import os

# 1. Corrigir detecção de modelos no local_llm.py
print("🔧 Corrigindo detecção de modelos...")

llm_code = '''# models/local_llm.py
import asyncio
import logging
import ollama
from typing import Optional, Dict, Any, List
from config.settings import ModelConfig

class LocalLLM:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = ollama.AsyncClient()
        self.conversation_history: List[Dict[str, str]] = []
        
    async def initialize(self):
        try:
            self.logger.info(f"Inicializando modelo {self.config.model_name}...")
            
            # Verificar se o modelo está disponível
            models = await self.list_available_models()
            
            # CORREÇÃO: Extrair nomes dos modelos corretamente
            model_names = []
            for model in models:
                if hasattr(model, 'model'):
                    model_names.append(model.model)
                elif isinstance(model, dict) and 'model' in model:
                    model_names.append(model['model'])
            
            self.logger.info(f"Modelos disponíveis: {model_names}")
            
            # Verificar se o modelo desejado existe
            if self.config.model_name in model_names:
                self.logger.info(f"Modelo {self.config.model_name} encontrado!")
            else:
                self.logger.warning(f"Modelo {self.config.model_name} não encontrado nos modelos: {model_names}")
                # Tentar usar o primeiro modelo Llama disponível
                for name in model_names:
                    if "llama" in name.lower():
                        self.logger.info(f"Usando modelo alternativo: {name}")
                        self.config.model_name = name
                        break
            
            # Testar o modelo
            await self.test_model()
            
            self.logger.info("Modelo inicializado com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar modelo: {e}")
            # Não fazer raise, continuar
    
    async def list_available_models(self) -> List[Any]:
        try:
            response = await self.client.list()
            models = response.get('models', [])
            return models
        except Exception as e:
            self.logger.error(f"Erro ao listar modelos: {e}")
            return []
    
    async def test_model(self):
        try:
            test_prompt = "Diga apenas 'Modelo funcionando' em português."
            response = await self.generate_response(test_prompt, use_history=False)
            
            if response and "erro" not in response.lower():
                self.logger.info(f"Teste do modelo bem-sucedido!")
            else:
                self.logger.warning(f"Modelo respondeu com: {response}")
                
        except Exception as e:
            self.logger.error(f"Erro no teste do modelo: {e}")
    
    async def generate_response(self, prompt: str, use_history: bool = True) -> Optional[str]:
        try:
            # Preparar mensagens
            messages = []
            
            if use_history and self.conversation_history:
                # Manter apenas as últimas conversas
                recent_history = self.conversation_history[-4:]  # Ainda menor
                messages.extend(recent_history)
            
            # Adicionar prompt atual
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            # Gerar resposta
            response = await self.client.chat(
                model=self.config.model_name,
                messages=messages,
                options={
                    'temperature': self.config.temperature,
                    'num_predict': self.config.max_tokens,
                    'top_p': 0.9,
                    'repeat_penalty': 1.1
                }
            )
            
            if response and 'message' in response and 'content' in response['message']:
                assistant_message = response['message']['content'].strip()
                
                # Adicionar ao histórico
                if use_history:
                    self.conversation_history.append({
                        'role': 'user',
                        'content': prompt
                    })
                    self.conversation_history.append({
                        'role': 'assistant',
                        'content': assistant_message
                    })
                    
                    # Limitar histórico
                    if len(self.conversation_history) > 8:
                        self.conversation_history = self.conversation_history[-6:]
                
                return assistant_message
            else:
                self.logger.error(f"Resposta inválida: {response}")
                return "Desculpe, não consegui gerar uma resposta adequada."
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta: {e}")
            return f"Desculpe, houve um erro: {str(e)[:100]}"
    
    def clear_history(self):
        self.conversation_history = []
        self.logger.info("Histórico limpo")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            'model_name': self.config.model_name,
            'max_tokens': self.config.max_tokens,
            'temperature': self.config.temperature,
            'history_length': len(self.conversation_history)
        }
'''

# 2. Adicionar input de texto + melhorar loop de escuta
agent_code = '''# core/agent.py
import asyncio
import logging
import threading
from datetime import datetime
from typing import Optional, Dict, Any

from core.speech_to_text import SpeechToText
from core.text_to_speech import TextToSpeech
from core.conversation import ConversationManager
from memory.user_profile import UserProfile
from memory.database import DatabaseManager
from models.local_llm import LocalLLM
from config.settings import AgentConfig

class AIAgent:
    """Classe principal do agente de IA"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Componentes principais
        self.stt: Optional[SpeechToText] = None
        self.tts: Optional[TextToSpeech] = None
        self.llm: Optional[LocalLLM] = None
        self.conversation_manager: Optional[ConversationManager] = None
        self.user_profile: Optional[UserProfile] = None
        self.database: Optional[DatabaseManager] = None
        
        # Estado do agente
        self.is_listening = False
        self.is_speaking = False
        self.is_running = False
        
    async def initialize(self):
        """Inicializa todos os componentes do agente"""
        self.logger.info("Inicializando componentes do agente...")
        
        try:
            # Inicializar banco de dados
            self.database = DatabaseManager(self.config.database)
            await self.database.initialize()
            
            # Inicializar perfil do usuário
            self.user_profile = UserProfile(self.database)
            await self.user_profile.load_profile()
            
            # Inicializar modelo de IA
            self.llm = LocalLLM(self.config.model)
            await self.llm.initialize()
            
            # Inicializar componentes de voz
            self.stt = SpeechToText(self.config.voice)
            self.tts = TextToSpeech(self.config.voice)
            
            # Inicializar gerenciador de conversas
            self.conversation_manager = ConversationManager(
                self.database, 
                self.user_profile,
                self.config
            )
            
            self.logger.info("Todos os componentes inicializados com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar agente: {e}")
            raise
    
    async def run(self):
        """Loop principal do agente"""
        self.is_running = True
        
        # Saudação inicial
        user_name = self.user_profile.get_user_name()
        greeting = f"Olá {user_name}! Sou a {self.config.name}, sua assistente pessoal. Como posso ajudá-lo hoje?"
        await self.speak(greeting)
        
        print("\\n" + "="*60)
        print("🤖 AGENTE ATIVO - Escolha como interagir:")
        print("🎤 [ENTER] para falar (reconhecimento de voz)")
        print("⌨️  [TEXTO] digite sua mensagem + ENTER")
        print("❌ [sair] para encerrar")
        print("="*60 + "\\n")
        
        try:
            while self.is_running:
                # Aguardar input do usuário
                user_input = await self.get_user_input()
                
                if user_input:
                    # Verificar comandos especiais
                    if self.check_exit_command(user_input):
                        break
                    
                    # Processar entrada do usuário
                    response = await self.process_input(user_input)
                    
                    # Responder ao usuário
                    if response:
                        await self.speak(response)
                
        except KeyboardInterrupt:
            print("\\n⚠️ Interrupção detectada...")
        finally:
            await self.shutdown()
    
    async def get_user_input(self) -> Optional[str]:
        """Obtém input do usuário (texto ou voz)"""
        try:
            print("\\n💬 Sua vez (ENTER=voz, texto+ENTER=texto):")
            
            # Executar input em thread separada
            loop = asyncio.get_event_loop()
            user_text = await loop.run_in_executor(None, input, ">>> ")
            
            if user_text.strip():
                # Input de texto
                print(f"👤 Você (texto): {user_text}")
                await self.conversation_manager.add_message("user", user_text)
                return user_text.strip()
            else:
                # Input de voz
                print("🎤 Escutando... (fale agora, 5 segundos)")
                voice_input = await self.listen()
                return voice_input
                
        except Exception as e:
            self.logger.error(f"Erro ao obter input: {e}")
            return None
    
    async def listen(self) -> Optional[str]:
        """Escuta entrada de voz do usuário"""
        if self.is_speaking or self.is_listening:
            return None
            
        self.is_listening = True
        try:
            # Usar reconhecimento de voz
            text = await self.stt.listen()
            if text:
                self.logger.info(f"Usuário disse: {text}")
                print(f"👤 Você (voz): {text}")
                # Salvar na conversa
                await self.conversation_manager.add_message("user", text)
            else:
                print("❌ Não consegui ouvir nada")
            return text
        except Exception as e:
            self.logger.error(f"Erro no reconhecimento de voz: {e}")
            print(f"❌ Erro no reconhecimento: {e}")
            return None
        finally:
            self.is_listening = False
    
    async def speak(self, text: str):
        """Fala o texto fornecido"""
        if self.is_speaking:
            return
            
        self.is_speaking = True
        try:
            self.logger.info(f"Assistente: {text}")
            print(f"\\n🤖 ARIA: {text}")
            await self.tts.speak(text)
            # Salvar na conversa
            await self.conversation_manager.add_message("assistant", text)
        except Exception as e:
            self.logger.error(f"Erro na síntese de voz: {e}")
            print(f"❌ Erro na fala: {e}")
        finally:
            self.is_speaking = False
    
    async def process_input(self, user_input: str) -> Optional[str]:
        """Processa a entrada do usuário e gera resposta"""
        try:
            print("🧠 Processando...")
            
            # Extrair informações pessoais do usuário
            await self.user_profile.extract_and_update_info(user_input)
            
            # Obter contexto da conversa
            context = await self.conversation_manager.get_context()
            
            # Criar prompt personalizado
            prompt = self.create_personalized_prompt(user_input, context)
            
            # Gerar resposta usando o modelo local
            response = await self.llm.generate_response(prompt)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao processar entrada: {e}")
            return "Desculpe, houve um erro interno. Pode repetir por favor?"
    
    def create_personalized_prompt(self, user_input: str, context: str) -> str:
        """Cria prompt personalizado baseado no perfil do usuário"""
        user_info = self.user_profile.get_summary()
        
        prompt = f"""Você é {self.config.name}, uma assistente pessoal IA {self.config.personality}.

INFORMAÇÕES DO USUÁRIO:
{user_info}

ENTRADA DO USUÁRIO: {user_input}

Responda de forma natural, amigável e concisa (máximo 2-3 frases). Se o usuário compartilhar informações pessoais, reconheça isso.

RESPOSTA:"""
        
        return prompt
    
    def check_exit_command(self, text: str) -> bool:
        """Verifica se o usuário quer sair"""
        exit_commands = ["sair", "tchau", "até logo", "encerrar", "parar", "quit", "exit"]
        return any(cmd in text.lower() for cmd in exit_commands)
    
    async def shutdown(self):
        """Encerra o agente de forma limpa"""
        print("\\n🔄 Encerrando agente...")
        self.is_running = False
        
        # Salvar dados do usuário
        if self.user_profile:
            await self.user_profile.save_profile()
        
        # Fechar conexões
        if self.database:
            await self.database.close()
        
        # Despedida
        print("👋 Até logo! Obrigada por usar a ARIA!")
        self.logger.info("Agente encerrado com sucesso!")
'''

# Salvar arquivos corrigidos
print("📝 Atualizando models/local_llm.py...")
with open("models/local_llm.py", "w", encoding="utf-8") as f:
    f.write(llm_code)

print("📝 Atualizando core/agent.py...")
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(agent_code)

print("✅ Correções aplicadas!")
print("")
print("🎯 MUDANÇAS FEITAS:")
print("• ✅ Detecção correta de modelos Ollama")
print("• ✅ Input por TEXTO + ENTER")
print("• ✅ Input por VOZ (só ENTER)")
print("• ✅ Interface melhorada")
print("• ✅ Tratamento de erros melhorado")
print("")
print("🚀 Execute: python main.py")
print("💡 Agora você pode digitar OU falar!")