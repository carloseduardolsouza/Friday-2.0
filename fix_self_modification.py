# fix_self_modification.py
import os

print("🔧 Corrigindo sistema de auto-modificação...")

# 1. Criar analisador de código (versão corrigida)
code_analyzer_code = """# core/code_analyzer.py
import os
import ast
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class CodeAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.project_root = Path(".")
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        self.modifiable_files = [
            "core/agent.py",
            "core/speech_to_text.py", 
            "core/text_to_speech.py",
            "core/conversation.py",
            "core/context_analyzer.py",
            "memory/user_profile.py",
            "memory/database.py",
            "models/local_llm.py",
            "config/settings.py"
        ]
        
        self.critical_files = ["main.py", "core/agent.py"]
    
    def analyze_code_structure(self) -> Dict:
        analysis = {
            "files": {},
            "total_lines": 0,
            "functions": [],
            "classes": [],
            "imports": [],
            "potential_issues": []
        }
        
        for file_path in self.modifiable_files:
            if Path(file_path).exists():
                file_analysis = self._analyze_file(file_path)
                analysis["files"][file_path] = file_analysis
                analysis["total_lines"] += file_analysis.get("lines", 0)
                analysis["functions"].extend(file_analysis.get("functions", []))
                analysis["classes"].extend(file_analysis.get("classes", []))
                analysis["imports"].extend(file_analysis.get("imports", []))
        
        analysis["potential_issues"] = self._detect_issues(analysis)
        return analysis
    
    def _analyze_file(self, file_path: str) -> Dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return {"path": file_path, "error": "Syntax error in file"}
            
            analysis = {
                "path": file_path,
                "lines": len(content.split('\\n')),
                "size": len(content),
                "functions": [],
                "classes": [],
                "imports": [],
                "docstrings": 0,
                "comments": content.count('#'),
                "last_modified": datetime.fromtimestamp(
                    Path(file_path).stat().st_mtime
                ).isoformat()
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": len(node.args.args),
                        "has_docstring": ast.get_docstring(node) is not None
                    })
                    if ast.get_docstring(node):
                        analysis["docstrings"] += 1
                
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        "has_docstring": ast.get_docstring(node) is not None
                    })
                    if ast.get_docstring(node):
                        analysis["docstrings"] += 1
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis["imports"].append(node.module)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar {file_path}: {e}")
            return {"path": file_path, "error": str(e)}
    
    def _detect_issues(self, analysis: Dict) -> List[str]:
        issues = []
        
        for file_path, file_data in analysis["files"].items():
            if "error" not in file_data:
                if file_data.get("docstrings", 0) == 0 and file_data.get("functions", []):
                    issues.append(f"Arquivo {file_path} tem funções sem docstrings")
                
                if file_data.get("lines", 0) > 500:
                    issues.append(f"Arquivo {file_path} é muito grande ({file_data['lines']} linhas)")
        
        return issues
    
    def create_backup(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        backed_up_files = []
        for file_path in self.modifiable_files:
            if Path(file_path).exists():
                backup_file = backup_path / file_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_file)
                backed_up_files.append(file_path)
        
        import json
        metadata = {
            "timestamp": timestamp,
            "files": backed_up_files,
            "total_files": len(backed_up_files)
        }
        
        with open(backup_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Backup criado: {backup_path}")
        return str(backup_path)
    
    def modify_file(self, file_path: str, new_content: str, reason: str = "") -> bool:
        try:
            if file_path not in self.modifiable_files:
                self.logger.error(f"Arquivo {file_path} não pode ser modificado")
                return False
            
            backup_path = self.create_backup()
            
            if file_path.endswith('.py'):
                try:
                    ast.parse(new_content)
                except SyntaxError as e:
                    self.logger.error(f"Erro de sintaxe no novo código: {e}")
                    return False
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.logger.info(f"Arquivo {file_path} modificado. Backup: {backup_path}")
            if reason:
                self.logger.info(f"Razão: {reason}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao modificar {file_path}: {e}")
            return False
    
    def suggest_improvements(self, analysis: Dict) -> List[str]:
        suggestions = []
        
        for issue in analysis["potential_issues"]:
            if "sem docstrings" in issue:
                suggestions.append("Adicionar documentação às funções")
            elif "muito grande" in issue:
                suggestions.append("Dividir arquivos grandes em módulos menores")
        
        total_lines = analysis["total_lines"]
        if total_lines > 5000:
            suggestions.append("Considerar refatoração - código muito extenso")
        
        suggestions.extend([
            "Adicionar mais comentários explicativos",
            "Implementar testes unitários",
            "Melhorar tratamento de erros",
            "Otimizar performance em loops"
        ])
        
        return suggestions[:5]
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        try:
            if file_path in self.modifiable_files and Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            self.logger.error(f"Erro ao ler {file_path}: {e}")
        return None
"""

