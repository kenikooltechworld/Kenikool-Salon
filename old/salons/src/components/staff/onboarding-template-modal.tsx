import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { X, Plus, Trash2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface TemplateItem {
  title: string;
  description: string;
  assigned_to: "manager" | "staff" | "owner";
  order: number;
}

interface OnboardingTemplateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateTemplate?: (
    templateName: string,
    items: TemplateItem[],
  ) => Promise<void>;
}

export const OnboardingTemplateModal: React.FC<
  OnboardingTemplateModalProps
> = ({ isOpen, onClose, onCreateTemplate }) => {
  const { showToast } = useToast();
  const [templateName, setTemplateName] = useState("");
  const [items, setItems] = useState<TemplateItem[]>([
    {
      title: "Complete Paperwork",
      description: "Fill out employment forms and tax documents",
      assigned_to: "manager",
      order: 1,
    },
  ]);
  const [loading, setLoading] = useState(false);

  const handleAddItem = () => {
    setItems([
      ...items,
      {
        title: "",
        description: "",
        assigned_to: "manager",
        order: items.length + 1,
      },
    ]);
  };

  const handleRemoveItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleItemChange = (
    index: number,
    field: keyof TemplateItem,
    value: any,
  ) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
  };

  const handleCreateTemplate = async () => {
    if (!templateName.trim()) {
      showToast({
        title: "Validation Error",
        description: "Please enter a template name",
        variant: "destructive",
      });
      return;
    }

    if (items.some((item) => !item.title.trim())) {
      showToast({
        title: "Validation Error",
        description: "All items must have a title",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      if (onCreateTemplate) {
        await onCreateTemplate(templateName, items);
      }
      setTemplateName("");
      setItems([
        {
          title: "Complete Paperwork",
          description: "Fill out employment forms and tax documents",
          assigned_to: "manager",
          order: 1,
        },
      ]);
      onClose();
    } catch (error) {
      console.error("Failed to create template:", error);
      showToast({
        title: "Error",
        description: "Failed to create template",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[80vh] flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between border-b">
          <CardTitle>Create Onboarding Template</CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>

        <CardContent className="flex-1 overflow-hidden flex flex-col p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Template Name *
            </label>
            <Input
              placeholder="e.g., Standard Onboarding"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
            />
          </div>

          <div className="flex-1 overflow-hidden flex flex-col">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium">Items</label>
              <Button onClick={handleAddItem} variant="outline" size="sm">
                <Plus className="w-4 h-4 mr-1" />
                Add Item
              </Button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 border rounded-lg p-3 bg-slate-50">
              {items.map((item, index) => (
                <div
                  key={index}
                  className="bg-white border rounded-lg p-3 space-y-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 space-y-2">
                      <Input
                        placeholder="Item title"
                        value={item.title}
                        onChange={(e) =>
                          handleItemChange(index, "title", e.target.value)
                        }
                        className="text-sm"
                      />
                      <Textarea
                        placeholder="Item description"
                        value={item.description}
                        onChange={(e) =>
                          handleItemChange(index, "description", e.target.value)
                        }
                        rows={2}
                        className="text-sm"
                      />
                      <Select
                        value={item.assigned_to}
                        onValueChange={(value) =>
                          handleItemChange(index, "assigned_to", value)
                        }
                      >
                        <SelectTrigger className="text-sm">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="manager">Manager</SelectItem>
                          <SelectItem value="staff">Staff</SelectItem>
                          <SelectItem value="owner">Owner</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveItem(index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-2 border-t pt-4">
            <Button
              onClick={handleCreateTemplate}
              disabled={loading}
              className="flex-1"
            >
              Create Template
            </Button>
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
