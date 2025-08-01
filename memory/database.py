# memory/database.py
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from config.settings import DatabaseConfig

class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connection: Optional[sqlite3.Connection] = None
        Path("data").mkdir(exist_ok=True)
    
    async def initialize(self):
        try:
            self.connection = sqlite3.connect(
                self.config.conversations_db,
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row
            await self.create_tables()
            self.logger.info("Banco de dados inicializado!")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar banco: {e}")
            raise
    
    async def create_tables(self):
        try:
            cursor = self.connection.cursor()
            
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS user_profile ("
                "id INTEGER PRIMARY KEY, "
                "data TEXT NOT NULL, "
                "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            )
            
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS conversations ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "session_id TEXT NOT NULL, "
                "role TEXT NOT NULL, "
                "content TEXT NOT NULL, "
                "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
                "metadata TEXT)"
            )
            
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS knowledge_base ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "topic TEXT NOT NULL, "
                "content TEXT NOT NULL, "
                "source TEXT, "
                "confidence REAL DEFAULT 1.0, "
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            )
            
            self.connection.commit()
            self.logger.info("Tabelas criadas!")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar tabelas: {e}")
            raise
    
    async def save_user_profile(self, profile_data: Dict[str, Any]):
        try:
            cursor = self.connection.cursor()
            profile_json = json.dumps(profile_data, ensure_ascii=False)
            cursor.execute(
                "INSERT OR REPLACE INTO user_profile (id, data, updated_at) VALUES (1, ?, ?)",
                (profile_json, datetime.now())
            )
            self.connection.commit()
        except Exception as e:
            self.logger.error(f"Erro ao salvar perfil: {e}")
    
    async def get_user_profile(self) -> Optional[Dict[str, Any]]:
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
        try:
            cursor = self.connection.cursor()
            metadata_json = json.dumps(metadata) if metadata else None
            cursor.execute(
                "INSERT INTO conversations (session_id, role, content, metadata) VALUES (?, ?, ?, ?)",
                (session_id, role, content, metadata_json)
            )
            self.connection.commit()
        except Exception as e:
            self.logger.error(f"Erro ao salvar mensagem: {e}")
    
    async def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT role, content, timestamp, metadata FROM conversations "
                "WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit)
            )
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
            return list(reversed(messages))
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico: {e}")
            return []
    
    async def add_knowledge(self, topic: str, content: str, source: str = None, confidence: float = 1.0):
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO knowledge_base (topic, content, source, confidence) VALUES (?, ?, ?, ?)",
                (topic, content, source, confidence)
            )
            self.connection.commit()
        except Exception as e:
            self.logger.error(f"Erro ao adicionar conhecimento: {e}")
    
    async def close(self):
        if self.connection:
            self.connection.close()
            self.logger.info("Conexão com banco fechada")
