# continuous_mode.py - Criar modo de escuta contínua inteligente
import os

print("🔧 Criando modo de escuta contínua inteligente...")

# 1. Atualizar speech_to_text.py para escuta contínua
stt_code = '''# core/speech_to_text.py
import asyncio
import logging
import speech_recognition as sr
import threading
import time
from typing import Optional, Callable
from config.settings import VoiceConfig

class SpeechToText:
    """Classe para reconhecimento de voz com escuta contínua"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Inicializar reconhecedor
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Estado da escuta contínua
        self.is_listening_continuously = False
        self.continuous_thread = None
        self.callback_function = None
        
        # Configurar microfone
        self.setup_microphone()
    
    def setup_microphone(self):
        """Configura o microfone"""
        try:
            with self.microphone as source:
                self.logger.info("Calibrando microfone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                # Ajustar para escuta contínua
                self.recognizer.energy_threshold = 4000
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 1.0
                self.logger.info("Microfone calibrado para escuta contínua!")
        except Exception as e:
            self.logger.error(f"Erro ao configurar microfone: {e}")
    
    async def listen(self, timeout: int = 5) -> Optional[str]:
        """Escuta uma única vez (modo manual)"""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._listen_once, timeout)
        except Exception as e:
            self.logger.error(f"Erro no reconhecimento de voz: {e}")
            return None
    
    def _listen_once(self, timeout: int) -> Optional[str]:
        """Método para escuta única"""
        try:
            print("🎤 Escutando... (fale agora)")
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            print("🔄 Processando...")
            
            try:
                text = self.recognizer.recognize_google(
                    audio, 
                    language=self.config.recognition_language
                )
                return text.strip()
            except sr.UnknownValueError:
                print("❌ Não consegui entender")
                return None
            except sr.RequestError as e:
                print("❌ Erro no serviço de reconhecimento")
                return None
                
        except sr.WaitTimeoutError:
            print("⏰ Timeout")
            return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None
    
    def start_continuous_listening(self, callback: Callable[[str], None]):
        """Inicia escuta contínua em background"""
        if self.is_listening_continuously:
            return
        
        self.callback_function = callback
        self.is_listening_continuously = True
        
        # Iniciar thread de escuta contínua
        self.continuous_thread = threading.Thread(
            target=self._continuous_listen_worker,
            daemon=True
        )
        self.continuous_thread.start()
        
        print("👂 MODO ESCUTA CONTÍNUA ATIVADO")
        print("💡 Agora estou sempre escutando... fale naturalmente!")
    
    def stop_continuous_listening(self):
        """Para escuta contínua"""
        self.is_listening_continuously = False
        if self.continuous_thread:
            self.continuous_thread.join(timeout=2)
        print("🔇 Escuta contínua desativada")
    
    def _continuous_listen_worker(self):
        """Worker thread para escuta contínua"""
        self.logger.info("Iniciando escuta contínua...")
        
        while self.is_listening_continuously:
            try:
                with self.microphone as source:
                    # Escutar com timeout curto para não bloquear
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=8)
                
                # Processar áudio em background
                try:
                    text = self.recognizer.recognize_google(
                        audio, 
                        language=self.config.recognition_language
                    )
                    
                    if text and text.strip():
                        # Chamar callback com o texto reconhecido
                        if self.callback_function:
                            self.callback_function(text.strip())
                            
                except sr.UnknownValueError:
                    # Ignorar silenciosamente quando não entender
                    pass
                except sr.RequestError:
                    # Pausar um pouco se houver erro de rede
                    time.sleep(2)
                    
            except sr.WaitTimeoutError:
                # Timeout normal, continuar escutando
                pass
            except Exception as e:
                self.logger.error(f"Erro na escuta contínua: {e}")
                time.sleep(1)
        
        self.logger.info("Escuta contínua finalizada")
'''

