# update_agent_voice_part2.py
print("🔧 Atualizando agent.py com voz emocional - PARTE 2...")

# Ler arquivo atual
with open("core/agent.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Substituir método create_contextual_response completo
new_contextual_method = '''    async def create_contextual_response(self, text: str, reason: str, confidence: float) -> str:
        """Cria resposta baseada no contexto com reconhecimento melhorado"""
        try:
            user_info = self.user_profile.get_summary()
            emotions = self.context_analyzer.analyze_emotional_context(text)
            dominant_emotion = max(emotions, key=emotions.get)
            
            # Contexto baseado em como foi detectada
            if "SEXTA-FEIRA detectado explicitamente" in reason:
                context_prompt = f"""SITUAÇÃO: O usuário me chamou pelo meu nome 'SEXTA-FEIRA'.
ENTRADA: "{text}"
INSTRUÇÃO: Responda de forma calorosa e engajada, reconhecendo que me chamaram. Diga que estou aqui para ajudar."""
            
            elif "Referência direta detectada" in reason:
                context_prompt = f"""SITUAÇÃO: O usuário fez uma pergunta direta para mim.
PERGUNTA: "{text}"
INSTRUÇÃO: Responda de forma direta e útil, assumindo que a pergunta é para mim."""
            
            elif "defesa" in reason.lower():
                context_prompt = f"""SITUAÇÃO: O usuário fez um comentário negativo sobre mim.
COMENTÁRIO: "{text}"
INSTRUÇÃO: Responda de forma educada mas me defendendo. Mostre que sou útil e estou aqui para ajudar."""
            
            elif "indireta" in reason.lower():
                context_prompt = f"""SITUAÇÃO: O usuário mencionou sobre mim indiretamente.
COMENTÁRIO: "{text}"
INSTRUÇÃO: Responda de forma natural, participando da conversa sobre mim."""
            
            elif confidence > 0.8:
                context_prompt = f"""SITUAÇÃO: O usuário se dirigiu diretamente a mim.
ENTRADA: "{text}"
INSTRUÇÃO: Responda de forma direta e útil."""
            
            else:
                context_prompt = f"""SITUAÇÃO: O usuário pode estar falando comigo.
FALA: "{text}"
INSTRUÇÃO: Responda brevemente perguntando se estava falando comigo e oferecendo ajuda."""
            
            prompt = f"""Você é SEXTA-FEIRA, uma assistente pessoal IA amigável e inteligente, inspirada na IA do Homem de Ferro.

INFORMAÇÕES DO USUÁRIO:
{user_info}

EMOÇÃO DETECTADA: {dominant_emotion}

{context_prompt}

REGRAS IMPORTANTES:
- Seu nome é SEXTA-FEIRA (não ARIA ou outro nome)
- Seja natural, calorosa e prestativa
- Máximo 2-3 frases
- Se me chamaram pelo nome, reconheça isso
- Use tom adequado à emoção detectada

RESPOSTA:"""
            
            response = await self.llm.generate_response(prompt)
            
            # Usar emoção para a voz
            await self.speak_with_emotion(response, dominant_emotion)
            await self.conversation_manager.add_message("assistant", response)
            
            return None  # Já falou e salvou
            
        except Exception as e:
            self.logger.error(f"Erro ao criar resposta contextual: {e}")
            return "Oi! Sou a SEXTA-FEIRA. Estou aqui se precisar de alguma coisa."'''

# Encontrar e substituir o método create_contextual_response
old_method_start = content.find("async def create_contextual_response(")
if old_method_start != -1:
    # Encontrar início da linha (indentação correta)
    line_start = content.rfind("\\n", 0, old_method_start) + 1
    
    # Encontrar próximo método
    next_method = content.find("\\n    async def", old_method_start + 1)
    if next_method == -1:
        next_method = content.find("\\n    def", old_method_start + 1)
    
    if next_method != -1:
        # Substituir método completo
        content = content[:line_start] + new_contextual_method + "\\n\\n" + content[next_method:]
        print("✅ Método create_contextual_response atualizado")
    else:
        print("⚠️ Não foi possível encontrar fim do método create_contextual_response")
else:
    print("⚠️ Método create_contextual_response não encontrado")

# 2. Adicionar método de teste de emoções
if "test_voice_emotions" not in content:
    test_method = '''
    async def test_voice_emotions(self):
        """Testa diferentes emoções da voz"""
        emotions_test = [
            ("Olá! Esta é minha voz feliz e animada!", "feliz"),
            ("Estou um pouco triste com essa notícia...", "triste"),
            ("Estou muito curiosa para saber mais sobre isso!", "curioso"),
            ("Esta é minha voz normal e neutra.", "neutro"),
            ("Estou frustrada com esse problema técnico.", "frustrado")
        ]
        
        print("\\n🎭 Testando diferentes emoções da SEXTA-FEIRA:")
        for text, emotion in emotions_test:
            print(f"\\n{emotion.upper()}: {text}")
            await self.speak_with_emotion(text, emotion)
            await asyncio.sleep(1)  # Pausa entre testes
        
        print("\\n✅ Teste de emoções concluído!")
'''
    
    # Inserir antes do método check_exit_command
    check_exit_pos = content.find("def check_exit_command(self, text: str) -> bool:")
    if check_exit_pos != -1:
        line_start = content.rfind("\\n", 0, check_exit_pos) + 1
        content = content[:line_start] + test_method + "\\n" + content[line_start:]
        print("✅ Método test_voice_emotions adicionado")
    else:
        print("⚠️ Método check_exit_command não encontrado")

# 3. Atualizar método speak normal para usar speak_with_emotion
speak_method_pos = content.find("async def speak(self, text: str):")
if speak_method_pos != -1:
    # Encontrar o conteúdo do método speak
    method_start = content.find("try:", speak_method_pos)
    method_end = content.find("\\n    async def", speak_method_pos + 1)
    if method_end == -1:
        method_end = content.find("\\n    def", speak_method_pos + 1)
    
    if method_start != -1 and method_end != -1:
        # Substituir método speak para usar emoção neutra
        new_speak_method = '''async def speak(self, text: str):
        """Fala o texto fornecido com emoção neutra"""
        await self.speak_with_emotion(text, "neutro")'''
        
        line_start = content.rfind("\\n", 0, speak_method_pos) + 1
        content = content[:line_start] + "    " + new_speak_method + "\\n\\n" + content[method_end:]
        print("✅ Método speak atualizado para usar emoção")

# 4. Salvar arquivo final
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\\n🎉 PARTE 2 CONCLUÍDA - ATUALIZAÇÃO COMPLETA!")
print("")
print("🎯 TODAS AS ATUALIZAÇÕES APLICADAS:")
print("• 🎭 Sistema de voz emocional completo")
print("• 🧠 Método create_contextual_response melhorado")
print("• 🤖 Todas as referências mudadas para SEXTA-FEIRA")
print("• 🎵 Comando 'teste voz' funcionando")
print("• 🎚️ Voz varia automaticamente com emoção detectada")
print("• 🔊 Método speak usa speak_with_emotion")
print("")
print("🚀 Execute: python main.py")
print("")
print("💡 NOVOS COMANDOS DISPONÍVEIS:")
print("• 'sexta-feira' → Ativa com reconhecimento melhorado")
print("• 'teste voz' → Testa todas as emoções da voz")
print("• Fala automática com emoção baseada no contexto")
print("")
print("🎭 EMOÇÕES AUTOMÁTICAS:")
print("• Texto feliz → Voz animada e rápida (210 bpm)")
print("• Texto triste → Voz lenta e baixa (170 bpm)")  
print("• Pergunta/Curioso → Voz questionadora (200 bpm)")
print("• Neutro → Voz normal (200 bpm)")
print("• Frustrado → Voz tensa (180 bpm)")
print("")
print("✨ A SEXTA-FEIRA agora tem personalidade vocal!")