# create_intelligent_memory_part4.py
print("🔗 Criando Sistema Integrado e Scripts de Instalação...")

# Parte 4: Sistema Principal Integrado
integrated_system_code = '''# core/intelligent_memory.py
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from core.intelligent_extractor import IntelligentFactExtractor, ExtractedFact
from core.vector_memory import VectorMemorySystem
from core.temporal_inference import TemporalInferenceEngine

class IntelligentMemorySystem:
    """Sistema integrado de memória inteligente personalizada"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Componentes principais
        try:
            self.fact_extractor = IntelligentFactExtractor()
            self.vector_memory = VectorMemorySystem()
            self.temporal_engine = TemporalInferenceEngine()
            
            # Cache de perfil
            self._profile_cache = None
            self._cache_timestamp = None
            
            self.logger.info("Sistema de memória inteligente inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar sistema de memória: {e}")
            raise
        
    async def process_conversation_turn(self, user_text: str, conversation_context: str = "") -> Dict[str, Any]:
        """Processa uma rodada de conversa e atualiza conhecimento"""
        
        processing_result = {
            'facts_extracted': 0,
            'facts_stored': 0,
            'inferences_made': 0,
            'profile_updated': False,
            'interesting_facts': [],
            'confidence_summary': {}
        }
        
        try:
            # 1. Extrair fatos do texto
            extracted_facts = self.fact_extractor.extract_facts(user_text, conversation_context)
            processing_result['facts_extracted'] = len(extracted_facts)
            
            if not extracted_facts:
                return processing_result
            
            # 2. Obter perfil atual para contexto
            current_profile = await self.get_user_profile()
            
            # 3. Fazer inferências temporais
            temporal_inferences = self.temporal_engine.analyze_temporal_context(
                user_text, 
                current_profile.get('personal_info', {})
            )
            
            # Converter inferências para ExtractedFact
            inferred_facts = []
            for inference in temporal_inferences:
                inferred_fact = ExtractedFact(
                    category=inference['category'],
                    subcategory=inference['subcategory'],
                    fact=inference['fact'],
                    value=inference['value'],
                    context=conversation_context,
                    confidence=inference['confidence'],
                    timestamp=datetime.now().isoformat(),
                    source_text=inference.get('original', user_text),
                    inferred=True
                )
                inferred_facts.append(inferred_fact)
            
            processing_result['inferences_made'] = len(inferred_facts)
            
            # 4. Combinar fatos extraídos e inferidos
            all_facts = extracted_facts + inferred_facts
            
            # 5. Merge de fatos similares
            if all_facts:
                merged_facts = self.fact_extractor.merge_similar_facts(all_facts)
                
                # 6. Armazenar na memória vetorial
                stored_ids = self.vector_memory.store_facts(merged_facts)
                processing_result['facts_stored'] = len(stored_ids)
                
                # 7. Invalidar cache do perfil
                self._profile_cache = None
                processing_result['profile_updated'] = True
                
                # 8. Identificar fatos interessantes (alta confiança)
                high_confidence_facts = [
                    f for f in merged_facts 
                    if f.confidence > 0.8 and not f.inferred
                ]
                
                processing_result['interesting_facts'] = [
                    {
                        'category': f.subcategory,
                        'fact': f.fact,
                        'confidence': f.confidence,
                        'new': True
                    }
                    for f in high_confidence_facts
                ]
                
                # 9. Resumo de confiança
                confidences = [f.confidence for f in merged_facts]
                processing_result['confidence_summary'] = {
                    'average': sum(confidences) / len(confidences),
                    'max': max(confidences),
                    'min': min(confidences),
                    'high_confidence_count': len([c for c in confidences if c > 0.8])
                }
            
        except Exception as e:
            self.logger.error(f"Erro no processamento da conversa: {e}")
        
        return processing_result
    
    async def get_user_profile(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Obtém perfil completo do usuário"""
        
        # Usar cache se disponível e recente (5 minutos)
        if (not force_refresh and 
            self._profile_cache and 
            self._cache_timestamp and 
            (datetime.now() - self._cache_timestamp).seconds < 300):
            return self._profile_cache
        
        try:
            # Gerar perfil atualizado
            profile = self.vector_memory.get_user_profile_summary()
            
            # Atualizar cache
            self._profile_cache = profile
            self._cache_timestamp = datetime.now()
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Erro ao obter perfil: {e}")
            return {}
    
    async def search_memories(self, query: str, category: str = None) -> List[Dict]:
        """Busca por memórias relacionadas"""
        try:
            # Busca vetorial
            similar_facts = self.vector_memory.search_similar_facts(query)
            
            # Filtrar por categoria se especificada
            if category:
                similar_facts = [f for f in similar_facts if f.get('category') == category]
            
            return similar_facts
            
        except Exception as e:
            self.logger.error(f"Erro na busca de memórias: {e}")
            return []
    
    async def generate_personalized_response_context(self, user_message: str) -> str:
        """Gera contexto personalizado para resposta da IA"""
        
        try:
            # Obter perfil atual
            profile = await self.get_user_profile()
            
            # Construir contexto personalizado
            context_parts = []
            
            # Informações pessoais básicas
            personal_info = profile.get('personal_info', {})
            if personal_info:
                info_summary = []
                for key, value in personal_info.items():
                    if isinstance(value, dict) and value.get('confidence', 0) > 0.7:
                        info_summary.append(f"{key}: {value['value']}")
                
                if info_summary:
                    context_parts.append(f"SOBRE O USUÁRIO: {', '.join(info_summary)}")
            
            # Preferências conhecidas
            preferences = profile.get('preferences', {})
            likes = preferences.get('likes', [])
            dislikes = preferences.get('dislikes', [])
            
            pref_summary = []
            if likes:
                high_conf_likes = [item['item'] for item in likes if item['confidence'] > 0.7]
                if high_conf_likes:
                    pref_summary.append(f"gosta de: {', '.join(high_conf_likes[:3])}")
            
            if dislikes:
                high_conf_dislikes = [item['item'] for item in dislikes if item['confidence'] > 0.7]
                if high_conf_dislikes:
                    pref_summary.append(f"não gosta de: {', '.join(high_conf_dislikes[:2])}")
            
            if pref_summary:
                context_parts.append(f"PREFERÊNCIAS: {', '.join(pref_summary)}")
            
            # Relacionamentos
            relationships = profile.get('relationships', {})
            if relationships:
                rel_summary = []
                for rel_type, rel_info in relationships.items():
                    if isinstance(rel_info, dict) and rel_info.get('confidence', 0) > 0.8:
                        rel_summary.append(f"{rel_type}: {rel_info['name']}")
                
                if rel_summary:
                    context_parts.append(f"FAMÍLIA/RELACIONAMENTOS: {', '.join(rel_summary[:3])}")
            
            # Montar contexto final
            if context_parts:
                full_context = "\\n".join(context_parts)
                return f"CONTEXTO PERSONALIZADO:\\n{full_context}\\n\\nUse essas informações para dar uma resposta mais personalizada e relevante."
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar contexto personalizado: {e}")
        
        return ""
    
    async def get_learning_summary(self) -> Dict[str, Any]:
        """Gera resumo do que foi aprendido"""
        try:
            profile = await self.get_user_profile()
            
            summary = {
                'total_facts': profile.get('stats', {}).get('total_facts', 0),
                'confidence_avg': profile.get('stats', {}).get('confidence_avg', 0.0),
                'categories_learned': {},
                'knowledge_gaps': []
            }
            
            # Contar fatos por categoria
            for category in ['personal_info', 'preferences', 'relationships', 'activities']:
                category_data = profile.get(category, {})
                if isinstance(category_data, dict):
                    summary['categories_learned'][category] = len(category_data)
                elif isinstance(category_data, list):
                    summary['categories_learned'][category] = len(category_data)
            
            # Identificar lacunas de conhecimento
            basic_info = ['age', 'location', 'occupation']
            known_basic_info = profile.get('personal_info', {}).keys()
            gaps = [info for info in basic_info if info not in known_basic_info]
            
            if gaps:
                summary['knowledge_gaps'] = [f"Não sei sua {gap}" for gap in gaps]
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo de aprendizado: {e}")
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        try:
            total_facts = self.vector_memory.get_total_facts()
            return {
                'total_facts': total_facts,
                'system_status': 'active',
                'components': {
                    'fact_extractor': bool(self.fact_extractor),
                    'vector_memory': bool(self.vector_memory),
                    'temporal_engine': bool(self.temporal_engine)
                }
            }
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {'total_facts': 0, 'system_status': 'error'}
'''

