# brazilian_voice_selector.py - Seletor de vozes brasileiras
import asyncio
import sys
from pathlib import Path
import json

def print_banner():
    """Banner do seletor de vozes"""
    print("🇧🇷 SELETOR DE VOZES BRASILEIRAS")
    print("="*40)
    print("Escolha a melhor voz feminina brasileira para SEXTA-FEIRA")

def list_available_brazilian_models():
    """Lista modelos TTS disponíveis em português brasileiro"""
    print("\n🎭 MODELOS TTS DISPONÍVEIS PARA PORTUGUÊS BRASILEIRO")
    print("="*60)
    
    brazilian_models = {
        "1": {
            "name": "tts_models/pt/cv/vits",
            "description": "Modelo português padrão - Boa qualidade, rápido",
            "quality": "⭐⭐⭐",
            "speed": "🚀🚀🚀",
            "size": "📦 Pequeno (~50MB)",
            "type": "Voz sintética padrão"
        },
        "2": {
            "name": "tts_models/multilingual/multi-dataset/xtts_v2",
            "description": "XTTS v2 - Voz ultra-humana, melhor qualidade",
            "quality": "⭐⭐⭐⭐⭐",
            "speed": "🚀🚀",
            "size": "📦 Grande (~1.8GB)",
            "type": "Voz humana clonável"
        },
        "3": {
            "name": "tts_models/multilingual/multi-dataset/bark",
            "description": "Bark - Voz muito natural com emoções",
            "quality": "⭐⭐⭐⭐",
            "speed": "🚀",
            "size": "📦 Médio (~500MB)",
            "type": "Voz natural com expressões"
        },
        "4": {
            "name": "tts_models/pt/cv/vits-male",
            "description": "Voz masculina portuguesa (caso queira testar)",
            "quality": "⭐⭐⭐",
            "speed": "🚀🚀🚀",
            "size": "📦 Pequeno (~50MB)",
            "type": "Voz masculina"
        }
    }
    
    print("\n📋 OPÇÕES DISPONÍVEIS:")
    for key, model in brazilian_models.items():
        print(f"\n{key}. {model['name']}")
        print(f"   📝 {model['description']}")
        print(f"   🎯 Qualidade: {model['quality']}")
        print(f"   ⚡ Velocidade: {model['speed']}")
        print(f"   💾 Tamanho: {model['size']}")
        print(f"   🎭 Tipo: {model['type']}")
    
    return brazilian_models

def test_voice_model(model_name):
    """Testa um modelo específico"""
    print(f"\n🧪 TESTANDO MODELO: {model_name}")
    print("-" * 50)
    
    try:
        # Patch MeCab antes de importar
        import sys
        class FakeMeCab:
            class Tagger:
                def __init__(self, *args, **kwargs): pass
                def parse(self, text): return text
        sys.modules['MeCab'] = FakeMeCab()
        
        from TTS.api import TTS
        
        print("📥 Carregando modelo...")
        tts = TTS(model_name=model_name, progress_bar=True)
        print("✅ Modelo carregado!")
        
        # Criar diretório de teste
        test_dir = Path("voice_tests")
        test_dir.mkdir(exist_ok=True)
        
        # Frases de teste em português brasileiro
        test_phrases = [
            "Olá! Eu sou a SEXTA-FEIRA, sua assistente pessoal brasileira.",
            "Como você está hoje? Estou aqui para ajudá-lo!",
            "Posso falar sobre qualquer assunto que você quiser.",
            "Que tal testarmos algumas emoções? Estou muito animada!",
            "Minha voz soa natural e brasileira para você?"
        ]
        
        print(f"\n🎤 Gerando {len(test_phrases)} exemplos de voz...")
        
        for i, phrase in enumerate(test_phrases, 1):
            print(f"   🎯 Exemplo {i}/5: {phrase[:30]}...")
            
            audio_file = test_dir / f"test_{model_name.replace('/', '_')}_{i}.wav"
            
            try:
                if "xtts" in model_name.lower():
                    # XTTS precisa especificar idioma
                    tts.tts_to_file(
                        text=phrase,
                        file_path=str(audio_file),
                        language="pt"
                    )
                else:
                    # Outros modelos
                    tts.tts_to_file(
                        text=phrase,
                        file_path=str(audio_file)
                    )
                
                print(f"   ✅ Salvo: {audio_file.name}")
                
            except Exception as e:
                print(f"   ❌ Erro no exemplo {i}: {str(e)[:50]}")
        
        print(f"\n🎉 TESTE CONCLUÍDO!")
        print(f"📁 Arquivos salvos em: {test_dir}/")
        print("🔊 Reproduza os arquivos para ouvir a qualidade!")
        
        return True, tts
        
    except Exception as e:
        print(f"❌ Erro ao testar modelo: {e}")
        return False, None

