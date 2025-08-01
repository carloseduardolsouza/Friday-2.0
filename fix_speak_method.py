# fix_speak_method.py
print("🔧 Corrigindo método speak_with_emotion...")

# Ler agent.py
with open("core/agent.py", "r", encoding="utf-8") as f:
    content = f.read()

# Verificar se o método speak_with_emotion existe
if "def speak_with_emotion(" not in content:
    print("❌ Método speak_with_emotion não encontrado!")
    
    # Encontrar onde adicionar o método (antes do método speak_robust)
    insert_point = content.find("    async def speak_robust(")
    
    if insert_point == -1:
        # Se não encontrar speak_robust, adicionar antes do create_contextual_response
        insert_point = content.find("    async def create_contextual_response(")
    
    if insert_point != -1:
        # Adicionar o método speak_with_emotion
        speak_emotion_method = '''    async def speak_with_emotion(self, text: str, emotion: str = "neutro"):
        """Fala com emoção específica"""
        try:
            print(f"\\n🤖 SEXTA-FEIRA ({emotion}): {text}")
            await self.tts.speak(text, emotion)
            await self.conversation_manager.add_message("assistant", text)
        except Exception as e:
            self.logger.error(f"Erro na fala emocional: {e}")
            print(f"⚠️ [ERRO DE ÁUDIO] {text}")

'''
        
        # Inserir o método
        content = content[:insert_point] + speak_emotion_method + content[insert_point:]
        print("✅ Método speak_with_emotion adicionado!")
    else:
        print("❌ Não foi possível encontrar local para inserir o método")

else:
    print("✅ Método speak_with_emotion já existe!")

# Verificar se speak_robust está correto
if "async def speak_robust(" in content:
    # Verificar se está chamando speak_with_emotion corretamente
    if "await self.speak_with_emotion_robust(" in content:
        # Corrigir chamada incorreta
        content = content.replace("await self.speak_with_emotion_robust(", "await self.speak_with_emotion(")
        print("✅ Corrigida chamada incorreta para speak_with_emotion")
    
    # Verificar se speak_robust está chamando speak_with_emotion
    if "await self.speak_with_emotion(" not in content.split("async def speak_robust(")[1].split("async def ")[0]:
        # Corrigir speak_robust para usar speak_with_emotion
        old_speak_robust = content.split("async def speak_robust(")[1].split("async def ")[0]
        new_speak_robust = '''self, text: str, emotion: str = "neutro"):
        """Fala robusta com retry automático e fallback"""
        await self.speak_with_emotion(text, emotion)

    '''
        content = content.replace("async def speak_robust(" + old_speak_robust, "async def speak_robust(" + new_speak_robust)
        print("✅ Método speak_robust corrigido para usar speak_with_emotion")

# Corrigir chamadas no command_executor
content = content.replace("await self.agent.speak_with_emotion(", "await self.agent.speak_with_emotion(")

# Salvar arquivo corrigido
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Arquivo agent.py corrigido!")

# Verificar se command_executor.py precisa de correção
try:
    with open("core/command_executor.py", "r", encoding="utf-8") as f:
        executor_content = f.read()
    
    # Corrigir chamadas no command_executor
    if "self.agent.speak_with_emotion(" in executor_content:
        print("✅ Command executor já está correto")
    else:
        print("⚠️ Command executor pode precisar de correção")
        
except FileNotFoundError:
    print("⚠️ Arquivo command_executor.py não encontrado")

print("\n🚀 Execute: python main.py")
print("💡 Comando 'se melhore' deve funcionar agora!")