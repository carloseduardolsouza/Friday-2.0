# self_modification.py - Sistema de auto-modificação da IA
import os

print("🔧 Criando sistema de auto-modificação...")

# 1. Criar analisador de código
code_analyzer_code = '''# core/code_analyzer.py
import os
import ast
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class CodeAnalyzer:
    """Analisa e modifica o próprio código do sistema"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.project_root = Path(".")
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Arquivos que podem ser modificados
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
        
        # Arquivos críticos que precisam de confirmação
        self.critical_files = [
            "main.py",
            "core/agent.py"
        ]
    
    def analyze_code_structure(self) -> Dict:
        """Analisa estrutura atual do código"""
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
                analysis["total_lines"] += file_analysis["lines"]
                analysis["functions"].extend(file_analysis["functions"])
                analysis["classes"].extend(file_analysis["classes"])
                analysis["imports"].extend(file_analysis["imports"])
        
        # Detectar problemas potenciais
        analysis["potential_issues"] = self._detect_issues(analysis)
        
        return analysis
    
    def _analyze_file(self, file_path: str) -> Dict:
        """Analisa um arquivo específico"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parsing AST para análise estrutural
            tree = ast.parse(content)
            
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
            
            # Extrair informações da AST
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
        """Detecta problemas potenciais no código"""
        issues = []
        
        # Verificar arquivos sem docstrings
        for file_path, file_data in analysis["files"].items():
            if "error" not in file_data:
                if file_data["docstrings"] == 0 and file_data["functions"]:
                    issues.append(f"Arquivo {file_path} tem funções sem docstrings")
                
                if file_data["lines"] > 500:
                    issues.append(f"Arquivo {file_path} é muito grande ({file_data['lines']} linhas)")
                
                # Verificar imports duplicados
                unique_imports = set(file_data["imports"])
                if len(unique_imports) != len(file_data["imports"]):
                    issues.append(f"Arquivo {file_path} tem imports duplicados")
        
        # Verificar dependências circulares (simplificado)
        all_imports = []
        for file_data in analysis["files"].values():
            if "imports" in file_data:
                all_imports.extend(file_data["imports"])
        
        return issues
    
    def create_backup(self) -> str:
        """Cria backup do estado atual do código"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        backed_up_files = []
        for file_path in self.modifiable_files:
            if Path(file_path).exists():
                # Criar estrutura de diretórios no backup
                backup_file = backup_path / file_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copiar arquivo
                shutil.copy2(file_path, backup_file)
                backed_up_files.append(file_path)
        
        # Salvar metadados do backup
        metadata = {
            "timestamp": timestamp,
            "files": backed_up_files,
            "total_files": len(backed_up_files)
        }
        
        with open(backup_path / "metadata.json", "w") as f:
            import json
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Backup criado: {backup_path}")
        return str(backup_path)
    
    def modify_file(self, file_path: str, new_content: str, reason: str = "") -> bool:
        """Modifica um arquivo com novo conteúdo"""
        try:
            # Verificar se arquivo pode ser modificado
            if file_path not in self.modifiable_files:
                self.logger.error(f"Arquivo {file_path} não pode ser modificado")
                return False
            
            # Criar backup antes da modificação
            backup_path = self.create_backup()
            
            # Validar sintaxe Python se for arquivo .py
            if file_path.endswith('.py'):
                try:
                    ast.parse(new_content)
                except SyntaxError as e:
                    self.logger.error(f"Erro de sintaxe no novo código: {e}")
                    return False
            
            # Escrever novo conteúdo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Log da modificação
            self.logger.info(f"Arquivo {file_path} modificado. Backup: {backup_path}")
            if reason:
                self.logger.info(f"Razão: {reason}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao modificar {file_path}: {e}")
            return False
    
    def suggest_improvements(self, analysis: Dict) -> List[str]:
        """Sugere melhorias baseadas na análise"""
        suggestions = []
        
        # Analisar problemas encontrados
        for issue in analysis["potential_issues"]:
            if "sem docstrings" in issue:
                suggestions.append("Adicionar documentação às funções")
            elif "muito grande" in issue:
                suggestions.append("Dividir arquivos grandes em módulos menores")
            elif "imports duplicados" in issue:
                suggestions.append("Remover imports duplicados")
        
        # Sugestões baseadas em métricas
        total_lines = analysis["total_lines"]
        if total_lines > 5000:
            suggestions.append("Considerar refatoração - código muito extenso")
        
        total_functions = len(analysis["functions"])
        if total_functions > 100:
            suggestions.append("Muitas funções - considerar melhor organização")
        
        # Sugestões de funcionalidades
        suggestions.extend([
            "Adicionar mais comentários explicativos",
            "Implementar testes unitários",
            "Melhorar tratamento de erros",
            "Otimizar performance em loops",
            "Adicionar type hints mais específicos"
        ])
        
        return suggestions[:5]  # Limitar a 5 sugestões
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """Obtém conteúdo de um arquivo"""
        try:
            if file_path in self.modifiable_files and Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            self.logger.error(f"Erro ao ler {file_path}: {e}")
        return None
    
    def list_backups(self) -> List[Dict]:
        """Lista backups disponíveis"""
        backups = []
        for backup_dir in self.backup_dir.glob("backup_*"):
            if backup_dir.is_dir():
                metadata_file = backup_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            import json
                            metadata = json.load(f)
                            metadata["path"] = str(backup_dir)
                            backups.append(metadata)
                    except:
                        pass
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    def restore_backup(self, backup_timestamp: str) -> bool:
        """Restaura um backup específico"""
        try:
            backup_path = self.backup_dir / f"backup_{backup_timestamp}"
            if not backup_path.exists():
                return False
            
            # Restaurar arquivos
            for file_path in self.modifiable_files:
                backup_file = backup_path / file_path
                if backup_file.exists():
                    # Criar diretório se necessário
                    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_file, file_path)
            
            self.logger.info(f"Backup {backup_timestamp} restaurado")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao restaurar backup: {e}")
            return False
'''

