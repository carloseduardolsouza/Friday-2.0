# core/text_to_speech.py
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
