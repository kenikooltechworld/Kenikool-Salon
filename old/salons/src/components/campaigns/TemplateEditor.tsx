import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Loader2, Plus, X } from 'lucide-react';

interface TemplateEditorProps {
  template?: {
    id?: string;
    name: string;
    category: string;
    channels: string[];
    message_templates: Record<string, string>;
    email_subject?: string;
    variables: string[];
    description?: string;
  };
  onSave: (template: any) => Promise<void>;
  onCancel: () => void;
}

const AVAILABLE_CHANNELS = ['sms', 'whatsapp', 'email'];
const AVAILABLE_CATEGORIES = ['promotional', 'seasonal', 'retention', 'birthday', 'custom'];
const COMMON_VARIABLES = [
  'client_name',
  'salon_name',
  'discount_percentage',
  'promo_code',
  'booking_link',
  'feedback_link',
  'reward_points',
  'service_name',
  'season',
];

export const TemplateEditor: React.FC<TemplateEditorProps> = ({
  template,
  onSave,
  onCancel,
}) => {
  const [formData, setFormData] = useState(template || {
    name: '',
    category: 'promotional',
    channels: [],
    message_templates: {},
    email_subject: '',
    variables: [],
    description: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChannelToggle = (channel: string) => {
    setFormData(prev => ({
      ...prev,
      channels: prev.channels.includes(channel)
        ? prev.channels.filter(c => c !== channel)
        : [...prev.channels, channel],
      message_templates: {
        ...prev.message_templates,
        [channel]: prev.message_templates[channel] || '',
      },
    }));
  };

  const handleMessageChange = (channel: string, content: string) => {
    setFormData(prev => ({
      ...prev,
      message_templates: {
        ...prev.message_templates,
        [channel]: content,
      },
    }));
  };

  const handleVariableToggle = (variable: string) => {
    setFormData(prev => ({
      ...prev,
      variables: prev.variables.includes(variable)
        ? prev.variables.filter(v => v !== variable)
        : [...prev.variables, variable],
    }));
  };

  const insertVariable = (channel: string, variable: string) => {
    const textarea = document.getElementById(`message-${channel}`) as HTMLTextAreaElement;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = formData.message_templates[channel] || '';
      const newText = text.substring(0, start) + `{{${variable}}}` + text.substring(end);
      handleMessageChange(channel, newText);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!formData.name.trim()) {
        setError('Template name is required');
        return;
      }

      if (formData.channels.length === 0) {
        setError('Select at least one channel');
        return;
      }

      if (Object.values(formData.message_templates).some(msg => !msg?.trim())) {
        setError('All selected channels must have message content');
        return;
      }

      await onSave(formData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save template');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>{template?.id ? 'Edit Template' : 'Create Template'}</CardTitle>
          <CardDescription>
            Create a reusable campaign template with personalization variables
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          )}

          {/* Basic Info */}
          <div className="space-y-4">
            <h3 className="font-semibold">Basic Information</h3>

            <div>
              <label className="text-sm font-medium">Template Name</label>
              <Input
                value={formData.name}
                onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Birthday Special"
              />
            </div>

            <div>
              <label className="text-sm font-medium">Description</label>
              <Textarea
                value={formData.description || ''}
                onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe this template's purpose"
                rows={2}
              />
            </div>

            <div>
              <label className="text-sm font-medium">Category</label>
              <Select value={formData.category} onValueChange={category =>
                setFormData(prev => ({ ...prev, category }))
              }>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {AVAILABLE_CATEGORIES.map(cat => (
                    <SelectItem key={cat} value={cat}>
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Channels */}
          <div className="space-y-4">
            <h3 className="font-semibold">Channels</h3>
            <div className="space-y-2">
              {AVAILABLE_CHANNELS.map(channel => (
                <div key={channel} className="flex items-center space-x-2">
                  <Checkbox
                    id={channel}
                    checked={formData.channels.includes(channel)}
                    onCheckedChange={() => handleChannelToggle(channel)}
                  />
                  <label htmlFor={channel} className="text-sm font-medium cursor-pointer">
                    {channel.toUpperCase()}
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Messages */}
          <div className="space-y-4">
            <h3 className="font-semibold">Messages</h3>
            {formData.channels.map(channel => (
              <div key={channel} className="space-y-2 p-4 border rounded-lg">
                <div className="flex items-center justify-between">
                  <label className="font-medium">{channel.toUpperCase()} Message</label>
                  <div className="flex gap-1 flex-wrap">
                    {COMMON_VARIABLES.map(variable => (
                      <Button
                        key={variable}
                        size="sm"
                        variant="outline"
                        onClick={() => insertVariable(channel, variable)}
                      >
                        <Plus className="h-3 w-3 mr-1" />
                        {variable}
                      </Button>
                    ))}
                  </div>
                </div>

                {channel === 'email' && (
                  <Input
                    value={formData.email_subject || ''}
                    onChange={e => setFormData(prev => ({ ...prev, email_subject: e.target.value }))}
                    placeholder="Email subject"
                  />
                )}

                <Textarea
                  id={`message-${channel}`}
                  value={formData.message_templates[channel] || ''}
                  onChange={e => handleMessageChange(channel, e.target.value)}
                  placeholder={`Enter ${channel} message content`}
                  rows={4}
                />

                <div className="text-xs text-gray-500">
                  {channel === 'sms' && 'SMS: 160 characters recommended'}
                  {channel === 'whatsapp' && 'WhatsApp: 1024 characters max'}
                  {channel === 'email' && 'Email: No character limit'}
                </div>
              </div>
            ))}
          </div>

          {/* Variables */}
          <div className="space-y-4">
            <h3 className="font-semibold">Personalization Variables</h3>
            <div className="space-y-2">
              {COMMON_VARIABLES.map(variable => (
                <div key={variable} className="flex items-center space-x-2">
                  <Checkbox
                    id={`var-${variable}`}
                    checked={formData.variables.includes(variable)}
                    onCheckedChange={() => handleVariableToggle(variable)}
                  />
                  <label htmlFor={`var-${variable}`} className="text-sm font-medium cursor-pointer">
                    {variable}
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-4">
            <Button
              onClick={handleSave}
              disabled={loading}
              className="flex-1"
            >
              {loading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              {template?.id ? 'Update Template' : 'Create Template'}
            </Button>
            <Button
              onClick={onCancel}
              variant="outline"
              disabled={loading}
            >
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
