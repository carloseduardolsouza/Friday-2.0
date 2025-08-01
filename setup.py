# setup.py - Script de instalação e configuração inicial
import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Exibe banner do agente"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🤖 AGENTE IA OFFLINE 🤖                    ║
    ║                                                              ║
    ║              Seu Assistente Pessoal Inteligente             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Verifica versão do Python"""
    print("🔍 Verificando versão do Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário!")
        print(f"   Versão atual: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detectado")

def create_directories():
    """Cria estrutura de diretórios"""
    print("📁 Criando estrutura de diretórios...")
    
    directories = [
        "config", "core", "memory", "models", "data", 
        "logs", "utils", "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        # Criar __init__.py nos diretórios Python
        if directory not in ["data", "logs", "tests"]:
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("✅ Estrutura de diretórios criada!")

def install_dependencies():
    """Instala dependências Python"""
    print("📦 Instalando dependências...")
    
    try:
        # Atualizar pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Instalar dependências do requirements.txt
        if Path("requirements.txt").exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          check=True)
        else:
            # Instalar dependências essenciais manualmente
            essential_packages = [
                "ollama-python==0.1.7",
                "SpeechRecognition>=3.10.0",
                "pyttsx3>=2.90",
                "openai-whisper",
                "gTTS>=2.3.0",
                "pygame>=2.5.0",
                "sqlalchemy>=2.0.0",
                "python-dotenv>=1.0.0",
                "requests>=2.31.0"
            ]
            
            for package in essential_packages:
                print(f"   Instalando {package}...")
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                              check=True, capture_output=True)
        
        print("✅ Dependências instaladas com sucesso!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        print("💡 Tente executar manualmente: pip install -r requirements.txt")

def setup_ollama():
    """Configura Ollama"""
    print("🧠 Configurando Ollama (modelo de IA local)...")
    
    # Verificar se Ollama está instalado
    try:
        result = subprocess.run(["ollama", "--version"], 
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama já está instalado!")
            
            # Baixar modelo padrão
            print("📥 Baixando modelo llama3.2:3b (isso pode demorar)...")
            try:
                subprocess.run(["ollama", "pull", "llama3.2:3b"], 
                              check=True, timeout=300)
                print("✅ Modelo baixado com sucesso!")
            except subprocess.TimeoutExpired:
                print("⏰ Download do modelo demorou muito. Execute manualmente:")
                print("   ollama pull llama3.2:3b")
            except subprocess.CalledProcessError:
                print("⚠️  Erro ao baixar modelo. Tente manualmente:")
                print("   ollama pull llama3.2:3b")
        else:
            print("❌ Ollama não encontrado!")
            print_ollama_instructions()
            
    except FileNotFoundError:
        print("❌ Ollama não está instalado!")
        print_ollama_instructions()

def print_ollama_instructions():
    """Exibe instruções de instalação do Ollama"""
    system = platform.system().lower()
    
    print("\n📋 INSTRUÇÕES PARA INSTALAR OLLAMA:")
    print("=" * 50)
    
    if system == "windows":
        print("1. Acesse: https://ollama.ai/download/windows")
        print("2. Baixe e execute o instalador")
        print("3. Reinicie este script após a instalação")
    elif system == "darwin":  # macOS
        print("1. Acesse: https://ollama.ai/download/mac")
        print("2. Baixe e instale o Ollama")
        print("3. Ou use Homebrew: brew install ollama")
    else:  # Linux
        print("1. Execute: curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. Ou baixe de: https://ollama.ai/download/linux")
    
    print("\n4. Após instalar, execute: ollama pull llama3.2:3b")
    print("5. Execute este script novamente")

def setup_audio_dependencies():
    """Configura dependências de áudio"""
    print("🎤 Configurando dependências de áudio...")
    
    system = platform.system().lower()
    
    try:
        # Testar imports de áudio
        import speech_recognition
        import pyttsx3
        import pygame
        print("✅ Dependências de áudio OK!")
        
    except ImportError as e:
        print(f"⚠️  Problema com dependências de áudio: {e}")
        
        if system == "linux":
            print("📋 Execute os comandos:")
            print("   sudo apt-get install portaudio19-dev python3-pyaudio")
            print("   sudo apt-get install espeak espeak-data libespeak1 libespeak-dev")
            print("   sudo apt-get install ffmpeg")
        elif system == "darwin":
            print("📋 Execute os comandos:")
            print("   brew install portaudio")
            print("   brew install espeak")
            print("   brew install ffmpeg")
        elif system == "windows":
            print("📋 No Windows, pode ser necessário:")
            print("   - Instalar Microsoft Visual C++ Build Tools")
            print("   - Baixar PyAudio wheel manualmente")

def create_config_files():
    """Cria arquivos de configuração iniciais"""
    print("⚙️  Criando arquivos de configuração...")
    
    # Criar .env
    env_content = """# Configurações do Agente IA
AGENT_NAME=ARIA
AGENT_PERSONALITY=amigável, prestativo e inteligente
DEBUG_MODE=False

# Configurações de Voz
TTS_ENGINE=pyttsx3
VOICE_RATE=200
VOICE_VOLUME=0.9
WAKE_WORD=assistente

# Configurações do Modelo
MODEL_NAME=llama3.2:3b
MAX_TOKENS=2048
TEMPERATURE=0.7

# Configurações do Banco
DATABASE_PATH=data/conversations.db
USER_DATA_PATH=data/user_data.json
"""
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado!")

def test_installation():
    """Testa a instalação"""
    print("🧪 Testando instalação...")
    
    try:
        # Testar imports principais
        import sqlite3
        import json
        import asyncio
        print("✅ Módulos básicos: OK")
        
        # Testar dependências específicas
        import speech_recognition
        import pyttsx3
        import pygame
        print("✅ Módulos de áudio: OK")
        
        # Testar Ollama
        import ollama
        print("✅ Ollama Python: OK")
        
        print("🎉 Instalação testada com sucesso!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro no teste: {e}")
        return False

def print_final_instructions():
    """Exibe instruções finais"""
    print("\n" + "="*60)
    print("🎉 INSTALAÇÃO CONCLUÍDA!")
    print("="*60)
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Certifique-se que o Ollama está rodando:")
    print("   → ollama serve")
    print("\n2. Execute o agente:")
    print("   → python main.py")
    print("\n3. Teste sua voz:")
    print("   → Diga 'Olá' quando solicitado")
    
    print("\n🔧 COMANDOS ÚTEIS:")
    print("• Verificar modelos: ollama list")
    print("• Baixar modelo: ollama pull llama3.2:3b")
    print("• Testar modelo: ollama run llama3.2:3b")
    
    print("\n💡 DICAS:")
    print("• Use fones de ouvido para evitar eco")
    print("• Fale claramente e aguarde a resposta")
    print("• Diga 'sair' para encerrar")
    
    print("\n🆘 PROBLEMAS?")
    print("• Verifique logs em: logs/agent.log")
    print("• Teste componentes individualmente")
    print("• Consulte documentação do Ollama")

def main():
    """Função principal do setup"""
    print_banner()
    
    try:
        check_python_version()
        create_directories()
        install_dependencies()
        setup_audio_dependencies()
        create_config_files()
        setup_ollama()
        
        if test_installation():
            print_final_instructions()
        else:
            print("\n⚠️  Instalação parcial. Verifique os erros acima.")
            
    except KeyboardInterrupt:
        print("\n\n❌ Instalação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro durante instalação: {e}")
        print("💡 Tente executar novamente ou instale manualmente.")

if __name__ == "__main__":
    main()