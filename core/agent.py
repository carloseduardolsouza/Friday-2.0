# core/agent.py
import asyncio
import logging
import signal
import sys
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any

from core.speech_to_text import SpeechToText
from core.text_to_speech import HumanizedTTS
from core.conversation import ConversationManager
from core.context_analyzer import ContextAnalyzer
from memory.user_profile import UserProfile
from memory.database import DatabaseManager
from models.local_llm import LocalLLM
from config.settings import AgentConfig
from core.self_modifier import SelfModifier
from core.command_executor import InternalCommandExecutor

class AIAgent:
    """Classe principal do agente de IA SEXTA-FEIRA com todas as funcionalidades"""
    
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
        
        # Sistemas avançados
        self.self_modifier: Optional[SelfModifier] = None
        self.command_executor: Optional[InternalCommandExecutor] = None
        
        # Estado do agente
        self.is_listening = False
        self.is_speaking = False
        self.is_running = False
        self.continuous_mode = False
        
        # Loop assíncrono e monitoramento
        self.main_loop = None
        self._last_audio_check = time.time()
        
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
            self.tts = HumanizedTTS(self.config.voice)
            
            # Inicializar analisador de contexto
            self.context_analyzer = ContextAnalyzer(self.config.name)
            
            # Inicializar gerenciador de conversas
            self.conversation_manager = ConversationManager(
                self.database, 
                self.user_profile,
                self.config
            )
            
            # Inicializar sistemas avançados
            self.self_modifier = SelfModifier(self.llm, self.user_profile)
            self.command_executor = InternalCommandExecutor(self)
            
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
        
        print(f"\n🤖 SEXTA-FEIRA: {greeting}")
        
        print("\n" + "="*70)
        print("🤖 FUNCIONALIDADES DISPONÍVEIS:")
        print("⌨️  Digite normalmente para conversar")
        print("🎤 'voz' = usar reconhecimento de voz uma vez")  
        print("👂 'continuo' = MODO ESCUTA CONTÍNUA INTELIGENTE")
        print("🔧 'analise seu código' = AUTO-ANÁLISE DO PRÓPRIO CÓDIGO")
        print("🎭 'teste sua voz' = DEMONSTRAR EMOÇÕES DE VOZ")
        print("💾 'faça um backup' = BACKUP AUTOMÁTICO DO CÓDIGO")
        print("📊 'como você está' = RELATÓRIO COMPLETO DE STATUS")
        print("🚀 'se melhore' = AUTO-MELHORIA DO CÓDIGO")
        print("❌ 'sair' = encerrar")
        print("=" * 70 + "\n")
        
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
                        elif user_input.lower().startswith("nome "):
                            name = user_input[5:].strip()
                            await self.set_user_name(name)
                            continue
                        
                        response = await self.process_input(user_input)
                        if response:
                            await self.speak_robust(response)
                else:
                    # Modo contínuo ativo - monitoramento de áudio
                    await self.handle_audio_monitoring()
                    await asyncio.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n⚠️ Encerrando...")
        finally:
            await self.shutdown()
    
    async def handle_audio_monitoring(self):
        """Monitora saúde do áudio no modo contínuo"""
        try:
            current_time = time.time()
            
            # Verificar áudio a cada 3 minutos
            if current_time - self._last_audio_check > 180:
                self._last_audio_check = current_time
                
                # Testar sistema de áudio se disponível
                if hasattr(self.tts, 'test_audio_system'):
                    if not self.tts.test_audio_system():
                        print("🔄 Problema de áudio detectado, resetando...")
                        if hasattr(self.tts, 'reset_audio_system'):
                            self.tts.reset_audio_system()
                        
        except Exception as e:
            self.logger.error(f"Erro no monitoramento de áudio: {e}")
    
    async def start_continuous_mode(self):
        """Inicia modo de escuta contínua inteligente"""
        self.continuous_mode = True
        
        await self.speak_robust("Ativando modo de escuta contínua inteligente!")
        
        print("\n👂 MODO CONTÍNUO ATIVADO!")
        print("💡 Agora estou sempre escutando... fale naturalmente!")
        print("📢 Me mencione por 'SEXTA-FEIRA' ou fale sobre mim que eu respondo")
        print("🎯 Comandos funcionam normalmente: 'analise seu código', 'teste sua voz', etc.")
        print("🔇 Digite 'parar' para desativar")
        print("\n" + "="*60)
        
        # Iniciar escuta contínua
        self.stt.start_continuous_listening(self.on_continuous_speech)
        
        # Loop para comandos de texto enquanto escuta
        while self.continuous_mode and self.is_running:
            try:
                print("\n💬 [Digite 'parar' para sair do modo contínuo]:")
                
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
                        await self.speak_robust(response)
                        
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Erro no modo contínuo: {e}")
                break
    
    def stop_continuous_mode(self):
        """Para modo contínuo"""
        self.continuous_mode = False
        self.stt.stop_continuous_listening()
        print("\n🔇 Modo contínuo desativado")
        print("💬 Voltando ao modo normal...")
    
    def on_continuous_speech(self, text: str):
        """Callback chamado quando detecta fala no modo contínuo"""
        try:
            print(f"\n👂 Ouvi: '{text}'")
            
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
                await self.speak_robust(response)
        except Exception as e:
            self.logger.error(f"Erro na resposta contínua: {e}")
            await self.speak_robust("Desculpe, houve um erro interno.")
    
    async def speak_with_emotion(self, text: str, emotion: str = "neutro"):
        """Fala com emoção específica"""
        try:
            print(f"\n🤖 SEXTA-FEIRA ({emotion}): {text}")
            await self.tts.speak(text, emotion)
            await self.conversation_manager.add_message("assistant", text)
        except Exception as e:
            self.logger.error(f"Erro na fala emocional: {e}")
            print(f"⚠️ [ERRO DE ÁUDIO] {text}")

    async def speak_robust(self, text: str, emotion: str = "neutro"):
        """Fala robusta com retry automático e fallback"""
        await self.speak_with_emotion(text, emotion)

    async def create_contextual_response(self, text: str, reason: str, confidence: float) -> str:
        """Cria resposta baseada no contexto"""
        try:
            user_info = self.user_profile.get_summary()
            emotions = self.context_analyzer.analyze_emotional_context(text)
            dominant_emotion = max(emotions, key=emotions.get)
            
            # Contexto baseado em como foi detectada
            if "SEXTA-FEIRA detectado" in reason or "Nome SEXTA-FEIRA detectado" in reason:
                context_prompt = f"""SITUAÇÃO: O usuário me chamou pelo meu nome 'SEXTA-FEIRA'.
ENTRADA: "{text}"
INSTRUÇÃO: Responda de forma calorosa e engajada, reconhecendo que me chamaram."""
            
            elif "Referência direta detectada" in reason:
                context_prompt = f"""SITUAÇÃO: O usuário fez uma pergunta direta para mim.
PERGUNTA: "{text}"
INSTRUÇÃO: Responda de forma direta e útil."""
            
            elif confidence > 0.8:
                context_prompt = f"""SITUAÇÃO: O usuário se dirigiu diretamente a mim.
ENTRADA: "{text}"
INSTRUÇÃO: Responda de forma direta e útil."""
            
            else:
                context_prompt = f"""SITUAÇÃO: O usuário pode estar falando comigo.
FALA: "{text}"
INSTRUÇÃO: Responda brevemente oferecendo ajuda."""
            
            prompt = f"""Você é SEXTA-FEIRA, uma assistente pessoal IA amigável e inteligente.

USUÁRIO: {user_info}
EMOÇÃO: {dominant_emotion}

{context_prompt}

Responda de forma natural e concisa (máximo 2-3 frases).

RESPOSTA:"""
            
            response = await self.llm.generate_response(prompt)
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao criar resposta contextual: {e}")
            return "Oi! Sou a SEXTA-FEIRA. Estou aqui se precisar de alguma coisa."

    async def test_voice_quality(self):
        """Testa qualidade das vozes disponíveis"""
        print("🎭 Testando qualidade das vozes...")
        
        # Mostrar engines disponíveis
        if hasattr(self.tts, 'get_available_engines'):
            available_engines = self.tts.get_available_engines()
            print("🔊 Engines disponíveis:")
            for engine in available_engines:
                print(f"   • {engine}")
        
        # Testar qualidade
        if hasattr(self.tts, 'test_voice_quality'):
            self.tts.test_voice_quality()
        
        print("\n✅ Teste de qualidade concluído!")

    async def test_voice_emotions(self):
        """Testa diferentes emoções da voz"""
        emotions_test = [
            ("Olá! Esta é minha voz feliz e animada!", "feliz"),
            ("Estou um pouco triste com essa notícia...", "triste"),
            ("Estou muito curiosa para saber mais sobre isso!", "curioso"),
            ("Esta é minha voz normal e neutra.", "neutro"),
            ("Estou frustrada com esse problema técnico.", "frustrado")
        ]
        
        await self.speak_robust("Vou demonstrar minhas diferentes emoções!", "feliz")
        
        print("\n🎭 Testando diferentes emoções da SEXTA-FEIRA:")
        for text, emotion in emotions_test:
            print(f"\n{emotion.upper()}: {text}")
            await self.speak_robust(text, emotion)
            await asyncio.sleep(1.5)
        
        await self.speak_robust("Demonstração de emoções concluída!", "feliz")
        print("\n✅ Teste de emoções concluído!")

    async def set_user_name(self, name: str):
        """Define nome do usuário"""
        self.user_profile.user_info.name = name
        await self.user_profile.save_profile()
        response = f"Entendi! Agora sei que você se chama {name}."
        await self.speak_robust(response, "feliz")
    
    async def get_user_input(self) -> Optional[str]:
        """Obtém input de texto do usuário"""
        try:
            print("\n💬 Sua mensagem:")
            
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
            
            # PRIMEIRO: Verificar comandos internos (com resposta falada)
            if self.command_executor:
                internal_response = await self.command_executor.process_natural_command(user_input)
                if internal_response:
                    return internal_response
            
            # SEGUNDO: Verificar comandos de auto-modificação diretos
            mod_commands = [
                "analisar código", "analise seu código", "verifica seu código",
                "melhorar código", "melhore seu código", "otimize seu código", 
                "status código", "como está seu código",
                "backup código", "faça backup", "crie backup",
                "teste sua voz", "teste de voz", "demonstre emoções",
                "como você está", "qual seu status", "relatório completo"
            ]
            
            if any(cmd in user_input.lower() for cmd in mod_commands):
                if self.self_modifier:
                    return await self.self_modifier.handle_modification_request(user_input)
            
            # TERCEIRO: Processar como conversa normal
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
        
        prompt = f"""Você é SEXTA-FEIRA, uma assistente pessoal amigável e inteligente.

USUÁRIO: {user_info}

PERGUNTA: {user_input}

Responda de forma natural e concisa (máximo 2-3 frases).

RESPOSTA:"""
        
        return prompt
    
    def check_exit_command(self, text: str) -> bool:
        """Verifica comandos de saída"""
        exit_commands = ["sair", "tchau", "encerrar", "quit", "exit"]
        return any(cmd in text.lower() for cmd in exit_commands)
    
    async def shutdown(self):
        """Encerra o agente"""
        print("\n🔄 Encerrando...")
        self.is_running = False
        
        if self.continuous_mode:
            self.stop_continuous_mode()
        
        if self.user_profile:
            await self.user_profile.save_profile()
        
        if self.database:
            await self.database.close()
        
        await self.speak_robust("Até logo! Foi um prazer ajudá-lo.", "feliz")
        print("👋 SEXTA-FEIRA encerrada!")
