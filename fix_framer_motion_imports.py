#!/usr/bin/env python3
"""
Script to replace framer-motion imports with motion/react imports
"""
import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Replace framer-motion imports with motion/react in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace all variations of framer-motion imports
    content = content.replace('from "framer-motion"', 'from "motion/react"')
    content = content.replace("from 'framer-motion'", "from 'motion/react'")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Main function to process all TypeScript/TSX files"""
    salon_src = Path('salon/src')
    
    if not salon_src.exists():
        print(f"Error: {salon_src} directory not found")
        return
    
    files_updated = 0
    
    # Find all .ts and .tsx files
    for ext in ['**/*.ts', '**/*.tsx']:
        for file_path in salon_src.glob(ext):
            if fix_imports_in_file(file_path):
                print(f"Updated: {file_path}")
                files_updated += 1
    
    print(f"\nTotal files updated: {files_updated}")

if __name__ == '__main__':
    main()