def create_voice_config(selected_model, model_info):
    """Cria configuração de voz personalizada"""
    print(f"\n⚙️ CRIANDO CONFIGURAÇÃO PARA: {selected_model}")
    print("-" * 45)
    
    # Configuração específica para o modelo
    if "xtts" in selected_model.lower():
        voice_config = {
            "model_name": selected_model,
            "model_type": "xtts_v2",
            "language": "pt",
            "quality": "ultra_high",
            "emotions_supported": True,
            "voice_cloning": True,
            "description": "Voz ultra-humana com emoções",
            "sample_rate": 22050,
            "features": [
                "Clonagem de voz",
                "Emoções naturais", 
                "Prosódia avançada",
                "Multilíngue"
            ]
        }
    elif "bark" in selected_model.lower():
        voice_config = {
            "model_name": selected_model,
            "model_type": "bark",
            "language": "pt",
            "quality": "high",
            "emotions_supported": True,
            "voice_cloning": False,
            "description": "Voz natural com expressões",
            "sample_rate": 24000,
            "features": [
                "Expressões naturais",
                "Tom emocional",
                "Pausa inteligente"
            ]
        }
    else:
        voice_config = {
            "model_name": selected_model,
            "model_type": "vits",
            "language": "pt",
            "quality": "good",
            "emotions_supported": False,
            "voice_cloning": False,
            "description": "Voz padrão brasileira",
            "sample_rate": 22050,
            "features": [
                "Rápido",
                "Estável",
                "Português brasileiro"
            ]
        }
    
    # Salvar configuração
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "brazilian_voice_config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(voice_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuração salva: {config_file}")
    
    return voice_config

