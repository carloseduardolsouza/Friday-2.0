# evolution_demo.py - Demonstração do sistema de auto-evolução
"""
🧠 DEMONSTRAÇÃO DO SISTEMA DE AUTO-EVOLUÇÃO

Este script mostra todos os recursos do sistema de auto-evolução
da SEXTA-FEIRA em ação.

Execute: python evolution_demo.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path.cwd()))

async def demo_self_analysis():
    """Demonstra auto-análise do código"""
    print("🧠 DEMO: AUTO-ANÁLISE DO CÓDIGO")
    print("="*40)
    
    try:
        from core.self_evolution import SelfEvolutionSystem
        from models.local_llm import LocalLLM
        from memory.user_profile import UserProfile
        from memory.database import DatabaseManager
        from config.settings import load_config
        
        # Configurar sistema
        config = load_config()
        db = DatabaseManager(config.database)
        await db.initialize()
        
        profile = UserProfile(db)
        await profile.load_profile()
        
        llm = LocalLLM(config.model)
        await llm.initialize()
        
        # Criar sistema de evolução
        evolution = SelfEvolutionSystem(llm, profile)
        
        print("✅ Sistema de evolução inicializado")
        
        # Demonstrar análise
        print("\n🔍 Realizando auto-análise...")
        analysis = await evolution.analyze_self()
        
        print(f"\n📊 RESULTADOS:")
        print(f"   📄 Módulos: {analysis['modules_analyzed']}")
        print(f"   📏 Linhas: {analysis['total_lines']}")
        print(f"   🔧 Melhorias: {len(analysis['potential_improvements'])}")
        print(f"   ⭐ Score: {analysis['code_quality_score']}/100")
        
        # Mostrar algumas melhorias
        if analysis['potential_improvements']:
            print(f"\n🔧 MELHORIAS IDENTIFICADAS:")
            for i, imp in enumerate(analysis['potential_improvements'][:3], 1):
                print(f"   {i}. {imp['description']} ({imp['priority']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na demo: {e}")
        return False

async def demo_module_improvement():
    """Demonstra melhoria de módulo específico"""
    print("\n🔧 DEMO: MELHORIA DE MÓDULO")
    print("="*35)
    
    try:
        from core.self_evolution import SelfEvolutionSystem
        from models.local_llm import LocalLLM
        from memory.user_profile import UserProfile
        from memory.database import DatabaseManager
        from config.settings import load_config
        
        # Configurar sistema
        config = load_config()
        db = DatabaseManager(config.database)
        await db.initialize()
        
        profile = UserProfile(db)
        await profile.load_profile()
        
        llm = LocalLLM(config.model)
        await llm.initialize()
        
        evolution = SelfEvolutionSystem(llm, profile)
        
        # Demonstrar melhoria de módulo
        voice_modules = [path for path, info in evolution.core_modules.items() 
                        if 'voice' in path.lower() or 'speech' in path.lower()]
        
        if voice_modules:
            module_path = voice_modules[0]
            print(f"🎭 Analisando módulo: {module_path}")
            
            result = await evolution.improve_module(module_path)
            
            if 'improvements' in result:
                print(f"✅ {len(result['improvements'])} melhorias identificadas!")
                
                for i, imp in enumerate(result['improvements'][:2], 1):
                    print(f"   {i}. {imp['description']}")
            else:
                print("ℹ️ Nenhuma melhoria necessária no momento")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na demo: {e}")
        return False

async def demo_evolution_commands():
    """Demonstra comandos de evolução"""
    print("\n💬 DEMO: COMANDOS DE EVOLUÇÃO")
    print("="*35)
    
    try:
        from core.self_evolution import SelfEvolutionSystem
        from models.local_llm import LocalLLM
        from memory.user_profile import UserProfile
        from memory.database import DatabaseManager
        from config.settings import load_config
        
        # Configurar sistema
        config = load_config()
        db = DatabaseManager(config.database)
        await db.initialize()
        
        profile = UserProfile(db)
        await profile.load_profile()
        
        llm = LocalLLM(config.model)
        await llm.initialize()
        
        evolution = SelfEvolutionSystem(llm, profile)
        
        # Demonstrar comandos
        commands = [
            "analise seu código",
            "melhore seu sistema de voz",
            "como está seu código"
        ]
        
        for cmd in commands:
            print(f"\n📝 Comando: '{cmd}'")
            try:
                response = await evolution.handle_evolution_command(cmd)
                print(f"🤖 Resposta: {response[:150]}...")
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na demo: {e}")
        return False

def demo_git_integration():
    """Demonstra integração com Git"""
    print("\n📝 DEMO: INTEGRAÇÃO GIT")
    print("="*25)
    
    try:
        import git
        
        # Verificar se é repositório Git
        repo = git.Repo(Path.cwd())
        
        print("✅ Repositório Git detectado")
        
        # Mostrar commits recentes
        commits = list(repo.iter_commits(max_count=5))
        
        print("📝 Commits recentes:")
        for commit in commits:
            if "[AUTO-EVOLUÇÃO]" in commit.message:
                print(f"   🧠 {commit.message[:50]}...")
            else:
                print(f"   📝 {commit.message[:50]}...")
        
        return True
        
    except git.InvalidGitRepositoryError:
        print("⚠️ Não é um repositório Git")
        print("💡 O sistema criará um automaticamente")
        return True
    except Exception as e:
        print(f"❌ Erro Git: {e}")
        return False

def show_evolution_capabilities():
    """Mostra capacidades do sistema"""
    print("\n🌟 CAPACIDADES DO SISTEMA DE AUTO-EVOLUÇÃO")
    print("="*55)
    
    capabilities = [
        "🔍 Análise completa do próprio código",
        "📊 Métricas de qualidade e complexidade",
        "🔧 Identificação automática de melhorias",
        "🎯 Otimizações baseadas em IA local",
        "💾 Sistema de backup automático",
        "📝 Controle de versão integrado",
        "🛡️ Modo seguro com rollback",
        "🧪 Testes automáticos de validação",
        "💬 Comandos em linguagem natural",
        "🚀 Evolução contínua e automática"
    ]
    
    for cap in capabilities:
        print(f"   {cap}")
    
    print("\n🎯 COMANDOS PRINCIPAIS:")
    commands = [
        "'analise seu código' - Análise completa",
        "'melhore seu sistema de voz' - Otimizar TTS",
        "'otimize sua memória' - Melhorar database",
        "'revise todos os módulos' - Análise total",
        "'como está seu código' - Status atual",
        "'evolua' - Melhoria automática"
    ]
    
    for cmd in commands:
        print(f"   • {cmd}")

async def run_complete_demo():
    """Executa demonstração completa"""
    print("🧠" * 30)
    print("🎭 DEMONSTRAÇÃO COMPLETA DO SISTEMA DE AUTO-EVOLUÇÃO")
    print("🧠" * 30)
    
    print("\n🎯 Esta demo mostra:")
    print("• Como a SEXTA-FEIRA analisa seu próprio código")
    print("• Como identifica e propõe melhorias")
    print("• Como responde a comandos de evolução")
    print("• Integração com controle de versão")
    
    input("\nPressione ENTER para continuar...")
    
    # Executar demos
    demos = [
        ("Auto-análise", demo_self_analysis),
        ("Melhoria de módulo", demo_module_improvement),
        ("Comandos de evolução", demo_evolution_commands),
        ("Integração Git", demo_git_integration)
    ]
    
    results = []
    
    for name, demo_func in demos:
        print(f"\n{'='*60}")
        try:
            if asyncio.iscoroutinefunction(demo_func):
                success = await demo_func()
            else:
                success = demo_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Erro em {name}: {e}")
            results.append((name, False))
    
    # Mostrar resultados
    print(f"\n{'='*60}")
    print("📊 RESULTADOS DA DEMONSTRAÇÃO")
    print("="*30)
    
    for name, success in results:
        status = "✅ SUCESSO" if success else "❌ FALHOU"
        print(f"   {name}: {status}")
    
    # Mostrar capacidades
    show_evolution_capabilities()
    
    print(f"\n{'🧠' * 30}")
    print("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
    print("🌟 Sistema de auto-evolução em funcionamento!")
    print("🧠" * 30)

def main():
    """Demo principal"""
    try:
        # Verificar se sistema está disponível
        try:
            from core.self_evolution import SelfEvolutionSystem
            print("✅ Sistema de auto-evolução disponível")
        except ImportError:
            print("❌ Sistema de auto-evolução não instalado")
            print("💡 Execute: python activate_self_evolution.py")
            return
        
        # Executar demo
        asyncio.run(run_complete_demo())
        
    except KeyboardInterrupt:
        print("\n❌ Demo cancelada")
    except Exception as e:
        print(f"\n❌ Erro na demo: {e}")

if __name__ == "__main__":
    main()