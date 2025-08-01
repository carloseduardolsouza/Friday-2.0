# mecab_patch.py - Patch definitivo para MeCab
"""
Patch para corrigir erro do MeCab no Windows
Execute ANTES de qualquer import do TTS
"""

import sys
import os

def apply_mecab_patch():
    """Aplica patch para MeCab antes de qualquer import"""
    print("🔧 Aplicando patch MeCab...")
    
    # Patch 1: Mock do MeCab completo
    class FakeMeCab:
        def __init__(self):
            pass
            
        class Tagger:
            def __init__(self, *args, **kwargs):
                pass
                
            def parse(self, text):
                return text
                
            def parseToNode(self, text):
                # Mock node para compatibilidade
                class MockNode:
                    def __init__(self):
                        self.surface = text
                        self.feature = "Unknown"
                        self.next = None
                return MockNode()
    
    # Aplicar mock
    sys.modules['MeCab'] = FakeMeCab()
    
    # Patch 2: Variáveis de ambiente para MeCab (caso alguém tente usar)
    os.environ['MECAB_PATH'] = ''
    os.environ['MECABRC'] = ''
    
    print("✅ Patch MeCab aplicado com sucesso!")

def apply_torch_patch():
    """Aplica patch para torch.load"""
    print("🔧 Aplicando patch PyTorch...")
    
    try:
        import torch
        
        # Salvar função original
        if not hasattr(torch, '_original_load'):
            torch._original_load = torch.load
            
            def patched_load(*args, **kwargs):
                kwargs['weights_only'] = False
                return torch._original_load(*args, **kwargs)
            
            torch.load = patched_load
            print("✅ Patch PyTorch aplicado!")
    except ImportError:
        print("⚠️ PyTorch não instalado ainda")

def apply_all_patches():
    """Aplica todos os patches necessários"""
    print("🛠️ APLICANDO PATCHES NECESSÁRIOS")
    print("="*40)
    
    apply_mecab_patch()
    apply_torch_patch()
    
    print("✅ Todos os patches aplicados!")

if __name__ == "__main__":
    apply_all_patches()