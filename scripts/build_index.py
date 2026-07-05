import os
import yaml
import re

def get_prompts():
    prompts_by_category = {}
    for root, dirs, files in os.walk('.'):
        # Skip hidden dirs (but not the root '.') and scripts
        parts = root.split(os.sep)
        if any(p.startswith('.') and p != '.' for p in parts) or 'scripts' in parts:
            continue

        for file in files:
            if file.endswith('.md') and file not in ['README.md', 'CONTRIBUTING.md']:
                path = os.path.join(root, file)
                try:
                    with open(path, 'r') as f:
                        content = f.read()

                    # Extract YAML front matter
                    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                    if match:
                        metadata = yaml.safe_load(match.group(1))
                        category = metadata.get('category', 'other')
                        if category not in prompts_by_category:
                            prompts_by_category[category] = []

                        prompts_by_category[category].append({
                            'title': metadata.get('title', file),
                            'description': metadata.get('description', ''),
                            'path': path.replace('./', '')
                        })
                except Exception as e:
                    print(f"Error parsing {path}: {e}")

    return prompts_by_category

def build_index_markdown(prompts_by_category):
    lines = []
    for category in sorted(prompts_by_category.keys()):
        lines.append(f"### {category.capitalize()}")
        for prompt in sorted(prompts_by_category[category], key=lambda x: x['title']):
            lines.append(f"- [{prompt['title']}]({prompt['path']}): {prompt['description']}")
        lines.append("")
    return "\n".join(lines).strip()

def update_readme(index_content):
    with open('README.md', 'r') as f:
        content = f.read()

    start_marker = "<!-- INDEX_START -->"
    end_marker = "<!-- INDEX_END -->"

    pattern = f"{start_marker}.*?{end_marker}"
    replacement = f"{start_marker}\n\n{index_content}\n\n{end_marker}"

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open('README.md', 'w') as f:
        f.write(new_content)

if __name__ == "__main__":
    prompts = get_prompts()
    index_md = build_index_markdown(prompts)
    update_readme(index_md)
    print("README index updated successfully.")