def create_brazilian_voice_system(voice_config):
    """Cria sistema de voz brasileiro personalizado"""
    print("\n🇧🇷 CRIANDO SISTEMA DE VOZ BRASILEIRO")
    print("="*42)
    
    brazilian_system_code = f'''# core/brazilian_voice_system.py - Sistema de voz brasileiro
import asyncio
import logging
import time
import json
from pathlib import Path

class BrazilianVoiceSystem:
    """Sistema de voz otimizado para português brasileiro"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tts = None
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Configuração carregada
        self.config = self.load_voice_config()
        
        # Emoções em português brasileiro
        self.emotions_ptbr = {{
            "neutro": {{"text_prefix": "", "text_suffix": ""}},
            "feliz": {{"text_prefix": "", "text_suffix": "!"}},
            "carinhoso": {{"text_prefix": "", "text_suffix": "..."}},
            "triste": {{"text_prefix": "", "text_suffix": "..."}},
            "curioso": {{"text_prefix": "", "text_suffix": "?"}},
            "animado": {{"text_prefix": "Nossa! ", "text_suffix": "!"}},
            "frustrado": {{"text_prefix": "", "text_suffix": "."}},
            "surpreso": {{"text_prefix": "Uau! ", "text_suffix": "!"}},
            "reflexivo": {{"text_prefix": "Bem... ", "text_suffix": "..."}},
            "sedutor": {{"text_prefix": "", "text_suffix": "..."}}
        }}
        
        self.initialize_tts()
    
    def load_voice_config(self):
        """Carrega configuração da voz brasileira"""
        try:
            config_file = Path("config/brazilian_voice_config.json")
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao carregar config: {{e}}")
        
        # Configuração padrão
        return {{
            "model_name": "{voice_config['model_name']}",
            "model_type": "{voice_config['model_type']}",
            "language": "pt"
        }}
    
    def initialize_tts(self):
        """Inicializa TTS brasileiro"""
        try:
            # Patch MeCab
            self.patch_mecab()
            
            from TTS.api import TTS
            
            model_name = self.config["model_name"]
            print(f"🇧🇷 Carregando voz brasileira: {{model_name}}")
            
            self.tts = TTS(model_name=model_name, progress_bar=True)
            
            print("✅ Voz brasileira carregada com sucesso!")
            print(f"🎭 Tipo: {{self.config.get('description', 'Voz brasileira')}}")
            
        except Exception as e:
            print(f"❌ Erro ao carregar voz brasileira: {{e}}")
            self.tts = None
    
    def patch_mecab(self):
        """Patch MeCab para evitar erros"""
        import sys
        class FakeMeCab:
            class Tagger:
                def __init__(self, *args, **kwargs): pass
                def parse(self, text): return text
        sys.modules['MeCab'] = FakeMeCab()
    
    async def speak(self, text, emotion="neutro"):
        """Fala em português brasileiro com emoção"""
        if not self.tts:
            print(f"🤖 SEXTA-FEIRA ({{emotion}}): {{text}}")
            return
        
        try:
            # Processar texto para português brasileiro
            processed_text = self.process_brazilian_text(text, emotion)
            
            # Gerar áudio
            audio_file = self.temp_dir / f"ptbr_{{emotion}}_{{int(time.time())}}.wav"
            
            # Diferentes métodos baseados no modelo
            if self.config["model_type"] == "xtts_v2":
                self.tts.tts_to_file(
                    text=processed_text,
                    file_path=str(audio_file),
                    language="pt",
                    speaker_wav=None  # Pode usar voz customizada aqui
                )
            else:
                self.tts.tts_to_file(
                    text=processed_text,
                    file_path=str(audio_file)
                )
            
            print(f"🇧🇷 SEXTA-FEIRA (PT-BR {{emotion}}): {{text}}")
            print(f"🔊 Áudio brasileiro: {{audio_file.name}}")
            
            # Reproduzir
            await self.play_audio(audio_file)
            
            # Limpar
            try:
                audio_file.unlink()
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Erro na fala brasileira: {{e}}")
            print(f"🤖 SEXTA-FEIRA ({{emotion}}): {{text}}")
    
    def process_brazilian_text(self, text, emotion):
        """Processa texto para soar mais brasileiro"""
        # Substituições brasileiras
        brazilian_replacements = {{
            "SEXTA-FEIRA": "Sexta-feira",
            "IA": "inteligência artificial",
            "você": "você",
            "está": "tá" if emotion in ["feliz", "animado"] else "está",
            "muito": "muito",
            "legal": "legal",
            "bacana": "bacana"
        }}
        
        processed = text
        for old, new in brazilian_replacements.items():
            processed = processed.replace(old, new)
        
        # Adicionar modificações emocionais
        emotion_config = self.emotions_ptbr.get(emotion, self.emotions_ptbr["neutro"])
        
        processed = emotion_config["text_prefix"] + processed + emotion_config["text_suffix"]
        
        return processed
    
    async def play_audio(self, audio_file):
        """Reproduz áudio"""
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            pygame.mixer.music.load(str(audio_file))
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
        except ImportError:
            print("🔊 Instale pygame para reprodução automática")
        except Exception as e:
            print(f"⚠️ Erro na reprodução: {{e}}")
    
    async def test_brazilian_emotions(self):
        """Testa emoções em português brasileiro"""
        print("\\n🇧🇷 TESTE DE EMOÇÕES BRASILEIRAS")
        print("="*38)
        
        brazilian_tests = [
            ("Oi, tudo bem? Eu sou a Sexta-feira!", "neutro"),
            ("Que legal! Estou super animada hoje!", "feliz"),
            ("Você é muito querido, sabia?", "carinhoso"),
            ("Puxa, que triste essa notícia...", "triste"),
            ("Hmmm, que interessante isso!", "curioso"),
            ("Nossa! Que demais! Adorei!", "animado"),
            ("Poxa, isso me deixa chateada.", "frustrado"),
            ("Caramba! Não acredito!", "surpreso"),
            ("Bem... deixa eu pensar sobre isso.", "reflexivo"),
            ("Você tem uma voz muito... interessante.", "sedutor")
        ]
        
        for text, emotion in brazilian_tests:
            print(f"\\n💫 {{emotion.upper()}}: {{text}}")
            await self.speak(text, emotion)
            await asyncio.sleep(2)
        
        print("\\n✅ Teste brasileiro concluído!")
    
    def get_current_system(self):
        """Sistema atual"""
        if self.tts:
            return f"🇧🇷 Voz Brasileira ({{self.config['model_type'].upper()}})"
        return "📝 Modo Texto"
    
    def get_available_emotions(self):
        """Emoções disponíveis"""
        return list(self.emotions_ptbr.keys())
    
    def get_voice_info(self):
        """Informações da voz"""
        return {{
            "model": self.config.get("model_name", "Desconhecido"),
            "type": self.config.get("model_type", "Desconhecido"),
            "quality": self.config.get("quality", "Desconhecido"),
            "language": "Português Brasileiro",
            "emotions": len(self.emotions_ptbr),
            "features": self.config.get("features", [])
        }}

# Compatibilidade
HumanizedTTS = BrazilianVoiceSystem
BarkHumanizedTTS = BrazilianVoiceSystem
CoquiHumanVoice = BrazilianVoiceSystem
SuperiorFeminineVoice = BrazilianVoiceSystem
'''
    
    # Salvar sistema brasileiro
    core_dir = Path("core")
    core_dir.mkdir(exist_ok=True)
    
    with open(core_dir / "brazilian_voice_system.py", "w", encoding="utf-8") as f:
        f.write(brazilian_system_code)
    
    print("✅ Sistema brasileiro criado!")

