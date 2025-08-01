# fix_all_issues.py
import os

print("🔧 Corrigindo todos os problemas...")

# 1. Corrigir speech_to_text.py - Problema com Whisper
stt_code = '''# core/speech_to_text.py
import asyncio
import logging
import speech_recognition as sr
import tempfile
import os
from typing import Optional
from config.settings import VoiceConfig

class SpeechToText:
    """Classe para reconhecimento de voz"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Inicializar reconhecedor
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Configurar microfone
        self.setup_microphone()
    
    def setup_microphone(self):
        """Configura o microfone"""
        try:
            with self.microphone as source:
                self.logger.info("Calibrando microfone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.logger.info("Microfone calibrado!")
        except Exception as e:
            self.logger.error(f"Erro ao configurar microfone: {e}")
    
    async def listen(self, timeout: int = 5) -> Optional[str]:
        """Escuta e converte fala em texto"""
        try:
            # Executar em thread separada para não bloquear
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._listen_sync, timeout)
        except Exception as e:
            self.logger.error(f"Erro no reconhecimento de voz: {e}")
            return None
    
    def _listen_sync(self, timeout: int) -> Optional[str]:
        """Método síncrono para escutar"""
        try:
            print("🎤 Escutando... (fale agora)")
            
            # Capturar áudio
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            print("🔄 Processando...")
            
            # SIMPLIFICADO: Usar apenas Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(
                    audio, 
                    language=self.config.recognition_language
                )
                return text.strip()
            except sr.UnknownValueError:
                print("❌ Não consegui entender o que foi dito")
                return None
            except sr.RequestError as e:
                self.logger.error(f"Erro no serviço de reconhecimento: {e}")
                print("❌ Erro no serviço de reconhecimento (verifique internet)")
                return None
                
        except sr.WaitTimeoutError:
            print("⏰ Timeout - nenhuma fala detectada")
            return None
        except Exception as e:
            self.logger.error(f"Erro inesperado no reconhecimento: {e}")
            print(f"❌ Erro no reconhecimento: {e}")
            return None
'''

# 2. Corrigir text_to_speech.py - Problema com pyttsx3
tts_code = '''# core/text_to_speech.py
import asyncio
import logging
import pyttsx3
import threading
from typing import Optional
from config.settings import VoiceConfig

class TextToSpeech:
    """Classe para síntese de voz"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Engine de TTS (criar novo para cada uso)
        self.engine_lock = threading.Lock()
        
    def _get_engine(self):
        """Cria um novo engine TTS"""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', self.config.voice_rate)
            engine.setProperty('volume', self.config.voice_volume)
            
            # Tentar definir voz em português
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'portuguese' in voice.name.lower() or 'pt' in voice.id.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            return engine
        except Exception as e:
            self.logger.error(f"Erro ao criar engine TTS: {e}")
            return None
    
    async def speak(self, text: str):
        """Converte texto em fala"""
        if not text.strip():
            return
        
        try:
            # Executar TTS em thread separada com engine próprio
            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.run_in_executor(None, self._speak_sync, text),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            self.logger.warning("TTS timeout")
            print("[Áudio indisponível]")
        except Exception as e:
            self.logger.error(f"Erro na síntese de voz: {e}")
            print(f"[TTS Error: {e}]")
    
    def _speak_sync(self, text: str):
        """Método síncrono para TTS"""
        with self.engine_lock:
            try:
                # Criar novo engine para cada fala
                engine = self._get_engine()
                if engine:
                    engine.say(text)
                    engine.runAndWait()
                    # Limpar engine
                    engine.stop()
                    del engine
                else:
                    print(f"[FALA] {text}")
            except Exception as e:
                self.logger.error(f"Erro no TTS sync: {e}")
                print(f"[FALA] {text}")
'''

