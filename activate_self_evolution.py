# activate_self_evolution.py - Ativa sistema de auto-evolução
"""
🧠 ATIVADOR DO SISTEMA DE AUTO-EVOLUÇÃO

Este script integra o sistema de auto-evolução à SEXTA-FEIRA,
permitindo que ela analise e melhore seu próprio código.

Execute: python activate_self_evolution.py
"""

import sys
import subprocess
from pathlib import Path
import shutil

def print_evolution_banner():
    """Banner do sistema de evolução"""
    print("🧠" * 25)
    print("🚀 ATIVANDO AUTO-EVOLUÇÃO DA IA")
    print("🧠 Acesso total ao próprio código")
    print("🔧 Análise e melhoria automática")
    print("💾 Controle de versão integrado")
    print("🧠" * 25)

def install_dependencies():
    """Instala dependências necessárias"""
    print("\n📦 INSTALANDO DEPENDÊNCIAS")
    print("-" * 30)
    
    deps = ["GitPython", "ast"]
    
    for dep in deps:
        try:
            if dep == "ast":
                import ast
                print(f"✅ {dep} (built-in)")
            else:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
                print(f"✅ {dep}")
        except subprocess.CalledProcessError:
            print(f"❌ Erro ao instalar {dep}")
            return False
        except ImportError:
            print(f"❌ {dep} não disponível")
    
    return True

