# core/self_modifier.py
import logging
from core.code_analyzer import CodeAnalyzer

class SelfModifier:
    def __init__(self, llm, user_profile):
        self.llm = llm
        self.user_profile = user_profile
        self.code_analyzer = CodeAnalyzer()
        self.logger = logging.getLogger(__name__)
        self.auto_modify_enabled = False
        
    async def analyze_self(self):
        print("🔍 Analisando meu próprio código...")
        
        analysis = self.code_analyzer.analyze_code_structure()
        
        print("📊 Análise completa:")
        print(f"   • {len(analysis['files'])} arquivos analisados")
        print(f"   • {analysis['total_lines']} linhas de código")
        print(f"   • {analysis['functions']} funções")
        print(f"   • {analysis['classes']} classes")
        print(f"   • {len(analysis['potential_issues'])} problemas detectados")
        
        if analysis['potential_issues']:
            print("\n⚠️  Problemas encontrados:")
            for issue in analysis['potential_issues']:
                print(f"   • {issue}")
        
        return analysis
    
    async def handle_modification_request(self, request):
        request_lower = request.lower()
        
        if "analis" in request_lower:
            analysis = await self.analyze_self()
            
            response = "📋 Análise do meu código completa!\n\n"
            response += f"Encontrei {len(analysis['potential_issues'])} problemas.\n\n"
            response += "💡 Status atual:\n"
            response += f"• {len(analysis['files'])} arquivos monitorados\n"
            response += f"• {analysis['total_lines']} linhas de código\n"
            response += f"• {analysis['functions']} funções\n"
            response += f"• {analysis['classes']} classes"
            
            return response
        
        elif "melhor" in request_lower or "otimiz" in request_lower:
            analysis = await self.analyze_self()
            
            if analysis['potential_issues']:
                return "✨ Identifiquei algumas áreas para melhoria! Posso trabalhar nisso."
            else:
                return "✅ Meu código está em bom estado! Nenhuma melhoria crítica necessária."
        
        elif "backup" in request_lower:
            backup_path = self.code_analyzer.create_backup()
            return f"💾 Backup criado: {backup_path}"
        
        elif "status" in request_lower:
            analysis = self.code_analyzer.analyze_code_structure()
            
            status = "📊 Status atual do meu código:\n"
            status += f"• {len(analysis['files'])} arquivos monitorados\n"
            status += f"• {analysis['total_lines']} linhas de código\n"
            status += f"• {analysis['functions']} funções\n"
            status += f"• {analysis['classes']} classes\n"
            status += f"• {len(analysis['potential_issues'])} problemas detectados\n"
            
            if self.auto_modify_enabled:
                status += "• Auto-modificação: 🟢 Ativa"
            else:
                status += "• Auto-modificação: 🔴 Inativa"
            
            return status
        
        else:
            return "🤔 Comandos disponíveis: analisar, melhorar, backup, status"
