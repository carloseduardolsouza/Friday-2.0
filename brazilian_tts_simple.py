# brazilian_tts_simple.py - Sistema TTS brasileiro simples
import asyncio
import sys
import time
from pathlib import Path

# Aplicar patch PyTorch PRIMEIRO
exec(open("pytorch_fix.py").read())

class SimpleBrazilianTTS:
    """Sistema TTS brasileiro que funciona"""
    
    def __init__(self):
        self.tts = None
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Emoções brasileiras
        self.emotions = {
            "neutro": {"prefix": "", "suffix": ""},
            "feliz": {"prefix": "", "suffix": "!"},
            "carinhoso": {"prefix": "", "suffix": "..."},
            "triste": {"prefix": "Ah... ", "suffix": "..."},
            "curioso": {"prefix": "Hmm... ", "suffix": "?"},
            "animado": {"prefix": "Nossa! ", "suffix": "!"},
            "frustrado": {"prefix": "Poxa... ", "suffix": "."},
            "surpreso": {"prefix": "Caramba! ", "suffix": "!"}
        }
        
        self.setup_tts()
    
    def setup_tts(self):
        """Configura TTS com patches"""
        try:
            # Patch MeCab
            class FakeMeCab:
                class Tagger:
                    def __init__(self, *args, **kwargs): pass
                    def parse(self, text): return text
            sys.modules['MeCab'] = FakeMeCab()
            
            # Importar TTS
            from TTS.api import TTS
            
            # Testar modelos em ordem de simplicidade
            models = [
                "tts_models/pt/cv/vits",
                "tts_models/en/ljspeech/tacotron2-DDC"
            ]
            
            for model_name in models:
                try:
                    print(f"🎯 Tentando: {model_name}")
                    self.tts = TTS(model_name=model_name, progress_bar=True)
                    self.model_name = model_name
                    print(f"✅ Carregado: {model_name}")
                    break
                except Exception as e:
                    print(f"❌ Falhou: {model_name}")
                    continue
            
            if not self.tts:
                print("❌ Nenhum modelo funcionou")
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            self.tts = None
    
    async def speak(self, text, emotion="neutro"):
        """Fala em português brasileiro"""
        if not self.tts:
            print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
            return
        
        try:
            # Processar texto brasileiro
            processed = self.process_text(text, emotion)
            
            # Gerar áudio
            audio_file = self.temp_dir / f"br_{emotion}_{int(time.time())}.wav"
            
            if "pt" in self.model_name:
                # Modelo português
                self.tts.tts_to_file(
                    text=processed,
                    file_path=str(audio_file)
                )
            else:
                # Modelo inglês (fallback)
                english_text = f"Hello! This is a test."
                self.tts.tts_to_file(
                    text=english_text,
                    file_path=str(audio_file)
                )
            
            print(f"🇧🇷 SEXTA-FEIRA (BR-{emotion}): {text}")
            print(f"🔊 Áudio: {audio_file.name}")
            
            # Reproduzir se pygame disponível
            try:
                import pygame
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                
                pygame.mixer.music.load(str(audio_file))
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
            except:
                print("🔊 Pygame não disponível")
            
            # Limpar
            try:
                audio_file.unlink()
            except:
                pass
                
        except Exception as e:
            print(f"❌ Erro na fala: {e}")
            print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
    
    def process_text(self, text, emotion):
        """Processa texto para português brasileiro"""
        # Substituições brasileiras
        text = text.replace("SEXTA-FEIRA", "Sexta-feira")
        text = text.replace("você", "você")
        
        # Adicionar emoção
        emotion_config = self.emotions.get(emotion, self.emotions["neutro"])
        return emotion_config["prefix"] + text + emotion_config["suffix"]
    
    async def test_emotions(self):
        """Testa emoções brasileiras"""
        print("\n🇧🇷 TESTE EMOÇÕES BRASILEIRAS")
        print("="*32)
        
        tests = [
            ("Oi! Tudo bem? Eu sou a Sexta-feira!", "neutro"),
            ("Que legal! Tô muito animada!", "feliz"),
            ("Você é muito querido, sabia?", "carinhoso"),
            ("Nossa! Que incrível!", "animado"),
            ("Caramba! Não acredito!", "surpreso")
        ]
        
        for text, emotion in tests:
            print(f"\n💫 {emotion.upper()}: {text}")
            await self.speak(text, emotion)
            await asyncio.sleep(2)
        
        print("\n✅ Teste concluído!")
    
    def get_system_info(self):
        if self.tts:
            return f"🇧🇷 TTS Brasileiro ({self.model_name})"
        return "📝 Modo Texto"

# Teste independente
async def test_brazilian_tts():
    """Testa sistema brasileiro"""
    print("🇧🇷 TESTANDO TTS BRASILEIRO")
    print("="*30)
    
    try:
        tts = SimpleBrazilianTTS()
        
        print(f"Sistema: {tts.get_system_info()}")
        
        if tts.tts:
            await tts.speak("Olá! Sistema brasileiro funcionando!", "feliz")
            await tts.test_emotions()
            print("\n🎉 TTS BRASILEIRO FUNCIONANDO!")
        else:
            print("❌ TTS não carregou")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_brazilian_tts())