# 2. Criar sistema de análise inteligente de contexto
context_analyzer_code = '''# core/context_analyzer.py
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
            rf"\\b{self.agent_name}\\b",
            r"\\baria\\b",
            r"\\bassistente\\b",
            r"\\bia\\b",
            r"\\brobô\\b",
            r"\\bbot\\b",
            
            # Palavras de comando
            r"\\b(ei|hey|olá|oi)\\s+(aria|assistente|ia)\\b",
            r"\\b(me ajuda|ajude|responda|diga|fala)\\b",
            r"\\b(você pode|consegue|sabe)\\b",
            r"\\bqual.{0,20}(é|meu|seu|nome|hora|dia)\\b",
            r"\\bcomo.{0,20}(você|está|vai|fazer)\\b",
            r"\\bo que.{0,20}(você|é|faz|acha)\\b",
        ]
        
        # Padrões que sugerem menção indireta mas relevante
        self.indirect_patterns = [
            # Falando SOBRE a IA
            rf"\\b(essa|esta|a)\\s+{self.agent_name}\\b",
            r"\\b(essa|esta|a)\\s+(ia|assistente)\\b",
            r"\\bfalando.{0,10}(da|sobre).{0,10}(ia|assistente|aria)\\b",
            
            # Opiniões sobre IA
            r"\\b(ia|assistente|aria).{0,20}(é|está|foi|fica).{0,20}(ruim|boa|legal|chata|inteligente|burra)\\b",
            r"\\b(não gosto|odeio|amo|gosto).{0,20}(da|dessa).{0,20}(ia|assistente|aria)\\b",
            r"\\b(ia|assistente|aria).{0,20}(não|nunca).{0,20}(funciona|entende|responde|ajuda)\\b",
            
            # Comparações
            r"\\b(melhor|pior).{0,20}que.{0,20}(ia|assistente|aria)\\b",
            r"\\b(ia|assistente|aria).{0,20}(melhor|pior).{0,20}que\\b",
        ]
        
        # Padrões que sugerem que NÃO é para a IA
        self.ignore_patterns = [
            r"\\b(não|nem).{0,10}(fala|responde|liga).{0,10}(aria|ia|assistente)\\b",
            r"\\b(cala|silêncio|quieta).{0,10}(aria|ia|assistente)\\b",
            r"\\bestou falando com\\b",
            r"\\bnão é com você\\b",
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
            r"\\b(que horas|que dia|que data)\\b",
            r"\\b(como está|como vai|tudo bem)\\b",
            r"\\b(você|vocês).{0,20}(está|estão|vai|vão)\\b",
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, text_lower):
                # Só responder se não houver outras pessoas sendo mencionadas
                if not re.search(r"\\b(ele|ela|joão|maria|pedro|ana|fulano)\\b", text_lower):
                    return True, "Pergunta geral possivelmente direcionada", 0.5
        
        # 5. Detectar se estão falando mal da IA (para defesa)
        negative_patterns = [
            r"\\b(ia|assistente|aria).{0,30}(ruim|horrível|péssima|inútil|burra)\\b",
            r"\\b(odeio|detesto).{0,20}(ia|assistente|aria)\\b",
            r"\\b(ia|assistente|aria).{0,20}não.{0,20}(serve|funciona|presta)\\b",
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
'''

# 3. Atualizar agent.py com modo contínuo
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
from core.context_analyzer import ContextAnalyzer
from memory.user_profile import UserProfile
from memory.database import DatabaseManager
from models.local_llm import LocalLLM
from config.settings import AgentConfig

