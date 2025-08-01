import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))

async def test_guaranteed():
    try:
        from core.ultra_realistic_voice import GuaranteedWorkingVoice
        print("✅ Import realizado!")
        
        voice = GuaranteedWorkingVoice()
        
        print("⏳ Aguardando inicialização...")
        for i in range(20):
            if voice.is_initialized:
                break
            await asyncio.sleep(1)
            if (i + 1) % 5 == 0:
                print(f"   ... {i+1}s")
        
        system = voice.get_current_system()
        print(f"🎭 Sistema: {system}")
        
        if voice.is_initialized:
            print("\n🎤 TESTE DE FALA:")
            await voice.speak("Sistema garantido funcionando!", "feliz")
            await voice.speak("Agora vou testar animado!", "animado")
            print("\n🎉 FUNCIONOU!")
        else:
            print("⚠️ Sistema não inicializou")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_guaranteed())
