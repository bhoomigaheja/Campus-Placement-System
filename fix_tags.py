import os
import re

def fix_template_tags(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Fix {{ \n variable }} or {{ variable \n }}
                # Find all {{ ... }} avoiding nested braces if any
                def replacer(match):
                    inner = match.group(1)
                    # Replace newlines and extra spaces with a single space
                    cleaned = re.sub(r'\s+', ' ', inner).strip()
                    return f'{{{{ {cleaned} }}}}'

                new_content = re.sub(r'\{\{([^{}]*?)\}\}', replacer, content)

                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Fixed {filepath}")

if __name__ == "__main__":
    templates_dir = r"C:\Users\mohit\Downloads\campus placement cell\templates"
    fix_template_tags(templates_dir)
