# fix_database.py
"""Script para corrigir o arquivo database.py"""

import os
from pathlib import Path

def fix_database_file():
    """Corrige o arquivo database.py"""
    
    # Conteúdo corrigido do database.py
    database_content = '''# memory/database.py
import asyncio
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from config.settings import DatabaseConfig

class DatabaseManager:
    """Gerencia banco de dados SQLite local"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connection: Optional[sqlite3.Connection] = None
        
        # Criar diretório data se não existir
        Path("data").mkdir(exist_ok=True)
    
    async def initialize(self):
        """Inicializa banco de dados e cria tabelas"""
        try:
            # Conectar ao banco
            self.connection = sqlite3.connect(
                self.config.conversations_db,
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row
            
            # Criar tabelas
            await self.create_tables()
            
            self.logger.info("Banco de dados inicializado com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco: {e}")
            raise
    
    async def create_tables(self):
        """Cria tabelas necessárias"""
        try:
            cursor = self.connection.cursor()
            
            # Tabela de perfil do usuário
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY,
                    data TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de conversas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Tabela de conhecimento/memórias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT,
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de preferências e configurações
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            self.logger.info("Tabelas criadas com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar tabelas: {e}")
            raise
    
    async def save_user_profile(self, profile_data: Dict[str, Any]):
        """Salva perfil do usuário"""
        try:
            cursor = self.connection.cursor()
            
            # Converter para JSON
            profile_json = json.dumps(profile_data, ensure_ascii=False)
            
            # Inserir ou atualizar
            cursor.execute("""
                INSERT OR REPLACE INTO user_profile (id, data, updated_at)
                VALUES (1, ?, ?)
            """, (profile_json, datetime.now()))
            
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar perfil: {e}")
            raise
    
    async def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """Carrega perfil do usuário"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT data FROM user_profile WHERE id = 1')
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['data'])
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar perfil: {e}")
            return None
    
    async def save_conversation_message(self, session_id: str, role: str, content: str, metadata: Dict = None):
        """Salva mensagem da conversa"""
        try:
            cursor = self.connection.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO conversations (session_id, role, content, metadata)
                VALUES (?, ?, ?, ?)
            """, (session_id, role, content, metadata_json))
            
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar mensagem: {e}")
    
    async def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtém histórico de conversa"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT role, content, timestamp, metadata
                FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            
            rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                message = {
                    'role': row['role'],
                    'content': row['content'],
                    'timestamp': row['timestamp']
                }
                
                if row['metadata']:
                    message['metadata'] = json.loads(row['metadata'])
                
                messages.append(message)
            
            return list(reversed(messages))  # Ordem cronológica
            
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico: {e}")
            return []
    
    async def add_knowledge(self, topic: str, content: str, source: str = None, confidence: float = 1.0):
        """Adiciona conhecimento à base"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO knowledge_base (topic, content, source, confidence)
                VALUES (?, ?, ?, ?)
            """, (topic, content, source, confidence))
            
            self.connection.commit()
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar conhecimento: {e}")
    
    async def close(self):
        """Fecha conexão com banco"""
        if self.connection:
            self.connection.close()
            self.logger.info("Conexão com banco fechada")
'''
    
    # Salvar arquivo corrigido
    db_file = Path("memory/database.py")
    
    print("🔧 Corrigindo arquivo database.py...")
    
    with open(db_file, 'w', encoding='utf-8') as f:
        f.write(database_content)
    
    print("✅ Arquivo database.py corrigido!")
    print("🚀 Agora execute: python main.py")

if __name__ == "__main__":
    fix_database_file()
'''