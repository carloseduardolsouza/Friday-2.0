# install_voice_dependencies.py
import subprocess
import sys

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except:
        return False

print("📦 Instalando dependências para voz humanizada...")

packages = [
    "gtts",           # Google Text-to-Speech
    "pygame",         # Para reprodução de áudio
    "pydub",          # Processamento de áudio
    "requests",       # Para APIs de voz
]

for package in packages:
    print(f"Instalando {package}...")
    if install_package(package):
        print(f"✅ {package} instalado")
    else:
        print(f"❌ Falha ao instalar {package}")

print("\n🎭 Dependências instaladas!")
print("Execute: python update_voice_system.py")
