'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { AlertCircle, CheckCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface EditHistoryEntry {
  original_text: string;
  edited_text: string;
  edited_by: string;
  edited_at: string;
}

interface ReviewEditHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  reviewId: string;
}

export function ReviewEditHistoryModal({
  isOpen,
  onClose,
  reviewId
}: ReviewEditHistoryModalProps) {
  const [history, setHistory] = useState<EditHistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchEditHistory();
    }
  }, [isOpen, reviewId]);

  const fetchEditHistory = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/reviews/${reviewId}/edit-history`);

      if (!response.ok) {
        throw new Error('Failed to fetch edit history');
      }

      const data = await response.json();
      setHistory(data.edit_history || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load edit history');
    } finally {
      setLoading(false);
    }
  };

  const highlightDifferences = (original: string, edited: string) => {
    // Simple diff highlighting - in production, use a proper diff library
    const originalWords = original.split(' ');
    const editedWords = edited.split(' ');

    return (
      <div className="space-y-2">
        <div>
          <p className="text-xs font-semibold text-gray-700 mb-1">Original:</p>
          <p className="text-xs text-gray-600 bg-red-50 p-2 rounded border border-red-200">
            {original}
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold text-gray-700 mb-1">Updated:</p>
          <p className="text-xs text-gray-600 bg-green-50 p-2 rounded border border-green-200">
            {edited}
          </p>
        </div>
      </div>
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Review Edit History</DialogTitle>
          <DialogDescription>
            View all edits made to this review comment
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

          {loading ? (
            <div className="text-center py-8">
              <p className="text-gray-600">Loading edit history...</p>
            </div>
          ) : history.length === 0 ? (
            <Card>
              <CardContent className="pt-6 text-center py-8">
                <p className="text-gray-600">No edit history available</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {history.map((edit, index) => (
                <Card key={index} className="border-l-4 border-l-blue-500">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <p className="font-semibold text-gray-900">
                          Edit #{history.length - index}
                        </p>
                        <p className="text-sm text-gray-600">
                          Edited by: <strong>{edit.edited_by}</strong>
                        </p>
                      </div>
                      <p className="text-sm text-gray-600">
                        {new Date(edit.edited_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit'
                        })}
                      </p>
                    </div>

                    {/* Diff View */}
                    <div className="space-y-3">
                      {highlightDifferences(edit.original_text, edit.edited_text)}
                    </div>

                    {/* Character Count */}
                    <div className="mt-3 flex gap-4 text-xs text-gray-600">
                      <span>
                        Original: <strong>{edit.original_text.length}</strong> characters
                      </span>
                      <span>
                        Updated: <strong>{edit.edited_text.length}</strong> characters
                      </span>
                      <span>
                        Change: <strong>{edit.edited_text.length - edit.original_text.length > 0 ? '+' : ''}{edit.edited_text.length - edit.original_text.length}</strong> characters
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