# 3. Corrigir agent.py - Melhorar prompts e fluxo
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
        greeting = f"Olá {user_name}! Sou a ARIA, sua assistente pessoal."
        print(f"\\n🤖 ARIA: {greeting}")
        
        print("\\n" + "="*50)
        print("🤖 COMANDOS DISPONÍVEIS:")
        print("• Digite sua mensagem + ENTER")
        print("• 'voz' = usar microfone")  
        print("• 'nome João' = definir seu nome")
        print("• 'sair' = encerrar")
        print("="*50 + "\\n")
        
        try:
            while self.is_running:
                user_input = await self.get_user_input()
                
                if user_input:
                    if self.check_exit_command(user_input):
                        break
                    
                    if user_input.lower() == "voz":
                        voice_input = await self.listen()
                        if voice_input:
                            user_input = voice_input
                        else:
                            continue
                    
                    # Comandos especiais
                    if user_input.lower().startswith("nome "):
                        name = user_input[5:].strip()
                        await self.set_user_name(name)
                        continue
                    
                    response = await self.process_input(user_input)
                    if response:
                        await self.speak(response)
                
        except Exception as e:
            print(f"\\n❌ Erro: {e}")
        finally:
            await self.shutdown()
    
    async def set_user_name(self, name: str):
        """Define nome do usuário"""
        self.user_profile.user_info.name = name
        await self.user_profile.save_profile()
        response = f"Entendi! Agora sei que você se chama {name}. Prazer em conhecê-lo!"
        print(f"\\n🤖 ARIA: {response}")
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
    
    async def listen(self) -> Optional[str]:
        """Escuta entrada de voz do usuário"""
        if self.is_listening:
            return None
            
        self.is_listening = True
        try:
            text = await self.stt.listen()
            if text:
                print(f"👤 Você (voz): {text}")
                await self.conversation_manager.add_message("user", text)
            return text
        except Exception as e:
            self.logger.error(f"Erro no reconhecimento: {e}")
            return None
        finally:
            self.is_listening = False
    
    async def speak(self, text: str):
        """Fala o texto fornecido"""
        try:
            print(f"\\n🤖 ARIA: {text}")
            await self.tts.speak(text)
            await self.conversation_manager.add_message("assistant", text)
        except Exception as e:
            self.logger.error(f"Erro na fala: {e}")
    
    async def process_input(self, user_input: str) -> Optional[str]:
        """Processa a entrada do usuário"""
        try:
            print("🧠 Processando...")
            
            # Extrair informações do usuário
            await self.user_profile.extract_and_update_info(user_input)
            
            # Criar prompt melhorado
            prompt = self.create_simple_prompt(user_input)
            
            # Gerar resposta
            response = await self.llm.generate_response(prompt)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao processar: {e}")
            return "Desculpe, houve um erro. Pode repetir?"
    
    def create_simple_prompt(self, user_input: str) -> str:
        """Cria prompt simples e direto"""
        user_info = self.user_profile.get_summary()
        
        if "Nenhuma informação" in user_info:
            user_context = "Usuário ainda não compartilhou informações pessoais."
        else:
            user_context = user_info
        
        prompt = f"""Você é ARIA, uma assistente pessoal amigável.

CONTEXTO DO USUÁRIO:
{user_context}

PERGUNTA/MENSAGEM DO USUÁRIO:
{user_input}

INSTRUÇÕES:
- Responda de forma natural e amigável
- Seja concisa (1-2 frases)
- Se o usuário perguntar sobre seu nome, diga que não sabe ainda
- Se ele disser o nome dele, reconheça e lembre-se

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
        
        if self.user_profile:
            await self.user_profile.save_profile()
        
        if self.database:
            await self.database.close()
        
        print("👋 Até logo!")
'''

# Salvar correções
print("📝 Corrigindo speech_to_text.py...")
with open("core/speech_to_text.py", "w", encoding="utf-8") as f:
    f.write(stt_code)

print("📝 Corrigindo text_to_speech.py...")
with open("core/text_to_speech.py", "w", encoding="utf-8") as f:
    f.write(tts_code)

print("📝 Corrigindo agent.py...")
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(agent_code)

print("✅ Todas as correções aplicadas!")
print("")
print("🎯 PROBLEMAS CORRIGIDOS:")
print("• ✅ Whisper removido (só Google Speech)")
print("• ✅ TTS com engine dedicado por thread")
print("• ✅ Prompts mais simples e diretos")
print("• ✅ Comando 'nome João' para definir nome")
print("• ✅ Interface mais clara")
print("")
print("🚀 Execute: python main.py")
print("💡 Teste com: 'nome João' e depois 'qual o meu nome?'")