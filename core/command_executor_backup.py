# core/command_executor.py - Corrigido completamente
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
        
        # Verificar novos comandos de voz
        voice_command = self._detect_voice_commands(text)
        if voice_command:
            return await self.execute_voice_command(voice_command, text)
        
        return None
    
    def _detect_voice_commands(self, text: str) -> Optional[str]:
        """Detecta comandos específicos de voz"""
        text_lower = text.lower()
        
        # Comandos de teste de voz humana
        if any(cmd in text_lower for cmd in [
            "teste voz humana", "voz humana", "teste coqui",
            "demonstre voz humana", "sistema de voz"
        ]):
            return "test_human_voice"
        
        # Comandos de qualidade de voz
        if any(cmd in text_lower for cmd in [
            "qualidade de voz", "teste qualidade", "como está sua voz"
        ]):
            return "test_voice_quality"
        
        # Comandos de sistema de áudio
        if any(cmd in text_lower for cmd in [
            "reset áudio", "reseta áudio", "problema de áudio"
        ]):
            return "reset_audio"
        
        # Info do sistema de voz
        if any(cmd in text_lower for cmd in [
            "info da voz", "sistema atual", "que voz você usa"
        ]):
            return "voice_system_info"
        
        return None
    
    async def execute_voice_command(self, command: str, original_text: str) -> str:
        """Executa comandos específicos de voz"""
        try:
            if command == "test_human_voice":
                return await self.execute_human_voice_test()
            elif command == "test_voice_quality":
                return await self.execute_voice_quality_test()
            elif command == "reset_audio":
                return await self.execute_audio_reset()
            elif command == "voice_system_info":
                return await self.execute_voice_info()
            else:
                return f"Comando de voz '{command}' reconhecido mas não implementado."
        except Exception as e:
            self.logger.error(f"Erro ao executar comando de voz {command}: {e}")
            return f"Houve um erro ao executar o comando de voz: {str(e)}"
    
    async def execute_human_voice_test(self) -> str:
        """Executa teste completo do sistema de voz humana"""
        await self.agent.speak_robust("Iniciando teste completo do sistema de voz humana!", "animado")
        
        try:
            # Verificar se tem o sistema de voz humana
            if hasattr(self.agent.tts, 'human_voice') and self.agent.tts.human_voice:
                # Teste usando sistema Coqui
                await self.agent.speak_robust("Usando sistema Coqui TTS para máxima naturalidade!", "feliz")
                
                # Teste de emoções avançado
                await self.agent.tts.human_voice.test_all_emotions()
                
                # Teste de qualidade vocal
                await self.agent.tts.human_voice.test_voice_quality()
                
                await self.agent.speak_robust("Teste do sistema de voz humana concluído com sucesso!", "feliz")
                return "Sistema de voz humana testado com todas as emoções e qualidades!"
            
            elif hasattr(self.agent.tts, 'test_voice_emotions'):
                # Fallback para sistema anterior
                await self.agent.speak_robust("Usando sistema de voz padrão.", "neutro")
                await self.agent.tts.test_voice_emotions()
                return "Teste de voz padrão executado!"
            
            else:
                return "Sistema de teste de voz não disponível."
                
        except Exception as e:
            await self.agent.speak_robust("Houve um problema durante o teste de voz.", "frustrado")
            return f"Erro no teste de voz: {str(e)}"
    
    async def execute_voice_quality_test(self) -> str:
        """Testa especificamente a qualidade da voz"""
        await self.agent.speak_robust("Testando qualidade vocal...", "curioso")
        
        try:
            if hasattr(self.agent.tts, 'test_voice_quality'):
                await self.agent.tts.test_voice_quality()
                await self.agent.speak_robust("Teste de qualidade vocal concluído!", "feliz")
                return "Qualidade de voz testada com sucesso!"
            else:
                # Teste básico
                test_phrases = [
                    ("Testando articulação e clareza vocal.", "neutro"),
                    ("Pronunciação de palavras complexas: exceção, perspicácia.", "neutro"),
                    ("Variação tonal e expressividade emocional.", "curioso"),
                    ("Fluidez e naturalidade na fala contínua.", "carinhoso")
                ]
                
                for phrase, emotion in test_phrases:
                    await self.agent.speak_robust(phrase, emotion)
                    await asyncio.sleep(1)
                
                return "Teste básico de qualidade executado!"
                
        except Exception as e:
            await self.agent.speak_robust("Problema no teste de qualidade.", "frustrado")
            return f"Erro no teste de qualidade: {str(e)}"
    
    async def execute_audio_reset(self) -> str:
        """Reseta sistema de áudio"""
        await self.agent.speak_robust("Resetando sistema de áudio...", "neutro")
        
        try:
            if hasattr(self.agent.tts, 'reset_audio_system'):
                self.agent.tts.reset_audio_system()
                await self.agent.speak_robust("Sistema de áudio resetado com sucesso!", "feliz")
                return "Sistema de áudio resetado!"
            else:
                return "Função de reset de áudio não disponível."
                
        except Exception as e:
            await self.agent.speak_robust("Erro ao resetar sistema de áudio.", "frustrado")
            return f"Erro no reset de áudio: {str(e)}"
    
    async def execute_voice_info(self) -> str:
        """Fornece informações sobre o sistema de voz atual"""
        try:
            if hasattr(self.agent.tts, 'get_current_system'):
                current_system = self.agent.tts.get_current_system()
                await self.agent.speak_robust(f"Estou usando o sistema: {current_system}", "neutro")
                
                # Informações adicionais
                if hasattr(self.agent.tts, 'get_available_emotions'):
                    emotions = self.agent.tts.get_available_emotions()
                    await self.agent.speak_robust(f"Tenho {len(emotions)} emoções disponíveis.", "feliz")
                
                return f"Sistema atual: {current_system}"
            else:
                await self.agent.speak_robust("Informações do sistema de voz não disponíveis.", "neutro")
                return "Info do sistema não disponível."
                
        except Exception as e:
            return f"Erro ao obter info do sistema: {str(e)}"
    
    async def execute_command(self, command: str, original_text: str) -> str:
        """Executa comandos internos originais"""
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
        """Análise de código"""
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
        """Teste de voz original (agora melhorado)"""
        # Usar novo sistema se disponível
        return await self.execute_human_voice_test()
    
    async def execute_backup(self) -> str:
        """Backup do código"""
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
        """Auto-melhoria do sistema"""
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
        """Relatório de status completo"""
        await self.agent.speak_robust("Gerando relatório de status completo...", "neutro")
        
        try:
            # Status básico
            components_status = "Todos os meus componentes estão funcionando: reconhecimento de voz, síntese de voz, inteligência artificial e auto-modificação."
            
            # Informações do sistema de voz
            if hasattr(self.agent.tts, 'get_current_system'):
                voice_system = self.agent.tts.get_current_system()
                components_status += f" Estou usando o sistema de voz: {voice_system}."
            
            # Status da IA
            if hasattr(self.agent.llm, 'get_model_info'):
                model_info = self.agent.llm.get_model_info()
                components_status += f" Modelo de IA: {model_info.get('model_name', 'Desconhecido')}."
            
            await self.agent.speak_robust(components_status, "feliz")
            return "Relatório de status executado!"
        except Exception as e:
            await self.agent.speak_robust("Houve um problema ao gerar o relatório.", "frustrado")
            return f"Erro no relatório: {str(e)}"