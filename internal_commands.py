# internal_commands.py
print("🔧 Implementando sistema de comandos internos da SEXTA-FEIRA...")

# 1. Criar detector de comandos internos
command_detector_code = '''# core/command_detector.py
import re
import logging
from typing import Tuple, Optional

class InternalCommandDetector:
    """Detecta comandos internos na fala natural do usuário"""
    
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
        """
        Detecta comando interno no texto
        
        Returns:
            (command_type: str, reason: str, confidence: float)
        """
        text_lower = text.lower()
        
        # Verificar análise de código
        for pattern in self.code_analysis_patterns:
            if re.search(pattern, text_lower):
                return "analyze_code", f"Comando de análise detectado: '{pattern}'", 0.95
        
        # Verificar teste de voz
        for pattern in self.voice_test_patterns:
            if re.search(pattern, text_lower):
                return "test_voice", f"Comando de teste de voz detectado: '{pattern}'", 0.95
        
        # Verificar backup
        for pattern in self.backup_patterns:
            if re.search(pattern, text_lower):
                return "create_backup", f"Comando de backup detectado: '{pattern}'", 0.95
        
        # Verificar melhorias
        for pattern in self.improvement_patterns:
            if re.search(pattern, text_lower):
                return "self_improve", f"Comando de melhoria detectado: '{pattern}'", 0.95
        
        # Verificar status geral
        for pattern in self.status_patterns:
            if re.search(pattern, text_lower):
                return "status_report", f"Comando de status detectado: '{pattern}'", 0.95
        
        return None, "Nenhum comando interno detectado", 0.0
    
    def is_internal_command(self, text: str) -> bool:
        """Verifica rapidamente se há comando interno"""
        command, _, confidence = self.detect_command(text)
        return command is not None and confidence > 0.8
'''

