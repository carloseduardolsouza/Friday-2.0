# fix_voice_update.py
print("🎭 Corrigindo sistema de voz da SEXTA-FEIRA...")

# Ler agent.py
with open("core/agent.py", "r", encoding="utf-8") as f:
    content = f.read()

# Atualizar import
if "from core.text_to_speech import HumanizedTTS" not in content:
    # Substituir import antigo
    if "from core.text_to_speech import TextToSpeech" in content:
        content = content.replace(
            "from core.text_to_speech import TextToSpeech",
            "from core.text_to_speech import HumanizedTTS"
        )
        print("✅ Import atualizado")

# Atualizar inicialização do TTS
old_tts_init = "self.tts = TextToSpeech(self.config.voice)"
new_tts_init = "self.tts = HumanizedTTS(self.config.voice)"

if old_tts_init in content:
    content = content.replace(old_tts_init, new_tts_init)
    print("✅ Inicialização do TTS atualizada")

# Adicionar método de teste de voz melhorado (sem aspas triplas problemáticas)
if "test_voice_quality" not in content:
    voice_test_method = '''    async def test_voice_quality(self):
        """Testa qualidade das vozes disponíveis"""
        print("🎭 Testando qualidade das vozes...")
        
        # Mostrar engines disponíveis
        if hasattr(self.tts, 'get_available_engines'):
            available_engines = self.tts.get_available_engines()
            print("🔊 Engines disponíveis:")
            for engine in available_engines:
                print(f"   • {engine}")
        
        # Testar qualidade
        if hasattr(self.tts, 'test_voice_quality'):
            self.tts.test_voice_quality()
        
        print("\\n✅ Teste de qualidade concluído!")

'''
    
    # Inserir método antes de test_voice_emotions
    insert_point = content.find("    async def test_voice_emotions(self):")
    if insert_point != -1:
        content = content[:insert_point] + voice_test_method + content[insert_point:]
        print("✅ Método de teste de qualidade adicionado")

# Verificar se HumanizedTTS foi importado corretamente
if "HumanizedTTS" in content:
    print("✅ HumanizedTTS configurado corretamente")
else:
    print("⚠️ HumanizedTTS pode não estar configurado")

# Salvar arquivo atualizado
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ Sistema de voz atualizado!")
print("\n🎯 MELHORIAS IMPLEMENTADAS:")
print("• 🎤 Google TTS (mais natural)")
print("• 🎭 Voz feminina otimizada") 
print("• 🔊 Qualidade de áudio melhorada")
print("• ⏸️ Pausas naturais e respiração")
print("• 🎪 Variação emocional sofisticada")
print("• 🔄 Sistema de fallback robusto")
print("\n🚀 Execute: python main.py")
print("💡 Teste com: 'teste sua voz' ou 'teste qualidade da voz'")