import re

# Read the file
with open('.kiro/specs/salon-spa-gym-saas/requirements.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all requirement numbers
matches = re.findall(r'### Requirement (\d+):', content)
max_num = max([int(m) for m in matches]) if matches else 0

print(f'Found requirements up to number: {max_num}')

# We need to fix the duplicate Requirement 5
# First, find the second occurrence of "### Requirement 5:" and change it to "### Requirement 6:"
# Then cascade all subsequent numbers

# Split by "### Requirement" to find all occurrences
parts = content.split('### Requirement ')
print(f'Found {len(parts) - 1} requirements')

# Rebuild with correct numbering
result = parts[0]  # Keep everything before first requirement
req_num = 1

for i in range(1, len(parts)):
    result += f'### Requirement {req_num}: {parts[i]}'
    req_num += 1

# Write back
with open('.kiro/specs/salon-spa-gym-saas/requirements.md', 'w', encoding='utf-8') as f:
    f.write(result)

print('Fixed all requirement numbers')
