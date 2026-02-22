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
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { AlertCircle } from 'lucide-react';

interface ReviewFlagModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (reason: string, details?: string) => Promise<void>;
  isLoading?: boolean;
}

const FLAG_REASONS = [
  { value: 'spam', label: 'Spam', description: 'Promotional or irrelevant content' },
  { value: 'offensive', label: 'Offensive', description: 'Abusive, hateful, or inappropriate language' },
  { value: 'fake', label: 'Fake Review', description: 'Appears to be fraudulent or unverified' },
  { value: 'other', label: 'Other', description: 'Something else' }
];

export function ReviewFlagModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false
}: ReviewFlagModalProps) {
  const [selectedReason, setSelectedReason] = useState<string>('');
  const [details, setDetails] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!selectedReason) {
      setError('Please select a reason');
      return;
    }

    try {
      setError(null);
      await onSubmit(selectedReason, details);
      handleClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to flag review');
    }
  };

  const handleClose = () => {
    setSelectedReason('');
    setDetails('');
    setError(null);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-amber-600" />
            Flag Review
          </DialogTitle>
          <DialogDescription>
            Help us maintain quality by reporting inappropriate reviews
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Reason Selection */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Reason for flagging</Label>
            <div className="space-y-2">
              {FLAG_REASONS.map(reason => (
                <label
                  key={reason.value}
                  className="flex items-start gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                >
                  <input
                    type="radio"
                    name="reason"
                    value={reason.value}
                    checked={selectedReason === reason.value}
                    onChange={(e) => setSelectedReason(e.target.value)}
                    className="w-4 h-4 mt-1"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-sm text-gray-900">{reason.label}</p>
                    <p className="text-xs text-gray-600">{reason.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Additional Details */}
          {selectedReason && (
            <div className="space-y-2">
              <Label htmlFor="details" className="text-sm">
                Additional details (optional)
              </Label>
              <Textarea
                id="details"
                placeholder="Provide any additional context..."
                value={details}
                onChange={(e) => setDetails(e.target.value)}
                className="min-h-[100px] text-sm"
                disabled={isLoading}
              />
              <p className="text-xs text-gray-500">
                {details.length}/500 characters
              </p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-xs text-blue-800">
              Flagged reviews are reviewed by our moderation team. False reports may result in account restrictions.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!selectedReason || isLoading}
            className="bg-amber-600 hover:bg-amber-700"
          >
            {isLoading ? 'Flagging...' : 'Flag Review'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
