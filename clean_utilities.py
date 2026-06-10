import os
import re

TEMPLATE_DIR = r"c:\Users\mohit\Downloads\campus placement cell\templates"

replacements = {
    r'\bopacity-75\b': 'text-desc',
    r'\bopacity-50\b': 'text-desc',
    r'\btext-muted\b': 'text-desc',
    r'\btext-secondary\b': 'text-desc',
    r'\btext-dark\b': 'text-title',
    r'\bbg-light\b': 'bg-transparent',
    r'\bbg-white\b': 'premium-card',
}

files_changed = 0

for root, dirs, files in os.walk(TEMPLATE_DIR):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            for pattern, repl in replacements.items():
                new_content = re.sub(pattern, repl, new_content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                files_changed += 1
                print(f"Updated: {filepath}")

print(f"Total templates cleaned: {files_changed}")