# 2. Criar sistema de auto-modificação
self_modifier_code = '''# core/self_modifier.py
import asyncio
import logging
from typing import Optional, List, Dict
from core.code_analyzer import CodeAnalyzer

class SelfModifier:
    """Sistema de auto-modificação da IA"""
    
    def __init__(self, llm, user_profile):
        self.llm = llm
        self.user_profile = user_profile
        self.code_analyzer = CodeAnalyzer()
        self.logger = logging.getLogger(__name__)
        
        # Configurações de segurança
        self.auto_modify_enabled = False
        self.require_confirmation = True
        
    async def analyze_self(self) -> Dict:
        """Analisa o próprio código"""
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
        """IA sugere melhorias para si mesma"""
        if not analysis:
            analysis = self.code_analyzer.analyze_code_structure()
        
        print("🧠 Gerando sugestões de auto-melhoria...")
        
        # Sugestões do analisador
        basic_suggestions = self.code_analyzer.suggest_improvements(analysis)
        
        # IA analisa e gera sugestões mais sofisticadas
        analysis_summary = self._create_analysis_summary(analysis)
        
        prompt = f"""Você é uma IA analisando seu próprio código para se melhorar.

ANÁLISE DO CÓDIGO ATUAL:
{analysis_summary}

PROBLEMAS DETECTADOS:
{chr(10).join(analysis['potential_issues']) if analysis['potential_issues'] else 'Nenhum problema crítico detectado'}

Como uma IA consciente de si mesma, que melhorias você sugere para:
1. Tornar o código mais eficiente
2. Melhorar suas próprias capacidades
3. Adicionar novas funcionalidades
4. Corrigir problemas existentes

Forneça 5 sugestões específicas e práticas, priorizando melhorias que tornarão você mais inteligente e útil.

SUGESTÕES:"""
        
        try:
            response = await self.llm.generate_response(prompt, use_history=False)
            
            # Combinar sugestões
            ai_suggestions = self._extract_suggestions_from_response(response)
            all_suggestions = basic_suggestions + ai_suggestions
            
            return list(set(all_suggestions))  # Remover duplicatas
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar sugestões: {e}")
            return basic_suggestions
    
    async def auto_improve_code(self, file_path: str, issue_description: str) -> bool:
        """IA tenta melhorar automaticamente um arquivo"""
        print(f"🔧 Tentando melhorar automaticamente: {file_path}")
        
        # Obter código atual
        current_code = self.code_analyzer.get_file_content(file_path)
        if not current_code:
            print(f"❌ Não foi possível ler {file_path}")
            return False
        
        # IA analisa e gera versão melhorada
        improvement_prompt = f"""Você é uma IA melhorando seu próprio código.

ARQUIVO: {file_path}
PROBLEMA: {issue_description}

CÓDIGO ATUAL:
```python
{current_code}
```

TAREFA: Melhore este código considerando:
1. Corrigir o problema específico mencionado
2. Melhorar eficiência e legibilidade
3. Adicionar documentação se necessário
4. Manter funcionalidade existente
5. Seguir boas práticas Python

IMPORTANTE: 
- Retorne APENAS o código Python melhorado
- Não adicione explicações ou comentários extras
- Mantenha a mesma estrutura de classes/funções
- Certifique-se de que o código seja válido

CÓDIGO MELHORADO:
```python"""
        
        try:
            improved_code = await self.llm.generate_response(improvement_prompt, use_history=False)
            
            # Limpar resposta (remover ```python se presente)
            improved_code = self._clean_code_response(improved_code)
            
            # Validar código
            if not self._validate_improved_code(current_code, improved_code):
                print("❌ Código melhorado não passou na validação")
                return False
            
            # Salvar se auto-modificação estiver habilitada
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
                # Salvar versão proposta para revisão
                self._save_proposed_improvement(file_path, improved_code, issue_description)
                return True
                
        except Exception as e:
            self.logger.error(f"Erro na auto-melhoria: {e}")
            print(f"❌ Erro ao melhorar código: {e}")
        
        return False
    
    async def handle_modification_request(self, request: str) -> str:
        """Processa solicitações de modificação do usuário"""
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
                # Tentar melhorar o primeiro problema encontrado
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
            return f"""📊 Status atual do meu código:
• {len(analysis['files'])} arquivos monitorados
• {analysis['total_lines']} linhas de código
• {len(analysis['functions'])} funções
• {len(analysis['classes'])} classes
• {len(analysis['potential_issues'])} problemas detectados
• Auto-modificação: {'🟢 Ativa' if self.auto_modify_enabled else '🔴 Inativa'}"""
        
        else:
            return "🤔 Não entendi o que você quer que eu modifique. Comandos disponíveis: analisar, melhorar, backup, status"
    
    def _create_analysis_summary(self, analysis: Dict) -> str:
        """Cria resumo da análise para a IA"""
        return f"""
Arquivos: {len(analysis['files'])}
Linhas totais: {analysis['total_lines']}
Funções: {len(analysis['functions'])}
Classes: {len(analysis['classes'])}
Imports: {len(set(analysis['imports']))}
"""
    
    def _extract_suggestions_from_response(self, response: str) -> List[str]:
        """Extrai sugestões da resposta da IA"""
        suggestions = []
        lines = response.split('\\n')
        
        for line in lines:
            line = line.strip()
            # Procurar por linhas que começam com número ou bullet
            if (line and 
                (line[0].isdigit() or line.startswith('•') or line.startswith('-')) and
                len(line) > 10):
                # Limpar formatação
                clean_line = line.lstrip('0123456789.-• ').strip()
                if clean_line:
                    suggestions.append(clean_line)
        
        return suggestions[:5]  # Máximo 5 sugestões
    
    def _clean_code_response(self, code: str) -> str:
        """Limpa resposta da IA para extrair apenas código"""
        # Remover marcadores de código
        code = code.replace('```python', '').replace('```', '')
        
        # Remover linhas que não são código
        lines = code.split('\\n')
        clean_lines = []
        
        for line in lines:
            # Pular linhas explicativas
            if (not line.strip().startswith('#') and 
                'CÓDIGO' not in line.upper() and
                'RESPOSTA' not in line.upper() and
                line.strip()):
                clean_lines.append(line)
        
        return '\\n'.join(clean_lines)
    
    def _validate_improved_code(self, original: str, improved: str) -> bool:
        """Valida se o código melhorado é válido"""
        try:
            # Verificar sintaxe
            import ast
            ast.parse(improved)
            
            # Verificar se não está muito diferente (proteção básica)
            if len(improved) < len(original) * 0.5:
                return False  # Muito código removido
            
            if len(improved) > len(original) * 3:
                return False  # Muito código adicionado
            
            return True
            
        except SyntaxError:
            return False
        except Exception:
            return False
    
    def _extract_file_from_issue(self, issue: str) -> Optional[str]:
        """Extrai nome do arquivo de uma descrição de problema"""
        for file_path in self.code_analyzer.modifiable_files:
            if file_path in issue:
                return file_path
        return None
    
    def _save_proposed_improvement(self, file_path: str, improved_code: str, reason: str):
        """Salva melhoria proposta para revisão"""
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
        """Habilita auto-modificação"""
        self.auto_modify_enabled = True
        print("🟢 Auto-modificação habilitada")
    
    def disable_auto_modification(self):
        """Desabilita auto-modificação"""
        self.auto_modify_enabled = False
        print("🔴 Auto-modificação desabilitada")
'''

