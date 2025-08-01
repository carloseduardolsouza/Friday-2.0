# memory/user_profile.py
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from memory.database import DatabaseManager

@dataclass
class UserInfo:
    """Estrutura para informações do usuário"""
    name: str = ""
    age: Optional[int] = None
    location: str = ""
    occupation: str = ""
    hobbies: List[str] = None
    preferences: Dict[str, Any] = None
    important_dates: Dict[str, str] = None
    family: Dict[str, str] = None
    goals: List[str] = None
    personality_traits: List[str] = None
    
    def __post_init__(self):
        if self.hobbies is None:
            self.hobbies = []
        if self.preferences is None:
            self.preferences = {}
        if self.important_dates is None:
            self.important_dates = {}
        if self.family is None:
            self.family = {}
        if self.goals is None:
            self.goals = []
        if self.personality_traits is None:
            self.personality_traits = []

class UserProfile:
    """Gerencia perfil e informações do usuário"""
    
    def __init__(self, database: DatabaseManager):
        self.database = database
        self.logger = logging.getLogger(__name__)
        self.user_info = UserInfo()
        self.last_updated = datetime.now()
        
        # Padrões para extração de informações
        self.extraction_patterns = {
            'name': [
                r'me chamo (.+?)(?:\.|,|$)',
                r'meu nome é (.+?)(?:\.|,|$)',
                r'sou o (.+?)(?:\.|,|$)',
                r'eu sou (.+?)(?:\.|,|$)'
            ],
            'age': [
                r'tenho (\d+) anos',
                r'eu tenho (\d+) anos',
                r'minha idade é (\d+)'
            ],
            'location': [
                r'moro em (.+?)(?:\.|,|$)',
                r'vivo em (.+?)(?:\.|,|$)',
                r'sou de (.+?)(?:\.|,|$)'
            ],
            'occupation': [
                r'trabalho como (.+?)(?:\.|,|$)',
                r'sou (.+?) de profissão',
                r'minha profissão é (.+?)(?:\.|,|$)',
                r'trabalho de (.+?)(?:\.|,|$)'
            ],
            'hobbies': [
                r'gosto de (.+?)(?:\.|,|$)',
                r'amo (.+?)(?:\.|,|$)',
                r'meu hobby é (.+?)(?:\.|,|$)',
                r'nas horas vagas (.+?)(?:\.|,|$)'
            ]
        }
    
    async def load_profile(self):
        """Carrega perfil do banco de dados"""
        try:
            # Tentar carregar do banco
            profile_data = await self.database.get_user_profile()
            
            if profile_data:
                self.user_info = UserInfo(**profile_data)
                self.logger.info("Perfil do usuário carregado do banco de dados")
            else:
                # Tentar carregar de arquivo JSON (backup)
                await self.load_from_file()
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar perfil: {e}")
            # Criar perfil vazio
            self.user_info = UserInfo()
    
    async def load_from_file(self):
        """Carrega perfil de arquivo JSON"""
        try:
            profile_file = Path("data/user_data.json")
            if profile_file.exists():
                with open(profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_info = UserInfo(**data)
                self.logger.info("Perfil carregado do arquivo JSON")
        except Exception as e:
            self.logger.error(f"Erro ao carregar do arquivo: {e}")
    
    async def save_profile(self):
        """Salva perfil no banco e arquivo"""
        try:
            # Salvar no banco
            await self.database.save_user_profile(asdict(self.user_info))
            
            # Backup em arquivo JSON
            await self.save_to_file()
            
            self.last_updated = datetime.now()
            self.logger.info("Perfil do usuário salvo com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar perfil: {e}")
    
    async def save_to_file(self):
        """Salva perfil em arquivo JSON"""
        try:
            profile_file = Path("data/user_data.json")
            profile_file.parent.mkdir(exist_ok=True)
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.user_info), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar arquivo: {e}")
    
    async def extract_and_update_info(self, text: str):
        """Extrai e atualiza informações do texto"""
        text_lower = text.lower()
        updated = False
        
        try:
            # Extrair nome
            if not self.user_info.name:
                for pattern in self.extraction_patterns['name']:
                    match = re.search(pattern, text_lower)
                    if match:
                        name = match.group(1).strip().title()
                        if len(name) > 1 and len(name) < 50:  # Validação básica
                            self.user_info.name = name
                            updated = True
                            self.logger.info(f"Nome extraído: {name}")
                            break
            
            # Extrair idade
            if not self.user_info.age:
                for pattern in self.extraction_patterns['age']:
                    match = re.search(pattern, text_lower)
                    if match:
                        age = int(match.group(1))
                        if 1 <= age <= 120:  # Validação básica
                            self.user_info.age = age
                            updated = True
                            self.logger.info(f"Idade extraída: {age}")
                            break
            
            # Extrair localização
            if not self.user_info.location:
                for pattern in self.extraction_patterns['location']:
                    match = re.search(pattern, text_lower)
                    if match:
                        location = match.group(1).strip().title()
                        if len(location) > 1:
                            self.user_info.location = location
                            updated = True
                            self.logger.info(f"Localização extraída: {location}")
                            break
            
            # Extrair profissão
            if not self.user_info.occupation:
                for pattern in self.extraction_patterns['occupation']:
                    match = re.search(pattern, text_lower)
                    if match:
                        occupation = match.group(1).strip()
                        if len(occupation) > 1:
                            self.user_info.occupation = occupation
                            updated = True
                            self.logger.info(f"Profissão extraída: {occupation}")
                            break
            
            # Extrair hobbies
            for pattern in self.extraction_patterns['hobbies']:
                match = re.search(pattern, text_lower)
                if match:
                    hobby = match.group(1).strip()
                    if hobby not in self.user_info.hobbies and len(hobby) > 1:
                        self.user_info.hobbies.append(hobby)
                        updated = True
                        self.logger.info(f"Hobby extraído: {hobby}")
            
            # Extrair informações sobre família
            family_patterns = [
                (r'minha mãe se chama (.+?)(?:\.|,|$)', 'mãe'),
                (r'meu pai se chama (.+?)(?:\.|,|$)', 'pai'),
                (r'minha esposa se chama (.+?)(?:\.|,|$)', 'esposa'),
                (r'meu marido se chama (.+?)(?:\.|,|$)', 'marido'),
                (r'tenho um filho chamado (.+?)(?:\.|,|$)', 'filho'),
                (r'tenho uma filha chamada (.+?)(?:\.|,|$)', 'filha')
            ]
            
            for pattern, relation in family_patterns:
                match = re.search(pattern, text_lower)
                if match and relation not in self.user_info.family:
                    name = match.group(1).strip().title()
                    self.user_info.family[relation] = name
                    updated = True
                    self.logger.info(f"Família extraída: {relation} - {name}")
            
            # Salvar se houve atualizações
            if updated:
                await self.save_profile()
                
        except Exception as e:
            self.logger.error(f"Erro na extração de informações: {e}")
    
    def get_user_name(self) -> str:
        """Retorna nome do usuário ou padrão"""
        return self.user_info.name if self.user_info.name else "usuário"
    
    def get_summary(self) -> str:
        """Retorna resumo das informações do usuário"""
        summary_parts = []
        
        if self.user_info.name:
            summary_parts.append(f"Nome: {self.user_info.name}")
        
        if self.user_info.age:
            summary_parts.append(f"Idade: {self.user_info.age} anos")
        
        if self.user_info.location:
            summary_parts.append(f"Localização: {self.user_info.location}")
        
        if self.user_info.occupation:
            summary_parts.append(f"Profissão: {self.user_info.occupation}")
        
        if self.user_info.hobbies:
            hobbies_str = ", ".join(self.user_info.hobbies)
            summary_parts.append(f"Hobbies: {hobbies_str}")
        
        if self.user_info.family:
            family_str = ", ".join([f"{k}: {v}" for k, v in self.user_info.family.items()])
            summary_parts.append(f"Família: {family_str}")
        
        if not summary_parts:
            return "Nenhuma informação pessoal conhecida ainda."
        
        return "\n".join(summary_parts)
    
    def add_preference(self, key: str, value: Any):
        """Adiciona preferência do usuário"""
        self.user_info.preferences[key] = value
        import asyncio
        asyncio.create_task(self.save_profile())
    
    def get_preference(self, key: str, default=None):
        """Obtém preferência do usuário"""
        return self.user_info.preferences.get(key, default)
    
    def add_goal(self, goal: str):
        """Adiciona objetivo do usuário"""
        if goal not in self.user_info.goals:
            self.user_info.goals.append(goal)
            import asyncio
            asyncio.create_task(self.save_profile())
    
    def add_important_date(self, date_name: str, date_value: str):
        """Adiciona data importante"""
        self.user_info.important_dates[date_name] = date_value
        import asyncio
        asyncio.create_task(self.save_profile())