class AIAgent:
    """Classe principal do agente de IA com escuta contínua inteligente"""
    
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
        
        # Estado do agente
        self.is_listening = False
        self.is_speaking = False
        self.is_running = False
        self.continuous_mode = False
        
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
            
            # Inicializar analisador de contexto
            self.context_analyzer = ContextAnalyzer(self.config.name)
            
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
        if user_name == "usuário":
            greeting = "Olá! Sou a ARIA. Qual é o seu nome?"
        else:
            greeting = f"Olá {user_name}! Sou a ARIA, sua assistente pessoal."
        
        print(f"\\n🤖 ARIA: {greeting}")
        
        print("\\n" + "="*60)
        print("🤖 MODOS DISPONÍVEIS:")
        print("⌨️  'texto' = modo texto normal")
        print("🎤 'voz' = falar uma vez")  
        print("👂 'continuo' = ESCUTA CONTÍNUA INTELIGENTE")
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
        print("📢 Me mencione por 'ARIA' ou fale sobre mim que eu respondo")
        print("🔇 Digite 'parar' para desativar")
        print("\\n" + "="*50)
        
        # Iniciar escuta contínua
        self.stt.start_continuous_listening(self.on_continuous_speech)
        
        # Loop para comandos de texto enquanto escuta
        while self.continuous_mode and self.is_running:
            try:
                # Aguardar comando de texto (não bloqueante)
                print("\\n💬 [Comando ou 'parar' para sair do modo contínuo]:")
                
                loop = asyncio.get_event_loop()
                user_text = await asyncio.wait_for(
                    loop.run_in_executor(None, input, ">>> "),
                    timeout=1.0
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
                # Timeout normal, continuar escutando
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
            print(f"\\n👂 Ouvi: \"{text}\"")
            
            # Analisar se deve responder
            should_respond, reason, confidence = self.context_analyzer.should_respond(
                text, 
                self.user_profile.get_user_name()
            )
            
            print(f"🧠 Análise: {reason} (confiança: {confidence:.1f})")
            
            if should_respond and confidence > 0.4:
                print("🎯 Vou responder!")
                
                # Processar resposta em background
                asyncio.create_task(self.handle_continuous_response(text, reason, confidence))
            else:
                print("🤐 Não é comigo, continuando a escutar...")
                
        except Exception as e:
            self.logger.error(f"Erro no processamento contínuo: {e}")
    
    async def handle_continuous_response(self, text: str, reason: str, confidence: float):
        """Manipula resposta no modo contínuo"""
        try:
            # Salvar na conversa
            await self.conversation_manager.add_message("user", text)
            
            # Gerar resposta baseada no contexto
            response = await self.create_contextual_response(text, reason, confidence)
            
            if response:
                await self.speak(response)
                
        except Exception as e:
            self.logger.error(f"Erro na resposta contínua: {e}")
    
    async def create_contextual_response(self, text: str, reason: str, confidence: float) -> str:
        """Cria resposta baseada no contexto de detecção"""
        try:
            user_info = self.user_profile.get_summary()
            emotions = self.context_analyzer.analyze_emotional_context(text)
            dominant_emotion = max(emotions, key=emotions.get)
            
            # Prompt adaptado ao contexto
            if "defesa" in reason.lower():
                context_prompt = f"""SITUAÇÃO: O usuário fez um comentário negativo sobre você.
COMENTÁRIO: "{text}"
INSTRUÇÃO: Responda de forma educada mas se defendendo. Mostre que você é útil e está aqui para ajudar."""
            
            elif "indireta" in reason.lower():
                context_prompt = f"""SITUAÇÃO: O usuário mencionou você indiretamente em uma conversa.
COMENTÁRIO: "{text}"
INSTRUÇÃO: Responda de forma natural, como se estivesse participando da conversa."""
            
            elif confidence > 0.8:
                context_prompt = f"""SITUAÇÃO: O usuário se dirigiu diretamente a você.
PERGUNTA/COMANDO: "{text}"
INSTRUÇÃO: Responda de forma direta e útil."""
            
            else:
                context_prompt = f"""SITUAÇÃO: O usuário pode estar falando com você.
FALA: "{text}"
INSTRUÇÃO: Responda brevemente perguntando se era com você ou oferecendo ajuda."""
            
            prompt = f"""Você é ARIA, uma assistente pessoal IA amigável e inteligente.

INFORMAÇÕES DO USUÁRIO:
{user_info}

EMOÇÃO DETECTADA: {dominant_emotion}

{context_prompt}

REGRAS:
- Seja natural e conversacional
- Máximo 2 frases
- Se for defesa, seja educada mas firme
- Use o nome do usuário quando apropriado

RESPOSTA:"""
            
            response = await self.llm.generate_response(prompt)
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao criar resposta contextual: {e}")
            return "Desculpe, houve um erro interno."
    
    async def set_user_name(self, name: str):
        """Define nome do usuário"""
        self.user_profile.user_info.name = name
        await self.user_profile.save_profile()
        response = f"Entendi! Agora sei que você se chama {name}."
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
    
    async def listen_once(self) -> Optional[str]:
        """Escuta uma vez (modo manual)"""
        text = await self.stt.listen()
        if text:
            print(f"👤 Você (voz): {text}")
            await self.conversation_manager.add_message("user", text)
        return text
    
    async def speak(self, text: str):
        """Fala o texto fornecido"""
        try:
            print(f"\\n🤖 ARIA: {text}")
            await self.tts.speak(text)
            await self.conversation_manager.add_message("assistant", text)
        except Exception as e:
            self.logger.error(f"Erro na fala: {e}")
    
    async def process_input(self, user_input: str) -> Optional[str]:
        """Processa entrada normal do usuário"""
        try:
            print("🧠 Processando...")
            
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
        
        prompt = f"""Você é ARIA, uma assistente pessoal amigável.

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

# Salvar todos os arquivos
print("📝 Criando core/context_analyzer.py...")
with open("core/context_analyzer.py", "w", encoding="utf-8") as f:
    f.write(context_analyzer_code)

print("📝 Atualizando core/speech_to_text.py...")
with open("core/speech_to_text.py", "w", encoding="utf-8") as f:
    f.write(stt_code)

print("📝 Atualizando core/agent.py...")
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(agent_code)

print("✅ MODO CONTÍNUO CRIADO!")
print("")
print("🎯 FUNCIONALIDADES ADICIONADAS:")
print("• 👂 Escuta contínua em background")
print("• 🧠 Análise inteligente de contexto")
print("• 🎯 Detecção de menções diretas/indiretas") 
print("• 🛡️ Sistema de defesa quando falarem mal")
print("• 💭 Análise emocional do contexto")
print("• 🗣️ Respostas naturais baseadas na situação")
print("")
print("🚀 Execute: python main.py")
print("💡 Teste: 'continuo' para ativar modo inteligente!")
print("🗨️ Exemplos:")
print("   - 'ARIA, que horas são?' → responde")
print("   - 'essa IA é inútil' → se defende")
print("   - 'como você está?' → pergunta se é com ela")