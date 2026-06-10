import os
template_dir = r'c:\Users\mohit\Downloads\campus placement cell\templates'
for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            c = content
            c = c.replace('card-premium', 'premium-card')
            c = c.replace('bg-white', 'bg-transparent')
            c = c.replace('text-dark', '')
            c = c.replace('text-muted', 'opacity-75')
            c = c.replace('btn-light', 'btn-premium btn-premium-secondary')
            
            if c != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(c)
                print('Fixed: ' + file)
