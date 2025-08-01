# main.py - Arquivo principal do agente
import asyncio
import logging
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from core.agent import AIAgent
from config.settings import load_config

def setup_logging():
    """Configura o sistema de logs"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/agent.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

async def main():
    """Função principal do agente"""
    print("🤖 Iniciando Agente IA Offline...")
    setup_logging()
    
    try:
        # Carregar configurações
        config = load_config()
        
        # Criar instância do agente
        agent = AIAgent(config)
        
        # Inicializar o agente
        await agent.initialize()
        
        print("✅ Agente inicializado com sucesso!")
        print("🎤 Diga 'Olá' para começar ou 'sair' para encerrar")
        
        # Loop principal
        await agent.run()
        
    except KeyboardInterrupt:
        print("\n👋 Encerrando agente...")
    except Exception as e:
        logging.error(f"Erro crítico: {e}")
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(main())