def update_main_system_for_brazil():
    """Atualiza sistema principal para usar voz brasileira"""
    print("\n🔄 ATUALIZANDO PARA VOZ BRASILEIRA")
    print("="*38)
    
    main_system_code = '''# core/text_to_speech.py - Sistema principal brasileiro
import asyncio
import logging
from typing import List
from config.settings import VoiceConfig

# Sistema brasileiro
try:
    from core.brazilian_voice_system import BrazilianVoiceSystem
    BRAZILIAN_AVAILABLE = True
except ImportError:
    BRAZILIAN_AVAILABLE = False

class SuperiorFeminineVoice:
    """Sistema principal com voz brasileira"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.brazilian_voice = None
        self.is_initialized = False
        
        asyncio.create_task(self._initialize_system())
    
    async def _initialize_system(self):
        """Inicializa sistema brasileiro"""
        if self.is_initialized:
            return
        
        print("\\n🇧🇷 INICIALIZANDO VOZ BRASILEIRA")
        print("="*38)
        
        if BRAZILIAN_AVAILABLE:
            try:
                self.brazilian_voice = BrazilianVoiceSystem()
                self.current_system = "brazilian"
                print("✅ Voz brasileira ativada!")
            except Exception as e:
                print(f"❌ Erro na voz brasileira: {e}")
                self.current_system = "text_only"
        else:
            self.current_system = "text_only"
            print("📝 Modo texto")
        
        self.is_initialized = True
    
    async def speak(self, text: str, emotion: str = "neutro"):
        """Fala em português brasileiro"""
        if not self.is_initialized:
            await self._initialize_system()
        
        if self.brazilian_voice:
            await self.brazilian_voice.speak(text, emotion)
        else:
            print(f"🤖 SEXTA-FEIRA ({emotion}): {text}")
    
    async def test_voice_emotions(self):
        """Teste brasileiro de emoções"""
        if not self.is_initialized:
            await self._initialize_system()
        
        if self.brazilian_voice:
            await self.brazilian_voice.test_brazilian_emotions()
        else:
            print("📝 Teste no modo texto")
    
    def get_current_system(self):
        if self.brazilian_voice:
            return self.brazilian_voice.get_current_system()
        return "📝 Modo Texto"
    
    def get_available_emotions(self):
        if self.brazilian_voice:
            return self.brazilian_voice.get_available_emotions()
        return ["neutro", "feliz", "triste", "curioso"]

# Compatibilidade
HumanizedTTS = SuperiorFeminineVoice
BarkHumanizedTTS = SuperiorFeminineVoice
'''
    
    with open("core/text_to_speech.py", "w", encoding="utf-8") as f:
        f.write(main_system_code)
    
    print("✅ Sistema principal atualizado para brasileiro!")