# Script de instalação
installation_script = '''# install_intelligent_memory.py
print("🧠 Instalando sistema de memória inteligente...")

import subprocess
import sys
import os

def install_dependencies():
    """Instala dependências necessárias"""
    dependencies = [
        "scikit-learn",
        "numpy", 
        "scipy"
    ]
    
    print("📦 Instalando dependências...")
    
    for dep in dependencies:
        print(f"   Instalando {dep}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"   ✅ {dep} instalado")
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ Erro ao instalar {dep}: {e}")
            print(f"   💡 Continuando sem {dep} (modo básico)")
        except Exception as e:
            print(f"   ⚠️ Erro inesperado com {dep}: {e}")
    
    print("✅ Instalação de dependências concluída!")

def check_installation():
    """Verifica se a instalação foi bem-sucedida"""
    print("\\n🧪 Testando instalação...")
    
    try:
        # Testar imports básicos
        import numpy as np
        print("✅ NumPy funcionando")
        
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            print("✅ Scikit-learn funcionando - busca vetorial disponível")
        except ImportError:
            print("⚠️ Scikit-learn não disponível - usando busca básica")
        
        print("✅ Instalação verificada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

if __name__ == "__main__":
    install_dependencies()
    if check_installation():
        print("\\n🚀 Execute: python integrate_intelligent_memory.py")
    else:
        print("\\n⚠️ Problemas na instalação, mas sistema básico deve funcionar")
        print("🚀 Tente executar: python integrate_intelligent_memory.py")
'''

