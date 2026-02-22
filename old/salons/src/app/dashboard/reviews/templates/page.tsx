'use client';

import { useEffect, useState } from 'react';
import { useResponseTemplates } from '@/lib/api/hooks/useClientReviews';
import { TemplateManager } from '@/components/reviews/template-manager';
import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertCircle } from 'lucide-react';

interface Template {
  _id: string;
  name: string;
  category: 'positive' | 'negative' | 'neutral';
  text: string;
  is_default: boolean;
}

export default function TemplatesPage() {
  const { data: templates = [], isLoading, error } = useResponseTemplates();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const handleCreateTemplate = async (data: {
    name: string;
    category: string;
    text: string;
  }) => {
    try {
      setIsSubmitting(true);
      setSubmitError(null);

      const response = await fetch('/api/reviews/templates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create template');
      }

      // Refresh templates
      window.location.reload();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to create template');
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateTemplate = async (
    id: string,
    data: { name?: string; category?: string; text?: string }
  ) => {
    try {
      setIsSubmitting(true);
      setSubmitError(null);

      const response = await fetch(`/api/reviews/templates/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update template');
      }

      // Refresh templates
      window.location.reload();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to update template');
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteTemplate = async (id: string) => {
    try {
      setIsSubmitting(true);
      setSubmitError(null);

      const response = await fetch(`/api/reviews/templates/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete template');
      }

      // Refresh templates
      window.location.reload();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to delete template');
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDuplicateTemplate = async (id: string) => {
    try {
      setIsSubmitting(true);
      setSubmitError(null);

      const template = templates.find((t) => t._id === id);
      if (!template) throw new Error('Template not found');

      const response = await fetch('/api/reviews/templates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: `${template.name} (Copy)`,
          category: template.category,
          text: template.text,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to duplicate template');
      }

      // Refresh templates
      window.location.reload();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to duplicate template');
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  };

  if (error) {
    return (
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">Response Templates</h1>
        <Card className="p-4 bg-destructive/10 border-destructive/20">
          <div className="flex items-start gap-3">
            <AlertCircle className="text-destructive mt-0.5 flex-shrink-0" size={20} />
            <div>
              <h3 className="font-semibold text-destructive">Error Loading Templates</h3>
              <p className="text-sm text-destructive/80">
                {error instanceof Error ? error.message : 'Failed to load templates'}
              </p>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Response Templates</h1>
        <p className="text-muted-foreground mt-2">
          Manage response templates for common review scenarios
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-10 w-full" />
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-48" />
            ))}
          </div>
        </div>
      ) : (
        <TemplateManager
          templates={templates}
          isLoading={isSubmitting}
          onCreateTemplate={handleCreateTemplate}
          onUpdateTemplate={handleUpdateTemplate}
          onDeleteTemplate={handleDeleteTemplate}
          onDuplicateTemplate={handleDuplicateTemplate}
        />
      )}

      {submitError && (
        <Card className="p-4 bg-destructive/10 border-destructive/20">
          <div className="flex items-start gap-3">
            <AlertCircle className="text-destructive mt-0.5 flex-shrink-0" size={20} />
            <div>
              <h3 className="font-semibold text-destructive">Error</h3>
              <p className="text-sm text-destructive/80">{submitError}</p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
