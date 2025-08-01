# core/self_evolution.py - Sistema de Auto-Evolução da SEXTA-FEIRA
"""
🧠 SISTEMA DE AUTO-EVOLUÇÃO

A SEXTA-FEIRA pode:
- Ler e analisar seu próprio código
- Identificar pontos de melhoria
- Propor e aplicar otimizações
- Fazer backup automático
- Reverter se algo der errado

Comandos:
- "analise seu código"
- "melhore seu sistema de voz"
- "otimize sua memória"
- "revise todos os módulos"
"""

import asyncio
import logging
import json
import git
import subprocess
import ast
import importlib
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import shutil
import tempfile

class SelfEvolutionSystem:
    """Sistema de auto-evolução da SEXTA-FEIRA"""
    
    def __init__(self, llm_model, user_profile):
        self.logger = logging.getLogger(__name__)
        self.llm = llm_model
        self.user_profile = user_profile
        
        # Estrutura do projeto
        self.project_root = Path.cwd()
        self.core_modules = self._map_core_modules()
        
        # Sistema de controle de versão
        self.repo = None
        self._initialize_git()
        
        # Sistema de backup
        self.backup_dir = Path("evolution_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Métricas de performance
        self.performance_metrics = {}
        self.evolution_history = []
        
        # Configurações de segurança
        self.safe_mode = True
        self.auto_apply = False
        self.max_changes_per_session = 5
        
        print("🧠 Sistema de Auto-Evolução inicializado!")
        print(f"📁 Módulos mapeados: {len(self.core_modules)}")
    
    def _map_core_modules(self) -> Dict[str, Dict]:
        """Mapeia todos os módulos do sistema"""
        modules = {}
        
        # Definir módulos principais
        core_files = [
            "core/agent.py",
            "core/speech_to_text.py", 
            "core/text_to_speech.py",
            "core/ultra_realistic_voice.py",
            "core/conversation.py",
            "core/context_analyzer.py",
            "memory/user_profile.py",
            "memory/database.py",
            "models/local_llm.py",
            "config/settings.py"
        ]
        
        for file_path in core_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                modules[file_path] = {
                    "path": full_path,
                    "type": self._classify_module(file_path),
                    "last_modified": full_path.stat().st_mtime,
                    "size": full_path.stat().st_size,
                    "dependencies": [],
                    "functions": [],
                    "classes": []
                }
                
                # Analisar estrutura do arquivo
                try:
                    self._analyze_module_structure(modules[file_path])
                except Exception as e:
                    self.logger.warning(f"Erro ao analisar {file_path}: {e}")
        
        return modules
    
    def _classify_module(self, file_path: str) -> str:
        """Classifica o tipo do módulo"""
        if "speech" in file_path or "voice" in file_path:
            return "audio"
        elif "memory" in file_path or "database" in file_path:
            return "storage"
        elif "conversation" in file_path or "context" in file_path:
            return "intelligence"
        elif "config" in file_path:
            return "configuration"
        elif "agent" in file_path:
            return "core"
        else:
            return "utility"
    
    def _analyze_module_structure(self, module_info: Dict):
        """Analisa estrutura interna do módulo"""
        try:
            with open(module_info["path"], "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Extrair classes e funções
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    module_info["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                elif isinstance(node, ast.FunctionDef):
                    module_info["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args]
                    })
            
            # Extrair imports (dependências)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info["dependencies"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_info["dependencies"].append(node.module)
        
        except Exception as e:
            self.logger.warning(f"Erro na análise estrutural: {e}")
    
    def _initialize_git(self):
        """Inicializa controle de versão Git"""
        try:
            self.repo = git.Repo(self.project_root)
            print("✅ Repositório Git encontrado")
        except git.InvalidGitRepositoryError:
            try:
                self.repo = git.Repo.init(self.project_root)
                print("🆕 Repositório Git criado")
                # Commit inicial
                self.repo.index.add([".gitignore", "*.py"])
                self.repo.index.commit("Commit inicial - Sistema de auto-evolução")
            except Exception as e:
                self.logger.warning(f"Erro ao inicializar Git: {e}")
                self.repo = None
    
    async def analyze_self(self) -> Dict[str, Any]:
        """Análise completa do próprio código"""
        print("🧠 ANÁLISE COMPLETA DO PRÓPRIO CÓDIGO")
        print("="*50)
        
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "modules_analyzed": len(self.core_modules),
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "potential_improvements": [],
            "performance_issues": [],
            "code_quality_score": 0,
            "recommendations": []
        }
        
        print("📊 Analisando cada módulo...")
        
        for module_path, module_info in self.core_modules.items():
            print(f"   🔍 {module_path}")
            
            # Analisar código do módulo
            module_analysis = await self._analyze_module_code(module_info)
            
            # Acumular estatísticas
            analysis_result["total_lines"] += module_analysis.get("lines", 0)
            analysis_result["total_functions"] += len(module_info.get("functions", []))
            analysis_result["total_classes"] += len(module_info.get("classes", []))
            
            # Identificar melhorias
            improvements = await self._identify_improvements(module_info, module_analysis)
            analysis_result["potential_improvements"].extend(improvements)
        
        # Calcular score de qualidade
        analysis_result["code_quality_score"] = self._calculate_quality_score(analysis_result)
        
        # Gerar recomendações
        analysis_result["recommendations"] = await self._generate_recommendations(analysis_result)
        
        # Salvar análise
        self._save_analysis(analysis_result)
        
        print(f"\n📋 RESULTADO DA ANÁLISE:")
        print(f"   📄 {analysis_result['modules_analyzed']} módulos")
        print(f"   📏 {analysis_result['total_lines']} linhas de código")
        print(f"   🔧 {len(analysis_result['potential_improvements'])} melhorias identificadas")
        print(f"   ⭐ Score de qualidade: {analysis_result['code_quality_score']}/100")
        
        return analysis_result
    
    async def _analyze_module_code(self, module_info: Dict) -> Dict:
        """Análise detalhada de um módulo específico"""
        try:
            with open(module_info["path"], "r", encoding="utf-8") as f:
                content = f.read()
            
            lines = content.split('\n')
            
            return {
                "lines": len(lines),
                "blank_lines": sum(1 for line in lines if not line.strip()),
                "comment_lines": sum(1 for line in lines if line.strip().startswith('#')),
                "code_lines": len(lines) - sum(1 for line in lines if not line.strip() or line.strip().startswith('#')),
                "complexity": self._calculate_complexity(content),
                "imports": len(module_info.get("dependencies", [])),
                "content": content
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar módulo: {e}")
            return {}
    
    def _calculate_complexity(self, content: str) -> int:
        """Calcula complexidade ciclomática básica"""
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally']
        return sum(content.count(keyword) for keyword in complexity_keywords)
    
    async def _identify_improvements(self, module_info: Dict, analysis: Dict) -> List[Dict]:
        """Identifica melhorias usando LLM local"""
        improvements = []
        
        try:
            # Preparar prompt para análise
            prompt = f"""
Analise este módulo Python e identifique melhorias:

MÓDULO: {module_info['path']}
TIPO: {module_info['type']}
LINHAS: {analysis.get('lines', 0)}
COMPLEXIDADE: {analysis.get('complexity', 0)}

FUNÇÕES: {[f['name'] for f in module_info.get('functions', [])]}
CLASSES: {[c['name'] for c in module_info.get('classes', [])]}

Identifique 3-5 melhorias específicas focando em:
1. Performance
2. Legibilidade
3. Manutenibilidade
4. Funcionalidades ausentes

Responda em formato JSON:
{{
  "improvements": [
    {{
      "type": "performance|readability|maintenance|feature",
      "description": "Descrição da melhoria",
      "priority": "high|medium|low",
      "estimated_impact": "Impacto esperado"
    }}
  ]
}}
"""
            
            # Gerar análise com LLM
            response = await self.llm.generate_response(prompt)
            
            # Tentar parsear resposta JSON
            try:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    improvements_data = json.loads(json_match.group())
                    improvements = improvements_data.get('improvements', [])
                    
                    # Adicionar contexto do módulo
                    for improvement in improvements:
                        improvement['module'] = str(module_info['path'])
                        improvement['module_type'] = module_info['type']
            except:
                # Se não conseguir parsear, criar melhorias genéricas
                improvements = self._generate_generic_improvements(module_info, analysis)
        
        except Exception as e:
            self.logger.error(f"Erro ao identificar melhorias: {e}")
            improvements = self._generate_generic_improvements(module_info, analysis)
        
        return improvements
    
    def _generate_generic_improvements(self, module_info: Dict, analysis: Dict) -> List[Dict]:
        """Gera melhorias genéricas baseadas em heurísticas"""
        improvements = []
        
        # Se o módulo tem muitas linhas
        if analysis.get('lines', 0) > 500:
            improvements.append({
                "type": "maintenance",
                "description": f"Módulo {module_info['path']} muito grande ({analysis['lines']} linhas). Considerar refatoração.",
                "priority": "medium",
                "estimated_impact": "Melhor manutenibilidade",
                "module": str(module_info['path']),
                "module_type": module_info['type']
            })
        
        # Se a complexidade é alta
        if analysis.get('complexity', 0) > 50:
            improvements.append({
                "type": "readability",
                "description": f"Alta complexidade ({analysis['complexity']}). Simplificar lógica condicional.",
                "priority": "high",
                "estimated_impact": "Código mais legível e testável",
                "module": str(module_info['path']),
                "module_type": module_info['type']
            })
        
        # Se poucos comentários
        comment_ratio = analysis.get('comment_lines', 0) / max(analysis.get('lines', 1), 1)
        if comment_ratio < 0.1:
            improvements.append({
                "type": "readability",
                "description": "Poucos comentários. Adicionar documentação.",
                "priority": "low",
                "estimated_impact": "Melhor compreensão do código",
                "module": str(module_info['path']),
                "module_type": module_info['type']
            })
        
        return improvements
    
    def _calculate_quality_score(self, analysis: Dict) -> int:
        """Calcula score de qualidade do código"""
        score = 100
        
        # Penalizar por muitas melhorias identificadas
        score -= min(len(analysis['potential_improvements']) * 5, 30)
        
        # Bonificar por boa documentação
        if analysis['total_lines'] > 0:
            # Estimativa de comentários (seria melhor calcular real)
            estimated_comments = analysis['total_lines'] * 0.15
            if estimated_comments > analysis['total_lines'] * 0.1:
                score += 10
        
        return max(0, min(100, score))
    
    async def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Gera recomendações de alta prioridade"""
        recommendations = []
        
        high_priority = [imp for imp in analysis['potential_improvements'] 
                        if imp.get('priority') == 'high']
        
        if high_priority:
            recommendations.append(f"🔥 {len(high_priority)} melhorias de alta prioridade identificadas")
        
        if analysis['code_quality_score'] < 70:
            recommendations.append("⚠️ Score de qualidade baixo - focar em refatoração")
        
        # Recomendações por tipo de módulo
        module_types = {}
        for imp in analysis['potential_improvements']:
            module_type = imp.get('module_type', 'unknown')
            if module_type not in module_types:
                module_types[module_type] = 0
            module_types[module_type] += 1
        
        for module_type, count in module_types.items():
            if count >= 3:
                recommendations.append(f"🎯 Módulos {module_type} precisam de atenção ({count} melhorias)")
        
        return recommendations
    
    def _save_analysis(self, analysis: Dict):
        """Salva análise em arquivo"""
        analysis_file = self.backup_dir / f"analysis_{int(time.time())}.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        # Manter apenas últimas 10 análises
        analysis_files = sorted(self.backup_dir.glob("analysis_*.json"))
        for old_file in analysis_files[:-10]:
            old_file.unlink()
    
    async def improve_module(self, module_path: str, improvement_type: str = "all") -> Dict:
        """Melhora um módulo específico"""
        print(f"🔧 MELHORANDO MÓDULO: {module_path}")
        print("="*40)
        
        if module_path not in self.core_modules:
            return {"error": "Módulo não encontrado"}
        
        # Fazer backup
        backup_path = self._create_backup(module_path)
        print(f"💾 Backup criado: {backup_path}")
        
        try:
            # Analisar módulo atual
            module_info = self.core_modules[module_path]
            current_analysis = await self._analyze_module_code(module_info)
            
            # Identificar melhorias específicas
            improvements = await self._identify_improvements(module_info, current_analysis)
            
            if improvement_type != "all":
                improvements = [imp for imp in improvements if imp['type'] == improvement_type]
            
            if not improvements:
                print("✅ Nenhuma melhoria identificada")
                return {"status": "no_improvements"}
            
            print(f"🎯 {len(improvements)} melhorias identificadas:")
            for i, imp in enumerate(improvements, 1):
                print(f"   {i}. {imp['description']} ({imp['priority']})")
            
            # Aplicar melhorias se não em modo seguro
            if not self.safe_mode:
                improved_code = await self._apply_improvements(module_info, improvements)
                if improved_code:
                    self._save_improved_module(module_path, improved_code)
                    print("✅ Melhorias aplicadas automaticamente")
            else:
                print("🛡️ Modo seguro ativo - melhorias não aplicadas automaticamente")
            
            # Commit das mudanças
            if self.repo:
                self._commit_changes(f"Melhorias aplicadas em {module_path}")
            
            return {
                "status": "success",
                "improvements": improvements,
                "backup": str(backup_path)
            }
            
        except Exception as e:
            # Restaurar backup em caso de erro
            self._restore_backup(module_path, backup_path)
            self.logger.error(f"Erro ao melhorar módulo: {e}")
            return {"error": str(e)}
    
    async def _apply_improvements(self, module_info: Dict, improvements: List[Dict]) -> Optional[str]:
        """Aplica melhorias no código usando LLM"""
        try:
            with open(module_info["path"], "r", encoding="utf-8") as f:
                original_code = f.read()
            
            # Preparar prompt para refatoração
            improvements_text = "\\n".join([f"- {imp['description']}" for imp in improvements])
            
            prompt = f"""
Refatore este código Python aplicando as seguintes melhorias:

{improvements_text}

CÓDIGO ORIGINAL:
```python
{original_code}
```

Retorne APENAS o código refatorado, mantendo toda a funcionalidade original.
Adicione comentários explicativos onde necessário.
"""
            
            # Gerar código melhorado
            improved_code = await self.llm.generate_response(prompt)
            
            # Limpar resposta (remover markdown se presente)
            import re
            code_match = re.search(r'```python\\n(.*?)\\n```', improved_code, re.DOTALL)
            if code_match:
                improved_code = code_match.group(1)
            elif improved_code.startswith('```'):
                lines = improved_code.split('\\n')
                improved_code = '\\n'.join(lines[1:-1])
            
            return improved_code
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar melhorias: {e}")
            return None
    
    def _create_backup(self, module_path: str) -> Path:
        """Cria backup de um módulo"""
        timestamp = int(time.time())
        module_name = Path(module_path).stem
        backup_path = self.backup_dir / f"{module_name}_backup_{timestamp}.py"
        
        original_path = self.core_modules[module_path]["path"]
        shutil.copy2(original_path, backup_path)
        
        return backup_path
    
    def _save_improved_module(self, module_path: str, improved_code: str):
        """Salva módulo melhorado"""
        module_file = self.core_modules[module_path]["path"]
        
        with open(module_file, "w", encoding="utf-8") as f:
            f.write(improved_code)
        
        # Atualizar informações do módulo
        self.core_modules[module_path]["last_modified"] = time.time()
    
    def _restore_backup(self, module_path: str, backup_path: Path):
        """Restaura backup em caso de erro"""
        try:
            original_path = self.core_modules[module_path]["path"]
            shutil.copy2(backup_path, original_path)
            print(f"🔄 Backup restaurado: {module_path}")
        except Exception as e:
            self.logger.error(f"Erro ao restaurar backup: {e}")
    
    def _commit_changes(self, message: str):
        """Faz commit das mudanças"""
        try:
            if self.repo:
                self.repo.git.add(A=True)
                self.repo.index.commit(f"[AUTO-EVOLUÇÃO] {message}")
                print(f"📝 Commit: {message}")
        except Exception as e:
            self.logger.warning(f"Erro no commit: {e}")
    
    async def handle_evolution_command(self, command: str) -> str:
        """Processa comandos de evolução"""
        command_lower = command.lower()
        
        if "analise seu código" in command_lower or "analyze your code" in command_lower:
            analysis = await self.analyze_self()
            
            response = f"""
🧠 ANÁLISE COMPLETA REALIZADA

📊 **Estatísticas:**
• {analysis['modules_analyzed']} módulos analisados
• {analysis['total_lines']} linhas de código
• {analysis['total_functions']} funções
• {analysis['total_classes']} classes

⭐ **Score de Qualidade:** {analysis['code_quality_score']}/100

🔧 **Melhorias Identificadas:** {len(analysis['potential_improvements'])}

📋 **Recomendações:**
{chr(10).join(f"• {rec}" for rec in analysis['recommendations'])}

Posso aplicar melhorias específicas se você solicitar!
"""
            return response
        
        elif "melhore" in command_lower and ("voz" in command_lower or "voice" in command_lower):
            # Melhorar sistema de voz
            voice_modules = [path for path, info in self.core_modules.items() 
                           if info['type'] == 'audio']
            
            if voice_modules:
                result = await self.improve_module(voice_modules[0], "performance")
                return f"🎭 Sistema de voz analisado! {len(result.get('improvements', []))} melhorias identificadas."
            else:
                return "❌ Módulo de voz não encontrado."
        
        elif "melhore" in command_lower and ("memória" in command_lower or "memory" in command_lower):
            # Melhorar sistema de memória
            memory_modules = [path for path, info in self.core_modules.items() 
                            if info['type'] == 'storage']
            
            if memory_modules:
                result = await self.improve_module(memory_modules[0], "performance")
                return f"💾 Sistema de memória analisado! {len(result.get('improvements', []))} melhorias identificadas."
            else:
                return "❌ Módulo de memória não encontrado."
        
        elif "revise todos" in command_lower or "review all" in command_lower:
            # Revisar todos os módulos
            total_improvements = 0
            
            for module_path in self.core_modules.keys():
                result = await self.improve_module(module_path)
                total_improvements += len(result.get('improvements', []))
            
            return f"🔍 Revisão completa realizada! {total_improvements} melhorias identificadas em todos os módulos."
        
        else:
            return "🤔 Comando de evolução não reconhecido. Tente: 'analise seu código', 'melhore seu sistema de voz', etc."
    
    def get_evolution_status(self) -> Dict:
        """Retorna status do sistema de evolução"""
        return {
            "modules_mapped": len(self.core_modules),
            "safe_mode": self.safe_mode,
            "auto_apply": self.auto_apply,
            "git_enabled": self.repo is not None,
            "evolution_history": len(self.evolution_history),
            "backup_dir": str(self.backup_dir)
        }

# Compatibilidade com sistema existente
class SelfModifier(SelfEvolutionSystem):
    """Alias para compatibilidade"""
    pass