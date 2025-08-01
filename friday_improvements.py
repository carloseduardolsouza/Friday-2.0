# friday_improvements.py
import os

print("🔧 Melhorando reconhecimento de nome e voz da SEXTA-FEIRA...")

# 1. Atualizar context_analyzer.py com melhor reconhecimento do nome
context_analyzer_improved = '''# core/context_analyzer.py
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
            r"\\bsexta.feira\\b",
            r"\\bsexta\\s+feira\\b", 
            r"\\bsextafeira\\b",
            r"\\bsexta\\b(?!.*feira\\s+que)",  # "sexta" mas não "sexta-feira que vem"
            
            # Variações em inglês
            r"\\bfriday\\b",
            
            # Com saudações
            r"\\b(ei|oi|olá|hey)\\s+(sexta|friday)\\b",
            r"\\b(oi|olá)\\s+sexta.feira\\b",
            
            # Com títulos
            r"\\b(assistente|ia)\\s+sexta\\b",
            r"\\bminha\\s+sexta\\b",
            
            # Formas carinhosas
            r"\\bsextinha\\b",
            r"\\bfri\\b",
        ]
        
        # Padrões para quando ela SABE que é sobre ela
        self.self_reference_patterns = [
            # Quando perguntam sobre ela especificamente
            r"\\b(qual|como)\\s+(é\\s+)?o\\s+seu\\s+nome\\b",
            r"\\b(quem|o\\s+que)\\s+(é\\s+)?você\\b",
            r"\\bcomo\\s+você\\s+se\\s+chama\\b",
            r"\\bvocê\\s+é\\s+(a\\s+)?sexta\\b",
            r"\\bseu\\s+nome\\s+é\\s+sexta\\b",
            
            # Referências diretas a ela
            r"\\bvocê\\s+(é|está|pode|consegue|sabe)\\b",
            r"\\bme\\s+(ajuda|diga|fala|conte)\\b",
            r"\\b(pode|consegue)\\s+me\\s+ajudar\\b",
            
            # Comandos diretos
            r"\\b(responda|diga|fale|conte|explique)\\b",
            r"\\b(qual|como|quando|onde|por\\s+que)\\b.*\\?",
        ]
        
        # Padrões que NÃO são sobre sexta-feira (contexto temporal)
        self.temporal_friday_patterns = [
            r"\\bsexta.feira\\s+(passada|que\\s+vem|próxima|retrasada)\\b",
            r"\\bna\\s+sexta\\b",
            r"\\bessa\\s+sexta\\s+(feira\\s+)?(vai|vou|tem)\\b",
            r"\\bnesta\\s+sexta\\b",
            r"\\bsexta.feira\\s+à\\s+(noite|tarde|manhã)\\b",
            r"\\btoda\\s+sexta\\b",
        ]
        
        # Padrões de desativação
        self.deactivation_patterns = [
            r"\\bmudo\\b",
            r"\\bsilêncio\\b",
            r"\\bquieta\\b",
            r"\\bpara\\s+de\\s+(escutar|falar|responder)\\b",
            r"\\bnão\\s+(fale|responda|escute)\\b",
            r"\\bmodo\\s+silencioso\\b",
            r"\\bfique\\s+(quieta|calada)\\b",
            r"\\bchega\\s+(de\\s+)?conversa\\b",
        ]
        
        # Padrões indiretos (falando SOBRE a sexta-feira)
        self.indirect_patterns = [
            rf"\\b(essa|esta|a)\\s+(sexta|assistente|ia)\\b",
            r"\\bfalando.{0,15}(da|sobre|com).{0,15}(sexta|assistente)\\b",
            
            # Opiniões sobre ela
            r"\\b(sexta|assistente).{0,30}(é|está|foi|fica).{0,30}(ruim|boa|legal|chata|inteligente|útil)\\b",
            r"\\b(gosto|não\\s+gosto|amo|odeio).{0,20}(da|dessa).{0,20}(sexta|assistente)\\b",
            r"\\ba\\s+(sexta|assistente).{0,20}(me\\s+)?(ajuda|entende|sabe)\\b",
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
            r"\\b(sexta|assistente|ia).{0,30}(ruim|horrível|péssima|inútil|burra|idiota)\\b",
            r"\\b(odeio|detesto|não\\s+gosto).{0,20}(da|dessa).{0,20}(sexta|assistente)\\b",
            r"\\b(sexta|assistente).{0,20}(não|nunca).{0,20}(funciona|entende|ajuda|serve)\\b",
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
'''

