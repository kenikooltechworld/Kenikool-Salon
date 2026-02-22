import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Trash2, Save } from "lucide-react";

interface SavedSearch {
  id: string;
  name: string;
  filters: Record<string, any>;
  createdAt: string;
}

interface SavedSearchesProps {
  searches: SavedSearch[];
  onLoadSearch: (filters: Record<string, any>) => void;
  onDeleteSearch: (id: string) => Promise<void>;
  onSaveSearch?: (name: string, filters: Record<string, any>) => Promise<void>;
  currentFilters?: Record<string, any>;
}

export const SavedSearches: React.FC<SavedSearchesProps> = ({
  searches,
  onLoadSearch,
  onDeleteSearch,
  onSaveSearch,
  currentFilters,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [savingName, setSavingName] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSaveSearch = async () => {
    if (!savingName.trim() || !currentFilters) return;

    setSaving(true);
    try {
      await onSaveSearch?.(savingName, currentFilters);
      setSavingName("");
    } finally {
      setSaving(false);
    }
  };

  if (!searches || searches.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full p-2 border rounded hover:bg-gray-50"
      >
        <span className="font-medium text-sm">
          Saved Searches ({searches.length})
        </span>
        <span className="text-gray-500">{expanded ? "▼" : "▶"}</span>
      </button>

      {expanded && (
        <div className="space-y-3 p-3 border rounded bg-gray-50">
          {/* Save Current Search */}
          {currentFilters && onSaveSearch && (
            <div className="space-y-2 border-b border-gray-200 pb-3">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={savingName}
                  onChange={(e) => setSavingName(e.target.value)}
                  placeholder="Name this search..."
                  className="flex-1 rounded border border-gray-300 px-2 py-1 text-sm"
                  disabled={saving}
                />
                <Button
                  onClick={handleSaveSearch}
                  disabled={!savingName.trim() || saving}
                  size="sm"
                  className="gap-1"
                >
                  <Save className="h-3 w-3" />
                  Save
                </Button>
              </div>
            </div>
          )}

          {/* Saved Searches List */}
          <div className="space-y-2">
            {searches.map((search) => (
              <div
                key={search.id}
                className="flex items-center justify-between p-2 rounded bg-white border border-gray-200 hover:border-blue-300"
              >
                <button
                  onClick={() => onLoadSearch(search.filters)}
                  className="flex-1 text-left"
                >
                  <p className="text-sm font-medium text-gray-900">
                    {search.name}
                  </p>
                  <p className="text-xs text-gray-600">
                    Saved {new Date(search.createdAt).toLocaleDateString()}
                  </p>
                </button>
                <button
                  onClick={() => onDeleteSearch(search.id)}
                  className="text-gray-400 hover:text-red-600"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
