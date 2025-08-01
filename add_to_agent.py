# add_to_agent.py
print("🔧 Adicionando sistema de auto-modificação ao agent.py...")

# Ler arquivo agent.py
with open("core/agent.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Adicionar import se não existe
if "from core.self_modifier import SelfModifier" not in content:
    # Encontrar linha dos imports
    import_line = content.find("from config.settings import AgentConfig")
    if import_line != -1:
        # Encontrar fim da linha
        end_line = content.find("\n", import_line)
        # Inserir novo import
        new_import = "\nfrom core.self_modifier import SelfModifier"
        content = content[:end_line] + new_import + content[end_line:]

# 2. Adicionar variável no __init__
if "self.self_modifier" not in content:
    init_line = content.find("self.continuous_mode = False")
    if init_line != -1:
        end_line = content.find("\n", init_line)
        addition = "\n        \n        # Sistema de auto-modificação\n        self.self_modifier = None"
        content = content[:end_line] + addition + content[end_line:]

# 3. Adicionar inicialização
if "SelfModifier(self.llm" not in content:
    init_line = content.find('self.logger.info("Todos os componentes inicializados com sucesso!")')
    if init_line != -1:
        addition = "\n            # Inicializar sistema de auto-modificação\n            self.self_modifier = SelfModifier(self.llm, self.user_profile)\n"
        content = content[:init_line] + addition + content[init_line:]

# 4. Adicionar método
if "handle_self_modification" not in content:
    method_code = '''
    async def handle_self_modification(self, request: str) -> str:
        try:
            if self.self_modifier:
                return await self.self_modifier.handle_modification_request(request)
            else:
                return "❌ Sistema não inicializado"
        except Exception as e:
            return f"❌ Erro: {e}"
'''
    
    # Encontrar onde inserir (antes de check_exit_command)
    insert_point = content.find("def check_exit_command(self, text: str) -> bool:")
    if insert_point != -1:
        content = content[:insert_point] + method_code + "\n    " + content[insert_point:]

# 5. Modificar process_input
if "auto-modificação" not in content:
    # Encontrar process_input
    process_start = content.find('print("🧠 Processando...")')
    if process_start != -1:
        new_logic = '''print("🧠 Processando...")
            
            # Verificar comandos de auto-modificação
            mod_commands = ["analisar código", "melhorar código", "status código", "backup código"]
            if any(cmd in user_input.lower() for cmd in mod_commands):
                return await self.handle_self_modification(user_input)
            '''
        
        # Substituir apenas a linha do print
        end_line = content.find("\n", process_start)
        content = content[:process_start] + new_logic + content[end_line:]

# Salvar arquivo modificado
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Sistema de auto-modificação adicionado ao agent.py!")
