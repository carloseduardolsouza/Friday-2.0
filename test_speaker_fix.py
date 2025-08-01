# test_speaker_fix.py - Teste da correção de speaker
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path.cwd()))

async def test_speaker_fix():
    """Teste específico da correção de speaker"""
    print("🧪 TESTE DA CORREÇÃO DE SPEAKER")
    print("="*40)
    
    try:
        from core.ultra_realistic_voice import UltraRealisticVoice
        
        print("✅ Import realizado com sucesso!")
        
        # Criar sistema
        voice = UltraRealisticVoice()
        
        # Aguardar inicialização
        print("⏳ Aguardando inicialização...")
        for i in range(30):  # 30 segundos
            if voice.is_initialized:
                break
            await asyncio.sleep(1)
            if (i + 1) % 5 == 0:
                print(f"   ... {i+1}s")
        
        # Mostrar status
        system = voice.get_current_system()
        print(f"🎭 Sistema: {system}")
        
        # Teste de fala
        print("\n🎤 TESTANDO FALA:")
        await voice.speak("Olá! Correção de speaker funcionando!", "feliz")
        
        # Teste mini de emoções
        await voice.test_ultra_realistic_emotions()
        
        print("\n🎉 TESTE CONCLUÍDO!")
        print("✅ Correção de speaker funcionando!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_speaker_fix())
