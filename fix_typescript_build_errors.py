#!/usr/bin/env python3
"""
Script to fix TypeScript build errors systematically
"""
import os
import re

def fix_type_imports():
    """Fix type-only imports that need the 'type' keyword"""
    fixes = [
        ("salon/src/components/shifts/ShiftCard.tsx", 
         'import { Shift } from "@/hooks/useShifts";',
         'import type { Shift } from "@/hooks/useShifts";'),
        
        ("salon/src/components/shifts/ShiftForm.tsx",
         'import { Shift } from "@/hooks/useShifts";',
         'import type { Shift } from "@/hooks/useShifts";'),
        
        ("salon/src/lib/offline/sync.ts",
         'import { offlineDB, OfflineTransaction } from "./indexeddb";',
         'import { offlineDB } from "./indexeddb";\nimport type { OfflineTransaction } from "./indexeddb";'),
        
        ("salon/src/components/ui/confirmation-modal.tsx",
         'import { ReactNode } from "react";',
         'import type { ReactNode } from "react";'),
        
        ("salon/src/components/ui/error-boundary.tsx",
         'import React, { ReactNode, ReactElement } from "react";',
         'import React from "react";\nimport type { ReactNode, ReactElement } from "react";'),
        
        ("salon/src/components/ui/lazy-load.tsx",
         'import { Suspense, lazy, ComponentType } from "react";',
         'import { Suspense, lazy } from "react";\nimport type { ComponentType } from "react";'),
        
        ("salon/src/layouts/AdminLayout.tsx",
         'import { ReactNode } from "react";',
         'import type { ReactNode } from "react";'),
        
        ("salon/src/layouts/MainLayout.tsx",
         'import { ReactNode } from "react";',
         'import type { ReactNode } from "react";'),
        
        ("salon/src/lib/themes/default.ts",
         'import { Theme } from "./types";',
         'import type { Theme } from "./types";'),
        
        ("salon/src/lib/themes/elegant.ts",
         'import { Theme } from "./types";',
         'import type { Theme } from "./types";'),
        
        ("salon/src/lib/themes/vibrant.ts",
         'import { Theme } from "./types";',
         'import type { Theme } from "./types";'),
        
        ("salon/src/lib/themes/index.ts",
         'import { Theme, ThemeName, ThemeMode } from "./types";',
         'import type { Theme, ThemeName, ThemeMode } from "./types";'),
    ]
    
    for file_path, old_text, new_text in fixes:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_text in content:
                content = content.replace(old_text, new_text)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Fixed type imports in {file_path}")
        except Exception as e:
            print(f"✗ Error fixing {file_path}: {e}")

if __name__ == "__main__":
    print("Fixing TypeScript build errors...")
    fix_type_imports()
    print("\nDone! Run 'npm run build' in the salon directory to verify.")
