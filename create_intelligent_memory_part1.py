# create_intelligent_memory_part1.py
print("🧠 Criando Extrator de Fatos Inteligente...")

# Parte 1: Extrator de Fatos
extractor_code = '''# core/intelligent_extractor.py
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class ExtractedFact:
    """Fato extraído da conversa"""
    category: str           # "personal", "preference", "relationship", "activity", etc.
    subcategory: str       # "age", "location", "hobby", "family", etc.
    fact: str              # O fato em si
    value: Any             # Valor estruturado
    context: str           # Contexto da conversa
    confidence: float      # 0.0 a 1.0
    timestamp: str         # Quando foi extraído
    source_text: str       # Texto original
    inferred: bool         # Se foi inferido ou explícito

class IntelligentFactExtractor:
    """Extrator inteligente de fatos pessoais"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Padrões para extração de diferentes tipos de informação (corrigidos)
        self.extraction_patterns = {
            # Informações pessoais básicas
            "age_direct": [
                r"(?:eu )?tenho (\\d+) anos?",
                r"(?:minha )?idade (?:é|são) (\\d+)",
                r"(?:eu )?sou de (\\d{4})",  # Ano de nascimento
                r"(?:eu )?nasci em (\\d{4})",
            ],
            
            "age_relative": [
                r"quando (?:eu )?tinha (\\d+) anos?",
                r"aos (\\d+) anos?",
                r"desde os (\\d+)",
                r"há (\\d+) anos? atrás",
            ],
            
            "location": [
                r"(?:eu )?moro em ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?vivo em ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?sou de ([A-Za-zÀ-ÿ\\s]+)",
                r"estou em ([A-Za-zÀ-ÿ\\s]+)",
                r"aqui em ([A-Za-zÀ-ÿ\\s]+)",
                r"na cidade de ([A-Za-zÀ-ÿ\\s]+)",
            ],
            
            "family": [
                r"(?:minha )?(?:mãe|mamãe) (?:se chama|é a?) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:meu )?(?:pai|papai) (?:se chama|é o?) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:meu )?irmão (?:se chama|é o?) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:minha )?irmã (?:se chama|é a?) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:meu )?filho (?:se chama|é o?) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:minha )?filha (?:se chama|é a?) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:meu )?marido (?:se chama|é o?) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:minha )?esposa (?:se chama|é a?) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:meu )?namorado (?:se chama|é o?) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:minha )?namorada (?:se chama|é a?) ([A-Za-zÀ-ÿ\\s]+)",
            ],
            
            "occupation": [
                r"(?:eu )?trabalho (?:como|de) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?sou ([A-Za-zÀ-ÿ\\s]+) de profissão",
                r"(?:minha )?profissão é ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?atuo como ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?faço faculdade de ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?estudo ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?curso ([A-Za-zÀ-ÿ\\s]+)",
            ],
            
            "preferences": [
                r"(?:eu )?(?:gosto|amo|adoro) (?:de |muito )?([A-Za-zÀ-ÿ\\s,]+)",
                r"(?:eu )?(?:odeio|detesto|não gosto) (?:de |muito )?([A-Za-zÀ-ÿ\\s,]+)",
                r"(?:meu )?(?:favorito|preferido) é ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:minha )?(?:favorita|preferida) é ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?prefiro ([A-Za-zÀ-ÿ\\s]+)",
            ],
            
            "activities": [
                r"(?:eu )?(?:faço|pratico) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?jogo ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?assisto ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?leio ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?escuto ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:no )?(?:meu )?tempo livre (?:eu )?([A-Za-zÀ-ÿ\\s]+)",
            ],
            
            "emotions": [
                r"(?:eu )?(?:me sinto|estou) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:isso )?me (?:deixa|faz ficar) ([A-Za-zÀ-ÿ\\s]+)",
                r"(?:eu )?(?:fico|fiquei) ([A-Za-zÀ-ÿ\\s]+)",
            ]
        }
        
        # Contextos conhecidos
        self.known_contexts = {
            "brazilian_cities": ["são paulo", "rio de janeiro", "belo horizonte", "brasília", 
                               "salvador", "fortaleza", "recife", "porto alegre", "curitiba", 
                               "manaus", "goiânia", "belém", "natal", "aracaju", "campo grande"],
            "occupations": ["programador", "desenvolvedor", "engenheiro", "médico", "professor", 
                          "advogado", "designer", "estudante", "empresário"],
            "hobbies": ["futebol", "música", "leitura", "jogos", "filmes", "séries", "culinária", 
                       "viagem", "fotografia", "desenho"]
        }
    
    def extract_facts(self, text: str, context: str = "") -> List[ExtractedFact]:
        """Extrai fatos de um texto"""
        facts = []
        text_lower = text.lower()
        
        # Extrair fatos explícitos
        for category, patterns in self.extraction_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    fact = self._create_fact_from_match(category, match, text, context)
                    if fact:
                        facts.append(fact)
        
        # Fazer inferências
        inferred_facts = self._make_inferences(text, facts, context)
        facts.extend(inferred_facts)
        
        return facts
    
    def _create_fact_from_match(self, category: str, match, original_text: str, context: str) -> Optional[ExtractedFact]:
        """Cria fato a partir de match regex"""
        try:
            value = match.group(1).strip()
            
            # Determinar subcategoria e processar valor
            if category.startswith("age"):
                subcategory = "age"
                if category == "age_direct" and value.isdigit():
                    processed_value = int(value)
                    confidence = 0.95
                elif len(value) == 4 and value.isdigit():  # Ano de nascimento
                    processed_value = datetime.now().year - int(value)
                    confidence = 0.9
                    subcategory = "age_inferred"
                else:
                    processed_value = value
                    confidence = 0.7
            
            elif category == "location":
                subcategory = "location"
                processed_value = value.title()
                # Maior confiança se for cidade conhecida
                confidence = 0.9 if any(city in value.lower() for city in self.known_contexts["brazilian_cities"]) else 0.7
            
            elif category == "family":
                # Determinar tipo de parentesco
                text_lower = original_text.lower()
                if "mãe" in text_lower or "mamãe" in text_lower:
                    subcategory = "mother"
                elif "pai" in text_lower or "papai" in text_lower:
                    subcategory = "father"
                elif "irmão" in text_lower:
                    subcategory = "brother"
                elif "irmã" in text_lower:
                    subcategory = "sister"
                elif "filho" in text_lower:
                    subcategory = "son"
                elif "filha" in text_lower:
                    subcategory = "daughter"
                elif "marido" in text_lower:
                    subcategory = "husband"
                elif "esposa" in text_lower:
                    subcategory = "wife"
                elif "namorado" in text_lower:
                    subcategory = "boyfriend"
                elif "namorada" in text_lower:
                    subcategory = "girlfriend"
                else:
                    subcategory = "family_member"
                
                processed_value = value.title()
                confidence = 0.85
            
            elif category == "occupation":
                subcategory = "occupation"
                processed_value = value.lower()
                confidence = 0.8
            
            elif category == "preferences":
                text_context = match.string[max(0, match.start()-20):match.end()+20]
                if any(neg in text_context for neg in ["não gosto", "odeio", "detesto"]):
                    subcategory = "dislikes"
                else:
                    subcategory = "likes"
                processed_value = value.lower()
                confidence = 0.75
            
            elif category == "activities":
                subcategory = "hobby"
                processed_value = value.lower()
                confidence = 0.7
            
            elif category == "emotions":
                subcategory = "current_emotion"
                processed_value = value.lower()
                confidence = 0.6  # Emoções são temporárias
            
            else:
                subcategory = category
                processed_value = value
                confidence = 0.6
            
            return ExtractedFact(
                category="personal",
                subcategory=subcategory,
                fact=f"{subcategory}: {processed_value}",
                value=processed_value,
                context=context,
                confidence=confidence,
                timestamp=datetime.now().isoformat(),
                source_text=match.group(0),
                inferred=False
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao criar fato: {e}")
            return None
    
    def _make_inferences(self, text: str, explicit_facts: List[ExtractedFact], context: str) -> List[ExtractedFact]:
        """Faz inferências baseadas nos fatos explícitos e contexto"""
        inferences = []
        
        # Inferir idade a partir de eventos temporais
        for fact in explicit_facts:
            if fact.subcategory == "age_inferred" and isinstance(fact.value, int):
                # Se sabemos a idade, podemos inferir ano de nascimento
                birth_year = datetime.now().year - fact.value
                birth_fact = ExtractedFact(
                    category="personal",
                    subcategory="birth_year",
                    fact=f"birth_year: {birth_year}",
                    value=birth_year,
                    context=context,
                    confidence=fact.confidence * 0.9,
                    timestamp=datetime.now().isoformat(),
                    source_text=fact.source_text,
                    inferred=True
                )
                inferences.append(birth_fact)
        
        # Inferir localização a partir de contexto
        text_lower = text.lower()
        for city in self.known_contexts["brazilian_cities"]:
            if city in text_lower and not any(f.subcategory == "location" for f in explicit_facts):
                location_fact = ExtractedFact(
                    category="personal",
                    subcategory="location_mentioned",
                    fact=f"mentioned_location: {city}",
                    value=city.title(),
                    context=context,
                    confidence=0.4,  # Baixa confiança para inferência de contexto
                    timestamp=datetime.now().isoformat(),
                    source_text=f"mentioned {city}",
                    inferred=True
                )
                inferences.append(location_fact)
        
        return inferences
    
    def merge_similar_facts(self, facts: List[ExtractedFact]) -> List[ExtractedFact]:
        """Combina fatos similares, mantendo o de maior confiança"""
        merged = {}
        
        for fact in facts:
            key = f"{fact.category}_{fact.subcategory}"
            
            if key not in merged:
                merged[key] = fact
            else:
                # Manter o de maior confiança
                if fact.confidence > merged[key].confidence:
                    merged[key] = fact
        
        return list(merged.values())
'''

# Salvar parte 1
with open("core/intelligent_extractor.py", "w", encoding="utf-8") as f:
    f.write(extractor_code)

print("✅ Parte 1 criada: core/intelligent_extractor.py")
print("🔍 Extrator inteligente de fatos pessoais")
print("📝 Suporta idade, localização, família, trabalho, preferências")
print("🧮 Sistema de inferência automática")
print("")
print("🚀 Continue com: python create_intelligent_memory_part2.py")