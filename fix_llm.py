# fix_llm.py
import os

# Remover arquivo problemático
if os.path.exists("models/local_llm.py"):
    os.remove("models/local_llm.py")
    print("Arquivo local_llm.py problemático removido!")

# Criar novo arquivo local_llm.py corrigido
llm_code = """# models/local_llm.py
import asyncio
import logging
import ollama
from typing import Optional, Dict, Any, List
from config.settings import ModelConfig

class LocalLLM:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = ollama.AsyncClient()
        self.conversation_history: List[Dict[str, str]] = []
        
    async def initialize(self):
        try:
            self.logger.info(f"Inicializando modelo {self.config.model_name}...")
            
            # Verificar se o modelo está disponível
            models = await self.list_available_models()
            
            # Verificar se o modelo específico está na lista
            model_names = []
            for model in models:
                if isinstance(model, dict):
                    # Tentar diferentes chaves possíveis
                    if 'name' in model:
                        model_names.append(model['name'])
                    elif 'model' in model:
                        model_names.append(model['model'])
                    elif 'id' in model:
                        model_names.append(model['id'])
            
            self.logger.info(f"Modelos disponíveis: {model_names}")
            
            if not model_names:
                self.logger.warning("Nenhum modelo encontrado. Tentando baixar...")
                await self.download_model()
            elif self.config.model_name not in model_names:
                # Verificar se há uma versão similar
                similar_model = None
                for name in model_names:
                    if "llama" in name.lower() and "3" in name:
                        similar_model = name
                        break
                
                if similar_model:
                    self.logger.info(f"Usando modelo similar: {similar_model}")
                    self.config.model_name = similar_model
                else:
                    self.logger.warning(f"Modelo {self.config.model_name} não encontrado. Tentando baixar...")
                    await self.download_model()
            
            # Testar o modelo
            await self.test_model()
            
            self.logger.info("Modelo inicializado com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar modelo: {e}")
            # Não fazer raise, continuar com modelo padrão
            self.logger.info("Continuando sem modelo específico...")
    
    async def list_available_models(self) -> List[Dict[str, Any]]:
        try:
            response = await self.client.list()
            models = response.get('models', [])
            self.logger.info(f"Resposta da API: {response}")
            return models
        except Exception as e:
            self.logger.error(f"Erro ao listar modelos: {e}")
            return []
    
    async def download_model(self):
        try:
            self.logger.info(f"Baixando modelo {self.config.model_name}...")
            print(f"📥 Baixando modelo {self.config.model_name}... (isso pode demorar)")
            
            # Usar método mais simples
            import subprocess
            result = subprocess.run(
                ["ollama", "pull", self.config.model_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.logger.info("Modelo baixado com sucesso!")
            else:
                self.logger.error(f"Erro ao baixar modelo: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"Erro ao baixar modelo: {e}")
    
    async def test_model(self):
        try:
            test_prompt = "Diga apenas 'OK' em português."
            response = await self.generate_response(test_prompt, use_history=False)
            
            if response:
                self.logger.info(f"Teste do modelo bem-sucedido! Resposta: {response[:50]}...")
            else:
                self.logger.warning("Modelo não respondeu ao teste")
                
        except Exception as e:
            self.logger.error(f"Erro no teste do modelo: {e}")
    
    async def generate_response(self, prompt: str, use_history: bool = True) -> Optional[str]:
        try:
            # Preparar mensagens
            messages = []
            
            if use_history and self.conversation_history:
                # Manter apenas as últimas conversas para não exceder contexto
                recent_history = self.conversation_history[-6:]  # Últimas 6 trocas
                messages.extend(recent_history)
            
            # Adicionar prompt atual
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            # Gerar resposta
            response = await self.client.chat(
                model=self.config.model_name,
                messages=messages,
                options={
                    'temperature': self.config.temperature,
                    'num_predict': self.config.max_tokens,
                    'top_p': 0.9,
                    'repeat_penalty': 1.1
                }
            )
            
            if response and 'message' in response and 'content' in response['message']:
                assistant_message = response['message']['content'].strip()
                
                # Adicionar ao histórico
                if use_history:
                    self.conversation_history.append({
                        'role': 'user',
                        'content': prompt
                    })
                    self.conversation_history.append({
                        'role': 'assistant',
                        'content': assistant_message
                    })
                    
                    # Limitar tamanho do histórico
                    if len(self.conversation_history) > 12:
                        self.conversation_history = self.conversation_history[-10:]
                
                return assistant_message
            else:
                self.logger.error(f"Resposta inválida do modelo: {response}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta: {e}")
            return f"Desculpe, houve um erro interno: {str(e)}"
    
    def clear_history(self):
        self.conversation_history = []
        self.logger.info("Histórico de conversa limpo")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            'model_name': self.config.model_name,
            'max_tokens': self.config.max_tokens,
            'temperature': self.config.temperature,
            'context_length': self.config.context_length,
            'history_length': len(self.conversation_history)
        }
"""

# Salvar arquivo
with open("models/local_llm.py", "w", encoding="utf-8") as f:
    f.write(llm_code)

print("✅ Novo arquivo local_llm.py criado!")
print("🚀 Execute: python main.py")