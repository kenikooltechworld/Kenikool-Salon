import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { AlertTriangleIcon, XIcon } from "@/components/icons";
import { apiClient } from "@/lib/api/client";

export interface BulkTagModalProps {
  isOpen: boolean;
  selectedClientIds: string[];
  onClose: () => void;
  onSuccess?: () => void;
}

/**
 * Modal for adding tags to multiple clients in bulk
 * 
 * Requirements: REQ-CM-011 (Task 27.3)
 */
export function BulkTagModal({
  isOpen,
  selectedClientIds,
  onClose,
  onSuccess,
}: BulkTagModalProps) {
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const addBulkTags = useMutation({
    mutationFn: async () => {
      const response = await api.post("/clients/bulk/add-tags", {
        client_ids: selectedClientIds,
        tags,
      });
      return response.data;
    },
    onSuccess: () => {
      setTags([]);
      setTagInput("");
      onSuccess?.();
      onClose();
    },
    onError: (err: any) => {
      setError(err.response?.data?.error?.message || "Failed to add tags");
    },
  });

  const handleAddTag = () => {
    const trimmedTag = tagInput.trim().toLowerCase();

    if (!trimmedTag) {
      setError("Tag cannot be empty");
      return;
    }

    if (tags.includes(trimmedTag)) {
      setError("Tag already added");
      return;
    }

    if (trimmedTag.length > 50) {
      setError("Tag must be 50 characters or less");
      return;
    }

    setTags([...tags, trimmedTag]);
    setTagInput("");
    setError(null);
  };

  const handleRemoveTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddTag();
    }
  };

  const handleApply = () => {
    if (tags.length === 0) {
      setError("Please add at least one tag");
      return;
    }

    setError(null);
    addBulkTags.mutate();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Add Tags to Clients</DialogTitle>
          <DialogDescription>
            Add tags to {selectedClientIds.length} client
            {selectedClientIds.length !== 1 ? "s" : ""}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Tag Input */}
          <div className="space-y-2">
            <Label htmlFor="tag-input">Add Tag</Label>
            <div className="flex gap-2">
              <Input
                id="tag-input"
                placeholder="Enter tag name..."
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleKeyDown}
              />
              <Button
                onClick={handleAddTag}
                disabled={!tagInput.trim() || addBulkTags.isPending}
                variant="outline"
              >
                Add
              </Button>
            </div>
          </div>

          {/* Tags Display */}
          {tags.length > 0 && (
            <div className="space-y-2">
              <Label>Tags to Add ({tags.length})</Label>
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <Badge
                    key={tag}
                    variant="secondary"
                    className="flex items-center gap-1 px-2 py-1"
                  >
                    {tag}
                    <button
                      onClick={() => handleRemoveTag(tag)}
                      className="ml-1 hover:text-destructive"
                      title="Remove tag"
                    >
                      <XIcon size={14} />
                    </button>
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Error Alert */}
          {error && (
            <Alert variant="error">
              <AlertTriangleIcon size={16} />
              <div>{error}</div>
            </Alert>
          )}

          {/* Loading State */}
          {addBulkTags.isPending && (
            <div className="flex items-center justify-center gap-2 py-4">
              <Spinner size="sm" />
              <span className="text-sm text-muted-foreground">
                Adding tags...
              </span>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={addBulkTags.isPending}>
            Cancel
          </Button>
          <Button
            onClick={handleApply}
            disabled={addBulkTags.isPending || tags.length === 0}
          >
            {addBulkTags.isPending ? (
              <>
                <Spinner size="sm" className="mr-2" />
                Adding...
              </>
            ) : (
              "Apply Tags"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
