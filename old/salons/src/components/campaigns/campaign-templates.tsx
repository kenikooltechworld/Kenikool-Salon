import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { TrashIcon, CopyIcon } from "@/components/icons";
import { toast } from "sonner";

const DEFAULT_TEMPLATES = [
  {
    id: "birthday",
    name: "Birthday Special",
    message:
      "Happy Birthday {{client_name}}! 🎉 Enjoy 20% off all services at {{salon_name}}. Valid for 7 days!",
    variables: ["client_name", "salon_name"],
  },
  {
    id: "seasonal",
    name: "Seasonal Promotion",
    message:
      "{{client_name}}, it's time for a refresh! Get 15% off at {{salon_name}} this season. Book now!",
    variables: ["client_name", "salon_name"],
  },
  {
    id: "winback",
    name: "Win Back Campaign",
    message:
      "We miss you {{client_name}}! Come back to {{salon_name}} and get 25% off your next visit.",
    variables: ["client_name", "salon_name"],
  },
  {
    id: "referral",
    name: "Referral Program",
    message:
      "{{client_name}}, refer a friend to {{salon_name}} and both of you get ₦500 credit!",
    variables: ["client_name", "salon_name"],
  },
];

export function CampaignTemplates() {
  const [templates, setTemplates] = useState(DEFAULT_TEMPLATES);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTemplate, setNewTemplate] = useState({
    name: "",
    message: "",
  });

  const handleCreateTemplate = () => {
    if (!newTemplate.name || !newTemplate.message) {
      toast.error("Please fill in all fields");
      return;
    }

    const template = {
      id: Date.now().toString(),
      name: newTemplate.name,
      message: newTemplate.message,
      variables: extractVariables(newTemplate.message),
    };

    setTemplates([...templates, template]);
    toast.success("Template created successfully");
    setNewTemplate({ name: "", message: "" });
    setShowCreateForm(false);
  };

  const handleDeleteTemplate = (id: string) => {
    if (DEFAULT_TEMPLATES.find((t) => t.id === id)) {
      toast.error("Cannot delete default templates");
      return;
    }
    setTemplates(templates.filter((t) => t.id !== id));
    toast.success("Template deleted");
  };

  const handleCopyTemplate = (message: string) => {
    navigator.clipboard.writeText(message);
    toast.success("Template copied to clipboard");
  };

  const extractVariables = (message: string): string[] => {
    const regex = /\{\{(\w+)\}\}/g;
    const matches = [];
    let match;
    while ((match = regex.exec(message)) !== null) {
      matches.push(match[1]);
    }
    return [...new Set(matches)];
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold">Message Templates</h2>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          {showCreateForm ? "Cancel" : "Create Template"}
        </Button>
      </div>

      {showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Template</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Template Name</label>
              <Input
                placeholder="e.g., Holiday Special"
                value={newTemplate.name}
                onChange={(e) =>
                  setNewTemplate({ ...newTemplate, name: e.target.value })
                }
              />
            </div>
            <div>
              <label className="text-sm font-medium">Message</label>
              <Textarea
                placeholder="Use {{variable_name}} for dynamic content"
                value={newTemplate.message}
                onChange={(e) =>
                  setNewTemplate({ ...newTemplate, message: e.target.value })
                }
                rows={4}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Available variables: {"{client_name}"} {"{salon_name}"}
              </p>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleCreateTemplate}>Create</Button>
              <Button
                variant="outline"
                onClick={() => setShowCreateForm(false)}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4">
        {templates.map((template) => (
          <Card key={template.id}>
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold mb-2">{template.name}</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    {template.message}
                  </p>
                  <div className="flex gap-2 flex-wrap">
                    {template.variables.map((variable) => (
                      <span
                        key={variable}
                        className="text-xs bg-muted px-2 py-1 rounded"
                      >
                        {"{{"}
                        {variable}
                        {"}}"}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleCopyTemplate(template.message)}
                  >
                    <CopyIcon className="h-4 w-4" />
                  </Button>
                  {!DEFAULT_TEMPLATES.find((t) => t.id === template.id) && (
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDeleteTemplate(template.id)}
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
