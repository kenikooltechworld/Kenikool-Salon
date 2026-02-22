"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import {
  useNotificationTemplates,
  useCreateTemplate,
  useUpdateTemplate,
  useDeleteTemplate,
  NotificationTemplate,
} from "@/lib/api/hooks/useWaitlistTemplates";

const AVAILABLE_VARIABLES = [
  "{client_name}",
  "{salon_name}",
  "{service_name}",
  "{salon_phone}",
];

export const NotificationTemplateManager: React.FC = () => {
  const { data: templates, isLoading } = useNotificationTemplates();
  const createMutation = useCreateTemplate();
  const updateMutation = useUpdateTemplate();
  const deleteMutation = useDeleteTemplate();

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] =
    useState<NotificationTemplate | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    message: "",
    is_default: false,
  });

  const handleCreateTemplate = () => {
    if (!formData.name || !formData.message) {
      showToast("Please fill in all fields", "warning");
      return;
    }

    createMutation.mutate({
      name: formData.name,
      message: formData.message,
      variables: AVAILABLE_VARIABLES.filter((v) =>
        formData.message.includes(v),
      ),
      is_default: formData.is_default,
    });

    setFormData({ name: "", message: "", is_default: false });
    setIsCreateOpen(false);
  };

  const handleUpdateTemplate = () => {
    if (!editingTemplate || !formData.name || !formData.message) {
      showToast("Please fill in all fields", "warning");
      return;
    }

    updateMutation.mutate({
      id: editingTemplate.id,
      name: formData.name,
      message: formData.message,
      variables: AVAILABLE_VARIABLES.filter((v) =>
        formData.message.includes(v),
      ),
      is_default: formData.is_default,
    });

    setEditingTemplate(null);
    setFormData({ name: "", message: "", is_default: false });
  };

  const handleDeleteTemplate = (templateId: string) => {
    if (confirm("Delete this template?")) {
      deleteMutation.mutate(templateId);
    }
  };

  const openEditDialog = (template: NotificationTemplate) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      message: template.message,
      is_default: template.is_default,
    });
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading templates...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Create Template Button */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <Button
          className="bg-blue-600 hover:bg-blue-700"
          onClick={() => setIsCreateOpen(true)}
        >
          Create Template
        </Button>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Notification Template</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Template Name
              </label>
              <Input
                placeholder="e.g., Appointment Reminder"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Message</label>
              <Textarea
                placeholder="Enter template message with variables like {client_name}, {service_name}"
                value={formData.message}
                onChange={(e) =>
                  setFormData({ ...formData, message: e.target.value })
                }
                rows={6}
              />
              <div className="mt-2 text-sm text-gray-600">
                <p className="font-medium mb-1">Available variables:</p>
                <div className="flex flex-wrap gap-2">
                  {AVAILABLE_VARIABLES.map((v) => (
                    <Badge key={v} variant="outline">
                      {v}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Checkbox
                checked={formData.is_default}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, is_default: checked as boolean })
                }
              />
              <label className="text-sm font-medium">
                Set as default template
              </label>
            </div>

            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setIsCreateOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={handleCreateTemplate}
                disabled={createMutation.isPending}
              >
                Create
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Template Dialog */}
      <Dialog
        open={!!editingTemplate}
        onOpenChange={(open) => !open && setEditingTemplate(null)}
      >
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Template</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Template Name
              </label>
              <Input
                placeholder="e.g., Appointment Reminder"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Message</label>
              <Textarea
                placeholder="Enter template message with variables"
                value={formData.message}
                onChange={(e) =>
                  setFormData({ ...formData, message: e.target.value })
                }
                rows={6}
              />
              <div className="mt-2 text-sm text-gray-600">
                <p className="font-medium mb-1">Available variables:</p>
                <div className="flex flex-wrap gap-2">
                  {AVAILABLE_VARIABLES.map((v) => (
                    <Badge key={v} variant="outline">
                      {v}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Checkbox
                checked={formData.is_default}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, is_default: checked as boolean })
                }
              />
              <label className="text-sm font-medium">
                Set as default template
              </label>
            </div>

            <div className="flex gap-2 justify-end">
              <Button
                variant="outline"
                onClick={() => setEditingTemplate(null)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleUpdateTemplate}
                disabled={updateMutation.isPending}
              >
                Update
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Templates List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {templates?.map((template: NotificationTemplate) => (
          <Card key={template.id} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-semibold">{template.name}</h3>
                {template.is_default && <Badge className="mt-1">Default</Badge>}
              </div>
            </div>

            <p className="text-sm text-gray-600 mb-4 line-clamp-3">
              {template.message}
            </p>

            <div className="mb-4">
              <p className="text-xs font-medium text-gray-500 mb-2">
                Variables used:
              </p>
              <div className="flex flex-wrap gap-1">
                {template.variables.map((v) => (
                  <Badge key={v} variant="outline" className="text-xs">
                    {v}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => openEditDialog(template)}
              >
                Edit
              </Button>
              <Button
                size="sm"
                variant="destructive"
                onClick={() => handleDeleteTemplate(template.id)}
                disabled={deleteMutation.isPending}
              >
                Delete
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {!templates ||
        (templates.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No templates created yet. Create one to get started.
          </div>
        ))}
    </div>
  );
};
