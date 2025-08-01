# update_agent_voice_part1.py
print("🔧 Atualizando agent.py com voz emocional - PARTE 1...")

# Ler arquivo atual
with open("core/agent.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Adicionar método speak_with_emotion se não existe
if "speak_with_emotion" not in content:
    speak_method = '''
    async def speak_with_emotion(self, text: str, emotion: str = "neutro"):
        """Fala com emoção específica"""
        try:
            print(f"\\n🤖 SEXTA-FEIRA: {text}")
            await self.tts.speak(text, emotion)
        except Exception as e:
            self.logger.error(f"Erro na fala emocional: {e}")
'''
    
    # Inserir antes do método speak
    speak_pos = content.find("async def speak(self, text: str):")
    if speak_pos != -1:
        line_start = content.rfind("\\n", 0, speak_pos) + 1
        content = content[:line_start] + speak_method + "\\n" + content[line_start:]
        print("✅ Método speak_with_emotion adicionado")
    else:
        print("⚠️ Método speak não encontrado")

# 2. Atualizar todas as referências ARIA para SEXTA-FEIRA
replacements = [
    ('print(f"\\n🤖 ARIA: {text}")', 'print(f"\\n🤖 SEXTA-FEIRA: {text}")'),
    ('"Olá! Sou a ARIA. Qual é o seu nome?"', '"Olá! Sou a SEXTA-FEIRA. Qual é o seu nome?"'),
    ('f"Olá {user_name}! Sou a ARIA, sua assistente pessoal."', 'f"Olá {user_name}! Sou a SEXTA-FEIRA, sua assistente pessoal."'),
    ('🤖 ARIA: ', '🤖 SEXTA-FEIRA: '),
    ('Sou a ARIA', 'Sou a SEXTA-FEIRA'),
    ('nome é ARIA', 'nome é SEXTA-FEIRA'),
    ('chamo ARIA', 'chamo SEXTA-FEIRA'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"✅ Substituído: {old[:30]}...")

# 3. Adicionar comando teste voz na interface
if '"🎭 \'teste voz\' = TESTAR EMOÇÕES"' not in content:
    help_pattern = '"🔧 \'analisar código\' = AUTO-ANÁLISE"'
    if help_pattern in content:
        content = content.replace(
            help_pattern,
            help_pattern + '\\n        print("🎭 \'teste voz\' = TESTAR EMOÇÕES")'
        )
        print("✅ Comando teste voz adicionado na interface")

# 4. Adicionar tratamento do comando teste voz
if "teste voz" not in content:
    # Encontrar onde adicionar o comando no process_input
    nome_command_pos = content.find('elif user_input.lower().startswith("nome "):')
    if nome_command_pos != -1:
        new_command = '''elif user_input.lower() == "teste voz":
                            await self.test_voice_emotions()
                            continue
                        '''
        content = content.replace(
            'elif user_input.lower().startswith("nome "):',
            new_command + 'elif user_input.lower().startswith("nome "):'
        )
        print("✅ Tratamento do comando 'teste voz' adicionado")

# 5. Salvar progresso da parte 1
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\\n✅ PARTE 1 CONCLUÍDA!")
print("🎯 Modificações aplicadas:")
print("• Método speak_with_emotion adicionado")
print("• Todas as referências ARIA → SEXTA-FEIRA")
print("• Comando 'teste voz' na interface")
print("• Tratamento do comando 'teste voz'")
print("\\n🔄 Execute a PARTE 2 para completar...")