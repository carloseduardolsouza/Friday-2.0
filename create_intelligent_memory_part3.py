# create_intelligent_memory_part3.py
print("⏰ Criando Sistema de Inferência Temporal...")

# Parte 3: Sistema de Inferência Temporal
temporal_inference_code = '''# core/temporal_inference.py
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
import logging

class TemporalInferenceEngine:
    """Sistema de inferência temporal para deduzir informações baseadas no tempo"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Padrões temporais (corrigidos)
        self.temporal_patterns = {
            'absolute_dates': [
                r'em (\\d{4})',
                r'no ano de (\\d{4})',
                r'(\\d{1,2})/(\\d{1,2})/(\\d{4})',
                r'(\\d{1,2}) de ([a-záêçõ]+) de (\\d{4})'
            ],
            'relative_time': [
                r'há (\\d+) (anos?|meses?|semanas?|dias?)',
                r'faz (\\d+) (anos?|meses?|semanas?|dias?)',
                r'(\\d+) (anos?|meses?|semanas?|dias?) atrás',
                r'desde (\\d+)',
                r'quando (?:eu )?tinha (\\d+) anos?'
            ],
            'life_events': [
                r'quando (?:eu )?(?:estava|estudava) na (?:escola|faculdade|universidade)',
                r'quando (?:eu )?(?:trabalhava|era) (?:em|na|como) (.+)',
                r'antes de (?:eu )?(.+)',
                r'depois de (?:eu )?(.+)',
                r'durante (?:a|o) (.+)'
            ]
        }
        
        # Marcos temporais típicos (faixas etárias)
        self.life_milestones = {
            'escola_primaria': (6, 11),
            'escola_secundaria': (12, 17),
            'faculdade': (18, 25),
            'primeiro_emprego': (18, 28),
            'casamento': (20, 40),
            'filhos': (20, 45),
            'aposentadoria': (55, 70)
        }
        
        # Meses em português
        self.months = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
            'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
        }
    
    def analyze_temporal_context(self, text: str, existing_facts: Dict) -> List[Dict]:
        """Analisa contexto temporal e faz inferências"""
        inferences = []
        current_year = datetime.now().year
        
        # Extrair referências temporais
        temporal_refs = self._extract_temporal_references(text)
        
        for ref in temporal_refs:
            # Inferir idade baseada em eventos
            if ref['type'] == 'life_event':
                age_inference = self._infer_age_from_event(ref, existing_facts)
                if age_inference:
                    inferences.append(age_inference)
            
            # Inferir informações baseadas em datas
            elif ref['type'] == 'date':
                date_inferences = self._infer_from_date(ref, existing_facts)
                inferences.extend(date_inferences)
            
            # Inferir baseado em tempo relativo
            elif ref['type'] == 'relative_time':
                relative_inferences = self._infer_from_relative_time(ref, existing_facts)
                inferences.extend(relative_inferences)
        
        return inferences
    
    def _extract_temporal_references(self, text: str) -> List[Dict]:
        """Extrai referências temporais do texto"""
        references = []
        text_lower = text.lower()
        
        # Datas absolutas
        for pattern in self.temporal_patterns['absolute_dates']:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                if len(match.groups()) == 1:  # Apenas ano
                    year = int(match.group(1))
                    references.append({
                        'type': 'date',
                        'year': year,
                        'original': match.group(0),
                        'confidence': 0.9
                    })
                elif len(match.groups()) == 3:  # Data completa
                    day, month, year = match.groups()
                    references.append({
                        'type': 'date',
                        'day': int(day),
                        'month': int(month),
                        'year': int(year),
                        'original': match.group(0),
                        'confidence': 0.95
                    })
        
        # Tempo relativo
        for pattern in self.temporal_patterns['relative_time']:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                if len(match.groups()) >= 2:
                    amount = int(match.group(1))
                    unit = match.group(2).rstrip('s').lower()  # Remove plural
                    
                    references.append({
                        'type': 'relative_time',
                        'amount': amount,
                        'unit': unit,
                        'original': match.group(0),
                        'confidence': 0.8
                    })
        
        # Eventos da vida
        for pattern in self.temporal_patterns['life_events']:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                event_context = match.group(0)
                
                event_type = None
                if 'escola' in event_context or 'colégio' in event_context:
                    event_type = 'escola_secundaria'
                elif 'faculdade' in event_context or 'universidade' in event_context:
                    event_type = 'faculdade'
                elif 'trabalha' in event_context or 'emprego' in event_context:
                    event_type = 'primeiro_emprego'
                
                if event_type:
                    references.append({
                        'type': 'life_event',
                        'event': event_type,
                        'original': match.group(0),
                        'confidence': 0.7
                    })
        
        return references
    
    def _infer_age_from_event(self, event_ref: Dict, existing_facts: Dict) -> Optional[Dict]:
        """Infere idade baseada em evento da vida"""
        event_type = event_ref['event']
        
        if event_type in self.life_milestones:
            age_range = self.life_milestones[event_type]
            estimated_age = sum(age_range) // 2  # Média da faixa
            
            # Se já temos idade conhecida, usar para refinar
            if 'age' in existing_facts:
                known_age = existing_facts['age'].get('value', 0)
                # Verificar se é consistente
                if age_range[0] <= known_age <= age_range[1]:
                    confidence = 0.8
                else:
                    confidence = 0.4  # Baixa confiança se inconsistente
            else:
                confidence = 0.6
            
            return {
                'category': 'personal',
                'subcategory': 'age_inferred',
                'fact': f'age_from_event_{event_type}: {estimated_age}',
                'value': estimated_age,
                'confidence': confidence,
                'inference_method': 'life_event',
                'source_event': event_type
            }
        
        return None
    
    def _infer_from_date(self, date_ref: Dict, existing_facts: Dict) -> List[Dict]:
        """Faz inferências baseadas em data"""
        inferences = []
        current_year = datetime.now().year
        
        # Se a data é de nascimento (inferir idade)
        if 'birth' in date_ref.get('context', '').lower() or date_ref['year'] < current_year - 10:
            age = current_year - date_ref['year']
            
            if 0 < age < 120:  # Idade razoável
                inferences.append({
                    'category': 'personal',
                    'subcategory': 'age',
                    'fact': f'age_from_birth_year: {age}',
                    'value': age,
                    'confidence': 0.9,
                    'inference_method': 'birth_year_calculation',
                    'source_year': date_ref['year']
                })
                
                inferences.append({
                    'category': 'personal',
                    'subcategory': 'birth_year',
                    'fact': f'birth_year: {date_ref["year"]}',
                    'value': date_ref['year'],
                    'confidence': 0.9,
                    'inference_method': 'explicit_or_calculated'
                })
        
        return inferences
    
    def _infer_from_relative_time(self, time_ref: Dict, existing_facts: Dict) -> List[Dict]:
        """Faz inferências baseadas em tempo relativo"""
        inferences = []
        current_date = datetime.now()
        
        amount = time_ref['amount']
        unit = time_ref['unit']
        
        # Calcular data aproximada do evento
        if unit == 'ano':
            past_date = current_date - timedelta(days=amount * 365)
        elif unit == 'mês' or unit == 'mes':
            past_date = current_date - timedelta(days=amount * 30)
        elif unit == 'semana':
            past_date = current_date - timedelta(weeks=amount)
        elif unit == 'dia':
            past_date = current_date - timedelta(days=amount)
        else:
            return inferences
        
        # Se é sobre idade no passado, inferir idade atual
        if 'tinha' in time_ref['original'] and 'anos' in time_ref['original']:
            # "há 5 anos eu tinha 20 anos" -> idade atual = 25
            match = re.search(r'tinha (\\d+) anos?', time_ref['original'])
            if match:
                past_age = int(match.group(1))
                current_age = past_age + amount
                
                inferences.append({
                    'category': 'personal',
                    'subcategory': 'age',
                    'fact': f'current_age_from_past: {current_age}',
                    'value': current_age,
                    'confidence': 0.85,
                    'inference_method': 'relative_time_calculation',
                    'calculation': f'{past_age} + {amount} anos'
                })
        
        return inferences
    
    def validate_temporal_consistency(self, facts: List[Dict]) -> Dict[str, Any]:
        """Valida consistência temporal dos fatos"""
        validation_results = {
            'consistent': True,
            'conflicts': [],
            'warnings': []
        }
        
        # Agrupar fatos por tipo
        age_facts = [f for f in facts if f.get('subcategory') == 'age']
        birth_year_facts = [f for f in facts if f.get('subcategory') == 'birth_year']
        
        # Verificar consistência idade/ano de nascimento
        if age_facts and birth_year_facts:
            current_year = datetime.now().year
            
            for age_fact in age_facts:
                for birth_fact in birth_year_facts:
                    if isinstance(birth_fact.get('value'), (int, str)):
                        try:
                            birth_year = int(birth_fact['value'])
                            calculated_age = current_year - birth_year
                            stated_age = int(age_fact.get('value', 0))
                            age_diff = abs(calculated_age - stated_age)
                            
                            if age_diff > 1:  # Diferença maior que 1 ano
                                validation_results['consistent'] = False
                                validation_results['conflicts'].append({
                                    'type': 'age_birth_year_mismatch',
                                    'age_fact': age_fact,
                                    'birth_fact': birth_fact,
                                    'calculated_age': calculated_age,
                                    'stated_age': stated_age,
                                    'difference': age_diff
                                })
                        except (ValueError, TypeError):
                            continue
        
        return validation_results
    
    def update_facts_with_time(self, facts: List[Dict]) -> List[Dict]:
        """Atualiza fatos considerando passagem do tempo"""
        updated_facts = []
        current_date = datetime.now()
        
        for fact in facts:
            updated_fact = fact.copy()
            
            # Atualizar idade se temos ano de nascimento
            if fact.get('subcategory') == 'birth_year':
                try:
                    birth_year = int(fact['value'])
                    current_age = current_date.year - birth_year
                    
                    # Criar/atualizar fato de idade
                    age_fact = {
                        'category': 'personal',
                        'subcategory': 'age',
                        'fact': f'current_age: {current_age}',
                        'value': current_age,
                        'confidence': fact.get('confidence', 0.8),
                        'inference_method': 'temporal_update',
                        'last_calculated': current_date.isoformat()
                    }
                    updated_facts.append(age_fact)
                except (ValueError, TypeError):
                    pass
            
            # Decrementar confiança de fatos emocionais antigos
            elif fact.get('subcategory') == 'current_emotion':
                try:
                    fact_timestamp = fact.get('timestamp', current_date.isoformat())
                    fact_date = datetime.fromisoformat(fact_timestamp.replace('Z', '+00:00'))
                    days_old = (current_date - fact_date).days
                    
                    if days_old > 1:  # Emoções ficam menos relevantes com o tempo
                        confidence_decay = max(0.1, fact.get('confidence', 0.5) * (0.9 ** days_old))
                        updated_fact['confidence'] = confidence_decay
                        updated_fact['temporal_decay_applied'] = True
                except (ValueError, TypeError):
                    pass
            
            updated_facts.append(updated_fact)
        
        return updated_facts
    
    def infer_age_from_birth_year(self, birth_year: int) -> int:
        """Calcula idade atual a partir do ano de nascimento"""
        current_year = datetime.now().year
        return current_year - birth_year
    
    def is_reasonable_age(self, age: int) -> bool:
        """Verifica se a idade é razoável"""
        return 0 < age < 120
    
    def get_life_stage(self, age: int) -> str:
        """Retorna estágio da vida baseado na idade"""
        if age < 13:
            return "criança"
        elif age < 18:
            return "adolescente"
        elif age < 25:
            return "jovem_adulto"
        elif age < 40:
            return "adulto"
        elif age < 60:
            return "adulto_maduro"
        else:
            return "idoso"
'''

# Salvar parte 3
with open("core/temporal_inference.py", "w", encoding="utf-8") as f:
    f.write(temporal_inference_code)

print("✅ Parte 3 criada: core/temporal_inference.py")
print("⏰ Sistema de inferência temporal avançado")
print("🧮 Cálculo automático de idade por ano de nascimento")
print("🔍 Detecção de eventos da vida e marcos temporais")
print("✅ Validação de consistência temporal")
print("")
print("🚀 Continue com: python create_intelligent_memory_part4.py")