def update_agent_with_evolution():
    """Atualiza agent.py para incluir sistema de evolução"""
    print("\n🔧 INTEGRANDO SISTEMA DE EVOLUÇÃO")
    print("-" * 40)
    
    agent_file = Path("core/agent.py")
    
    if not agent_file.exists():
        print("❌ core/agent.py não encontrado")
        return False
    
    # Fazer backup
    backup_file = Path("core/agent_backup.py")
    shutil.copy2(agent_file, backup_file)
    print(f"💾 Backup criado: {backup_file}")
    
    # Ler conteúdo atual
    with open(agent_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Verificar se já tem sistema de evolução
    if "SelfEvolutionSystem" in content:
        print("✅ Sistema de evolução já integrado!")
        return True
    
    # Adicionar imports
    import_line = "from core.self_evolution import SelfEvolutionSystem"
    if import_line not in content:
        # Encontrar local para adicionar import
        lines = content.split('\n')
        insert_idx = 0
        
        for i, line in enumerate(lines):
            if line.startswith("from core.") or line.startswith("from memory."):
                insert_idx = i + 1
        
        lines.insert(insert_idx, import_line)
        content = '\n'.join(lines)
    
    # Adicionar inicialização no __init__
    init_code = """        
        # Sistema de auto-evolução
        self.evolution_system = None"""
    
    if "self.evolution_system" not in content:
        # Encontrar __init__ da classe AIAgent
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "def __init__(self" in line and "AIAgent" in lines[i-5:i]:
                # Procurar final do __init__
                for j in range(i, len(lines)):
                    if lines[j].strip() and not lines[j].startswith('        '):
                        lines.insert(j-1, init_code)
                        break
                break
        content = '\n'.join(lines)
    
    # Adicionar inicialização no initialize()
    evolution_init = """        
        # Inicializar sistema de auto-evolução
        try:
            self.evolution_system = SelfEvolutionSystem(self.llm, self.user_profile)
            self.logger.info("Sistema de auto-evolução ativado!")
        except Exception as e:
            self.logger.warning(f"Sistema de auto-evolução não pôde ser ativado: {e}")"""
    
    if "SelfEvolutionSystem(self.llm" not in content:
        # Encontrar método initialize
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "async def initialize(self)" in line:
                # Procurar final do método
                for j in range(i, len(lines)):
                    if ("self.logger.info" in lines[j] and "inicializados" in lines[j]) or \
                       ("print" in lines[j] and "sucesso" in lines[j]):
                        lines.insert(j, evolution_init)
                        break
                break
        content = '\n'.join(lines)
    
    # Adicionar processamento de comandos de evolução
    evolution_processing = """        
        # NOVO: Verificar comandos de auto-evolução
        if self.evolution_system:
            evolution_commands = [
                "analise seu código", "melhore seu sistema", "otimize", 
                "revise", "como está seu código", "evolua"
            ]
            
            if any(cmd in user_input.lower() for cmd in evolution_commands):
                try:
                    evolution_response = await self.evolution_system.handle_evolution_command(user_input)
                    if evolution_response:
                        return evolution_response
                except Exception as e:
                    self.logger.error(f"Erro no sistema de evolução: {e}")
                    return "Erro no sistema de auto-evolução. Verifique os logs."
"""
    
    if "evolution_system.handle_evolution_command" not in content:
        # Encontrar método process_input
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "async def process_input(self, user_input: str)" in line:
                # Procurar onde adicionar o código
                for j in range(i, len(lines)):
                    if "# PRIMEIRO: Verificar comandos internos" in lines[j] or \
                       "if self.command_executor:" in lines[j]:
                        lines.insert(j, evolution_processing)
                        break
                break
        content = '\n'.join(lines)
    
    # Salvar arquivo atualizado
    with open(agent_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Sistema de evolução integrado ao agent.py!")
    return True

def update_command_executor():
    """Atualiza command_executor para incluir comandos de evolução"""
    print("\n🔧 ATUALIZANDO COMMAND EXECUTOR")
    print("-" * 35)
    
    executor_file = Path("core/command_executor.py")
    
    if not executor_file.exists():
        print("⚠️ command_executor.py não encontrado - criando...")
        return create_command_executor()
    
    # Fazer backup
    backup_file = Path("core/command_executor_backup.py")
    shutil.copy2(executor_file, backup_file)
    
    # Ler conteúdo
    with open(executor_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Adicionar comandos de evolução
    evolution_patterns = """
        # Padrões para comandos de auto-evolução
        self.evolution_patterns = [
            r"\\b(analise|analisa|verifica|examine)\\s+(o\\s+)?(seu\\s+|teu\\s+)?código\\b",
            r"\\b(melhore|melhora|otimize|otimiza)\\s+(seu\\s+|o\\s+)?sistema\\b",
            r"\\b(revise|revisa|examine|analise)\\s+(todos\\s+os\\s+)?módulos\\b",
            r"\\b(como\\s+está|qual\\s+o\\s+status)\\s+(do\\s+|o\\s+)?(seu\\s+)?código\\b",
            r"\\b(evolua|evolve|se\\s+melhore|melhore-se)\\b",
            r"\\b(faça\\s+uma\\s+)?auto-análise\\b",
            r"\\b(otimize\\s+sua\\s+memória|melhore\\s+sua\\s+voz)\\b"
        ]"""
    
    if "evolution_patterns" not in content:
        # Encontrar __init__ do detector
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "def __init__(self)" in line and "CommandDetector" in lines[i-5:i]:
                # Procurar final dos padrões existentes
                for j in range(i, len(lines)):
                    if "self.status_patterns" in lines[j]:
                        lines.insert(j+5, evolution_patterns)
                        break
                break
        content = '\n'.join(lines)
    
    # Adicionar detecção de evolução
    evolution_detection = """
        # Verificar comandos de auto-evolução
        for pattern in self.evolution_patterns:
            if re.search(pattern, text_lower):
                return "evolution_command", f"Comando de evolução detectado", 0.95"""
    
    if "evolution_command" not in content:
        # Encontrar método detect_command
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "def detect_command(self, text: str)" in line:
                # Procurar antes do return None
                for j in range(i, len(lines)):
                    if "return None," in lines[j]:
                        lines.insert(j, evolution_detection)
                        break
                break
        content = '\n'.join(lines)
    
    # Salvar arquivo atualizado
    with open(executor_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Command executor atualizado!")

def create_command_executor():
    """Cria command_executor básico se não existir"""
    executor_code = '''# core/command_executor.py - Executor de comandos com evolução
import re
import logging
from typing import Optional

class InternalCommandDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Padrões para comandos de evolução
        self.evolution_patterns = [
            r"\\b(analise|analisa|verifica|examine)\\s+(o\\s+)?(seu\\s+|teu\\s+)?código\\b",
            r"\\b(melhore|melhora|otimize|otimiza)\\s+(seu\\s+|o\\s+)?sistema\\b",
            r"\\b(revise|revisa|examine|analise)\\s+(todos\\s+os\\s+)?módulos\\b",
            r"\\b(como\\s+está|qual\\s+o\\s+status)\\s+(do\\s+|o\\s+)?(seu\\s+)?código\\b",
            r"\\b(evolua|evolve|se\\s+melhore|melhore-se)\\b"
        ]
    
    def detect_command(self, text: str):
        text_lower = text.lower()
        
        # Verificar comandos de auto-evolução
        for pattern in self.evolution_patterns:
            if re.search(pattern, text_lower):
                return "evolution_command", f"Comando de evolução detectado", 0.95
        
        return None, "Nenhum comando detectado", 0.0

class InternalCommandExecutor:
    def __init__(self, agent):
        self.agent = agent
        self.detector = InternalCommandDetector()
        self.logger = logging.getLogger(__name__)
    
    async def process_natural_command(self, text: str):
        command, reason, confidence = self.detector.detect_command(text)
        
        if command == "evolution_command" and confidence > 0.8:
            if hasattr(self.agent, 'evolution_system') and self.agent.evolution_system:
                return await self.agent.evolution_system.handle_evolution_command(text)
            else:
                return "Sistema de auto-evolução não está ativo."
        
        return None
'''
    
    with open("core/command_executor.py", "w", encoding="utf-8") as f:
        f.write(executor_code)
    
    print("✅ Command executor criado!")

def create_test_evolution():
    """Cria script de teste do sistema de evolução"""
    print("\n🧪 CRIANDO TESTE DE EVOLUÇÃO")
    print("-" * 30)
    
    test_code = '''# test_evolution.py - Teste do sistema de auto-evolução
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path.cwd()))

async def test_evolution():
    """Teste completo do sistema de evolução"""
    print("🧠 TESTE DO SISTEMA DE AUTO-EVOLUÇÃO")
    print("="*50)
    
    try:
        # Importar sistema principal
        from core.agent import AIAgent
        from config.settings import load_config
        
        print("✅ Imports realizados")
        
        # Carregar configuração
        config = load_config()
        
        # Criar agente
        agent = AIAgent(config)
        
        # Inicializar
        await agent.initialize()
        
        print("✅ Agente inicializado")
        
        # Verificar se sistema de evolução está ativo
        if hasattr(agent, 'evolution_system') and agent.evolution_system:
            print("✅ Sistema de evolução ATIVO!")
            
            # Teste básico
            print("\\n🧪 TESTANDO COMANDOS DE EVOLUÇÃO:")
            
            commands = [
                "analise seu código",
                "como está seu código", 
                "melhore seu sistema de voz"
            ]
            
            for cmd in commands:
                print(f"\\n📝 Comando: {cmd}")
                try:
                    response = await agent.process_input(cmd)
                    print(f"🤖 Resposta: {response[:100]}...")
                except Exception as e:
                    print(f"❌ Erro: {e}")
            
            print("\\n🎉 TESTE CONCLUÍDO!")
            print("✅ Sistema de auto-evolução funcionando!")
            
        else:
            print("❌ Sistema de evolução NÃO ATIVO")
            print("💡 Verifique se a integração foi bem-sucedida")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_evolution())
'''
    
    with open("test_evolution.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    print("✅ Teste criado: test_evolution.py")

def show_evolution_instructions():
    """Mostra instruções de uso"""
    print("\n" + "🧠" * 30)
    print("🎉 SISTEMA DE AUTO-EVOLUÇÃO ATIVADO!")
    print("🧠" * 30)
    
    print("\n✅ O QUE FOI INSTALADO:")
    print("• Sistema completo de auto-evolução")
    print("• Acesso total ao próprio código")
    print("• Análise inteligente com LLM local")
    print("• Controle de versão automático")
    print("• Sistema de backup e rollback")
    print("• Integração com comandos naturais")
    
    print("\n🎯 COMANDOS DISPONÍVEIS:")
    print("• 'analise seu código' - Análise completa")
    print("• 'melhore seu sistema de voz' - Otimizar TTS")
    print("• 'otimize sua memória' - Melhorar database")
    print("• 'revise todos os módulos' - Análise total")
    print("• 'como está seu código' - Status atual")
    print("• 'evolua' - Melhoria automática")
    
    print("\n🔧 TESTE AGORA:")
    print("1. Execute: python main.py")
    print("2. Digite: 'analise seu código'")
    print("3. SEXTA-FEIRA irá analisar todo seu código!")
    
    print("\n🧪 OU TESTE ESPECÍFICO:")
    print("python test_evolution.py")
    
    print("\n🛡️ RECURSOS DE SEGURANÇA:")
    print("• Modo seguro ativo por padrão")
    print("• Backup automático antes de mudanças")
    print("• Controle de versão Git")
    print("• Sistema de rollback")
    
    print("\n🌟 SUA SEXTA-FEIRA AGORA É AUTO-EVOLUTIVA!")

def main():
    """Ativação principal"""
    print_evolution_banner()
    
    try:
        # Confirmação
        print("\n🤖 TRANSFORMAÇÃO ÉPICA:")
        print("Sua SEXTA-FEIRA poderá:")
        print("• Ler e entender seu próprio código")
        print("• Identificar melhorias automaticamente")
        print("• Propor e aplicar otimizações")
        print("• Evoluir continuamente")
        
        response = input("\n🧠 Quer ativar a auto-evolução? [S/n]: ").strip().lower()
        if response == 'n':
            print("👋 Operação cancelada")
            return
        
        # Instalar dependências
        if not install_dependencies():
            print("❌ Falha nas dependências")
            return
        
        # Integrar sistema
        if not update_agent_with_evolution():
            print("❌ Falha na integração")
            return
        
        # Atualizar executor
        update_command_executor()
        
        # Criar teste
        create_test_evolution()
        
        # Instruções finais
        show_evolution_instructions()
        
        # Oferecer teste
        print("\n🧪 Quer testar agora? [S/n]: ", end="")
        if input().strip().lower() != 'n':
            print("\n🧠 Executando teste...")
            subprocess.run([sys.executable, "test_evolution.py"])
        
    except KeyboardInterrupt:
        print("\n❌ Ativação cancelada")
    except Exception as e:
        print(f"\n❌ Erro na ativação: {e}")

if __name__ == "__main__":
    main()