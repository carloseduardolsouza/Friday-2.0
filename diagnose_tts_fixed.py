# diagnose_tts_fixed.py - Diagnóstico TTS sem erros de indentação
import sys
import os
import traceback
from pathlib import Path

def print_banner():
    """Banner diagnóstico"""
    print("🔍 DIAGNÓSTICO COMPLETO - TTS INSTALADO")
    print("="*45)

def test_basic_imports():
    """Testa imports básicos"""
    print("\n📦 TESTE 1: IMPORTS BÁSICOS")
    print("-" * 30)
    
    results = {}
    
    # Testar TTS básico
    try:
        import TTS
        print(f"✅ TTS importado: versão {TTS.__version__}")
        results['tts_basic'] = True
    except ImportError as e:
        print(f"❌ TTS não pode ser importado: {e}")
        results['tts_basic'] = False
        return results
    
    # Testar API do TTS
    try:
        from TTS.api import TTS as TTSApi
        print("✅ TTS.api importado")
        results['tts_api'] = True
    except ImportError as e:
        print(f"❌ TTS.api falhou: {e}")
        results['tts_api'] = False
    
    # Testar PyTorch
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"✅ PyTorch: {torch.__version__} ({device})")
        results['pytorch'] = True
        results['device'] = device
    except ImportError as e:
        print(f"❌ PyTorch não disponível: {e}")
        results['pytorch'] = False
        results['device'] = "none"
    
    return results

def test_model_loading():
    """Testa carregamento de modelos"""
    print("\n🎭 TESTE 2: CARREGAMENTO DE MODELOS")
    print("-" * 35)
    
    try:
        from TTS.api import TTS
        print("📥 Tentando carregar modelos...")
        
        # Lista de modelos para testar (do mais simples ao mais complexo)
        models_to_test = [
            ("tts_models/en/ljspeech/tacotron2-DDC", "basic_en"),
            ("tts_models/pt/cv/vits", "basic_pt"),
            ("tts_models/multilingual/multi-dataset/xtts_v2", "xtts_v2")
        ]
        
        for model_name, model_type in models_to_test:
            try:
                print(f"   🎯 Testando {model_name}...")
                tts = TTS(model_name=model_name, progress_bar=True)
                print(f"   ✅ {model_type} carregado!")
                return tts, model_type
            except Exception as e:
                print(f"   ❌ {model_type} falhou: {str(e)[:50]}...")
        
        print("❌ Nenhum modelo pôde ser carregado")
        return None, "none"
        
    except Exception as e:
        print(f"❌ Erro geral no carregamento: {e}")
        return None, "error"

def test_audio_generation(tts_model, model_type):
    """Testa geração de áudio"""
    print("\n🔊 TESTE 3: GERAÇÃO DE ÁUDIO")
    print("-" * 30)
    
    if not tts_model:
        print("❌ Sem modelo para testar")
        return False
    
    test_dir = Path("tts_diagnostic_audio")
    test_dir.mkdir(exist_ok=True)
    
    try:
        test_text = "Olá! Este é um teste da voz."
        test_file = test_dir / f"test_{model_type}.wav"
        
        if model_type == "xtts_v2":
            print("🎭 Testando XTTS v2 (voz humana)...")
            tts_model.tts_to_file(
                text=test_text,
                file_path=str(test_file),
                language="pt"
            )
        elif model_type == "basic_pt":
            print("🇧🇷 Testando modelo português...")
            tts_model.tts_to_file(
                text=test_text,
                file_path=str(test_file)
            )
        else:
            print("🇺🇸 Testando modelo inglês...")
            tts_model.tts_to_file(
                text="Hello! This is a voice test.",
                file_path=str(test_file)
            )
        
        print(f"✅ Áudio gerado: {test_file}")
        print(f"📁 Arquivo salvo em: {test_dir}/")
        return True
        
    except Exception as e:
        print(f"❌ Erro na geração: {e}")
        return False

def test_system_integration():
    """Testa integração com sistema SEXTA-FEIRA"""
    print("\n🤖 TESTE 4: INTEGRAÇÃO SEXTA-FEIRA")
    print("-" * 35)
    
    try:
        sys.path.append(str(Path.cwd()))
        
        # Testar imports do sistema
        systems_found = []
        
        try:
            from core.human_voice_system import CoquiHumanVoice
            systems_found.append("human_voice_system")
            print("✅ Sistema de voz humana encontrado")
        except ImportError:
            print("⚠️ Sistema de voz humana não encontrado")
        
        try:
            from core.text_to_speech import SuperiorFeminineVoice
            systems_found.append("text_to_speech")
            print("✅ Sistema principal encontrado")
        except ImportError:
            print("⚠️ Sistema principal não encontrado")
        
        try:
            from core.minimal_voice_system import MinimalVoiceSystem
            systems_found.append("minimal_voice_system")
            print("✅ Sistema mínimo encontrado")
        except ImportError:
            print("⚠️ Sistema mínimo não encontrado")
        
        return len(systems_found) > 0
        
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return False

