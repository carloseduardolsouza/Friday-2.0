# test_mecab_fix.py - Teste após correção MeCab
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path.cwd()))

async def test_after_fix():
    """Teste após correção do MeCab"""
    print("🧪 TESTE APÓS CORREÇÃO DO MECAB")
    print("="*40)
    
    try:
        print("📦 Testando imports...")
        
        # Teste 1: Import direto
        from core.ultra_realistic_voice import UltraRealisticVoice
        print("✅ ultra_realistic_voice importado!")
        
        # Teste 2: Sistema principal
        from core.text_to_speech import SuperiorFeminineVoice
        from config.settings import VoiceConfig
        print("✅ text_to_speech importado!")
        
        # Teste 3: Inicialização
        config = VoiceConfig()
        voice = SuperiorFeminineVoice(config)
        
        # Aguardar inicialização
        print("⏳ Aguardando inicialização...")
        await asyncio.sleep(5)
        
        # Teste 4: Sistema atual
        system = voice.get_current_system()
        print(f"🎭 Sistema ativo: {system}")
        
        # Teste 5: Fala básica
        print("\n🎤 Teste de fala:")
        await voice.speak("Olá! Correção do MeCab funcionou perfeitamente!", "feliz")
        
        # Teste 6: Emoções (opcional)
        emotions = voice.get_available_emotions()
        print(f"🎪 Emoções disponíveis: {emotions}")
        
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Erro MeCab corrigido com sucesso!")
        print("🌟 SEXTA-FEIRA está funcionando!")
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        print("💡 Execute: python one_click_ultra_voice_fixed.py")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_after_fix())