# 2. Criar executor de comandos internos
command_executor_code = '''# core/command_executor.py
import asyncio
import logging
from typing import Optional
from core.command_detector import InternalCommandDetector

class InternalCommandExecutor:
    """Executa comandos internos da SEXTA-FEIRA"""
    
    def __init__(self, agent):
        self.agent = agent
        self.detector = InternalCommandDetector()
        self.logger = logging.getLogger(__name__)
    
    async def process_natural_command(self, text: str) -> Optional[str]:
        """
        Processa comando natural e executa se for interno
        
        Returns:
            response: str se foi comando interno, None caso contrário
        """
        command, reason, confidence = self.detector.detect_command(text)
        
        if command and confidence > 0.8:
            self.logger.info(f"Comando interno detectado: {command} ({confidence:.2f})")
            return await self.execute_command(command, text)
        
        return None
    
    async def execute_command(self, command: str, original_text: str) -> str:
        """Executa comando interno específico"""
        try:
            if command == "analyze_code":
                return await self.execute_code_analysis()
            
            elif command == "test_voice":
                return await self.execute_voice_test()
            
            elif command == "create_backup":
                return await self.execute_backup()
            
            elif command == "self_improve":
                return await self.execute_self_improvement()
            
            elif command == "status_report":
                return await self.execute_status_report()
            
            else:
                return f"Comando '{command}' reconhecido mas não implementado ainda."
                
        except Exception as e:
            self.logger.error(f"Erro ao executar comando {command}: {e}")
            return f"Houve um erro ao executar o comando. Detalhes: {str(e)}"
    
    async def execute_code_analysis(self) -> str:
        """Executa análise do próprio código"""
        # Falar primeiro que está analisando
        await self.agent.speak_with_emotion("Analisando meu código...", "curioso")
        
        try:
            # Executar análise real
            if self.agent.self_modifier:
                analysis = await self.agent.self_modifier.analyze_self()
                
                # Criar resposta falada sobre o status
                files_count = len(analysis.get('files', {}))
                total_lines = analysis.get('total_lines', 0)
                functions_count = analysis.get('functions', 0)
                classes_count = analysis.get('classes', 0)
                issues_count = len(analysis.get('potential_issues', []))
                
                status_response = f"""Análise concluída! Meu código possui {files_count} arquivos com {total_lines} linhas, 
{functions_count} funções e {classes_count} classes. """
                
                if issues_count > 0:
                    status_response += f"Encontrei {issues_count} pontos para melhoria."
                else:
                    status_response += "Está tudo funcionando perfeitamente!"
                
                # Falar resultado
                await self.agent.speak_with_emotion(status_response, "feliz" if issues_count == 0 else "neutro")
                
                return "Análise de código executada com sucesso!"
            else:
                return "Sistema de auto-análise não está disponível."
                
        except Exception as e:
            await self.agent.speak_with_emotion("Houve um problema durante a análise.", "triste")
            return f"Erro na análise: {str(e)}"
    
    async def execute_voice_test(self) -> str:
        """Executa teste de voz com emoções"""
        await self.agent.speak_with_emotion("Vou demonstrar minhas diferentes emoções!", "feliz")
        
        try:
            await self.agent.test_voice_emotions()
            await self.agent.speak_with_emotion("Demonstração de emoções concluída!", "feliz")
            return "Teste de voz executado com sucesso!"
            
        except Exception as e:
            await self.agent.speak_with_emotion("Houve um problema no teste de voz.", "frustrado")
            return f"Erro no teste de voz: {str(e)}"
    
    async def execute_backup(self) -> str:
        """Executa backup do código"""
        await self.agent.speak_with_emotion("Criando backup do meu código...", "neutro")
        
        try:
            if self.agent.self_modifier and self.agent.self_modifier.code_analyzer:
                backup_path = self.agent.self_modifier.code_analyzer.create_backup()
                await self.agent.speak_with_emotion(f"Backup criado com sucesso!", "feliz")
                return f"Backup criado em: {backup_path}"
            else:
                return "Sistema de backup não está disponível."
                
        except Exception as e:
            await self.agent.speak_with_emotion("Houve um problema ao criar o backup.", "frustrado")
            return f"Erro no backup: {str(e)}"
    
    async def execute_self_improvement(self) -> str:
        """Executa processo de auto-melhoria"""
        await self.agent.speak_with_emotion("Analisando possibilidades de melhoria...", "curioso")
        
        try:
            if self.agent.self_modifier:
                # Fazer análise primeiro
                analysis = await self.agent.self_modifier.analyze_self()
                suggestions = await self.agent.self_modifier.suggest_self_improvements(analysis)
                
                if suggestions:
                    await self.agent.speak_with_emotion(
                        f"Identifiquei {len(suggestions)} áreas para melhoria. Trabalhando nisso!", 
                        "feliz"
                    )
                else:
                    await self.agent.speak_with_emotion(
                        "Meu código está otimizado! Não há melhorias necessárias no momento.", 
                        "feliz"
                    )
                
                return "Processo de auto-melhoria executado!"
            else:
                return "Sistema de auto-melhoria não está disponível."
                
        except Exception as e:
            await self.agent.speak_with_emotion("Houve um problema na auto-melhoria.", "frustrado")
            return f"Erro na auto-melhoria: {str(e)}"
    
    async def execute_status_report(self) -> str:
        """Executa relatório de status completo"""
        await self.agent.speak_with_emotion("Gerando relatório de status completo...", "neutro")
        
        try:
            # Coletar informações de status
            status_parts = []
            
            # Status dos componentes
            components_status = "Todos os meus componentes estão funcionando: "
            active_components = []
            
            if self.agent.stt:
                active_components.append("reconhecimento de voz")
            if self.agent.tts:
                active_components.append("síntese de voz")
            if self.agent.llm:
                active_components.append("inteligência artificial")
            if self.agent.self_modifier:
                active_components.append("auto-modificação")
            
            components_status += ", ".join(active_components) + "."
            
            # Status da conversa
            if hasattr(self.agent.context_analyzer, 'conversation_state'):
                conv_status = self.agent.context_analyzer.get_conversation_status()
                status_parts.append(f"Status da conversa: {conv_status}")
            
            # Falar status
            full_status = f"{components_status} {' '.join(status_parts)}"
            await self.agent.speak_with_emotion(full_status, "feliz")
            
            return "Relatório de status executado!"
            
        except Exception as e:
            await self.agent.speak_with_emotion("Houve um problema ao gerar o relatório.", "frustrado")
            return f"Erro no relatório: {str(e)}"
'''