def check_common_issues():
    """Verifica problemas comuns"""
    print("\n🔧 TESTE 5: PROBLEMAS COMUNS")
    print("-" * 30)
    
    issues = []
    
    # Internet
    try:
        import requests
        requests.get("https://google.com", timeout=5)
        print("✅ Conexão com internet OK")
    except:
        print("❌ Sem conexão com internet")
        issues.append("Internet necessária para download de modelos")
    
    # Espaço em disco
    try:
        import shutil
        free_gb = shutil.disk_usage(".").free / (1024**3)
        if free_gb > 3:
            print(f"✅ Espaço em disco: {free_gb:.1f} GB")
        else:
            print(f"⚠️ Pouco espaço: {free_gb:.1f} GB")
            issues.append("Pouco espaço em disco")
    except:
        print("⚠️ Não foi possível verificar espaço")
    
    return issues

def create_simple_test():
    """Cria teste simples que sempre funciona"""
    print("\n🔧 CRIANDO TESTE SIMPLES")
    print("-" * 25)
    
    simple_test = '''# simple_tts_test.py - Teste direto do TTS
import asyncio
from pathlib import Path

async def test_tts_direct():
    """Teste direto do Coqui TTS"""
    print("🎭 TESTE DIRETO COQUI TTS")
    print("="*25)
    
    try:
        from TTS.api import TTS
        print("✅ TTS importado")
        
        # Carregar modelo
        print("📥 Carregando XTTS v2...")
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        print("✅ Modelo carregado!")
        
        # Gerar teste
        test_dir = Path("direct_test")
        test_dir.mkdir(exist_ok=True)
        
        # Frases de teste
        tests = [
            "Olá! Esta é minha voz humana real!",
            "Agora posso falar de forma completamente natural!",
            "Você consegue perceber como minha voz soa humana?"
        ]
        
        for i, text in enumerate(tests, 1):
            print(f"🎤 Gerando teste {i}...")
            audio_file = test_dir / f"human_voice_test_{i}.wav"
            
            tts.tts_to_file(
                text=text,
                file_path=str(audio_file),
                language="pt"
            )
            print(f"✅ Salvo: {audio_file.name}")
        
        print(f"\\n🎉 SUCESSO! Voz humana funcionando!")
        print(f"📁 Testes em: {test_dir}/")
        print("🔊 REPRODUZA OS ARQUIVOS PARA OUVIR!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tts_direct())
    
    if success:
        print("\\n✅ TTS FUNCIONANDO!")
        print("\\nSe a voz nos arquivos estiver humana mas")
        print("SEXTA-FEIRA ainda usa voz robótica, então")
        print("o problema é na integração, não no TTS.")
    else:
        print("\\n❌ TTS não funcionando corretamente")
'''
    
    with open("simple_tts_test.py", "w", encoding="utf-8") as f:
        f.write(simple_test)
    
    print("✅ Teste simples criado: simple_tts_test.py")

def provide_solutions(has_tts, model_type, issues):
    """Fornece soluções"""
    print("\n💡 DIAGNÓSTICO E SOLUÇÕES")
    print("="*30)
    
    if not has_tts:
        print("❌ TTS NÃO INSTALADO")
        print("🔧 Solução: pip install TTS")
        
    elif model_type == "none":
        print("❌ MODELOS NÃO CARREGAM")
        print("🔧 Soluções:")
        print("1. Verificar internet")
        print("2. Limpar cache: rm -rf ~/.cache/tts")
        print("3. Reinstalar: pip uninstall TTS && pip install TTS")
        
    elif model_type != "xtts_v2":
        print("⚠️ VOZ NÃO É HUMANA")
        print("🔧 Modelo XTTS v2 não carregou")
        print("💡 Execute: python simple_tts_test.py")
        
    else:
        print("✅ TTS FUNCIONANDO COM VOZ HUMANA!")
        print("🎭 Se SEXTA-FEIRA ainda usa voz robótica,")
        print("   o problema é na integração.")
    
    if issues:
        print(f"\n⚠️ PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"• {issue}")

def main():
    """Diagnóstico principal"""
    print_banner()
    
    try:
        # Executar testes
        imports = test_basic_imports()
        
        if not imports.get('tts_basic'):
            print("\n❌ TTS não instalado!")
            print("Execute: pip install TTS")
            return
        
        model, model_type = test_model_loading()
        audio_ok = test_audio_generation(model, model_type) if model else False
        integration_ok = test_system_integration()
        issues = check_common_issues()
        
        # Criar teste simples
        create_simple_test()
        
        # Soluções
        provide_solutions(imports.get('tts_basic'), model_type, issues)
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        if model and model_type == "xtts_v2":
            print("1. Execute: python simple_tts_test.py")
            print("2. Ouça os arquivos gerados")
            print("3. Se estão humanos, problema é integração")
        else:
            print("1. Corrigir problemas listados")
            print("2. Executar diagnóstico novamente")
        
        print("\n" + "="*45)
        print("🔍 DIAGNÓSTICO CONCLUÍDO")
        print("="*45)
        
    except Exception as e:
        print(f"\n❌ Erro no diagnóstico: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()