# Script de integração
integration_script = '''# integrate_intelligent_memory.py
print("🔗 Integrando sistema de memória inteligente com SEXTA-FEIRA...")

import re
import os

def update_agent_py():
    """Atualiza agent.py para incluir sistema de memória"""
    
    if not os.path.exists("core/agent.py"):
        print("❌ Arquivo core/agent.py não encontrado!")
        return False
    
    try:
        # Ler arquivo atual
        with open("core/agent.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verificar se já foi integrado
        if "IntelligentMemorySystem" in content:
            print("✅ Sistema já integrado no agent.py!")
            return True
        
        print("🔗 Integrando sistema de memória...")
        
        # 1. Adicionar import
        if "from config.settings import AgentConfig" in content:
            content = content.replace(
                "from config.settings import AgentConfig",
                "from config.settings import AgentConfig\\nfrom core.intelligent_memory import IntelligentMemorySystem"
            )
            print("  ✅ Import adicionado")
        
        # 2. Adicionar variável no __init__
        if "self.continuous_mode = False" in content:
            content = content.replace(
                "self.continuous_mode = False",
                "self.continuous_mode = False\\n        \\n        # Sistema de memória inteligente\\n        self.intelligent_memory: Optional[IntelligentMemorySystem] = None"
            )
            print("  ✅ Variável adicionada ao __init__")
        
        # 3. Adicionar inicialização
        init_pattern = r"(self\\.self_modifier = SelfModifier\\(self\\.llm, self\\.user_profile\\))"
        if re.search(init_pattern, content):
            content = re.sub(
                init_pattern,
                r"\\1\\n            \\n            # Inicializar sistema de memória inteligente\\n            self.intelligent_memory = IntelligentMemorySystem()\\n            self.logger.info(\\"Sistema de memória inteligente inicializado!\\")",
                content
            )
            print("  ✅ Inicialização adicionada")
        
        # 4. Atualizar process_input
        if "async def process_input(self, user_input: str)" in content:
            # Encontrar o método process_input e adicionar lógica de aprendizado
            process_input_pattern = r"(print\\(\\"🧠 Processando\\.\\.\\.\\"))"
            if re.search(process_input_pattern, content):
                replacement = '''print("🧠 Processando e aprendendo...")
            
            # PRIMEIRO: Processar com sistema de memória inteligente
            if self.intelligent_memory:
                try:
                    learning_result = await self.intelligent_memory.process_conversation_turn(
                        user_input, 
                        "conversa_geral"
                    )
                    
                    # Log do aprendizado
                    if learning_result['facts_extracted'] > 0:
                        print(f"📚 Aprendi {learning_result['facts_extracted']} fatos novos!")
                    
                    if learning_result['interesting_facts']:
                        print("🎯 Fatos interessantes descobertos:")
                        for fact in learning_result['interesting_facts'][:2]:
                            print(f"   • {fact['category']}: confiança {fact['confidence']:.1f}")
                except Exception as e:
                    self.logger.error(f"Erro no aprendizado: {e}")
            
            print("🧠 Processando...")'''
                
                content = re.sub(process_input_pattern, replacement, content)
                print("  ✅ Lógica de aprendizado adicionada ao process_input")
        
        # 5. Adicionar métodos de memória
        memory_methods = '''
    async def handle_memory_commands(self, user_input: str) -> Optional[str]:
        """Trata comandos relacionados à memória"""
        user_lower = user_input.lower()
        
        if any(cmd in user_lower for cmd in ["o que você sabe sobre mim", "me conte sobre mim", "meu perfil"]):
            return await self.generate_profile_summary()
        
        elif any(cmd in user_lower for cmd in ["o que você aprendeu", "quanto você sabe", "resumo do aprendizado"]):
            return await self.generate_learning_summary()
        
        elif user_lower.startswith("buscar memória"):
            query = user_input[14:].strip()
            return await self.search_user_memories(query)
        
        return None
    
    async def generate_profile_summary(self) -> str:
        """Gera resumo personalizado do perfil"""
        try:
            if not self.intelligent_memory:
                return "Sistema de memória não disponível."
            
            profile = await self.intelligent_memory.get_user_profile()
            
            summary_parts = []
            
            # Informações pessoais
            personal_info = profile.get('personal_info', {})
            if personal_info:
                info_items = []
                for key, value in personal_info.items():
                    if isinstance(value, dict) and value.get('confidence', 0) > 0.7:
                        if key == 'age' or key == 'age_inferred':
                            info_items.append(f"você tem {value['value']} anos")
                        elif key == 'location':
                            info_items.append(f"você mora em {value['value']}")
                        elif key == 'occupation':
                            info_items.append(f"você trabalha como {value['value']}")
                
                if info_items:
                    summary_parts.append("📋 Sobre você: " + ", ".join(info_items) + ".")
            
            # Preferências
            preferences = profile.get('preferences', {})
            likes = preferences.get('likes', [])
            if likes:
                high_conf_likes = [item['item'] for item in likes if item['confidence'] > 0.7]
                if high_conf_likes:
                    summary_parts.append(f"❤️ Você gosta de: {', '.join(high_conf_likes[:4])}.")
            
            dislikes = preferences.get('dislikes', [])
            if dislikes:
                high_conf_dislikes = [item['item'] for item in dislikes if item['confidence'] > 0.7]
                if high_conf_dislikes:
                    summary_parts.append(f"❌ Você não gosta de: {', '.join(high_conf_dislikes[:3])}.")
            
            # Relacionamentos
            relationships = profile.get('relationships', {})
            if relationships:
                rel_items = []
                for rel_type, rel_info in relationships.items():
                    if isinstance(rel_info, dict) and rel_info.get('confidence', 0) > 0.8:
                        if rel_type == 'mother':
                            rel_items.append(f"sua mãe se chama {rel_info['name']}")
                        elif rel_type == 'father':
                            rel_items.append(f"seu pai se chama {rel_info['name']}")
                        elif rel_type in ['brother', 'sister']:
                            rel_items.append(f"seu {rel_type} se chama {rel_info['name']}")
                
                if rel_items:
                    summary_parts.append("👨‍👩‍👧‍👦 Família: " + ", ".join(rel_items) + ".")
            
            # Estatísticas
            stats = profile.get('stats', {})
            total_facts = stats.get('total_facts', 0)
            confidence_avg = stats.get('confidence_avg', 0)
            
            if total_facts > 0:
                summary_parts.append(f"📊 Eu sei {total_facts} fatos sobre você com {confidence_avg:.0%} de confiança média.")
            
            if summary_parts:
                return "\\n".join(summary_parts)
            else:
                return "🤔 Ainda estou aprendendo sobre você! Continue conversando comigo para que eu possa te conhecer melhor."
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo do perfil: {e}")
            return "Houve um erro ao gerar seu perfil."
    
    async def generate_learning_summary(self) -> str:
        """Gera resumo do aprendizado"""
        try:
            if not self.intelligent_memory:
                return "Sistema de memória não disponível."
            
            summary = await self.intelligent_memory.get_learning_summary()
            
            response_parts = []
            
            total_facts = summary.get('total_facts', 0)
            confidence_avg = summary.get('confidence_avg', 0)
            
            response_parts.append(f"🧠 **RESUMO DO APRENDIZADO:**")
            response_parts.append(f"📚 Total de fatos aprendidos: **{total_facts}**")
            
            if confidence_avg > 0:
                response_parts.append(f"🎯 Confiança média: **{confidence_avg:.0%}**")
            
            # Categorias aprendidas
            categories = summary.get('categories_learned', {})
            if categories:
                response_parts.append("\\n📂 **Categorias conhecidas:**")
                for category, count in categories.items():
                    if count > 0:
                        category_name = {
                            'personal_info': 'Informações pessoais',
                            'preferences': 'Preferências',
                            'relationships': 'Relacionamentos',
                            'activities': 'Atividades'
                        }.get(category, category)
                        response_parts.append(f"   • {category_name}: {count} itens")
            
            # Lacunas de conhecimento
            gaps = summary.get('knowledge_gaps', [])
            if gaps:
                response_parts.append("\\n❓ **Ainda não sei:**")
                for gap in gaps[:3]:
                    response_parts.append(f"   • {gap}")
                response_parts.append("\\n💡 *Conte-me mais sobre você para que eu possa aprender!*")
            
            return "\\n".join(response_parts)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo de aprendizado: {e}")
            return "Houve um erro ao gerar resumo do aprendizado."
    
    async def search_user_memories(self, query: str) -> str:
        """Busca por memórias específicas"""
        try:
            if not self.intelligent_memory:
                return "Sistema de memória não disponível."
            
            results = await self.intelligent_memory.search_memories(query)
            
            if not results:
                return f"🔍 Não encontrei nenhuma memória relacionada a '{query}'."
            
            response_parts = [f"🔍 **Memórias sobre '{query}':**\\n"]
            
            for i, result in enumerate(results[:5], 1):
                confidence = result.get('confidence', 0)
                fact_text = result.get('fact_text', 'N/A')
                
                confidence_emoji = "🎯" if confidence > 0.8 else "📋" if confidence > 0.6 else "🤔"
                response_parts.append(f"{confidence_emoji} **{i}.** {fact_text} *(confiança: {confidence:.0%})*")
            
            if len(results) > 5:
                response_parts.append(f"\\n... e mais {len(results) - 5} resultados.")
            
            return "\\n".join(response_parts)
            
        except Exception as e:
            self.logger.error(f"Erro na busca de memórias: {e}")
            return "Houve um erro ao buscar suas memórias."
    
    def create_personalized_prompt(self, user_input: str, personalized_context: str) -> str:
        """Cria prompt personalizado com contexto aprendido"""
        
        prompt = f\"\"\"Você é SEXTA-FEIRA, uma assistente pessoal que conhece muito bem seu usuário.

