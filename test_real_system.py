import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))

async def test_real():
    try:
        from core.ultra_realistic_voice import RealWorkingVoice
        print("✅ Sistema real importado!")
        
        voice = RealWorkingVoice()
        
        print("⏳ Inicializando...")
        await asyncio.sleep(3)
        
        if voice.is_initialized:
            print(f"🎭 Sistema: {voice.get_current_system()}")
            
            print("\n🎤 TESTE BÁSICO:")
            await voice.speak("Olá! Agora eu tenho uma voz que REALMENTE funciona!", "feliz")
            
            print("\n🎪 TESTE DE EMOÇÕES:")
            await voice.speak("Estou muito animada!", "animado")
            await voice.speak("Você é muito querido...", "carinhoso")
            
            print("\n🎉 FUNCIONOU DE VERDADE!")
        else:
            print("❌ Sistema não inicializou")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_real())
