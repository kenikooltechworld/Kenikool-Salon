#!/usr/bin/env python3
"""
Fix all TypeScript build errors systematically
"""

import re
import os

def fix_icons_duplicates():
    """Remove duplicate icon exports from icons/index.tsx"""
    file_path = "salon/src/components/icons/index.tsx"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all duplicate export lines (lines 2477-2778)
    # Remove the second set of exports
    lines = content.split('\n')
    
    # Find where duplicates start (around line 2477)
    seen_exports = set()
    new_lines = []
    in_duplicate_section = False
    
    for i, line in enumerate(lines):
        # Check if this is an export line
        if line.strip().startswith('export const'):
            match = re.match(r'export const (\w+) =', line)
            if match:
                export_name = match.group(1)
                if export_name in seen_exports:
                    # Skip duplicate
                    in_duplicate_section = True
                    continue
                else:
                    seen_exports.add(export_name)
                    in_duplicate_section = False
        
        if not in_duplicate_section:
            new_lines.append(line)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✓ Fixed duplicate exports in {file_path}")

def fix_shift_type_imports():
    """Fix type imports in shift components"""
    files = [
        "salon/src/components/shifts/ShiftCard.tsx",
        "salon/src/components/shifts/ShiftForm.tsx"
    ]
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace regular import with type import
        content = re.sub(
            r'import \{ Shift \} from',
            r'import type { Shift } from',
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Fixed type import in {file_path}")

def fix_offline_sync_import():
    """Fix type import in offline sync"""
    file_path = "salon/src/lib/offline/sync.ts"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the import
    content = re.sub(
        r'import \{ offlineDB, OfflineTransaction \}',
        r'import { offlineDB, type OfflineTransaction }',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed type import in {file_path}")

def main():
    print("Fixing TypeScript errors...")
    
    fix_icons_duplicates()
    fix_shift_type_imports()
    fix_offline_sync_import()
    
    print("\nDone! Run 'npm run build' in the salon directory to verify.")

if __name__ == "__main__":
    main()