{personalized_context}

IMPORTANTE: Use as informações do contexto para dar uma resposta personalizada, mas de forma natural. Não mencione explicitamente que você "armazenou" ou "lembrou" das informações - aja como se fosse parte natural do seu conhecimento sobre a pessoa.

PERGUNTA DO USUÁRIO: {user_input}

Responda de forma calorosa, personalizada e relevante, usando seu conhecimento sobre a pessoa:\"\"\"
        
        return prompt
'''
        
        # Encontrar local para inserir métodos
        if "def check_exit_command(self, text: str) -> bool:" in content:
            content = content.replace(
                "def check_exit_command(self, text: str) -> bool:",
                memory_methods + "\\n    def check_exit_command(self, text: str) -> bool:"
            )
            print("  ✅ Métodos de memória adicionados")
        
        # 6. Adicionar verificação de comandos de memória no process_input
        if "# SEGUNDO: Verificar comandos de auto-modificação" in content:
            memory_check = '''            # SEGUNDO: Verificar comandos especiais de memória
            memory_response = await self.handle_memory_commands(user_input)
            if memory_response:
                return memory_response
            
            # TERCEIRO: Verificar comandos de auto-modificação'''
            
            content = content.replace(
                "# SEGUNDO: Verificar comandos de auto-modificação",
                memory_check
            )
            print("  ✅ Verificação de comandos de memória adicionada")
        
        # 7. Adicionar contexto personalizado
        if "prompt = self.create_simple_prompt(user_input)" in content:
            personalized_prompt_logic = '''            # Gerar contexto personalizado para resposta
            personalized_context = ""
            if self.intelligent_memory:
                try:
                    personalized_context = await self.intelligent_memory.generate_personalized_response_context(user_input)
                except Exception as e:
                    self.logger.error(f"Erro ao gerar contexto personalizado: {e}")
            
            # Processar como conversa normal com contexto personalizado
            if personalized_context:
                prompt = self.create_personalized_prompt(user_input, personalized_context)
            else:
                prompt = self.create_simple_prompt(user_input)'''
            
            content = content.replace(
                "prompt = self.create_simple_prompt(user_input)",
                personalized_prompt_logic
            )
            print("  ✅ Contexto personalizado adicionado")
        
        # Salvar arquivo atualizado
        with open("core/agent.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ agent.py atualizado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar agent.py: {e}")
        return False

