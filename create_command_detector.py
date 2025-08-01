# create_command_detector.py
print("🔧 Criando detector de comandos internos...")

command_detector_code = """# core/command_detector.py
import re
import logging
from typing import Tuple, Optional

class InternalCommandDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Padrões para detectar comandos de análise de código
        self.code_analysis_patterns = [
            r"\\b(analise|analisa|verifica|check)\\s+(o\\s+)?(seu\\s+|teu\\s+|o\\s+)?código\\b",
            r"\\b(como\\s+está|qual\\s+o\\s+status)\\s+(do\\s+|o\\s+)?(seu\\s+|teu\\s+)?código\\b",
            r"\\b(verifica|checa|olha)\\s+(seu\\s+|teu\\s+)?próprio\\s+código\\b",
            r"\\b(faz|faça)\\s+(uma\\s+)?análise\\s+(do\\s+|de\\s+)?(seu\\s+)?código\\b",
            r"\\b(auto.?análise|autoanálise)\\b",
            r"\\b(examine|examina)\\s+(seu\\s+|o\\s+)?código\\b",
            r"\\bse\\s+(analise|analisa|verifica)\\b",
            r"\\bstatus\\s+(do\\s+|de\\s+)?(seu\\s+)?código\\b",
        ]
        
        # Padrões para teste de voz
        self.voice_test_patterns = [
            r"\\b(teste|testa)\\s+(sua\\s+|a\\s+|tua\\s+)?voz\\b",
            r"\\b(mostra|mostre)\\s+(suas\\s+|as\\s+)?emoções\\b",
            r"\\b(fala|fale)\\s+com\\s+(todas\\s+as\\s+|diferentes\\s+)?emoções\\b",
            r"\\b(demonstra|demonstre)\\s+(sua\\s+|a\\s+)?voz\\b",
            r"\\b(teste|testa)\\s+(as\\s+|suas\\s+)?emoções\\b",
            r"\\bemoções\\s+(da\\s+|de\\s+)?voz\\b",
            r"\\bcomo\\s+(é\\s+|fica\\s+)?(sua\\s+|a\\s+|tua\\s+)?voz\\b",
        ]
        
        # Padrões para backup
        self.backup_patterns = [
            r"\\b(faz|faça|cria|crie)\\s+(um\\s+)?backup\\b",
            r"\\b(salva|salve)\\s+(o\\s+|seu\\s+)?código\\b",
            r"\\b(backup|cópia)\\s+(do\\s+|de\\s+)?(seu\\s+)?código\\b",
            r"\\bguarda\\s+(o\\s+|seu\\s+)?código\\b",
        ]
        
        # Padrões para melhorias
        self.improvement_patterns = [
            r"\\b(melhore.se|se\\s+melhore|melhora\\s+você\\s+mesma)\\b",
            r"\\b(otimize.se|se\\s+otimize|otimiza\\s+você\\s+mesma)\\b",
            r"\\b(melhore|melhora|otimize|otimiza)\\s+(seu\\s+|o\\s+)?código\\b",
            r"\\b(se\\s+)?(aprimore|aprimore.se)\\b",
            r"\\bfica\\s+(melhor|mais\\s+inteligente)\\b",
        ]
        
        # Padrões para status geral
        self.status_patterns = [
            r"\\b(como\\s+você\\s+está|qual\\s+seu\\s+status)\\b",
            r"\\b(status\\s+geral|estado\\s+atual)\\b",
            r"\\b(relatório|report)\\s+(completo|geral)\\b",
            r"\\b(diagnóstico|diagnóstica)\\s+(completo|geral)\\b",
        ]
    
    def detect_command(self, text: str) -> Tuple[Optional[str], str, float]:
        text_lower = text.lower()
        
        # Verificar análise de código
        for pattern in self.code_analysis_patterns:
            if re.search(pattern, text_lower):
                return "analyze_code", f"Comando de análise detectado", 0.95
        
        # Verificar teste de voz
        for pattern in self.voice_test_patterns:
            if re.search(pattern, text_lower):
                return "test_voice", f"Comando de teste de voz detectado", 0.95
        
        # Verificar backup
        for pattern in self.backup_patterns:
            if re.search(pattern, text_lower):
                return "create_backup", f"Comando de backup detectado", 0.95
        
        # Verificar melhorias
        for pattern in self.improvement_patterns:
            if re.search(pattern, text_lower):
                return "self_improve", f"Comando de melhoria detectado", 0.95
        
        # Verificar status geral
        for pattern in self.status_patterns:
            if re.search(pattern, text_lower):
                return "status_report", f"Comando de status detectado", 0.95
        
        return None, "Nenhum comando interno detectado", 0.0
    
    def is_internal_command(self, text: str) -> bool:
        command, _, confidence = self.detect_command(text)
        return command is not None and confidence > 0.8
"""

# Salvar arquivo
with open("core/command_detector.py", "w", encoding="utf-8") as f:
    f.write(command_detector_code)

print("✅ command_detector.py criado com sucesso!")
print("🔄 Execute o próximo script: create_command_executor.py")