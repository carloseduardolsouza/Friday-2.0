# clean_self_mod.py
import os

print("🔧 Criando sistema de auto-modificação (versão limpa)...")

# Primeiro, criar os arquivos separadamente

# 1. code_analyzer.py
print("📝 Criando core/code_analyzer.py...")
with open("core/code_analyzer.py", "w", encoding="utf-8") as f:
    f.write("""# core/code_analyzer.py
import os
import logging
import shutil
from pathlib import Path
from datetime import datetime

class CodeAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        self.modifiable_files = [
            "core/agent.py",
            "core/speech_to_text.py", 
            "core/text_to_speech.py",
            "memory/user_profile.py",
            "models/local_llm.py"
        ]
    
    def analyze_code_structure(self):
        analysis = {
            "files": {},
            "total_lines": 0,
            "functions": 0,
            "classes": 0,
            "potential_issues": []
        }
        
        for file_path in self.modifiable_files:
            if Path(file_path).exists():
                file_data = self._analyze_file(file_path)
                analysis["files"][file_path] = file_data
                analysis["total_lines"] += file_data.get("lines", 0)
                analysis["functions"] += len(file_data.get("functions", []))
                analysis["classes"] += len(file_data.get("classes", []))
        
        analysis["potential_issues"] = self._detect_issues(analysis)
        return analysis
    
    def _analyze_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\\n')
            
            return {
                "path": file_path,
                "lines": len(lines),
                "size": len(content),
                "functions": self._count_functions(content),
                "classes": self._count_classes(content),
                "comments": content.count('#')
            }
            
        except Exception as e:
            return {"path": file_path, "error": str(e)}
    
    def _count_functions(self, content):
        functions = []
        lines = content.split('\\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') and ':' in line:
                func_name = line.split('def ')[1].split('(')[0].strip()
                functions.append({"name": func_name, "line": i+1})
        return functions
    
    def _count_classes(self, content):
        classes = []
        lines = content.split('\\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('class ') and ':' in line:
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                classes.append({"name": class_name, "line": i+1})
        return classes
    
    def _detect_issues(self, analysis):
        issues = []
        
        for file_path, file_data in analysis["files"].items():
            if "error" not in file_data:
                if file_data.get("lines", 0) > 500:
                    issues.append(f"Arquivo {file_path} muito grande ({file_data['lines']} linhas)")
                
                if file_data.get("comments", 0) < 5:
                    issues.append(f"Arquivo {file_path} tem poucos comentários")
        
        return issues
    
    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        for file_path in self.modifiable_files:
            if Path(file_path).exists():
                backup_file = backup_path / file_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_file)
        
        return str(backup_path)
""")

# 2. self_modifier.py
print("📝 Criando core/self_modifier.py...")
with open("core/self_modifier.py", "w", encoding="utf-8") as f:
    f.write("""# core/self_modifier.py
import logging
from core.code_analyzer import CodeAnalyzer

class SelfModifier:
    def __init__(self, llm, user_profile):
        self.llm = llm
        self.user_profile = user_profile
        self.code_analyzer = CodeAnalyzer()
        self.logger = logging.getLogger(__name__)
        self.auto_modify_enabled = False
        
    async def analyze_self(self):
        print("🔍 Analisando meu próprio código...")
        
        analysis = self.code_analyzer.analyze_code_structure()
        
        print("📊 Análise completa:")
        print(f"   • {len(analysis['files'])} arquivos analisados")
        print(f"   • {analysis['total_lines']} linhas de código")
        print(f"   • {analysis['functions']} funções")
        print(f"   • {analysis['classes']} classes")
        print(f"   • {len(analysis['potential_issues'])} problemas detectados")
        
        if analysis['potential_issues']:
            print("\\n⚠️  Problemas encontrados:")
            for issue in analysis['potential_issues']:
                print(f"   • {issue}")
        
        return analysis
    
    async def handle_modification_request(self, request):
        request_lower = request.lower()
        
        if "analis" in request_lower:
            analysis = await self.analyze_self()
            
            response = "📋 Análise do meu código completa!\\n\\n"
            response += f"Encontrei {len(analysis['potential_issues'])} problemas.\\n\\n"
            response += "💡 Status atual:\\n"
            response += f"• {len(analysis['files'])} arquivos monitorados\\n"
            response += f"• {analysis['total_lines']} linhas de código\\n"
            response += f"• {analysis['functions']} funções\\n"
            response += f"• {analysis['classes']} classes"
            
            return response
        
        elif "melhor" in request_lower or "otimiz" in request_lower:
            analysis = await self.analyze_self()
            
            if analysis['potential_issues']:
                return "✨ Identifiquei algumas áreas para melhoria! Posso trabalhar nisso."
            else:
                return "✅ Meu código está em bom estado! Nenhuma melhoria crítica necessária."
        
        elif "backup" in request_lower:
            backup_path = self.code_analyzer.create_backup()
            return f"💾 Backup criado: {backup_path}"
        
        elif "status" in request_lower:
            analysis = self.code_analyzer.analyze_code_structure()
            
            status = "📊 Status atual do meu código:\\n"
            status += f"• {len(analysis['files'])} arquivos monitorados\\n"
            status += f"• {analysis['total_lines']} linhas de código\\n"
            status += f"• {analysis['functions']} funções\\n"
            status += f"• {analysis['classes']} classes\\n"
            status += f"• {len(analysis['potential_issues'])} problemas detectados\\n"
            
            if self.auto_modify_enabled:
                status += "• Auto-modificação: 🟢 Ativa"
            else:
                status += "• Auto-modificação: 🔴 Inativa"
            
            return status
        
        else:
            return "🤔 Comandos disponíveis: analisar, melhorar, backup, status"
""")

# 3. Script para adicionar ao agent.py manualmente
print("📝 Criando add_to_agent.py...")
with open("add_to_agent.py", "w", encoding="utf-8") as f:
    f.write("""# add_to_agent.py
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
        end_line = content.find("\\n", import_line)
        # Inserir novo import
        new_import = "\\nfrom core.self_modifier import SelfModifier"
        content = content[:end_line] + new_import + content[end_line:]

# 2. Adicionar variável no __init__
if "self.self_modifier" not in content:
    init_line = content.find("self.continuous_mode = False")
    if init_line != -1:
        end_line = content.find("\\n", init_line)
        addition = "\\n        \\n        # Sistema de auto-modificação\\n        self.self_modifier = None"
        content = content[:end_line] + addition + content[end_line:]

# 3. Adicionar inicialização
if "SelfModifier(self.llm" not in content:
    init_line = content.find('self.logger.info("Todos os componentes inicializados com sucesso!")')
    if init_line != -1:
        addition = "\\n            # Inicializar sistema de auto-modificação\\n            self.self_modifier = SelfModifier(self.llm, self.user_profile)\\n"
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
        content = content[:insert_point] + method_code + "\\n    " + content[insert_point:]

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
        end_line = content.find("\\n", process_start)
        content = content[:process_start] + new_logic + content[end_line:]

# Salvar arquivo modificado
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Sistema de auto-modificação adicionado ao agent.py!")
""")

print("✅ Arquivos criados com sucesso!")
print("")
print("🚀 Para ativar o sistema:")
print("1. python add_to_agent.py")
print("2. python main.py")
print("")
print("💡 Comandos para testar:")
print("• 'analisar código'")
print("• 'status código'") 
print("• 'backup código'")
print("• 'melhorar código'")