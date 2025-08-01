# config/voice_system_config.py
# Configuração automática baseada na instalação

VOICE_SYSTEM_CONFIG = {
    "primary_system": "gtts_pygame",
    "available_systems": ['pytorch', 'tts', 'tts_api', 'gtts', 'pygame', 'pyttsx3', 'librosa'],
    "coqui_available": False,
    "fallbacks_available": True,
    "audio_available": True,
    "installation_date": "1754067759.068445"
}
