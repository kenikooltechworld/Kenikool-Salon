'use client';

import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { AlertCircle, CheckCircle, History } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface ReviewEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  review: {
    _id: string;
    comment?: string;
    edit_history?: Array<{
      original_text: string;
      edited_text: string;
      edited_by: string;
      edited_at: string;
    }>;
  };
  onSave: (newComment: string) => Promise<void>;
}

export function ReviewEditModal({
  isOpen,
  onClose,
  review,
  onSave
}: ReviewEditModalProps) {
  const [newComment, setNewComment] = useState(review.comment || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  const handleSave = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!newComment.trim()) {
        setError('Comment cannot be empty');
        return;
      }

      await onSave(newComment);
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        onClose();
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save changes');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setNewComment(review.comment || '');
      setError(null);
      setSuccess(false);
      setShowHistory(false);
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Edit Review Comment</DialogTitle>
          <DialogDescription>
            Update the review comment. The original text will be preserved in the edit history.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {error && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="pt-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700">{error}</p>
              </CardContent>
            </Card>
          )}

          {success && (
            <Card className="border-green-200 bg-green-50">
              <CardContent className="pt-4 flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-green-700">Comment updated successfully</p>
              </CardContent>
            </Card>
          )}

          {/* Original Comment */}
          {review.comment && (
            <div className="space-y-2">
              <Label className="text-sm font-semibold text-gray-600">Original Comment</Label>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-700">
                {review.comment}
              </div>
            </div>
          )}

          {/* New Comment */}
          <div className="space-y-2">
            <Label htmlFor="comment">Updated Comment</Label>
            <Textarea
              id="comment"
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Enter updated comment..."
              className="min-h-[120px]"
              disabled={loading}
            />
            <p className="text-xs text-gray-500">
              {newComment.length} characters
            </p>
          </div>

          {/* Edit History */}
          {review.edit_history && review.edit_history.length > 0 && (
            <div className="space-y-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowHistory(!showHistory)}
                className="gap-2"
              >
                <History size={16} />
                View Edit History ({review.edit_history.length})
              </Button>

              {showHistory && (
                <div className="space-y-3 bg-gray-50 border border-gray-200 rounded-lg p-4">
                  {review.edit_history.map((edit, index) => (
                    <div key={index} className="space-y-2 pb-3 border-b border-gray-200 last:border-b-0">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-gray-700">Edit #{index + 1}</span>
                        <span className="text-gray-600">
                          {new Date(edit.edited_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600">
                        <strong>Edited by:</strong> {edit.edited_by}
                      </p>
                      <div className="space-y-1">
                        <p className="text-xs font-semibold text-gray-700">Original:</p>
                        <p className="text-xs text-gray-600 bg-white p-2 rounded border border-gray-200">
                          {edit.original_text}
                        </p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-xs font-semibold text-gray-700">Updated:</p>
                        <p className="text-xs text-gray-600 bg-white p-2 rounded border border-gray-200">
                          {edit.edited_text}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={loading || newComment === review.comment}
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
