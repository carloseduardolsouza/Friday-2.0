# test_ultra_final.py - Teste final da voz
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path.cwd()))

async def test_final():
    print("🌟 TESTE FINAL - VOZ ULTRA-REALISTA")
    print("="*50)
    
    try:
        from core.text_to_speech import SuperiorFeminineVoice
        from config.settings import VoiceConfig
        
        config = VoiceConfig()
        voice = SuperiorFeminineVoice(config)
        
        # Aguardar inicialização
        print("⏳ Aguardando inicialização...")
        await asyncio.sleep(5)
        
        system = voice.get_current_system()
        print(f"🎭 Sistema: {system}")
        
        # Teste básico
        print("\n🎤 TESTE BÁSICO:")
        await voice.speak("Olá! Minha voz agora é ultra-realista!", "feliz")
        
        # Teste completo
        print("\n🎪 TESTE COMPLETO:")
        await voice.test_voice_emotions()
        
        print("\n🎉 SUCESSO TOTAL!")
        print("🌟 SEXTA-FEIRA agora tem voz humana!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_final())
