# fix_syntax_error.py
print("🔧 Corrigindo erro de sintaxe no agent.py...")

# Ler arquivo com problema
with open("core/agent.py", "r", encoding="utf-8") as f:
    content = f.read()

# Corrigir o erro específico na linha 109
problematic_line = 'print("🔧 \'analisar código\' = AUTO-ANÁLISE"\\n        print("🎭 \'teste voz\' = TESTAR EMOÇÕES"))'

# Substituir pela versão correta
correct_lines = '''print("🔧 'analisar código' = AUTO-ANÁLISE")
        print("🎭 'teste voz' = TESTAR EMOÇÕES")'''

if problematic_line in content:
    content = content.replace(problematic_line, correct_lines)
    print("✅ Erro de sintaxe corrigido!")
else:
    # Procurar por variações do erro
    error_patterns = [
        'print("🔧 \'analisar código\' = AUTO-ANÁLISE"\\n',
        'print("🔧 \\\'analisar código\\\' = AUTO-ANÁLISE"\\n',
        'print("🔧',
    ]
    
    for pattern in error_patterns:
        if pattern in content:
            # Encontrar a linha problemática e corrigir
            start_pos = content.find(pattern)
            if start_pos != -1:
                # Encontrar fim da linha problemática
                end_pos = content.find(')', start_pos) + 1
                if end_pos > start_pos:
                    content = content[:start_pos] + correct_lines + content[end_pos:]
                    print("✅ Padrão de erro corrigido!")
                    break

# Verificar e corrigir outros problemas similares
fixes = [
    # Corrigir caracteres de escape duplos
    ('\\\\n', '\\n'),
    ('\\\\"', '"'),
    ("\\\\\'", "'"),
    
    # Corrigir prints concatenados incorretamente
    ('print("🔧 \'analisar código\' = AUTO-ANÁLISE")\\n        print("🎭 \'teste voz\' = TESTAR EMOÇÕES")', 
     'print("🔧 \'analisar código\' = AUTO-ANÁLISE")\\n        print("🎭 \'teste voz\' = TESTAR EMOÇÕES")'),
]

for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        print(f"✅ Corrigido: {old[:50]}...")

# Verificar se há outras linhas problemáticas com escapes
lines = content.split('\\n')
for i, line in enumerate(lines):
    if '\\n' in line and 'print(' in line and line.count('"') % 2 != 0:
        # Linha com escape problemático
        print(f"⚠️ Linha {i+1} pode ter problema: {line[:80]}...")

# Salvar arquivo corrigido
with open("core/agent.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\\n✅ Arquivo agent.py corrigido!")
print("🚀 Teste: python main.py")

# Verificar se o arquivo está sintaticamente correto
try:
    with open("core/agent.py", "r", encoding="utf-8") as f:
        code = f.read()
    
    # Tentar compilar o código
    compile(code, "core/agent.py", "exec")
    print("✅ Sintaxe Python válida confirmada!")
    
except SyntaxError as e:
    print(f"❌ Ainda há erro de sintaxe na linha {e.lineno}: {e.msg}")
    print("🔧 Executando correção manual...")
    
    # Correção manual para problemas persistentes
    lines = content.split('\\n')
    for i, line in enumerate(lines):
        if 'print("🔧' in line and 'AUTO-ANÁLISE' in line:
            # Substituir linha problemática
            lines[i] = '        print("🔧 \'analisar código\' = AUTO-ANÁLISE")'
            if i + 1 < len(lines) and 'teste voz' not in lines[i + 1]:
                lines.insert(i + 1, '        print("🎭 \'teste voz\' = TESTAR EMOÇÕES")')
            break
    
    # Salvar versão manualmente corrigida
    with open("core/agent.py", "w", encoding="utf-8") as f:
        f.write('\\n'.join(lines))
    
    print("✅ Correção manual aplicada!")

except Exception as e:
    print(f"⚠️ Outro erro encontrado: {e}")