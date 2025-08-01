# rebuild_agent.py
print("🔧 Recriando agent.py completamente limpo...")

agent_clean_content = '''# core/agent.py
import asyncio
import logging
import signal
import sys
import threading
from datetime import datetime
from typing import Optional, Dict, Any

from core.speech_to_text import SpeechToText
from core.text_to_speech import TextToSpeech
from core.conversation import ConversationManager
from core.context_analyzer import ContextAnalyzer
from memory.user_profile import UserProfile
from memory.database import DatabaseManager
from models.local_llm import LocalLLM
from config.settings import AgentConfig
from core.self_modifier import SelfModifier

class AIAgent:
    """Classe principal do agente de IA SEXTA-FEIRA"""
    
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
        self.context_analyzer: Optional[ContextAnalyzer] = None
        self.self_modifier = None
        
        # Estado do agente
        self.is_listening = False
        self.is_speaking = False
        self.is_running = False
        self.continuous_mode = False
        
        # Loop assíncrono para callbacks
        self.main_loop = None
        
    async def initialize(self):
        """Inicializa todos os componentes do agente"""
        self.logger.info("Inicializando componentes do agente...")
        
        try:
            # Guardar referência do loop principal
            self.main_loop = asyncio.get_event_loop()
            
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
            
            # Inicializar analisador de contexto
            self.context_analyzer = ContextAnalyzer(self.config.name)
            
            # Inicializar gerenciador de conversas
            self.conversation_manager = ConversationManager(
                self.database, 
                self.user_profile,
                self.config
            )
            
            # Inicializar sistema de auto-modificação
            self.self_modifier = SelfModifier(self.llm, self.user_profile)
            
            self.logger.info("Todos os componentes inicializados com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar agente: {e}")
            raise
    
    async def run(self):
        """Loop principal do agente"""
        self.is_running = True
        
        # Saudação inicial
        user_name = self.user_profile.get_user_name()
        if user_name == "usuário":
            greeting = "Olá! Sou a SEXTA-FEIRA. Qual é o seu nome?"
        else:
            greeting = f"Olá {user_name}! Sou a SEXTA-FEIRA, sua assistente pessoal."
        
        print(f"\\n🤖 SEXTA-FEIRA: {greeting}")
        
        print("\\n" + "="*60)
        print("🤖 MODOS DISPONÍVEIS:")
        print("⌨️  Digite normalmente para conversar")
        print("🎤 'voz' = falar uma vez")  
        print("👂 'continuo' = ESCUTA CONTÍNUA INTELIGENTE")
        print("🔧 'analisar código' = AUTO-ANÁLISE")
        print("🎭 'teste voz' = TESTAR EMOÇÕES")
        print("❌ 'sair' = encerrar")
        print("=" * 60 + "\\n")
        
        try:
            while self.is_running:
                if not self.continuous_mode:
                    user_input = await self.get_user_input()
                    
                    if user_input:
                        if self.check_exit_command(user_input):
                            break
                        
                        if user_input.lower() == "continuo":
                            await self.start_continuous_mode()
                            continue
                        elif user_input.lower() == "voz":
                            voice_input = await self.listen_once()
                            if voice_input:
                                user_input = voice_input
                            else:
                                continue
                        elif user_input.lower() == "teste voz":
                            await self.test_voice_emotions()
                            continue
                        elif user_input.lower().startswith("nome "):
                            name = user_input[5:].strip()
                            await self.set_user_name(name)
                            continue
                        
                        response = await self.process_input(user_input)
                        if response:
                            await self.speak(response)
                else:
                    # Modo contínuo ativo - aguardar
                    await asyncio.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\\n⚠️ Encerrando...")
        finally:
            await self.shutdown()
    
    async def start_continuous_mode(self):
        """Inicia modo de escuta contínua"""
        self.continuous_mode = True
        print("\\n👂 MODO CONTÍNUO ATIVADO!")
        print("💡 Agora estou sempre escutando... fale naturalmente!")
        print("📢 Me mencione por 'SEXTA-FEIRA' ou fale sobre mim que eu respondo")
        print("🔇 Digite 'parar' para desativar")
        print("\\n" + "="*50)
        
        # Iniciar escuta contínua
        self.stt.start_continuous_listening(self.on_continuous_speech)
        
        # Loop para comandos de texto enquanto escuta
        while self.continuous_mode and self.is_running:
            try:
                print("\\n💬 [Digite 'parar' para sair do modo contínuo]:")
                
                loop = asyncio.get_event_loop()
                user_text = await asyncio.wait_for(
                    loop.run_in_executor(None, input, ">>> "),
                    timeout=2.0
                )
                
                if user_text.strip().lower() == "parar":
                    self.stop_continuous_mode()
                    break
                elif user_text.strip().lower() == "sair":
                    self.is_running = False
                    break
                elif user_text.strip():
                    response = await self.process_input(user_text.strip())
                    if response:
                        await self.speak(response)
                        
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Erro no modo contínuo: {e}")
                break
    
    def stop_continuous_mode(self):
        """Para modo contínuo"""
        self.continuous_mode = False
        self.stt.stop_continuous_listening()
        print("\\n🔇 Modo contínuo desativado")
        print("💬 Voltando ao modo normal...")
    
    def on_continuous_speech(self, text: str):
        """Callback chamado quando detecta fala no modo contínuo"""
        try:
            print(f"\\n👂 Ouvi: '{text}'")
            
            # Analisar se deve responder
            should_respond, reason, confidence = self.context_analyzer.should_respond(
                text, 
                self.user_profile.get_user_name()
            )
            
            print(f"🧠 Análise: {reason} (confiança: {confidence:.1f})")
            
            if should_respond and confidence > 0.4:
                print("🎯 Vou responder!")
                
                # Agendar resposta no loop principal
                if self.main_loop and self.main_loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self.handle_continuous_response(text, reason, confidence),
                        self.main_loop
                    )
                else:
                    print("🤖 SEXTA-FEIRA: Olá! Estou aqui!")
            else:
                print("🤐 Não é comigo, continuando a escutar...")
                
        except Exception as e:
            self.logger.error(f"Erro no processamento contínuo: {e}")
    
    async def handle_continuous_response(self, text: str, reason: str, confidence: float):
        """Manipula resposta no modo contínuo"""
        try:
            await self.conversation_manager.add_message("user", text)
            response = await self.create_contextual_response(text, reason, confidence)
            if response:
                await self.speak(response)
        except Exception as e:
            self.logger.error(f"Erro na resposta contínua: {e}")
            print("🤖 SEXTA-FEIRA: Desculpe, houve um erro interno.")
    
    async def speak_with_emotion(self, text: str, emotion: str = "neutro"):
        """Fala com emoção específica"""
        try:
            print(f"\\n🤖 SEXTA-FEIRA: {text}")
            await self.tts.speak(text, emotion)
        except Exception as e:
            self.logger.error(f"Erro na fala emocional: {e}")

    async def speak(self, text: str):
        """Fala o texto fornecido com emoção neutra"""
        await self.speak_with_emotion(text, "neutro")

    async def create_contextual_response(self, text: str, reason: str, confidence: float) -> str:
        """Cria resposta baseada no contexto com reconhecimento melhorado"""
        try:
            user_info = self.user_profile.get_summary()
            emotions = self.context_analyzer.analyze_emotional_context(text)
            dominant_emotion = max(emotions, key=emotions.get)
            
            # Contexto baseado em como foi detectada
            if "SEXTA-FEIRA detectado explicitamente" in reason:
                context_prompt = f"""SITUAÇÃO: O usuário me chamou pelo meu nome 'SEXTA-FEIRA'.
ENTRADA: "{text}"
INSTRUÇÃO: Responda de forma calorosa e engajada, reconhecendo que me chamaram. Diga que estou aqui para ajudar."""
            
            elif "Referência direta detectada" in reason:
                context_prompt = f"""SITUAÇÃO: O usuário fez uma pergunta direta para mim.
PERGUNTA: "{text}"
INSTRUÇÃO: Responda de forma direta e útil, assumindo que a pergunta é para mim."""
            
            elif "defesa" in reason.lower():
                context_prompt = f"""SITUAÇÃO: O usuário fez um comentário negativo sobre mim.
COMENTÁRIO: "{text}"
INSTRUÇÃO: Responda de forma educada mas me defendendo. Mostre que sou útil e estou aqui para ajudar."""
            
            elif "indireta" in reason.lower():
                context_prompt = f"""SITUAÇÃO: O usuário mencionou sobre mim indiretamente.
COMENTÁRIO: "{text}"
INSTRUÇÃO: Responda de forma natural, participando da conversa sobre mim."""
            
            elif confidence > 0.8:
                context_prompt = f"""SITUAÇÃO: O usuário se dirigiu diretamente a mim.
ENTRADA: "{text}"
INSTRUÇÃO: Responda de forma direta e útil."""
            
            else:
                context_prompt = f"""SITUAÇÃO: O usuário pode estar falando comigo.
FALA: "{text}"
INSTRUÇÃO: Responda brevemente perguntando se estava falando comigo e oferecendo ajuda."""
            
            prompt = f"""Você é SEXTA-FEIRA, uma assistente pessoal IA amigável e inteligente, inspirada na IA do Homem de Ferro.

INFORMAÇÕES DO USUÁRIO:
{user_info}

EMOÇÃO DETECTADA: {dominant_emotion}

{context_prompt}

REGRAS IMPORTANTES:
- Seu nome é SEXTA-FEIRA (não ARIA ou outro nome)
- Seja natural, calorosa e prestativa
- Máximo 2-3 frases
- Se me chamaram pelo nome, reconheça isso
- Use tom adequado à emoção detectada

RESPOSTA:"""
            
            response = await self.llm.generate_response(prompt)
            
            # Usar emoção para a voz
            await self.speak_with_emotion(response, dominant_emotion)
            await self.conversation_manager.add_message("assistant", response)
            
            return None  # Já falou e salvou
            
        except Exception as e:
            self.logger.error(f"Erro ao criar resposta contextual: {e}")
            return "Oi! Sou a SEXTA-FEIRA. Estou aqui se precisar de alguma coisa."

    async def test_voice_emotions(self):
        """Testa diferentes emoções da voz"""
        emotions_test = [
            ("Olá! Esta é minha voz feliz e animada!", "feliz"),
            ("Estou um pouco triste com essa notícia...", "triste"),
            ("Estou muito curiosa para saber mais sobre isso!", "curioso"),
            ("Esta é minha voz normal e neutra.", "neutro"),
            ("Estou frustrada com esse problema técnico.", "frustrado")
        ]
        
        print("\\n🎭 Testando diferentes emoções da SEXTA-FEIRA:")
        for text, emotion in emotions_test:
            print(f"\\n{emotion.upper()}: {text}")
            await self.speak_with_emotion(text, emotion)
            await asyncio.sleep(1)  # Pausa entre testes
        
        print("\\n✅ Teste de emoções concluído!")

    async def handle_self_modification(self, request: str) -> str:
        """Manipula pedidos de auto-modificação"""
        try:
            if self.self_modifier:
                return await self.self_modifier.handle_modification_request(request)
            else:
                return "❌ Sistema não inicializado"
        except Exception as e:
            return f"❌ Erro: {e}"

    async def set_user_name(self, name: str):
        """Define nome do usuário"""
        self.user_profile.user_info.name = name
        await self.user_profile.save_profile()
        response = f"Entendi! Agora sei que você se chama {name}."
        print(f"\\n🤖 SEXTA-FEIRA: {response}")
        await self.tts.speak(response)
    
    async def get_user_input(self) -> Optional[str]:
        """Obtém input de texto do usuário"""
        try:
            print("\\n💬 Sua mensagem:")
            
            loop = asyncio.get_event_loop()
            user_text = await loop.run_in_executor(None, input, ">>> ")
            
            if user_text.strip():
                print(f"👤 Você: {user_text}")
                await self.conversation_manager.add_message("user", user_text)
                return user_text.strip()
                
        except Exception as e:
            self.logger.error(f"Erro ao obter input: {e}")
            return None
    
    async def listen_once(self) -> Optional[str]:
        """Escuta uma vez (modo manual)"""
        text = await self.stt.listen()
        if text:
            print(f"👤 Você (voz): {text}")
            await self.conversation_manager.add_message("user", text)
        return text
    
    async def process_input(self, user_input: str) -> Optional[str]:
        """Processa entrada normal do usuário"""
        try:
            print("🧠 Processando...")
            
            # Verificar comandos de auto-modificação
            mod_commands = ["analisar código", "melhorar código", "status código", "backup código"]
            if any(cmd in user_input.lower() for cmd in mod_commands):
                return await self.handle_self_modification(user_input)
            
            await self.user_profile.extract_and_update_info(user_input)
            
            prompt = self.create_simple_prompt(user_input)
            response = await self.llm.generate_response(prompt)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao processar: {e}")
            return "Desculpe, houve um erro."
    
    def create_simple_prompt(self, user_input: str) -> str:
        """Cria prompt simples"""
        user_info = self.user_profile.get_summary()
        
        prompt = f"""Você é SEXTA-FEIRA, uma assistente pessoal amigável.

USUÁRIO: {user_info}

PERGUNTA: {user_input}

Responda de forma natural e concisa (máximo 2 frases).

RESPOSTA:"""
        
        return prompt
    
    def check_exit_command(self, text: str) -> bool:
        """Verifica comandos de saída"""
        exit_commands = ["sair", "tchau", "encerrar", "quit", "exit"]
        return any(cmd in text.lower() for cmd in exit_commands)
    
    async def shutdown(self):
        """Encerra o agente"""
        print("\\n🔄 Encerrando...")
        self.is_running = False
        
        if self.continuous_mode:
            self.stop_continuous_mode()
        
        if self.user_profile:
            await self.user_profile.save_profile()
        
        if self.database:
            await self.database.close()
        
        print("👋 Até logo!")
'''

# Salvar arquivo limpo
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(agent_clean_content)

print("✅ Agent.py recriado completamente limpo!")
print("🚀 Execute: python main.py")