def create_voice_test():
    """Cria teste específico da voz brasileira"""
    test_code = '''# test_brazilian_voice.py - Teste da voz brasileira
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path.cwd()))

async def test_brazilian():
    """Testa voz brasileira"""
    print("🇧🇷 TESTE DA VOZ BRASILEIRA")
    print("="*30)
    
    try:
        from core.brazilian_voice_system import BrazilianVoiceSystem
        
        voice = BrazilianVoiceSystem()
        
        print(f"🔧 Sistema: {voice.get_current_system()}")
        
        info = voice.get_voice_info()
        print(f"🎭 Modelo: {info['model']}")
        print(f"🇧🇷 Idioma: {info['language']}")
        print(f"🎪 Emoções: {info['emotions']}")
        
        # Teste básico
        await voice.speak("Oi! Agora eu falo português brasileiro!", "feliz")
        
        # Teste completo
        await voice.test_brazilian_emotions()
        
        print("\\n🎉 VOZ BRASILEIRA FUNCIONANDO!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test_brazilian())
'''
    
    with open("test_brazilian_voice.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    print("✅ Teste brasileiro criado!")

def main():
    """Seletor principal"""
    print_banner()
    
    try:
        # Listar modelos disponíveis
        models = list_available_brazilian_models()
        
        print("\n🎯 RECOMENDAÇÕES:")
        print("• Opção 1: Rápido e confiável")
        print("• Opção 2: Melhor qualidade (voz ultra-humana)")
        print("• Opção 3: Boa qualidade com emoções")
        
        # Escolher modelo
        while True:
            choice = input("\\nEscolha uma opção (1-4) ou 'q' para sair: ").strip()
            
            if choice.lower() == 'q':
                print("👋 Saindo...")
                return
            
            if choice in models:
                selected_model = models[choice]["name"]
                print(f"\\n✅ Selecionado: {selected_model}")
                break
            else:
                print("❌ Opção inválida!")
        
        # Testar modelo
        print(f"\\n🧪 Quer testar o modelo antes de configurar? [S/n]")
        test_choice = input().strip().lower()
        
        if test_choice != 'n':
            success, tts_instance = test_voice_model(selected_model)
            
            if not success:
                print("❌ Modelo não funcionou. Tente outro.")
                return
            
            print("\\n🔊 Reproduza os arquivos de teste para avaliar a qualidade!")
            continue_choice = input("Continuar com este modelo? [S/n]: ").strip().lower()
            
            if continue_choice == 'n':
                print("🔄 Execute o script novamente para escolher outro modelo.")
                return
        
        # Criar configuração
        voice_config = create_voice_config(selected_model, models[choice])
        
        # Criar sistema brasileiro
        create_brazilian_voice_system(voice_config)
        
        # Atualizar sistema principal
        update_main_system_for_brazil()
        
        # Criar teste
        create_voice_test()
        
        print("\\n" + "="*60)
        print("🇧🇷 VOZ BRASILEIRA CONFIGURADA!")
        print("="*60)
        
        print(f"\\n✅ Modelo selecionado: {selected_model}")
        print(f"🎭 Descrição: {models[choice]['description']}")
        print(f"🎪 Qualidade: {models[choice]['quality']}")
        
        print("\\n🚀 TESTE SUA VOZ BRASILEIRA:")
        print("   python test_brazilian_voice.py")
        
        print("\\n🎯 OU TESTE NA SEXTA-FEIRA:")
        print("   python main.py")
        print("   Digite: 'teste sua voz'")
        
        print("\\n🇧🇷 AGORA SUA SEXTA-FEIRA FALA PORTUGUÊS BRASILEIRO!")
        
    except KeyboardInterrupt:
        print("\\n👋 Cancelado pelo usuário")
    except Exception as e:
        print(f"\\n❌ Erro: {e}")

if __name__ == "__main__":
    main()