# 3. Criar script para integrar ao agent.py
integration_script = '''# integrate_commands.py
print("🔧 Integrando sistema de comandos internos ao agent.py...")

# Ler arquivo atual
with open("core/agent.py", "r", encoding="utf-8") as f:
    content = f.read()

# Adicionar import do executor de comandos
if "from core.command_executor import InternalCommandExecutor" not in content:
    # Encontrar linha dos imports
    import_pos = content.find("from core.self_modifier import SelfModifier")
    if import_pos != -1:
        end_line = content.find("\\n", import_pos)
        new_import = "\\nfrom core.command_executor import InternalCommandExecutor"
        content = content[:end_line] + new_import + content[end_line:]
        print("✅ Import do InternalCommandExecutor adicionado")

# Adicionar inicialização do executor
if "self.command_executor" not in content:
    init_pos = content.find("self.self_modifier = None")
    if init_pos != -1:
        end_line = content.find("\\n", init_pos)
        addition = "\\n        self.command_executor = None"
        content = content[:end_line] + addition + content[end_line:]
        print("✅ Variável command_executor adicionada")

# Adicionar inicialização no initialize()
if "InternalCommandExecutor(self)" not in content:
    init_pos = content.find("self.self_modifier = SelfModifier(self.llm, self.user_profile)")
    if init_pos != -1:
        end_line = content.find("\\n", init_pos)
        addition = "\\n            self.command_executor = InternalCommandExecutor(self)"
        content = content[:end_line] + addition + content[end_line:]
        print("✅ Inicialização do command_executor adicionada")

# Modificar process_input para verificar comandos internos primeiro
process_input_pos = content.find("async def process_input(self, user_input: str) -> Optional[str]:")
if process_input_pos != -1:
    method_start = content.find("print(\\"🧠 Processando...\\")", process_input_pos)
    if method_start != -1:
        new_logic = '''print("🧠 Processando...")
            
            # Verificar comandos internos primeiro
            if self.command_executor:
                internal_response = await self.command_executor.process_natural_command(user_input)
                if internal_response:
                    return internal_response
            
            # Verificar comandos de auto-modificação
            mod_commands = ["analisar código", "melhorar código", "status código", "backup código"]
            if any(cmd in user_input.lower() for cmd in mod_commands):
                return await self.handle_self_modification(user_input)'''
        
        # Encontrar fim da seção de comandos
        end_pos = content.find("await self.user_profile.extract_and_update_info(user_input)", method_start)
        if end_pos != -1:
            content = content[:method_start] + new_logic + "\\n            \\n            " + content[end_pos:]
            print("✅ Lógica de comandos internos integrada")

# Salvar arquivo modificado
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Sistema de comandos internos integrado!")
'''

# Salvar todos os arquivos
print("📝 Criando core/command_detector.py...")
with open("core/command_detector.py", "w", encoding="utf-8") as f:
    f.write(command_detector_code)

print("📝 Criando core/command_executor.py...")
with open("core/command_executor.py", "w", encoding="utf-8") as f:
    f.write(command_executor_code)

print("📝 Criando integrate_commands.py...")
with open("integrate_commands.py", "w", encoding="utf-8") as f:
    f.write(integration_script)

print("✅ Sistema de comandos internos criado!")
print("")
print("🎯 FUNCIONALIDADES IMPLEMENTADAS:")
print("• 🧠 Detecção automática de comandos internos")
print("• 🎤 Execução com resposta falada")
print("• 🔍 Análise de código por comando de voz")
print("• 🎭 Teste de voz por comando natural")
print("• 💾 Backup automático por comando")
print("• 📊 Relatório de status completo")
print("• 🚀 Auto-melhoria por comando")
print("")
print("🚀 Para ativar:")
print("1. python integrate_commands.py")
print("2. python main.py")
print("")
print("💡 EXEMPLOS DE COMANDOS NATURAIS:")
print("• 'analise seu código' → Executa análise + fala resultado")
print("• 'teste sua voz' → Demonstra emoções")
print("• 'faça um backup' → Cria backup + confirma")
print("• 'como você está?' → Relatório completo")
print("• 'se melhore' → Auto-melhoria")
print("• 'verifica seu próprio código' → Análise")
print("• 'mostra suas emoções' → Teste de voz")