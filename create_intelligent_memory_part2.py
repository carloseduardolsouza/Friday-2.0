# create_intelligent_memory_part2.py
print("💾 Criando Sistema de Armazenamento Vetorial...")

# Parte 2: Sistema de Memória Vetorial
vector_memory_code = '''# core/vector_memory.py
import numpy as np
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Tentar importar sklearn, se não disponível usar sistema básico
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ sklearn não disponível - usando sistema de busca básico")

class VectorMemorySystem:
    """Sistema de memória vetorial para armazenar conhecimento pessoal"""
    
    def __init__(self, db_path: str = "data/memory.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Configurar sistema de vetorização
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=500,
                ngram_range=(1, 2),
                stop_words=None  # Manter simples para português
            )
            self.fact_vectors = None
            self.facts_metadata = []
        
        # Inicializar banco
        self._init_database()
        if SKLEARN_AVAILABLE:
            self._load_vectors()
    
    def _init_database(self):
        """Inicializa banco de dados para memória"""
        Path("data").mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela principal de fatos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            subcategory TEXT NOT NULL,
            fact_text TEXT NOT NULL,
            value TEXT NOT NULL,
            context TEXT,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL,
            source_text TEXT,
            inferred BOOLEAN DEFAULT 0,
            active BOOLEAN DEFAULT 1
        )
        ''')
        
        # Tabela para atualizações de fatos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_fact_id INTEGER,
            new_fact_id INTEGER,
            update_reason TEXT,
            timestamp TEXT,
            FOREIGN KEY (original_fact_id) REFERENCES memory_facts (id),
            FOREIGN KEY (new_fact_id) REFERENCES memory_facts (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        self.logger.info("Banco de dados de memória inicializado")
    
    def store_facts(self, facts: List[Any]) -> List[int]:
        """Armazena fatos na memória vetorial"""
        if not facts:
            return []
        
        stored_ids = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for fact in facts:
                # Verificar se fato similar já existe
                existing_id = self._find_similar_fact(fact, cursor)
                
                if existing_id:
                    # Atualizar fato existente se nova informação for mais confiável
                    updated_id = self._update_fact_if_better(existing_id, fact, cursor)
                    stored_ids.append(updated_id)
                else:
                    # Armazenar novo fato
                    fact_id = self._insert_new_fact(fact, cursor)
                    stored_ids.append(fact_id)
            
            conn.commit()
            conn.close()
            
            # Atualizar vetores se sklearn disponível
            if SKLEARN_AVAILABLE:
                self._rebuild_vectors()
            
        except Exception as e:
            self.logger.error(f"Erro ao armazenar fatos: {e}")
        
        return stored_ids
    
    def _find_similar_fact(self, fact: Any, cursor) -> Optional[int]:
        """Encontra fato similar na base"""
        cursor.execute('''
        SELECT id, fact_text, confidence FROM memory_facts 
        WHERE category = ? AND subcategory = ? AND active = 1
        ''', (fact.category, fact.subcategory))
        
        results = cursor.fetchall()
        
        for fact_id, existing_text, existing_confidence in results:
            # Calcular similaridade textual simples
            similarity = self._text_similarity(fact.fact, existing_text)
            
            if similarity > 0.8:  # Muito similar
                return fact_id
        
        return None
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos (método básico)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _update_fact_if_better(self, existing_id: int, new_fact: Any, cursor) -> int:
        """Atualiza fato se nova informação for melhor"""
        cursor.execute('SELECT confidence FROM memory_facts WHERE id = ?', (existing_id,))
        result = cursor.fetchone()
        if not result:
            return existing_id
        
        existing_confidence = result[0]
        
        if new_fact.confidence > existing_confidence:
            # Marcar fato antigo como inativo
            cursor.execute('UPDATE memory_facts SET active = 0 WHERE id = ?', (existing_id,))
            
            # Inserir novo fato
            new_id = self._insert_new_fact(new_fact, cursor)
            
            # Registrar atualização
            cursor.execute('''
            INSERT INTO memory_updates (original_fact_id, new_fact_id, update_reason, timestamp)
            VALUES (?, ?, ?, ?)
            ''', (existing_id, new_id, "Higher confidence", datetime.now().isoformat()))
            
            return new_id
        
        return existing_id
    
    def _insert_new_fact(self, fact: Any, cursor) -> int:
        """Insere novo fato no banco"""
        cursor.execute('''
        INSERT INTO memory_facts 
        (category, subcategory, fact_text, value, context, confidence, timestamp, source_text, inferred)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fact.category,
            fact.subcategory, 
            fact.fact,
            json.dumps(fact.value) if not isinstance(fact.value, str) else str(fact.value),
            fact.context,
            fact.confidence,
            fact.timestamp,
            fact.source_text,
            fact.inferred
        ))
        
        return cursor.lastrowid
    
    def _rebuild_vectors(self):
        """Reconstrói vetores TF-IDF (apenas se sklearn disponível)"""
        if not SKLEARN_AVAILABLE:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, fact_text, context, category, subcategory, confidence 
            FROM memory_facts WHERE active = 1
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return
            
            # Preparar dados
            texts = [f"{row[1]} {row[2] or ''}" for row in results]
            self.facts_metadata = [
                {
                    'id': row[0],
                    'fact_text': row[1], 
                    'context': row[2],
                    'category': row[3],
                    'subcategory': row[4],
                    'confidence': row[5]
                }
                for row in results
            ]
            
            # Vetorizar
            if len(texts) > 0:
                self.fact_vectors = self.vectorizer.fit_transform(texts)
                self.logger.info(f"Vetores reconstruídos para {len(texts)} fatos")
            
        except Exception as e:
            self.logger.error(f"Erro ao reconstruir vetores: {e}")
    
    def _load_vectors(self):
        """Carrega vetores existentes"""
        if SKLEARN_AVAILABLE:
            self._rebuild_vectors()
    
    def search_similar_facts(self, query: str, limit: int = 5, min_similarity: float = 0.1) -> List[Dict]:
        """Busca fatos similares à query"""
        if SKLEARN_AVAILABLE and self.fact_vectors is not None and len(self.facts_metadata) > 0:
            return self._search_with_vectors(query, limit, min_similarity)
        else:
            return self._search_basic(query, limit)
    
    def _search_with_vectors(self, query: str, limit: int, min_similarity: float) -> List[Dict]:
        """Busca com vetores TF-IDF"""
        try:
            # Vetorizar query
            query_vector = self.vectorizer.transform([query])
            
            # Calcular similaridades
            similarities = cosine_similarity(query_vector, self.fact_vectors)[0]
            
            # Ordenar por similaridade
            similar_indices = np.argsort(similarities)[::-1]
            
            results = []
            for idx in similar_indices[:limit]:
                if similarities[idx] >= min_similarity:
                    fact_data = self.facts_metadata[idx].copy()
                    fact_data['similarity'] = float(similarities[idx])
                    results.append(fact_data)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca vetorial: {e}")
            return []
    
    def _search_basic(self, query: str, limit: int) -> List[Dict]:
        """Busca básica sem vetores"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Busca simples por texto
            cursor.execute('''
            SELECT id, fact_text, context, category, subcategory, confidence
            FROM memory_facts 
            WHERE active = 1 AND (
                fact_text LIKE ? OR 
                context LIKE ? OR 
                subcategory LIKE ?
            )
            ORDER BY confidence DESC
            LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
            
            results = cursor.fetchall()
            conn.close()
            
            facts = []
            for row in results:
                fact = {
                    'id': row[0],
                    'fact_text': row[1],
                    'context': row[2],
                    'category': row[3],
                    'subcategory': row[4],
                    'confidence': row[5],
                    'similarity': 0.5  # Similaridade padrão para busca básica
                }
                facts.append(fact)
            
            return facts
            
        except Exception as e:
            self.logger.error(f"Erro na busca básica: {e}")
            return []
    
    def get_facts_by_category(self, category: str, subcategory: str = None) -> List[Dict]:
        """Obtém fatos por categoria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if subcategory:
                cursor.execute('''
                SELECT id, fact_text, value, confidence, timestamp, inferred
                FROM memory_facts 
                WHERE category = ? AND subcategory = ? AND active = 1
                ORDER BY confidence DESC, timestamp DESC
                ''', (category, subcategory))
            else:
                cursor.execute('''
                SELECT id, fact_text, value, confidence, timestamp, inferred, subcategory
                FROM memory_facts 
                WHERE category = ? AND active = 1
                ORDER BY confidence DESC, timestamp DESC
                ''', (category,))
            
            results = cursor.fetchall()
            conn.close()
            
            facts = []
            for row in results:
                fact = {
                    'id': row[0],
                    'fact_text': row[1],
                    'value': row[2],
                    'confidence': row[3],
                    'timestamp': row[4],
                    'inferred': bool(row[5])
                }
                if not subcategory:
                    fact['subcategory'] = row[6]
                facts.append(fact)
            
            return facts
            
        except Exception as e:
            self.logger.error(f"Erro ao obter fatos: {e}")
            return []
    
    def get_user_profile_summary(self) -> Dict[str, Any]:
        """Gera resumo do perfil do usuário"""
        profile = {
            'personal_info': {},
            'preferences': {'likes': [], 'dislikes': []},
            'relationships': {},
            'activities': [],
            'stats': {'total_facts': 0, 'confidence_avg': 0.0}
        }
        
        try:
            # Informações pessoais básicas
            basic_info = ['age', 'location', 'occupation', 'birth_year', 'age_inferred']
            for info_type in basic_info:
                facts = self.get_facts_by_category('personal', info_type)
                if facts:
                    best_fact = max(facts, key=lambda x: x['confidence'])
                    profile['personal_info'][info_type] = {
                        'value': best_fact['value'],
                        'confidence': best_fact['confidence'],
                        'last_updated': best_fact['timestamp']
                    }
            
            # Família
            family_types = ['mother', 'father', 'brother', 'sister', 'son', 'daughter', 
                          'husband', 'wife', 'boyfriend', 'girlfriend']
            for family_type in family_types:
                facts = self.get_facts_by_category('personal', family_type)
                if facts:
                    best_fact = max(facts, key=lambda x: x['confidence'])
                    profile['