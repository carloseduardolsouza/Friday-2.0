# test_evolution.py - Teste do sistema de auto-evolução
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
            print("\n🧪 TESTANDO COMANDOS DE EVOLUÇÃO:")
            
            commands = [
                "analise seu código",
                "como está seu código", 
                "melhore seu sistema de voz"
            ]
            
            for cmd in commands:
                print(f"\n📝 Comando: {cmd}")
                try:
                    response = await agent.process_input(cmd)
                    print(f"🤖 Resposta: {response[:100]}...")
                except Exception as e:
                    print(f"❌ Erro: {e}")
            
            print("\n🎉 TESTE CONCLUÍDO!")
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