# 2. Atualizar text_to_speech.py para voz mais humanizada
tts_humanized = '''# core/text_to_speech.py
import asyncio
import logging
import pyttsx3
import threading
import random
from typing import Optional
from config.settings import VoiceConfig

class TextToSpeech:
    """Classe para síntese de voz humanizada"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Engine de TTS (criar novo para cada uso)
        self.engine_lock = threading.Lock()
        
        # Configurações de voz humanizada
        self.emotion_adjustments = {
            "feliz": {"rate": 210, "volume": 0.95},
            "triste": {"rate": 170, "volume": 0.8},
            "raiva": {"rate": 230, "volume": 1.0},
            "curioso": {"rate": 200, "volume": 0.9},
            "neutro": {"rate": 200, "volume": 0.9},
            "frustrado": {"rate": 180, "volume": 0.85}
        }
        
        # Pausas naturais para humanizar
        self.natural_pauses = [
            ("...", 0.8),
            (".", 0.5),
            (",", 0.3),
            ("!", 0.4),
            ("?", 0.6),
            (";", 0.4)
        ]
        
    def _get_engine(self, emotion="neutro"):
        """Cria um novo engine TTS otimizado para emoção"""
        try:
            engine = pyttsx3.init()
            
            # Configurações baseadas na emoção
            emotion_config = self.emotion_adjustments.get(emotion, self.emotion_adjustments["neutro"])
            
            engine.setProperty('rate', emotion_config["rate"])
            engine.setProperty('volume', emotion_config["volume"])
            
            # Tentar encontrar voz feminina em português
            voices = engine.getProperty('voices')
            
            # Prioridade: voz feminina em português
            female_pt_voice = None
            any_pt_voice = None
            female_voice = None
            
            for voice in voices:
                voice_name = voice.name.lower()
                voice_id = voice.id.lower()
                
                # Detectar voz feminina em português
                if any(keyword in voice_name for keyword in ['portuguese', 'brasil', 'pt', 'br']):
                    any_pt_voice = voice.id
                    if any(keyword in voice_name for keyword in ['female', 'feminina', 'maria', 'helena', 'ana']):
                        female_pt_voice = voice.id
                        break
                
                # Detectar qualquer voz feminina
                elif any(keyword in voice_name for keyword in ['female', 'woman', 'zira', 'helena', 'maria']):
                    female_voice = voice.id
            
            # Escolher a melhor voz disponível
            if female_pt_voice:
                engine.setProperty('voice', female_pt_voice)
                self.logger.info(f"Usando voz feminina em português")
            elif any_pt_voice:
                engine.setProperty('voice', any_pt_voice)
                self.logger.info(f"Usando voz em português")
            elif female_voice:
                engine.setProperty('voice', female_voice)
                self.logger.info(f"Usando voz feminina")
            
            return engine
            
        except Exception as e:
            self.logger.error(f"Erro ao criar engine TTS: {e}")
            return None
    
    async def speak(self, text: str, emotion="neutro"):
        """Converte texto em fala humanizada"""
        if not text.strip():
            return
        
        try:
            # Processar texto para soar mais natural
            processed_text = self._humanize_text(text)
            
            # Executar TTS em thread separada
            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.run_in_executor(None, self._speak_sync, processed_text, emotion),
                timeout=15.0
            )
        except asyncio.TimeoutError:
            self.logger.warning("TTS timeout")
            print("[Áudio indisponível]")
        except Exception as e:
            self.logger.error(f"Erro na síntese de voz: {e}")
            print(f"[TTS Error: {e}]")
    
    def _humanize_text(self, text: str) -> str:
        """Torna o texto mais natural para fala"""
        
        # Substituições para soar mais natural
        replacements = {
            # Abreviações
            "Dr.": "Doutor",
            "Dra.": "Doutora", 
            "Sr.": "Senhor",
            "Sra.": "Senhora",
            "etc.": "etcetera",
            "ex:": "por exemplo:",
            
            # Números
            "1º": "primeiro",
            "2º": "segundo", 
            "3º": "terceiro",
            "1ª": "primeira",
            "2ª": "segunda",
            "3ª": "terceira",
            
            # Símbolos
            "&": "e",
            "%": "por cento",
            "@": "arroba",
            "#": "hashtag",
            
            # Expressões técnicas
            "IA": "Inteligência Artificial",
            "AI": "Inteligência Artificial",
            "TTS": "síntese de voz",
            "CPU": "processador",
            "RAM": "memória",
            
            # Melhorar fluidez
            "SEXTA-FEIRA": "Sexta feira",  # Para pronunciar melhor
            "sexta-feira": "sexta feira",   # Para evitar hífen na fala
        }
        
        processed = text
        for old, new in replacements.items():
            processed = processed.replace(old, new)
        
        # Adicionar pausas naturais em pontuações
        for punct, pause in self.natural_pauses:
            if punct in processed:
                processed = processed.replace(punct, f"{punct} ")
        
        # Evitar repetições de palavras (soar mais natural)
        words = processed.split()
        natural_words = []
        last_word = ""
        
        for word in words:
            if word.lower() != last_word.lower() or len(natural_words) == 0:
                natural_words.append(word)
                last_word = word
            else:
                # Substituir repetição por sinônimo ou omitir
                natural_words.append("")  # Omitir repetição
        
        return " ".join(filter(None, natural_words))
    
    def _speak_sync(self, text: str, emotion: str):
        """Método síncrono para TTS com emoção"""
        with self.engine_lock:
            try:
                # Criar engine específico para a emoção
                engine = self._get_engine(emotion)
                
                if engine:
                    # Adicionar variação natural na velocidade (mais humano)
                    base_rate = self.emotion_adjustments[emotion]["rate"]
                    variation = random.randint(-10, 10)
                    engine.setProperty('rate', base_rate + variation)
                    
                    # Falar o texto
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
    
    def test_voice(self):
        """Testa a síntese de voz com diferentes emoções"""
        test_phrases = [
            ("Olá! Sou a Sexta feira, sua assistente pessoal.", "feliz"),
            ("Lamento que esteja chateado.", "triste"),
            ("Vou ajudá-lo com isso agora!", "curioso"),
            ("Entendi perfeitamente.", "neutro")
        ]
        
        for phrase, emotion in test_phrases:
            print(f"Testando emoção {emotion}: {phrase}")
            try:
                self._speak_sync(phrase, emotion)
            except Exception as e:
                print(f"Erro no teste: {e}")
    
    def get_available_voices(self) -> list:
        """Retorna lista de vozes disponíveis"""
        voices = []
        try:
            engine = pyttsx3.init()
            engine_voices = engine.getProperty('voices')
            for voice in engine_voices:
                voices.append({
                    'id': voice.id,
                    'name': voice.name,
                    'language': getattr(voice, 'languages', ['unknown'])
                })
            engine.stop()
        except Exception as e:
            self.logger.error(f"Erro ao obter vozes: {e}")
        
        return voices
'''

