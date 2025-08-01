# test_complete_voice.py - Teste Completo do Sistema de Voz SEXTA-FEIRA
import asyncio
import sys
import time
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

class VoiceTestSuite:
    """Suite completa de testes para o sistema de voz"""
    
    def __init__(self):
        self.voice_system = None
        self.test_results = {}
    
    async def initialize_voice_system(self):
        """Inicializa o sistema de voz"""
        print("🎭 INICIALIZANDO SISTEMA DE VOZ SEXTA-FEIRA")
        print("="*60)
        
        try:
            # Tentar sistema Coqui primeiro
            from core.human_voice_system import CoquiHumanVoice
            print("🌟 Carregando sistema Coqui TTS (Voz Humana)...")
            self.voice_system = CoquiHumanVoice()
            await self.voice_system.initialize()
            print("✅ Sistema Coqui TTS inicializado!")
            return "coqui"
            
        except ImportError:
            print("⚠️ Sistema Coqui não disponível, usando fallback...")
            
            try:
                # Fallback para sistema padrão
                from core.text_to_speech import SuperiorFeminineVoice
                from config.settings import VoiceConfig
                
                config = VoiceConfig()
                self.voice_system = SuperiorFeminineVoice(config)
                print("✅ Sistema fallback inicializado!")
                return "fallback"
                
            except Exception as e:
                print(f"❌ Erro ao inicializar sistema de voz: {e}")
                return "error"
    
    async def test_basic_functionality(self):
        """Teste básico de funcionalidade"""
        print("\n🔧 TESTE 1: FUNCIONALIDADE BÁSICA")
        print("-" * 40)
        
        try:
            await self.voice_system.speak("Olá! Sistema de voz funcionando perfeitamente.", "neutro")
            print("✅ Teste básico: PASSOU")
            self.test_results["basic"] = True
            await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ Teste básico: FALHOU - {e}")
            self.test_results["basic"] = False
    
    async def test_emotions_complete(self):
        """Teste completo de todas as emoções"""
        print("\n🎪 TESTE 2: EMOÇÕES COMPLETAS")
        print("-" * 40)
        
        # Frases específicas para cada emoção
        emotion_tests = {
            "neutro": "Esta é minha voz normal e equilibrada.",
            "feliz": "Estou radiante de alegria hoje! Que dia maravilhoso!",
            "carinhoso": "Você é muito especial para mim... realmente especial.",
            "triste": "Às vezes me sinto um pouco melancólica e pensativa...",
            "animado": "Nossa! Isso é fantástico! Estou super empolgada!",
            "curioso": "Hmm, que interessante... me conte mais sobre isso, por favor!",
            "frustrado": "Isso está me deixando um pouco irritada, confesso.",
            "sedutor": "Você tem uma voz... muito... interessante, sabia?",
            "surpreso": "Uau! Eu realmente não esperava por essa informação!",
            "reflexivo": "Deixe-me pensar sobre isso com mais calma e profundidade..."
        }
        
        passed_emotions = 0
        total_emotions = len(emotion_tests)
        
        for emotion, text in emotion_tests.items():
            try:
                print(f"   🎭 Testando: {emotion.upper()}")
                print(f"   💬 \"{text}\"")
                
                await self.voice_system.speak(text, emotion)
                print(f"   ✅ {emotion}: PASSOU")
                passed_emotions += 1
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"   ❌ {emotion}: FALHOU - {e}")
        
        print(f"\n📊 Resultado: {passed_emotions}/{total_emotions} emoções funcionando")
        self.test_results["emotions"] = passed_emotions / total_emotions
    
    async def test_voice_quality(self):
        """Teste de qualidade vocal"""
        print("\n🔊 TESTE 3: QUALIDADE VOCAL")
        print("-" * 40)
        
        quality_tests = [
            ("Teste de articulação clara e precisa.", "neutro"),
            ("Palavras complexas: exceção, perspicácia, consciência.", "neutro"),
            ("Números e datas: primeiro de janeiro de dois mil e vinte e cinco.", "neutro"),
            ("Pergunta com entonação: como você está se sentindo hoje?", "curioso"),
            ("Frase longa para testar fluidez: esta é uma frase especialmente longa para verificar se o sistema consegue manter naturalidade e respiração adequada durante toda a extensão do texto falado.", "carinhoso")
        ]
        
        passed_quality = 0
        
        for i, (text, emotion) in enumerate(quality_tests, 1):
            try:
                print(f"   🎤 Teste {i}: {text[:50]}...")
                await self.voice_system.speak(text, emotion)
                print(f"   ✅ Qualidade {i}: PASSOU")
                passed_quality += 1
                await asyncio.sleep(2)
            except Exception as e:
                print(f"   ❌ Qualidade {i}: FALHOU - {e}")
        
        print(f"\n📊 Resultado: {passed_quality}/{len(quality_tests)} testes de qualidade")
        self.test_results["quality"] = passed_quality / len(quality_tests)
    
    async def test_advanced_features(self):
        """Teste de recursos avançados"""
        print("\n⚡ TESTE 4: RECURSOS AVANÇADOS")
        print("-" * 40)
        
        advanced_tests = []
        
        # Testar se tem recursos avançados
        if hasattr(self.voice_system, 'test_all_emotions'):
            advanced_tests.append(("Teste automático de emoções", self.voice_system.test_all_emotions))
        
        if hasattr(self.voice_system, 'test_voice_quality'):
            advanced_tests.append(("Teste automático de qualidade", self.voice_system.test_voice_quality))
        
        if hasattr(self.voice_system, 'get_system_info'):
            try:
                info = self.voice_system.get_system_info()
                print(f"   ℹ️ Info do sistema: {info}")
                advanced_tests.append(("Info do sistema", lambda: print("✅ Info obtida")))
            except:
                pass
        
        passed_advanced = 0
        
        for test_name, test_func in advanced_tests:
            try:
                print(f"   🔬 {test_name}...")
                if asyncio.iscoroutinefunction(test_func):
                    await test_func()
                else:
                    test_func()
                print(f"   ✅ {test_name}: PASSOU")
                passed_advanced += 1
            except Exception as e:
                print(f"   ❌ {test_name}: FALHOU - {e}")
        
        if advanced_tests:
            print(f"\n📊 Resultado: {passed_advanced}/{len(advanced_tests)} recursos avançados")
            self.test_results["advanced"] = passed_advanced / len(advanced_tests)
        else:
            print("\n   📝 Nenhum recurso avançado detectado")
            self.test_results["advanced"] = 0
    
    async def test_stress_performance(self):
        """Teste de performance sob stress"""
        print("\n🚀 TESTE 5: PERFORMANCE E STRESS")
        print("-" * 40)
        
        stress_tests = [
            "Teste de velocidade um.",
            "Teste de velocidade dois.",
            "Teste de velocidade três.",
            "Teste de velocidade quatro.",
            "Teste de velocidade cinco."
        ]
        
        print("   ⏱️ Testando velocidade de resposta...")
        start_time = time.time()
        successful_tests = 0
        
        for i, text in enumerate(stress_tests, 1):
            try:
                print(f"   🏃 Teste rápido {i}/5")
                await self.voice_system.speak(text, "neutro")
                successful_tests += 1
                await asyncio.sleep(0.5)  # Pausa mínima
            except Exception as e:
                print(f"   ❌ Falha no teste {i}: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"   📊 {successful_tests}/5 testes em {total_time:.2f}s")
        print(f"   ⚡ Média: {total_time/len(stress_tests):.2f}s por frase")
        
        self.test_results["performance"] = successful_tests / len(stress_tests)
        self.test_results["speed"] = total_time / len(stress_tests)
    
    async def test_error_handling(self):
        """Teste de tratamento de erros"""
        print("\n🛡️ TESTE 6: TRATAMENTO DE ERROS")
        print("-" * 40)
        
        error_tests = [
            ("", "neutro", "Texto vazio"),
            ("   ", "feliz", "Apenas espaços"),
            ("Teste", "emocao_inexistente", "Emoção inválida"),
            ("Texto muito longo " * 100, "neutro", "Texto extremamente longo")
        ]
        
        handled_errors = 0
        
        for text, emotion, description in error_tests:
            try:
                print(f"   🧪 {description}...")
                await self.voice_system.speak(text, emotion)
                print(f"   ✅ {description}: Tratado graciosamente")
                handled_errors += 1
            except Exception as e:
                print(f"   ⚠️ {description}: Erro - {str(e)[:50]}...")
        
        print(f"\n📊 Resultado: {handled_errors}/{len(error_tests)} erros tratados")
        self.test_results["error_handling"] = handled_errors / len(error_tests)
    
    def generate_final_report(self):
        """Gera relatório final dos testes"""
        print("\n" + "="*60)
        print("📋 RELATÓRIO FINAL DOS TESTES DE VOZ")
        print("="*60)
        
        # Calcular pontuação geral
        total_score = 0
        total_tests = 0
        
        for test_name, score in self.test_results.items():
            if test_name != "speed":  # Speed não é pontuação
                total_score += score
                total_tests += 1
        
        overall_score = (total_score / total_tests) * 100 if total_tests > 0 else 0
        
        # Exibir resultados
        print(f"\n🎯 PONTUAÇÃO GERAL: {overall_score:.1f}%")
        
        print("\n📊 DETALHES POR CATEGORIA:")
        for test_name, score in self.test_results.items():
            if test_name == "speed":
                print(f"   ⚡ Velocidade média: {score:.2f}s por frase")
            else:
                percentage = score * 100
                status = "✅" if percentage >= 80 else "⚠️" if percentage >= 60 else "❌"
                print(f"   {status} {test_name.title()}: {percentage:.1f}%")
        
        # Recomendações
        print("\n💡 RECOMENDAÇÕES:")
        
        if overall_score >= 90:
            print("   🌟 Sistema excelente! Funcionando perfeitamente.")
        elif overall_score >= 70:
            print("   ✅ Sistema bom. Pequenos ajustes podem melhorar.")
        elif overall_score >= 50:
            print("   ⚠️ Sistema funcional mas precisa de melhorias.")
        else:
            print("   ❌ Sistema precisa de correções significativas.")
        
        # Sugestões específicas
        if self.test_results.get("emotions", 1) < 0.8:
            print("   • Verificar implementação de emoções")
        
        if self.test_results.get("quality", 1) < 0.8:
            print("   • Melhorar qualidade de síntese")
        
        if self.test_results.get("performance", 1) < 0.8:
            print("   • Otimizar performance do sistema")
        
        if self.test_results.get("speed", 0) > 3:
            print("   • Acelerar tempo de resposta")
        
        print("\n✨ TESTE CONCLUÍDO!")
    
    async def cleanup(self):
        """Limpa recursos após testes"""
        if self.voice_system and hasattr(self.voice_system, 'cleanup'):
            await self.voice_system.cleanup()

async def main():
    """Função principal do teste"""
    print("🎭 SUITE DE TESTES COMPLETA - SISTEMA DE VOZ SEXTA-FEIRA")
    print("="*70)
    print("Este teste irá avaliar completamente o sistema de voz.")
    print("Certifique-se de que seus alto-falantes estão funcionando!")
    print()
    
    input("Pressione ENTER para continuar...")
    
    # Criar suite de testes
    test_suite = VoiceTestSuite()
    
    try:
        # Inicializar sistema
        system_type = await test_suite.initialize_voice_system()
        
        if system_type == "error":
            print("❌ Não foi possível inicializar nenhum sistema de voz!")
            return
        
        # Executar todos os testes
        await test_suite.test_basic_functionality()
        await test_suite.test_emotions_complete()
        await test_suite.test_voice_quality()
        await test_suite.test_advanced_features()
        await test_suite.test_stress_performance()
        await test_suite.test_error_handling()
        
        # Gerar relatório final
        test_suite.generate_final_report()
        
    except KeyboardInterrupt:
        print("\n\n❌ Teste interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
    finally:
        # Limpeza
        await test_suite.cleanup()

if __name__ == "__main__":
    asyncio.run(main())