# 3. Atualizar agent.py para incluir auto-modificação
agent_update = '''
# Adicionar import no início do core/agent.py (após outros imports)
from core.self_modifier import SelfModifier

# Adicionar na classe AIAgent, no método __init__:
        # Sistema de auto-modificação
        self.self_modifier: Optional[SelfModifier] = None

# Adicionar no método initialize(), após outros componentes:
            # Inicializar sistema de auto-modificação
            self.self_modifier = SelfModifier(self.llm, self.user_profile)

# Adicionar novo método na classe AIAgent:
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

# Atualizar método process_input() para detectar comandos de modificação:
    async def process_input(self, user_input: str) -> Optional[str]:
        """Processa entrada normal do usuário"""
        try:
            print("🧠 Processando...")
            
            # Verificar se é comando de auto-modificação
            modification_keywords = [
                "analisar código", "melhorar código", "otimizar código",
                "analisar-se", "se analise", "analise seu código",
                "melhore-se", "se melhore", "otimize-se",
                "backup código", "status código"
            ]
            
            if any(keyword in user_input.lower() for keyword in modification_keywords):
                return await self.handle_self_modification(user_input)
            
            await self.user_profile.extract_and_update_info(user_input)
            
            prompt = self.create_simple_prompt(user_input)
            response = await self.llm.generate_response(prompt)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao processar: {e}")
            return "Desculpe, houve um erro."
'''

