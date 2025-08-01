"""Módulo de memória e persistência de dados"""

from .user_profile import UserProfile, UserInfo
from .database import DatabaseManager

__all__ = ['UserProfile', 'UserInfo', 'DatabaseManager']
