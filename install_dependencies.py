# install_dependencies.py
import subprocess
import sys

def install_package(package):
    """Instala um pacote Python"""
    try:
        print(f"📦 Instalando {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar {package}: {e}")
        return False

def main():
    """Instala todas as dependências necessárias"""
    print("🚀 Instalando dependências do Agente IA...")
    
    # Lista de pacotes essenciais
    packages = [
        "ollama",
        "SpeechRecognition",
        "pyttsx3",
        "openai-whisper",
        "gTTS",
        "pygame",
        "requests",
        "python-dotenv"
    ]
    
    # Atualizar pip primeiro
    print("🔄 Atualizando pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("✅ Pip atualizado!")
    except:
        print("⚠️  Aviso: Não foi possível atualizar o pip")
    
    # Instalar pacotes
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Resultado: {success_count}/{len(packages)} pacotes instalados")
    
    if success_count == len(packages):
        print("🎉 Todas as dependências foram instaladas com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Instale o Ollama: https://ollama.ai/download")
        print("2. Execute: ollama pull llama3.2:3b")
        print("3. Execute: python main.py")
    else:
        print("⚠️  Algumas dependências falharam. Tente instalar manualmente:")
        print("pip install ollama SpeechRecognition pyttsx3 openai-whisper gTTS pygame")

if __name__ == "__main__":
    main()