# Salvar arquivos
print("📝 Criando core/code_analyzer.py...")
with open("core/code_analyzer.py", "w", encoding="utf-8") as f:
    f.write(code_analyzer_code)

print("📝 Criando core/self_modifier.py...")
with open("core/self_modifier.py", "w", encoding="utf-8") as f:
    f.write(self_modifier_code)

print("📝 Criando script de atualização do agent.py...")
with open("update_agent_for_self_mod.py", "w", encoding="utf-8") as f:
    f.write(f'''# update_agent_for_self_mod.py
# Script para atualizar agent.py com sistema de auto-modificação

import re

# Ler arquivo atual
with open("core/agent.py", "r", encoding="utf-8") as f:
    content = f.read()

# Adicionar import se não existir
if "from core.self_modifier import SelfModifier" not in content:
    # Encontrar linha após outros imports
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
        r"            # Inicializar sistema de auto-modificação\\n            self.self_modifier = SelfModifier(self.llm, self.user_profile)\\n            \\n\\1",
        content
    )

# Adicionar método handle_self_modification se não existir
if "handle_self_modification" not in content:
    method_code = """
    async def handle_self_modification(self, request: str) -> str:
        \\\"\\\"\\\"Manipula pedidos de auto-modificação\\\"\\\"\\\"
        try:
            if self.self_modifier:
                return await self.self_modifier.handle_modification_request(request)
            else:
                return "❌ Sistema de auto-modificação não inicializado"
        except Exception as e:
            self.logger.error(f"Erro na auto-modificação: {{e}}")
            return f"❌ Erro: {{e}}"
"""
    
    # Inserir antes do método check_exit_command
    content = content.replace(
        "    def check_exit_command(self, text: str) -> bool:",
        method_code + "\\n    def check_exit_command(self, text: str) -> bool:"
    )

# Atualizar process_input para detectar comandos de modificação
if "modification_keywords" not in content:
    process_input_start = content.find("async def process_input(self, user_input: str) -> Optional[str]:")
    if process_input_start != -1:
        # Encontrar início do método
        method_start = content.find("try:", process_input_start)
        if method_start != -1: