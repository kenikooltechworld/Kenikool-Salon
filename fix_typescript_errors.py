#!/usr/bin/env python3
"""
Script to fix remaining TypeScript errors systematically
"""
import os
import re
from pathlib import Path

def remove_unused_import(file_path, unused_var):
    """Remove unused import from a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: Remove from destructured import
    # e.g., import { useQuery, useQueryClient } from ... -> import { useQuery } from ...
    pattern1 = rf',\s*{unused_var}\s*(?=}})'
    content = re.sub(pattern1, '', content)
    
    pattern2 = rf'{unused_var}\s*,\s*'
    content = re.sub(pattern2, '', content)
    
    # Pattern 3: Remove entire import if it's the only one
    pattern3 = rf'import\s+{{\s*{unused_var}\s*}}\s+from\s+["\'][^"\']+["\'];\s*\n'
    content = re.sub(pattern3, '', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def fix_api_import(file_path):
    """Fix @/lib/utils/api import to @/lib/utils"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace the import
    content = content.replace('from "@/lib/utils/api"', 'from "@/lib/utils"')
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def add_type_annotation(file_path, line_num, param_name):
    """Add type annotation to parameter"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if line_num <= len(lines):
        line = lines[line_num - 1]
        # Add type annotation
        line = line.replace(f'{param_name})', f'{param_name}: string)')
        line = line.replace(f'{param_name},', f'{param_name}: string,')
        line = line.replace(f'{param_name} ', f'{param_name}: string ')
        
        lines[line_num - 1] = line
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    return False

def main():
    """Main function to fix all errors"""
    salon_src = Path('salon/src')
    
    if not salon_src.exists():
        print(f"Error: {salon_src} directory not found")
        return
    
    fixes_applied = 0
    
    # Fix 1: Remove unused queryClient from useAuditLogs.ts
    file_path = salon_src / 'hooks' / 'useAuditLogs.ts'
    if file_path.exists():
        if remove_unused_import(file_path, 'queryClient'):
            print(f"✓ Fixed: Removed unused 'queryClient' from {file_path}")
            fixes_applied += 1
    
    # Fix 2: Remove unused useQueryClient from useCustomerPortal.ts
    file_path = salon_src / 'hooks' / 'useCustomerPortal.ts'
    if file_path.exists():
        if remove_unused_import(file_path, 'useQueryClient'):
            print(f"✓ Fixed: Removed unused 'useQueryClient' from {file_path}")
            fixes_applied += 1
    
    # Fix 3-16: Fix @/lib/utils/api imports
    files_with_api_import = [
        'hooks/useAuthMe.ts',
        'hooks/useAvailability.ts',
        'hooks/useBackup.ts',
        'hooks/useBookings.ts',
        'hooks/useCacheOptimization.ts',
        'hooks/useCart.ts',
        'hooks/useCheckout.ts',
        'hooks/useCommissions.ts',
        'hooks/useCustomerAuth.ts',
        'hooks/useCustomerHistory.ts',
        'hooks/useCustomerPortal.ts',
        'hooks/useCustomerPreferences.ts',
        'hooks/useCustomers.ts',
        'hooks/useDiscount.ts',
    ]
    
    for file_rel_path in files_with_api_import:
        file_path = salon_src / file_rel_path
        if file_path.exists():
            if fix_api_import(file_path):
                print(f"✓ Fixed: Updated import in {file_path}")
                fixes_applied += 1
    
    # Fix 17: Add type annotation to url parameter in useDocuments.ts
    file_path = salon_src / 'hooks' / 'useDocuments.ts'
    if file_path.exists():
        if add_type_annotation(file_path, 56, 'url'):
            print(f"✓ Fixed: Added type annotation to 'url' parameter in {file_path}")
            fixes_applied += 1
    
    print(f"\n✅ Total fixes applied: {fixes_applied}")

if __name__ == '__main__':
    main()
