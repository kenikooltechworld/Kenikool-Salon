import { useState, useCallback } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";

export interface BulkSelectorState {
  selectedIds: Set<string>;
  isSelectAll: boolean;
}

export interface BulkSelectorProps {
  totalCount: number;
  selectedCount: number;
  isSelectAll: boolean;
  onSelectAll: (selected: boolean) => void;
  onToggleSelect: (id: string, selected: boolean) => void;
}

/**
 * Checkbox component for bulk selection in client list
 * Provides individual and select-all functionality
 * 
 * Requirements: REQ-CM-011 (Task 27.1)
 */
export function ClientCheckbox({
  id,
  checked,
  onToggle,
}: {
  id: string;
  checked: boolean;
  onToggle: (id: string, checked: boolean) => void;
}) {
  return (
    <Checkbox
      checked={checked}
      onCheckedChange={(checked) => onToggle(id, checked as boolean)}
      className="h-4 w-4"
    />
  );
}

/**
 * Select All checkbox with label
 */
export function SelectAllCheckbox({
  checked,
  indeterminate,
  onToggle,
  selectedCount,
  totalCount,
}: {
  checked: boolean;
  indeterminate: boolean;
  onToggle: (checked: boolean) => void;
  selectedCount: number;
  totalCount: number;
}) {
  return (
    <div className="flex items-center gap-2">
      <Checkbox
        checked={checked}
        indeterminate={indeterminate}
        onCheckedChange={(checked) => onToggle(checked as boolean)}
        className="h-4 w-4"
      />
      <span className="text-sm text-muted-foreground">
        {selectedCount > 0 ? (
          <>
            <span className="font-medium">{selectedCount}</span> of{" "}
            <span className="font-medium">{totalCount}</span> selected
          </>
        ) : (
          "Select all"
        )}
      </span>
    </div>
  );
}

/**
 * Selection counter badge
 */
export function SelectionCounter({ count }: { count: number }) {
  if (count === 0) return null;

  return (
    <Badge variant="secondary" className="ml-2">
      {count} selected
    </Badge>
  );
}

/**
 * Hook for managing bulk selection state
 */
export function useBulkSelection(items: { id: string }[]) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const toggleSelect = useCallback((id: string, selected: boolean) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (selected) {
        next.add(id);
      } else {
        next.delete(id);
      }
      return next;
    });
  }, []);

  const toggleSelectAll = useCallback(
    (selected: boolean) => {
      if (selected) {
        setSelectedIds(new Set(items.map((item) => item.id)));
      } else {
        setSelectedIds(new Set());
      }
    },
    [items]
  );

  const clearSelection = useCallback(() => {
    setSelectedIds(new Set());
  }, []);

  const isSelectAll = selectedIds.size === items.length && items.length > 0;
  const isIndeterminate = selectedIds.size > 0 && selectedIds.size < items.length;

  return {
    selectedIds: Array.from(selectedIds),
    selectedCount: selectedIds.size,
    isSelectAll,
    isIndeterminate,
    toggleSelect,
    toggleSelectAll,
    clearSelection,
  };
}