# 3. Atualizar agent.py para usar as melhorias
agent_improvements = '''
# Adicionar no método create_contextual_response do agent.py
# (substituir o método existente)

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

async def speak_with_emotion(self, text: str, emotion: str = "neutro"):
    """Fala com emoção específica"""
    try:
        print(f"\\n🤖 SEXTA-FEIRA: {text}")
        await self.tts.speak(text, emotion)
    except Exception as e:
        self.logger.error(f"Erro na fala emocional: {e}")
'''

# Salvar arquivos
print("📝 Atualizando core/context_analyzer.py...")
with open("core/context_analyzer.py", "w", encoding="utf-8") as f:
    f.write(context_analyzer_improved)

print("📝 Atualizando core/text_to_speech.py...")
with open("core/text_to_speech.py", "w", encoding="utf-8") as f:
    f.write(tts_humanized)

print("📝 Criando instruções de atualização do agent.py...")
with open("agent_voice_instructions.txt", "w", encoding="utf-8") as f:
    f.write("""INSTRUÇÕES PARA ATUALIZAR AGENT.PY:

1. No método create_contextual_response, substitua por:
   [código fornecido no agent_improvements]

2. Adicione o método speak_with_emotion:
   [código fornecido no agent_improvements]

3. No método speak, substitua por:
   await self.speak_with_emotion(text, "neutro")

Isso melhorará o reconhecimento do nome SEXTA-FEIRA e adicionará voz emocional.
""")

print("✅ Melhorias implementadas!")
print("")
print("🎯 MELHORIAS APLICADAS:")
print("• 🎯 Reconhecimento MUITO melhor do nome 'SEXTA-FEIRA'")
print("• 🚫 Filtro para sexta-feira do calendário (não responde)")
print("• 🎭 Voz com emoções (feliz, triste, curioso, etc.)")
print("• 🔊 Voz feminina em português quando disponível") 
print("• 💬 Texto humanizado (pausas naturais, pronuncia melhor)")
print("• 🎚️ Velocidade da voz varia com emoção")
print("")
print("🚀 Execute: python main.py")
print("")
print("💡 TESTE MELHORADO:")
print("✅ 'sexta-feira' → Reconhece como nome")
print("✅ 'oi sexta' → Reconhece como nome") 
print("✅ 'sexta' → Reconhece como nome")
print("❌ 'nesta sexta-feira' → NÃO reconhece (calendário)")
print("❌ 'sexta-feira que vem' → NÃO reconhece (calendário)")
print("")
print("🎭 EMOÇÕES DA VOZ:")
print("• Feliz: velocidade alta, volume alto")
print("• Triste: velocidade baixa, volume baixo") 
print("• Curioso: velocidade normal, tom questionador")
print("• Neutro: configuração padrão")