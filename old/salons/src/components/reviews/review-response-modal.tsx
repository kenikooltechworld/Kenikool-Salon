'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertCircle, Eye, EyeOff } from 'lucide-react';

interface Review {
  _id: string;
  client_name: string;
  rating: number;
  comment: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  response?: {
    text: string;
    responder_name: string;
    responded_at: string;
  };
}

interface ResponseTemplate {
  _id: string;
  name: string;
  category: 'positive' | 'negative' | 'neutral';
  text: string;
}

interface ReviewResponseModalProps {
  review: Review | null;
  templates: ResponseTemplate[];
  isOpen: boolean;
  isLoading?: boolean;
  onSubmit: (response: string) => Promise<void>;
  onClose: () => void;
}

const MAX_CHARACTERS = 500;

export function ReviewResponseModal({
  review,
  templates,
  isOpen,
  isLoading = false,
  onSubmit,
  onClose,
}: ReviewResponseModalProps) {
  const [responseText, setResponseText] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [showPreview, setShowPreview] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen && review) {
      setResponseText(review.response?.text || '');
      setSelectedTemplate('');
      setShowPreview(false);
      setError(null);
    }
  }, [isOpen, review]);

  if (!review) return null;

  const handleTemplateSelect = (templateId: string) => {
    const template = templates.find((t) => t._id === templateId);
    if (template) {
      setResponseText(template.text);
      setSelectedTemplate(templateId);
    }
  };

  const handleSubmit = async () => {
    if (!responseText.trim()) {
      setError('Response cannot be empty');
      return;
    }

    if (responseText.length > MAX_CHARACTERS) {
      setError(`Response exceeds maximum length of ${MAX_CHARACTERS} characters`);
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit(responseText);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit response');
    } finally {
      setIsSubmitting(false);
    }
  };

  const characterCount = responseText.length;
  const characterPercentage = (characterCount / MAX_CHARACTERS) * 100;
  const isNearLimit = characterPercentage > 80;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {review.response ? 'Edit Response' : 'Add Response'}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Review Summary */}
          <div className="bg-muted p-4 rounded-lg space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold">{review.client_name}</h4>
              <Badge variant="outline">
                {review.rating} / 5 ⭐
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">{review.comment}</p>
            <p className="text-xs text-muted-foreground">
              {new Date(review.created_at).toLocaleString()}
            </p>
          </div>

          {/* Template Selector */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Response Template (Optional)</label>
            <Select value={selectedTemplate} onValueChange={handleTemplateSelect}>
              <SelectTrigger>
                <SelectValue placeholder="Select a template..." />
              </SelectTrigger>
              <SelectContent>
                {templates.map((template) => (
                  <SelectItem key={template._id} value={template._id}>
                    <span className="flex items-center gap-2">
                      {template.name}
                      <Badge variant="outline" className="text-xs">
                        {template.category}
                      </Badge>
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Response Editor */}
          <Tabs defaultValue="edit" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="edit">Edit</TabsTrigger>
              <TabsTrigger value="preview">Preview</TabsTrigger>
            </TabsList>

            <TabsContent value="edit" className="space-y-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Your Response</label>
                <Textarea
                  value={responseText}
                  onChange={(e) => {
                    setResponseText(e.target.value);
                    setError(null);
                  }}
                  placeholder="Write your response here..."
                  className="min-h-[150px] resize-none"
                  disabled={isSubmitting || isLoading}
                />
              </div>

              {/* Character Count */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className={isNearLimit ? 'text-warning' : 'text-muted-foreground'}>
                    {characterCount} / {MAX_CHARACTERS} characters
                  </span>
                  {isNearLimit && (
                    <span className="text-warning flex items-center gap-1">
                      <AlertCircle size={14} />
                      Approaching limit
                    </span>
                  )}
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      isNearLimit ? 'bg-warning' : 'bg-primary'
                    }`}
                    style={{ width: `${Math.min(characterPercentage, 100)}%` }}
                  />
                </div>
              </div>
            </TabsContent>
          </Tabs>

          {/* Error Message */}
          {error && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3 flex items-start gap-2">
              <AlertCircle size={16} className="text-destructive mt-0.5 flex-shrink-0" />
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          {/* Existing Response Info */}
          {review.response && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-xs font-medium text-blue-900 mb-1">
                Last response by {review.response.responder_name}
              </p>
              <p className="text-xs text-blue-800">
                {new Date(review.response.responded_at).toLocaleString()}
              </p>
            </div>
          )}
        </div>

        <DialogFooter className="flex gap-2">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isSubmitting || isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || isLoading || !responseText.trim()}
          >
            {isSubmitting || isLoading ? 'Submitting...' : 'Submit Response'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