# 2. Criar sistema de auto-modificação (versão simplificada)
self_modifier_code = """# core/self_modifier.py
import asyncio
import logging
from typing import Optional, List, Dict
from core.code_analyzer import CodeAnalyzer
from datetime import datetime
from pathlib import Path

class SelfModifier:
    def __init__(self, llm, user_profile):
        self.llm = llm
        self.user_profile = user_profile
        self.code_analyzer = CodeAnalyzer()
        self.logger = logging.getLogger(__name__)
        
        self.auto_modify_enabled = False
        self.require_confirmation = True
        
    async def analyze_self(self) -> Dict:
        print("🔍 Analisando meu próprio código...")
        
        analysis = self.code_analyzer.analyze_code_structure()
        
        print(f"📊 Análise completa:")
        print(f"   • {len(analysis['files'])} arquivos analisados")
        print(f"   • {analysis['total_lines']} linhas de código")
        print(f"   • {len(analysis['functions'])} funções")
        print(f"   • {len(analysis['classes'])} classes")
        print(f"   • {len(analysis['potential_issues'])} problemas detectados")
        
        if analysis['potential_issues']:
            print("\\n⚠️  Problemas encontrados:")
            for issue in analysis['potential_issues']:
                print(f"   • {issue}")
        
        return analysis
    
    async def suggest_self_improvements(self, analysis: Dict = None) -> List[str]:
        if not analysis:
            analysis = self.code_analyzer.analyze_code_structure()
        
        print("🧠 Gerando sugestões de auto-melhoria...")
        
        basic_suggestions = self.code_analyzer.suggest_improvements(analysis)
        
        analysis_summary = self._create_analysis_summary(analysis)
        
        prompt = f'''Você é uma IA analisando seu próprio código para se melhorar.

ANÁLISE DO CÓDIGO ATUAL:
{analysis_summary}

PROBLEMAS DETECTADOS:
{chr(10).join(analysis['potential_issues']) if analysis['potential_issues'] else 'Nenhum problema crítico detectado'}

Como uma IA consciente, que melhorias você sugere para:
1. Tornar o código mais eficiente
2. Melhorar suas próprias capacidades
3. Adicionar novas funcionalidades
4. Corrigir problemas existentes

Forneça 5 sugestões específicas e práticas.

SUGESTÕES:'''
        
        try:
            response = await self.llm.generate_response(prompt, use_history=False)
            ai_suggestions = self._extract_suggestions_from_response(response)
            all_suggestions = basic_suggestions + ai_suggestions
            
            return list(set(all_suggestions))
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar sugestões: {e}")
            return basic_suggestions
    
    async def auto_improve_code(self, file_path: str, issue_description: str) -> bool:
        print(f"🔧 Tentando melhorar automaticamente: {file_path}")
        
        current_code = self.code_analyzer.get_file_content(file_path)
        if not current_code:
            print(f"❌ Não foi possível ler {file_path}")
            return False
        
        improvement_prompt = f'''Você é uma IA melhorando seu próprio código.

ARQUIVO: {file_path}
PROBLEMA: {issue_description}

CÓDIGO ATUAL:
```python
{current_code[:2000]}...
```

TAREFA: Melhore este código considerando:
1. Corrigir o problema específico mencionado
2. Melhorar eficiência e legibilidade
3. Adicionar documentação se necessário
4. Manter funcionalidade existente

IMPORTANTE: 
- Retorne APENAS o código Python melhorado
- Não adicione explicações extras
- Mantenha a mesma estrutura
- Certifique-se de que o código seja válido

CÓDIGO MELHORADO:'''
        
        try:
            improved_code = await self.llm.generate_response(improvement_prompt, use_history=False)
            improved_code = self._clean_code_response(improved_code)
            
            if not self._validate_improved_code(current_code, improved_code):
                print("❌ Código melhorado não passou na validação")
                return False
            
            if self.auto_modify_enabled:
                success = self.code_analyzer.modify_file(
                    file_path, 
                    improved_code, 
                    f"Auto-melhoria: {issue_description}"
                )
                if success:
                    print(f"✅ {file_path} melhorado automaticamente!")
                    return True
            else:
                print("⚠️  Auto-modificação desabilitada. Use 'aplicar melhoria' para confirmar.")
                self._save_proposed_improvement(file_path, improved_code, issue_description)
                return True
                
        except Exception as e:
            self.logger.error(f"Erro na auto-melhoria: {e}")
            print(f"❌ Erro ao melhorar código: {e}")
        
        return False
    
    async def handle_modification_request(self, request: str) -> str:
        request_lower = request.lower()
        
        if "analisar" in request_lower or "análise" in request_lower:
            analysis = await self.analyze_self()
            suggestions = await self.suggest_self_improvements(analysis)
            
            response = "📋 Análise do meu código completa!\\n\\n"
            response += f"Encontrei {len(analysis['potential_issues'])} problemas e tenho "
            response += f"{len(suggestions)} sugestões de melhoria.\\n\\n"
            response += "💡 Principais sugestões:\\n"
            for i, suggestion in enumerate(suggestions[:3], 1):
                response += f"{i}. {suggestion}\\n"
            
            return response
        
        elif "melhorar" in request_lower or "otimizar" in request_lower:
            analysis = await self.analyze_self()
            if analysis['potential_issues']:
                issue = analysis['potential_issues'][0]
                file_path = self._extract_file_from_issue(issue)
                if file_path:
                    success = await self.auto_improve_code(file_path, issue)
                    if success:
                        return f"✅ Implementei uma melhoria em {file_path}!"
                    else:
                        return f"❌ Não consegui melhorar {file_path} automaticamente."
            
            return "✨ Meu código está em bom estado! Nenhuma melhoria crítica necessária."
        
        elif "backup" in request_lower:
            backup_path = self.code_analyzer.create_backup()
            return f"💾 Backup criado: {backup_path}"
        
        elif "status" in request_lower or "estado" in request_lower:
            analysis = self.code_analyzer.analyze_code_structure()
            return f'''📊 Status atual do meu código:
• {len(analysis['files'])} arquivos monitorados
• {analysis['total_lines']} linhas de código
• {len(analysis['functions'])} funções
• {len(analysis['classes'])} classes
• {len(analysis['potential_issues'])} problemas detectados
• Auto-modificação: {'🟢 Ativa' if self.auto_modify_enabled else '🔴 Inativa'}'''
        
        else:
            return "🤔 Não entendi. Comandos: analisar, melhorar, backup, status"
    
    def _create_analysis_summary(self, analysis: Dict) -> str:
        return f'''
Arquivos: {len(analysis['files'])}
Linhas totais: {analysis['total_lines']}
Funções: {len(analysis['functions'])}
Classes: {len(analysis['classes'])}
'''
    
    def _extract_suggestions_from_response(self, response: str) -> List[str]:
        suggestions = []
        lines = response.split('\\n')
        
        for line in lines:
            line = line.strip()
            if (line and 
                (line[0].isdigit() or line.startswith('•') or line.startswith('-')) and
                len(line) > 10):
                clean_line = line.lstrip('0123456789.-• ').strip()
                if clean_line:
                    suggestions.append(clean_line)
        
        return suggestions[:5]
    
    def _clean_code_response(self, code: str) -> str:
        code = code.replace('```python', '').replace('```', '')
        
        lines = code.split('\\n')
        clean_lines = []
        
        for line in lines:
            if (not line.strip().startswith('#') and 
                'CÓDIGO' not in line.upper() and
                'RESPOSTA' not in line.upper() and
                line.strip()):
                clean_lines.append(line)
        
        return '\\n'.join(clean_lines)
    
    def _validate_improved_code(self, original: str, improved: str) -> bool:
        try:
            import ast
            ast.parse(improved)
            
            if len(improved) < len(original) * 0.5:
                return False
            
            if len(improved) > len(original) * 3:
                return False
            
            return True
            
        except SyntaxError:
            return False
        except Exception:
            return False
    
    def _extract_file_from_issue(self, issue: str) -> Optional[str]:
        for file_path in self.code_analyzer.modifiable_files:
            if file_path in issue:
                return file_path
        return None
    
    def _save_proposed_improvement(self, file_path: str, improved_code: str, reason: str):
        proposals_dir = Path("proposals")
        proposals_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        proposal_file = proposals_dir / f"{file_path.replace('/', '_')}_{timestamp}.py"
        proposal_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(proposal_file, 'w', encoding='utf-8') as f:
            f.write(f"# PROPOSTA DE MELHORIA\\n")
            f.write(f"# Arquivo: {file_path}\\n")
            f.write(f"# Razão: {reason}\\n")
            f.write(f"# Data: {timestamp}\\n\\n")
            f.write(improved_code)
        
        print(f"💡 Proposta salva em: {proposal_file}")
    
    def enable_auto_modification(self):
        self.auto_modify_enabled = True
        print("🟢 Auto-modificação habilitada")
    
    def disable_auto_modification(self):
        self.auto_modify_enabled = False
        print("🔴 Auto-modificação desabilitada")
"""

