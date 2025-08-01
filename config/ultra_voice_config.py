# config/ultra_voice_config.py - Configuração da voz ultra-realista
from pathlib import Path
import json

class UltraVoiceConfig:
    """Configuração avançada para voz ultra-realista"""
    
    def __init__(self):
        self.config_file = Path("config/ultra_voice_settings.json")
        self.load_config()
    
    def load_config(self):
        """Carrega configuração"""
        default_config = {
            "model": {
                "name": "tts_models/multilingual/multi-dataset/xtts_v2",
                "type": "xtts_v2",
                "device": "auto",  # auto, cuda, cpu
                "sample_rate": 24000,
                "use_gpu": True
            },
            "voice": {
                "default_emotion": "neutro",
                "speaker_reference": "sexta_feira_ultra.wav",
                "voice_style": "natural_female_brazilian",
                "quality": "ultra_high"
            },
            "emotions": {
                "neutro": {
                    "temperature": 0.7,
                    "repetition_penalty": 1.1,
                    "speed_factor": 1.0,
                    "volume": 0.85,
                    "pause_after": 0.3
                },
                "feliz": {
                    "temperature": 0.85,
                    "repetition_penalty": 1.0,
                    "speed_factor": 1.15,
                    "volume": 0.9,
                    "pause_after": 0.2
                },
                "carinhoso": {
                    "temperature": 0.5,
                    "repetition_penalty": 1.2,
                    "speed_factor": 0.85,
                    "volume": 0.75,
                    "pause_after": 0.8
                },
                "triste": {
                    "temperature": 0.4,
                    "repetition_penalty": 1.3,
                    "speed_factor": 0.75,
                    "volume": 0.7,
                    "pause_after": 1.0
                },
                "animado": {
                    "temperature": 0.9,
                    "repetition_penalty": 0.9,
                    "speed_factor": 1.25,
                    "volume": 0.95,
                    "pause_after": 0.1
                },
                "curioso": {
                    "temperature": 0.75,
                    "repetition_penalty": 1.1,
                    "speed_factor": 1.05,
                    "volume": 0.85,
                    "pause_after": 0.4
                },
                "sedutor": {
                    "temperature": 0.45,
                    "repetition_penalty": 1.4,
                    "speed_factor": 0.8,
                    "volume": 0.7,
                    "pause_after": 1.2
                },
                "surpreso": {
                    "temperature": 0.95,
                    "repetition_penalty": 0.8,
                    "speed_factor": 1.3,
                    "volume": 0.9,
                    "pause_after": 0.2
                }
            },
            "processing": {
                "async_generation": True,
                "queue_size": 5,
                "timeout": 30,
                "enhance_audio": True,
                "normalize_volume": True
            },
            "performance": {
                "use_threading": True,
                "preload_model": True,
                "cache_size": 100,
                "cleanup_temps": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge com configuração padrão
                    self.config = self._merge_configs(default_config, loaded_config)
            except Exception as e:
                print(f"⚠️ Erro ao carregar config: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def _merge_configs(self, default, loaded):
        """Mescla configurações recursivamente"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        """Salva configuração"""
        try:
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erro ao salvar config: {e}")
    
    def get_model_config(self):
        """Configuração do modelo"""
        return self.config["model"]
    
    def get_voice_config(self):
        """Configuração da voz"""
        return self.config["voice"]
    
    def get_emotion_config(self, emotion: str):
        """Configuração de uma emoção específica"""
        return self.config["emotions"].get(emotion, self.config["emotions"]["neutro"])
    
    def get_processing_config(self):
        """Configuração de processamento"""
        return self.config["processing"]
    
    def get_performance_config(self):
        """Configuração de performance"""
        return self.config["performance"]
    
    def update_emotion(self, emotion: str, settings: dict):
        """Atualiza configuração de uma emoção"""
        if emotion in self.config["emotions"]:
            self.config["emotions"][emotion].update(settings)
            self.save_config()
    
    def set_device(self, device: str):
        """Define dispositivo (cuda/cpu)"""
        self.config["model"]["device"] = device
        self.save_config()
    
    def set_quality(self, quality: str):
        """Define qualidade (ultra_high/high/medium)"""
        quality_map = {
            "ultra_high": 24000,
            "high": 22050,
            "medium": 16000
        }
        
        if quality in quality_map:
            self.config["model"]["sample_rate"] = quality_map[quality]
            self.config["voice"]["quality"] = quality
            self.save_config()

# Configuração global
ULTRA_VOICE_CONFIG = UltraVoiceConfig()

# Funções de conveniência
def get_model_config():
    return ULTRA_VOICE_CONFIG.get_model_config()

def get_emotion_config(emotion: str):
    return ULTRA_VOICE_CONFIG.get_emotion_config(emotion)

def get_voice_config():
    return ULTRA_VOICE_CONFIG.get_voice_config()

def set_device(device: str):
    ULTRA_VOICE_CONFIG.set_device(device)

def set_quality(quality: str):
    ULTRA_VOICE_CONFIG.set_quality(quality)