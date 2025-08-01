import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))

async def test_final():
    try:
        from core.ultra_realistic_voice import PerfectWorkingVoice
        print("✅ Sistema final importado!")
        
        voice = PerfectWorkingVoice()
        
        print("⏳ Inicializando sistema final...")
        await asyncio.sleep(3)
        
        if voice.is_initialized:
            system = voice.get_current_system()
            print(f"🎭 Sistema: {system}")
            
            print("\n🎤 TESTE BÁSICO:")
            await voice.speak("Sistema final funcionando perfeitamente!", "feliz")
            
            print("\n🎪 TESTE RÁPIDO DE EMOÇÕES:")
            await voice.speak("Estou muito animada!", "animado")
            await voice.speak("Você é especial...", "carinhoso")
            await voice.speak("Nossa! Funcionou!", "surpreso")
            
            print("\n🎉 SISTEMA FINAL FUNCIONANDO!")
        else:
            print("❌ Sistema não inicializou")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

asyncio.run(test_final())
