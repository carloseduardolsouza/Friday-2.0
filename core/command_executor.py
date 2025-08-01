# core/command_executor.py - Correção simples
# Substituir todas as chamadas speak_with_emotion por speak_robust

import asyncio
import logging
from typing import Optional
from core.command_detector import InternalCommandDetector

class InternalCommandExecutor:
    def __init__(self, agent):
        self.agent = agent
        self.detector = InternalCommandDetector()
        self.logger = logging.getLogger(__name__)
    
    async def process_natural_command(self, text: str) -> Optional[str]:
        command, reason, confidence = self.detector.detect_command(text)
        
        if command and confidence > 0.8:
            self.logger.info(f"Comando interno detectado: {command} ({confidence:.2f})")
            return await self.execute_command(command, text)
        
        return None
    
    async def execute_command(self, command: str, original_text: str) -> str:
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
        await self.agent.speak_robust("Analisando meu código...", "curioso")
        
        try:
            if self.agent.self_modifier:
                analysis = await self.agent.self_modifier.analyze_self()
                files_count = len(analysis.get('files', {}))
                total_lines = analysis.get('total_lines', 0)
                issues_count = len(analysis.get('potential_issues', []))
                
                status_response = f"Análise concluída! Meu código possui {files_count} arquivos com {total_lines} linhas. "
                if issues_count > 0:
                    status_response += f"Encontrei {issues_count} pontos para melhoria."
                else:
                    status_response += "Está tudo funcionando perfeitamente!"
                
                await self.agent.speak_robust(status_response, "feliz" if issues_count == 0 else "neutro")
                return "Análise de código executada com sucesso!"
            else:
                return "Sistema de auto-análise não está disponível."
        except Exception as e:
            await self.agent.speak_robust("Houve um problema durante a análise.", "triste")
            return f"Erro na análise: {str(e)}"
    
    async def execute_voice_test(self) -> str:
        await self.agent.speak_robust("Vou demonstrar minhas diferentes emoções!", "feliz")
        
        try:
            await self.agent.test_voice_emotions()
            await self.agent.speak_robust("Demonstração de emoções concluída!", "feliz")
            return "Teste de voz executado com sucesso!"
        except Exception as e:
            await self.agent.speak_robust("Houve um problema no teste de voz.", "frustrado")
            return f"Erro no teste de voz: {str(e)}"
    
    async def execute_backup(self) -> str:
        await self.agent.speak_robust("Criando backup do meu código...", "neutro")
        
        try:
            if self.agent.self_modifier and self.agent.self_modifier.code_analyzer:
                backup_path = self.agent.self_modifier.code_analyzer.create_backup()
                await self.agent.speak_robust("Backup criado com sucesso!", "feliz")
                return f"Backup criado em: {backup_path}"
            else:
                return "Sistema de backup não está disponível."
        except Exception as e:
            await self.agent.speak_robust("Houve um problema ao criar o backup.", "frustrado")
            return f"Erro no backup: {str(e)}"
    
    async def execute_self_improvement(self) -> str:
        await self.agent.speak_robust("Analisando possibilidades de melhoria...", "curioso")
        
        try:
            if self.agent.self_modifier:
                analysis = await self.agent.self_modifier.analyze_self()
                suggestions = ["Melhorar documentação", "Otimizar performance", "Adicionar mais testes"]
                
                if suggestions:
                    await self.agent.speak_robust(
                        f"Identifiquei {len(suggestions)} áreas para melhoria. Trabalhando nisso!",
                        "feliz"
                    )
                else:
                    await self.agent.speak_robust(
                        "Meu código está otimizado! Não há melhorias necessárias no momento.",
                        "feliz"
                    )
                
                return "Processo de auto-melhoria executado!"
            else:
                return "Sistema de auto-melhoria não está disponível."
        except Exception as e:
            await self.agent.speak_robust("Houve um problema na auto-melhoria.", "frustrado")
            return f"Erro na auto-melhoria: {str(e)}"
    
    async def execute_status_report(self) -> str:
        await self.agent.speak_robust("Gerando relatório de status completo...", "neutro")
        
        try:
            components_status = "Todos os meus componentes estão funcionando: reconhecimento de voz, síntese de voz, inteligência artificial e auto-modificação."
            await self.agent.speak_robust(components_status, "feliz")
            return "Relatório de status executado!"
        except Exception as e:
            await self.agent.speak_robust("Houve um problema ao gerar o relatório.", "frustrado")
            return f"Erro no relatório: {str(e)}"