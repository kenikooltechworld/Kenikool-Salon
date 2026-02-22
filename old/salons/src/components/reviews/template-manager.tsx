'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { AlertCircle, Edit2, Trash2, Plus, Copy } from 'lucide-react';

interface Template {
  _id: string;
  name: string;
  category: 'positive' | 'negative' | 'neutral';
  text: string;
  is_default: boolean;
}

interface TemplateManagerProps {
  templates: Template[];
  isLoading?: boolean;
  onCreateTemplate?: (data: { name: string; category: string; text: string }) => Promise<void>;
  onUpdateTemplate?: (id: string, data: { name?: string; category?: string; text?: string }) => Promise<void>;
  onDeleteTemplate?: (id: string) => Promise<void>;
  onDuplicateTemplate?: (id: string) => Promise<void>;
}

const CATEGORY_COLORS = {
  positive: 'bg-green-100 text-green-800',
  negative: 'bg-red-100 text-red-800',
  neutral: 'bg-blue-100 text-blue-800',
};

export function TemplateManager({
  templates,
  isLoading = false,
  onCreateTemplate,
  onUpdateTemplate,
  onDeleteTemplate,
  onDuplicateTemplate,
}: TemplateManagerProps) {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);
  const [formData, setFormData] = useState({ name: '', category: 'positive', text: '' });
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredTemplates = templates.filter(
    (t) =>
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.text.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreateOpen = () => {
    setFormData({ name: '', category: 'positive', text: '' });
    setError(null);
    setIsCreateOpen(true);
  };

  const handleEditOpen = (template: Template) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      category: template.category,
      text: template.text,
    });
    setError(null);
    setIsEditOpen(true);
  };

  const handleCreateSubmit = async () => {
    if (!formData.name.trim()) {
      setError('Template name is required');
      return;
    }

    if (!formData.text.trim()) {
      setError('Template text is required');
      return;
    }

    if (formData.text.length > 1000) {
      setError('Template text cannot exceed 1000 characters');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onCreateTemplate?.(formData);
      setIsCreateOpen(false);
      setFormData({ name: '', category: 'positive', text: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create template');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateSubmit = async () => {
    if (!editingTemplate) return;

    if (!formData.name.trim()) {
      setError('Template name is required');
      return;
    }

    if (!formData.text.trim()) {
      setError('Template text is required');
      return;
    }

    if (formData.text.length > 1000) {
      setError('Template text cannot exceed 1000 characters');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onUpdateTemplate?.(editingTemplate._id, formData);
      setIsEditOpen(false);
      setEditingTemplate(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update template');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this template?')) return;

    try {
      await onDeleteTemplate?.(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete template');
    }
  };

  const handleDuplicate = async (id: string) => {
    try {
      await onDuplicateTemplate?.(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to duplicate template');
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Response Templates</h2>
        <Button onClick={handleCreateOpen} disabled={isLoading}>
          <Plus size={16} className="mr-2" />
          New Template
        </Button>
      </div>

      {/* Search */}
      <Input
        placeholder="Search templates..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        disabled={isLoading}
      />

      {/* Error Message */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3 flex items-start gap-2">
          <AlertCircle size={16} className="text-destructive mt-0.5 flex-shrink-0" />
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      {/* Templates Grid */}
      {filteredTemplates.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">No templates found</p>
          <Button onClick={handleCreateOpen} variant="outline">
            Create First Template
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredTemplates.map((template) => (
            <Card key={template._id} className="p-4 space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-sm">{template.name}</h3>
                  <Badge
                    className={`mt-1 ${CATEGORY_COLORS[template.category]}`}
                    variant="outline"
                  >
                    {template.category}
                  </Badge>
                  {template.is_default && (
                    <Badge className="ml-2 mt-1" variant="secondary">
                      Default
                    </Badge>
                  )}
                </div>
              </div>

              <p className="text-xs text-muted-foreground line-clamp-3">
                {template.text}
              </p>

              <div className="flex gap-2 pt-2 border-t">
                {!template.is_default && (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEditOpen(template)}
                      disabled={isLoading}
                      className="flex-1"
                    >
                      <Edit2 size={14} className="mr-1" />
                      Edit
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(template._id)}
                      disabled={isLoading}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 size={14} />
                    </Button>
                  </>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDuplicate(template._id)}
                  disabled={isLoading}
                  className="flex-1"
                >
                  <Copy size={14} className="mr-1" />
                  Duplicate
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create Dialog */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Template</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Template Name</label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Thank You - Positive Review"
                disabled={isSubmitting}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Category</label>
              <Select
                value={formData.category}
                onValueChange={(value) =>
                  setFormData({ ...formData, category: value })
                }
                disabled={isSubmitting}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="positive">Positive</SelectItem>
                  <SelectItem value="negative">Negative</SelectItem>
                  <SelectItem value="neutral">Neutral</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Template Text</label>
              <Textarea
                value={formData.text}
                onChange={(e) => setFormData({ ...formData, text: e.target.value })}
                placeholder="Write your template response..."
                className="min-h-[120px] resize-none"
                disabled={isSubmitting}
              />
              <p className="text-xs text-muted-foreground">
                {formData.text.length} / 1000 characters
              </p>
            </div>

            {error && (
              <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-2">
                <p className="text-xs text-destructive">{error}</p>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsCreateOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button onClick={handleCreateSubmit} disabled={isSubmitting}>
              {isSubmitting ? 'Creating...' : 'Create Template'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Template</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Template Name</label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Thank You - Positive Review"
                disabled={isSubmitting}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Category</label>
              <Select
                value={formData.category}
                onValueChange={(value) =>
                  setFormData({ ...formData, category: value })
                }
                disabled={isSubmitting}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="positive">Positive</SelectItem>
                  <SelectItem value="negative">Negative</SelectItem>
                  <SelectItem value="neutral">Neutral</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Template Text</label>
              <Textarea
                value={formData.text}
                onChange={(e) => setFormData({ ...formData, text: e.target.value })}
                placeholder="Write your template response..."
                className="min-h-[120px] resize-none"
                disabled={isSubmitting}
              />
              <p className="text-xs text-muted-foreground">
                {formData.text.length} / 1000 characters
              </p>
            </div>

            {error && (
              <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-2">
                <p className="text-xs text-destructive">{error}</p>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsEditOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button onClick={handleUpdateSubmit} disabled={isSubmitting}>
              {isSubmitting ? 'Updating...' : 'Update Template'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
