# pytorch_fix.py - Patch para weights_only
import torch

# Salvar função original
original_torch_load = torch.load

def fixed_torch_load(*args, **kwargs):
    """torch.load que sempre usa weights_only=False"""
    kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)

# Aplicar patch
torch.load = fixed_torch_load
print("✅ PyTorch patch aplicado!")