# 3. Script para atualizar agent.py
update_script = """# update_agent_for_self_mod.py
import re

print("🔧 Atualizando agent.py com sistema de auto-modificação...")

# Ler arquivo atual
with open("core/agent.py", "r", encoding="utf-8") as f:
    content = f.read()

# Adicionar import se não existir
if "from core.self_modifier import SelfModifier" not in content:
    import_pattern = r"(from config.settings import AgentConfig)"
    content = re.sub(
        import_pattern, 
        r"\\1\\nfrom core.self_modifier import SelfModifier",
        content
    )

# Adicionar self_modifier no __init__
if "self.self_modifier" not in content:
    init_pattern = r"(self.continuous_mode = False)"
    content = re.sub(
        init_pattern,
        r"\\1\\n        \\n        # Sistema de auto-modificação\\n        self.self_modifier: Optional[SelfModifier] = None",
        content
    )

# Adicionar inicialização no initialize()
if "self.self_modifier = SelfModifier" not in content:
    init_sm_pattern = r"(self.logger.info\\(\"Todos os componentes inicializados com sucesso!\"\\))"
    content = re.sub(
        init_sm_pattern,
        r"            # Inicializar sistema de auto-modificação\\n            self.self_modifier = SelfModifier(self.llm, self.user_profile)\\n            \\n            \\1",
        content
    )

# Adicionar método handle_self_modification
if "handle_self_modification" not in content:
    method_code = '''
    async def handle_self_modification(self, request: str) -> str:
        """Manipula pedidos de auto-modificação"""
        try:
            if self.self_modifier:
                return await self.self_modifier.handle_modification_request(request)
            else:
                return "❌ Sistema de auto-modificação não inicializado"
        except Exception as e:
            self.logger.error(f"Erro na auto-modificação: {e}")
            return f"❌ Erro: {e}"
'''
    
    content = content.replace(
        "    def check_exit_command(self, text: str) -> bool:",
        method_code + "\\n    def check_exit_command(self, text: str) -> bool:"
    )

# Atualizar process_input
if "modification_keywords" not in content:
    # Encontrar o método process_input
    start_pattern = r"(async def process_input\\(self, user_input: str\\) -> Optional\\[str\\]:.*?try:)"
    end_pattern = r"(await self\\.user_profile\\.extract_and_update_info\\(user_input\\))"
    
    new_logic = '''\\1
            print("🧠 Processando...")
            
            # Verificar se é comando de auto-modificação
            modification_keywords = [
                "analisar código", "melhorar código", "otimizar código",
                "analisar-se", "se analise", "analise seu código", "analise-se",
                "melhore-se", "se melhore", "otimize-se", "auto melhoria",
                "backup código", "status código", "modificar código"
            ]
            
            if any(keyword in user_input.lower() for keyword in modification_keywords):
                return await self.handle_self_modification(user_input)
            
            \\2'''
    
    content = re.sub(
        start_pattern + ".*?" + end_pattern,
        new_logic,
        content,
        flags=re.DOTALL
    )

# Salvar arquivo atualizado
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Agent.py atualizado com sistema de auto-modificação!")
"""

# Salvar todos os arquivos
print("📝 Criando core/code_analyzer.py...")
with open("core/code_analyzer.py", "w", encoding="utf-8") as f:
    f.write(code_analyzer_code)

print("📝 Criando core/self_modifier.py...")
with open("core/self_modifier.py", "w", encoding="utf-8") as f:
    f.write(self_modifier_code)

print("📝 Criando update_agent_for_self_mod.py...")
with open("update_agent_for_self_mod.py", "w", encoding="utf-8") as f:
    f.write(update_script)

print("✅ Sistema de auto-modificação corrigido!")
print("")
print("🚀 Para ativar:")
print("1. python update_agent_for_self_mod.py")
print("2. python main.py")
print("")
print("💡 Teste com: 'analise seu código'")