# fix_tts.py
import os

# 1. Corrigir text_to_speech.py para evitar travamentos
print("🔧 Corrigindo sistema de TTS...")

tts_code = '''# core/text_to_speech.py
import asyncio
import logging
import pyttsx3
import pygame
import tempfile
import os
import threading
from pathlib import Path
from typing import Optional
from gtts import gTTS
from config.settings import VoiceConfig

class TextToSpeech:
    """Classe para síntese de voz"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Engine de TTS
        self.engine: Optional[pyttsx3.Engine] = None
        
        # Inicializar pygame para tocar áudio
        try:
            pygame.mixer.init()
        except:
            self.logger.warning("Pygame mixer não pôde ser inicializado")
        
        # Configurar engine
        self.setup_engine()
    
    def setup_engine(self):
        """Configura o engine de TTS"""
        try:
            if self.config.tts_engine == "pyttsx3":
                self.engine = pyttsx3.init()
                
                # Configurar propriedades
                self.engine.setProperty('rate', self.config.voice_rate)
                self.engine.setProperty('volume', self.config.voice_volume)
                
                # Tentar definir voz em português
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if 'portuguese' in voice.name.lower() or 'pt' in voice.id.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                
                self.logger.info("Engine pyttsx3 configurado com sucesso!")
                
        except Exception as e:
            self.logger.error(f"Erro ao configurar engine TTS: {e}")
            self.engine = None
    
    async def speak(self, text: str):
        """Converte texto em fala"""
        if not text.strip():
            return
        
        try:
            # SIMPLIFICADO: Usar só método síncrono com timeout
            await self._speak_simple(text)
                
        except Exception as e:
            self.logger.error(f"Erro na síntese de voz: {e}")
            print(f"[TTS Error: {e}]")
    
    async def _speak_simple(self, text: str):
        """Método simplificado de TTS"""
        try:
            if self.engine:
                # Executar em thread com timeout
                def speak_sync():
                    try:
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except Exception as e:
                        self.logger.error(f"Erro no pyttsx3: {e}")
                
                # Usar asyncio.wait_for para timeout
                loop = asyncio.get_event_loop()
                await asyncio.wait_for(
                    loop.run_in_executor(None, speak_sync),
                    timeout=10.0  # Timeout de 10 segundos
                )
            else:
                # Fallback: apenas mostrar na tela
                print(f"[FALA] {text}")
                
        except asyncio.TimeoutError:
            self.logger.warning("TTS timeout - continuando sem áudio")
            print(f"[FALA] {text}")
        except Exception as e:
            self.logger.error(f"Erro na execução do TTS: {e}")
            print(f"[FALA] {text}")
    
    def test_voice(self):
        """Testa a síntese de voz"""
        test_text = "Teste de voz funcionando!"
        
        try:
            if self.engine:
                self.engine.say(test_text)
                self.engine.runAndWait()
                print("✅ Teste de voz concluído!")
            else:
                print("⚠️ Engine TTS não disponível")
                    
        except Exception as e:
            print(f"❌ Erro no teste de voz: {e}")
    
    def get_available_voices(self) -> list:
        """Retorna lista de vozes disponíveis"""
        voices = []
        try:
            if self.engine:
                engine_voices = self.engine.getProperty('voices')
                for voice in engine_voices:
                    voices.append({
                        'id': voice.id,
                        'name': voice.name,
                        'language': getattr(voice, 'languages', ['unknown'])
                    })
        except Exception as e:
            self.logger.error(f"Erro ao obter vozes: {e}")
        
        return voices
'''

# 2. Simplificar agent.py para evitar travamentos
agent_code = '''# core/agent.py
import asyncio
import logging
import signal
import sys
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
        
        # Setup signal handler para encerramento limpo
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handler para Ctrl+C"""
        print("\\n\\n⚠️ Encerramento solicitado...")
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
        
        # Saudação inicial (sem TTS para evitar travamento)
        user_name = self.user_profile.get_user_name()
        print(f"\\n🤖 ARIA: Olá {user_name}! Sou sua assistente pessoal. Como posso ajudar?")
        
        print("\\n" + "="*60)
        print("🤖 AGENTE ATIVO - Escolha como interagir:")
        print("⌨️  Digite sua mensagem + ENTER")
        print("🎤 Digite 'voz' + ENTER para usar reconhecimento de voz")  
        print("❌ Digite 'sair' para encerrar")
        print("="*60 + "\\n")
        
        try:
            while self.is_running:
                # Aguardar input do usuário
                user_input = await self.get_user_input()
                
                if user_input:
                    # Verificar comandos especiais
                    if self.check_exit_command(user_input):
                        break
                    
                    if user_input.lower() == "voz":
                        # Modo voz
                        voice_input = await self.listen()
                        if voice_input:
                            user_input = voice_input
                        else:
                            continue
                    
                    # Processar entrada do usuário
                    response = await self.process_input(user_input)
                    
                    # Responder ao usuário
                    if response:
                        await self.speak(response)
                
        except Exception as e:
            print(f"\\n❌ Erro no loop principal: {e}")
        finally:
            await self.shutdown()
    
    async def get_user_input(self) -> Optional[str]:
        """Obtém input de texto do usuário"""
        try:
            print("\\n💬 Sua mensagem:")
            
            # Executar input em thread separada
            loop = asyncio.get_event_loop()
            user_text = await loop.run_in_executor(None, input, ">>> ")
            
            if user_text.strip():
                print(f"👤 Você: {user_text}")
                await self.conversation_manager.add_message("user", user_text)
                return user_text.strip()
                
        except Exception as e:
            self.logger.error(f"Erro ao obter input: {e}")
            return None
    
    async def listen(self) -> Optional[str]:
        """Escuta entrada de voz do usuário"""
        if self.is_listening:
            return None
            
        self.is_listening = True
        try:
            print("🎤 Escutando... (fale agora, 5 segundos)")
            
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
            
            # TTS com timeout
            try:
                await asyncio.wait_for(self.tts.speak(text), timeout=5.0)
            except asyncio.TimeoutError:
                print("[Áudio indisponível - continuando apenas com texto]")
            
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
            
            # Criar prompt personalizado
            prompt = self.create_personalized_prompt(user_input)
            
            # Gerar resposta usando o modelo local
            response = await self.llm.generate_response(prompt)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao processar entrada: {e}")
            return "Desculpe, houve um erro interno. Pode repetir por favor?"
    
    def create_personalized_prompt(self, user_input: str) -> str:
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
        
        print("👋 Até logo! Obrigada por usar a ARIA!")
        self.logger.info("Agente encerrado com sucesso!")
'''

# Salvar arquivos corrigidos
print("📝 Atualizando core/text_to_speech.py...")
with open("core/text_to_speech.py", "w", encoding="utf-8") as f:
    f.write(tts_code)

print("📝 Atualizando core/agent.py...")
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(agent_code)

print("✅ Correções aplicadas!")
print("")
print("🎯 MUDANÇAS FEITAS:")
print("• ✅ TTS com timeout para evitar travamento")
print("• ✅ Sistema assíncrono mais estável")
print("• ✅ Handler para Ctrl+C")
print("• ✅ Fallback para texto se áudio falhar")
print("• ✅ Interface simplificada")
print("")
print("🚀 Execute: python main.py")
print("💡 Agora deve funcionar sem travar!")