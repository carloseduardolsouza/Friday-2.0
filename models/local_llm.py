# models/local_llm.py
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
            
            # CORREÇÃO: Extrair nomes dos modelos corretamente
            model_names = []
            for model in models:
                if hasattr(model, 'model'):
                    model_names.append(model.model)
                elif isinstance(model, dict) and 'model' in model:
                    model_names.append(model['model'])
            
            self.logger.info(f"Modelos disponíveis: {model_names}")
            
            # Verificar se o modelo desejado existe
            if self.config.model_name in model_names:
                self.logger.info(f"Modelo {self.config.model_name} encontrado!")
            else:
                self.logger.warning(f"Modelo {self.config.model_name} não encontrado nos modelos: {model_names}")
                # Tentar usar o primeiro modelo Llama disponível
                for name in model_names:
                    if "llama" in name.lower():
                        self.logger.info(f"Usando modelo alternativo: {name}")
                        self.config.model_name = name
                        break
            
            # Testar o modelo
            await self.test_model()
            
            self.logger.info("Modelo inicializado com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar modelo: {e}")
            # Não fazer raise, continuar
    
    async def list_available_models(self) -> List[Any]:
        try:
            response = await self.client.list()
            models = response.get('models', [])
            return models
        except Exception as e:
            self.logger.error(f"Erro ao listar modelos: {e}")
            return []
    
    async def test_model(self):
        try:
            test_prompt = "Diga apenas 'Modelo funcionando' em português."
            response = await self.generate_response(test_prompt, use_history=False)
            
            if response and "erro" not in response.lower():
                self.logger.info(f"Teste do modelo bem-sucedido!")
            else:
                self.logger.warning(f"Modelo respondeu com: {response}")
                
        except Exception as e:
            self.logger.error(f"Erro no teste do modelo: {e}")
    
    async def generate_response(self, prompt: str, use_history: bool = True) -> Optional[str]:
        try:
            # Preparar mensagens
            messages = []
            
            if use_history and self.conversation_history:
                # Manter apenas as últimas conversas
                recent_history = self.conversation_history[-4:]  # Ainda menor
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
                    
                    # Limitar histórico
                    if len(self.conversation_history) > 8:
                        self.conversation_history = self.conversation_history[-6:]
                
                return assistant_message
            else:
                self.logger.error(f"Resposta inválida: {response}")
                return "Desculpe, não consegui gerar uma resposta adequada."
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta: {e}")
            return f"Desculpe, houve um erro: {str(e)[:100]}"
    
    def clear_history(self):
        self.conversation_history = []
        self.logger.info("Histórico limpo")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            'model_name': self.config.model_name,
            'max_tokens': self.config.max_tokens,
            'temperature': self.config.temperature,
            'history_length': len(self.conversation_history)
        }