def create_test_script():
    """Cria script de teste do sistema"""
    test_script = '''# test_intelligent_memory.py
import asyncio
from core.intelligent_memory import IntelligentMemorySystem

async def test_intelligent_memory():
    """Testa o sistema de memória inteligente"""
    
    print("🧪 TESTANDO SISTEMA DE MEMÓRIA INTELIGENTE")
    print("=" * 50)
    
    try:
        # Inicializar sistema
        memory_system = IntelligentMemorySystem()
        print("✅ Sistema inicializado")
        
        # Teste 1: Conversas com fatos pessoais
        test_conversations = [
            "Oi, eu nasci em 2005 e moro em São Paulo",
            "Trabalho como programador há 2 anos",
            "Minha mãe se chama Maria e meu pai João",
            "Eu amo pizza mas odeio brócolis",
            "Jogo futebol nas horas vagas e assisto Netflix"
        ]
        
        print("\\n🔍 Processando conversas de teste...")
        for i, conversation in enumerate(test_conversations, 1):
            print(f"\\n{i}. Processando: '{conversation}'")
            
            result = await memory_system.process_conversation_turn(conversation, f"teste_{i}")
            
            print(f"   📚 Fatos extraídos: {result['facts_extracted']}")
            print(f"   💾 Fatos armazenados: {result['facts_stored']}")
            print(f"   🧮 Inferências: {result['inferences_made']}")
        
        print("\\n" + "=" * 50)
        print("📊 PERFIL APRENDIDO:")
        
        # Obter perfil completo
        profile = await memory_system.get_user_profile()
        
        # Mostrar informações pessoais
        personal_info = profile.get('personal_info', {})
        if personal_info:
            print("\\n👤 INFORMAÇÕES PESSOAIS:")
            for key, value in personal_info.items():
                if isinstance(value, dict):
                    print(f"