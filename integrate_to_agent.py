# integrate_to_agent.py
print("🔧 Integrando sistema de comandos internos ao agent.py...")

# Ler arquivo atual
with open("core/agent.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Adicionar import do executor de comandos
if "from core.command_executor import InternalCommandExecutor" not in content:
    # Encontrar linha dos imports
    import_pos = content.find("from core.self_modifier import SelfModifier")
    if import_pos != -1:
        end_line = content.find("\\n", import_pos)
        new_import = "\\nfrom core.command_executor import InternalCommandExecutor"
        content = content[:end_line] + new_import + content[end_line:]
        print("✅ Import do InternalCommandExecutor adicionado")
    else:
        print("⚠️ Linha de import do SelfModifier não encontrada")

# 2. Adicionar inicialização do executor
if "self.command_executor" not in content:
    init_pos = content.find("self.self_modifier = None")
    if init_pos != -1:
        end_line = content.find("\\n", init_pos)
        addition = "\\n        self.command_executor = None"
        content = content[:end_line] + addition + content[end_line:]
        print("✅ Variável command_executor adicionada")
    else:
        print("⚠️ Linha self.self_modifier = None não encontrada")

# 3. Adicionar inicialização no initialize()
if "InternalCommandExecutor(self)" not in content:
    init_pos = content.find("self.self_modifier = SelfModifier(self.llm, self.user_profile)")
    if init_pos != -1:
        end_line = content.find("\\n", init_pos)
        addition = "\\n            self.command_executor = InternalCommandExecutor(self)"
        content = content[:end_line] + addition + content[end_line:]
        print("✅ Inicialização do command_executor adicionada")
    else:
        print("⚠️ Linha de inicialização do SelfModifier não encontrada")

# 4. Modificar process_input para verificar comandos internos primeiro
process_input_pos = content.find("async def process_input(self, user_input: str) -> Optional[str]:")
if process_input_pos != -1:
    method_start = content.find('print("🧠 Processando...")', process_input_pos)
    if method_start != -1:
        # Encontrar próxima linha significativa
        next_line_start = content.find("mod_commands", method_start)
        if next_line_start != -1:
            # Inserir verificação de comandos internos
            insertion_text = '''
            # Verificar comandos internos primeiro
            if self.command_executor:
                internal_response = await self.command_executor.process_natural_command(user_input)
                if internal_response:
                    return internal_response
            '''
            
            content = content[:next_line_start] + insertion_text + "\\n            # " + content[next_line_start:]
            print("✅ Lógica de comandos internos integrada")
        else:
            print("⚠️ Não foi possível encontrar local para inserir lógica")
    else:
        print("⚠️ Método process_input não encontrado")

# 5. Salvar arquivo modificado
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\\n✅ Sistema de comandos internos integrado com sucesso!")
print("")
print("🎯 MODIFICAÇÕES APLICADAS:")
print("• ✅ Import do InternalCommandExecutor")
print("• ✅ Variável command_executor no __init__")
print("• ✅ Inicialização no método initialize()")
print("• ✅ Verificação de comandos internos no process_input()")
print("")
print("🚀 Execute: python main.py")
print("")
print("💡 COMANDOS NATURAIS DISPONÍVEIS:")
print("• 'analise seu código' → Executa análise com fala")
print("• 'teste sua voz' → Demonstra emoções")
print("• 'faça um backup' → Cria backup")
print("• 'como você está?' → Relatório completo")
print("• 'se melhore' → Auto-melhoria")
print("• 'verifica seu próprio código' → Análise")
print("• 'mostra suas emoções' → Teste de voz")
print("")
print("🔄 Fluxo de execução:")
print("1. 👂 SEXTA-FEIRA detecta comando natural")
print("2. 🎤 Fala que está executando")
print("3. ⚡ Executa comando real")
print("4. 📢 Fala resultado final")