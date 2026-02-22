import re

# Read the file
with open('.kiro/specs/salon-spa-gym-saas/requirements.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all requirement numbers
matches = re.findall(r'### Requirement (\d+):', content)
max_num = max([int(m) for m in matches]) if matches else 0

print(f'Found requirements up to number: {max_num}')

# Replace in reverse order to avoid conflicts
for i in range(max_num, 3, -1):
    old_pattern = f'### Requirement {i}:'
    new_pattern = f'### Requirement {i + 1}:'
    content = content.replace(old_pattern, new_pattern)

# Write back
with open('.kiro/specs/salon-spa-gym-saas/requirements.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('Renumbering complete')
