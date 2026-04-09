import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircleIcon, CheckCircleIcon } from "@/components/icons";

interface NotesEditorProps {
  initialNotes?: string;
  onSave: (notes: string) => Promise<void>;
  isLoading?: boolean;
  readOnly?: boolean;
}

export function NotesEditor({
  initialNotes = "",
  onSave,
  isLoading = false,
  readOnly = false,
}: NotesEditorProps) {
  const [notes, setNotes] = useState(initialNotes);
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const handleSave = async () => {
    setSuccessMessage(null);
    setErrorMessage(null);

    try {
      setIsSaving(true);
      await onSave(notes);
      setSuccessMessage("Notes saved successfully");
      setIsEditing(false);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Failed to save notes";
      setErrorMessage(errorMsg);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setNotes(initialNotes);
    setIsEditing(false);
    setErrorMessage(null);
  };

  if (readOnly) {
    return (
      <div className="space-y-2">
        <Label className="text-sm font-medium">Notes</Label>
        {notes ? (
          <div className="bg-muted/50 p-3 rounded text-sm text-foreground whitespace-pre-wrap">
            {notes}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground italic">No notes added</p>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label className="text-sm font-medium">Notes</Label>
        {!isEditing && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => setIsEditing(true)}
            disabled={isSaving || isLoading}
          >
            {notes ? "Edit" : "Add Notes"}
          </Button>
        )}
      </div>

      {isEditing ? (
        <div className="space-y-3">
          <Textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add private notes about this appointment..."
            disabled={isSaving || isLoading}
            className="min-h-[100px]"
          />
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={handleSave}
              disabled={isSaving || isLoading}
            >
              {isSaving ? "Saving..." : "Save Notes"}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleCancel}
              disabled={isSaving || isLoading}
            >
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        <>
          {notes ? (
            <div className="bg-muted/50 p-3 rounded text-sm text-foreground whitespace-pre-wrap">
              {notes}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">
              No notes added
            </p>
          )}
        </>
      )}

      {successMessage && (
        <Alert className="bg-success/10 border-success/30">
          <CheckCircleIcon className="h-4 w-4 text-success" />
          <AlertDescription className="text-success">
            {successMessage}
          </AlertDescription>
        </Alert>
      )}

      {errorMessage && (
        <Alert className="bg-destructive/10 border-destructive/30">
          <AlertCircleIcon className="h-4 w-4 text-destructive" />
          <AlertDescription className="text-destructive">
            {errorMessage}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
