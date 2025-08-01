# update_voice_system.py
print("🎭 Atualizando sistema de voz da SEXTA-FEIRA...")

# Ler agent.py
with open("core/agent.py", "r", encoding="utf-8") as f:
    content = f.read()

# Atualizar import
if "from core.text_to_speech import HumanizedTTS" not in content:
    # Adicionar import
    import_line = "from core.text_to_speech import TextToSpeech"
    if import_line in content:
        content = content.replace(import_line, "from core.text_to_speech import HumanizedTTS")
        print("✅ Import atualizado")

# Atualizar inicialização do TTS
old_tts_init = "self.tts = TextToSpeech(self.config.voice)"
new_tts_init = "self.tts = HumanizedTTS(self.config.voice)"

if old_tts_init in content:
    content = content.replace(old_tts_init, new_tts_init)
    print("✅ Inicialização do TTS atualizada")

# Adicionar método de teste de voz melhorado
voice_test_method = """
    async def test_voice_quality(self):
        """Testa qualidade das vozes disponíveis"""
        print("🎭 Testando qualidade das vozes...")
        
        # Mostrar engines disponíveis
        available_engines = self.tts.get_available_engines()
        print("🔊 Engines disponíveis:")
        for engine in available_engines:
            print(f"   • {engine}")
        
        # Testar qualidade
        self.tts.test_voice_quality()
        
        print("\n✅ Teste de qualidade concluído!")
"""

# Inserir método se não existir
if "test_voice_quality" not in content:
    insert_point = content.find("    async def test_voice_emotions(self):")
    if insert_point != -1:
        content = content[:insert_point] + voice_test_method + "\n" + content[insert_point:]
        print("✅ Método de teste de qualidade adicionado")

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
print("💡 Teste com: 'teste sua voz' ou 'como você está'")
