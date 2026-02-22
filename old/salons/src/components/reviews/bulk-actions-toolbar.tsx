import { useState } from "react";
import { Button } from "@/components/ui/button";
import { CheckIcon, XIcon, TrashIcon, XCircleIcon } from "@/components/icons";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface BulkActionsToolbarProps {
  selectedIds: Set<string>;
  onApprove: (ids: string[]) => Promise<void>;
  onReject: (ids: string[]) => Promise<void>;
  onDelete: (ids: string[]) => Promise<void>;
  onClear: () => void;
  isLoading?: boolean;
}

export function BulkActionsToolbar({
  selectedIds,
  onApprove,
  onReject,
  onDelete,
  onClear,
  isLoading = false,
}: BulkActionsToolbarProps) {
  const [showApproveDialog, setShowApproveDialog] = useState(false);
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  if (selectedIds.size === 0) {
    return null;
  }

  const selectedArray = Array.from(selectedIds);

  const handleApprove = async () => {
    setIsProcessing(true);
    try {
      await onApprove(selectedArray);
      setShowApproveDialog(false);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async () => {
    setIsProcessing(true);
    try {
      await onReject(selectedArray);
      setShowRejectDialog(false);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDelete = async () => {
    setIsProcessing(true);
    try {
      await onDelete(selectedArray);
      setShowDeleteDialog(false);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <>
      {/* Fixed Toolbar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-[var(--border)] shadow-lg z-40">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between gap-4">
          {/* Selection Info */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-[var(--foreground)]">
              {selectedIds.size} review{selectedIds.size !== 1 ? "s" : ""} selected
            </span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowApproveDialog(true)}
              disabled={isLoading || isProcessing}
              className="flex items-center gap-1"
            >
              <CheckIcon size={16} />
              Approve All
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowRejectDialog(true)}
              disabled={isLoading || isProcessing}
              className="flex items-center gap-1"
            >
              <XIcon size={16} />
              Reject All
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowDeleteDialog(true)}
              disabled={isLoading || isProcessing}
              className="flex items-center gap-1 text-destructive hover:text-destructive"
            >
              <TrashIcon size={16} />
              Delete All
            </Button>

            <div className="w-px h-6 bg-[var(--border)]" />

            <Button
              variant="ghost"
              size="sm"
              onClick={onClear}
              disabled={isLoading || isProcessing}
              className="flex items-center gap-1"
            >
              <XCircleIcon size={16} />
              Clear
            </Button>
          </div>
        </div>
      </div>

      {/* Spacer to prevent content overlap */}
      <div className="h-20" />

      {/* Approve Confirmation Dialog */}
      <AlertDialog open={showApproveDialog} onOpenChange={setShowApproveDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Approve Reviews</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to approve {selectedIds.size} review
              {selectedIds.size !== 1 ? "s" : ""}? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isProcessing}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleApprove}
              disabled={isProcessing}
              className="bg-green-600 hover:bg-green-700"
            >
              {isProcessing ? "Approving..." : "Approve"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Reject Confirmation Dialog */}
      <AlertDialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Reject Reviews</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to reject {selectedIds.size} review
              {selectedIds.size !== 1 ? "s" : ""}? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isProcessing}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleReject}
              disabled={isProcessing}
              className="bg-orange-600 hover:bg-orange-700"
            >
              {isProcessing ? "Rejecting..." : "Reject"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Reviews</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete {selectedIds.size} review
              {selectedIds.size !== 1 ? "s" : ""}? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isProcessing}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={isProcessing}
              className="bg-destructive hover:bg-destructive/90"
            >
              {isProcessing ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
