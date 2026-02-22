import React, { useState } from "react";
import { Button } from "@/components/ui/button";

interface NotesEditorProps {
  initialNotes: string;
  onSave: (notes: string) => Promise<void>;
  onCancel?: () => void;
  maxLength?: number;
}

export const NotesEditor: React.FC<NotesEditorProps> = ({
  initialNotes,
  onSave,
  onCancel,
  maxLength = 500,
}) => {
  const [notes, setNotes] = useState(initialNotes);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    setSaving(true);
    setError(null);

    try {
      await onSave(notes);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save notes");
    } finally {
      setSaving(false);
    }
  };

  const hasChanges = notes !== initialNotes;

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-center justify-between">
        <label className="font-medium text-gray-900">Edit Notes</label>
        <span className="text-xs text-gray-600">
          {notes.length}/{maxLength}
        </span>
      </div>

      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value.slice(0, maxLength))}
        rows={4}
        className="w-full rounded border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none resize-none"
      />

      {error && (
        <div className="text-sm text-red-900 bg-red-100 rounded p-2">
          {error}
        </div>
      )}

      <div className="flex gap-2 border-t border-gray-200 pt-3">
        <Button
          onClick={handleSave}
          disabled={!hasChanges || saving}
          className="flex-1"
        >
          {saving ? "Saving..." : "Save Changes"}
        </Button>
        <Button
          onClick={onCancel}
          variant="outline"
          disabled={saving}
          className="flex-1"
        >
          Cancel
        </Button>
      </div>
    </div>
  );
};
