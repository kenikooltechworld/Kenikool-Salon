"use client";

import { WhiteLabelBranding } from "@/lib/api/hooks/useWhiteLabel";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";
import { Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export interface ThemeTemplate {
  id: string;
  name: string;
  description: string;
  category: "spa" | "barber" | "salon" | "modern" | "classic";
  branding: WhiteLabelBranding;
  previewImage?: string;
}

interface TemplateSelectorProps {
  templates?: ThemeTemplate[];
  onApplyTemplate: (template: ThemeTemplate) => void;
  onSaveAsTemplate?: (
    name: string,
    branding: WhiteLabelBranding,
  ) => Promise<void>;
  currentBranding?: WhiteLabelBranding;
  useHooks?: boolean;
}

const DEFAULT_TEMPLATES: ThemeTemplate[] = [
  {
    id: "spa-luxury",
    name: "Spa Luxury",
    description: "Elegant and calming design for spa services",
    category: "spa",
    branding: {
      company_name: "Serenity Spa",
      tagline: "Relax and Rejuvenate",
      primary_color: "#8B7355",
      secondary_color: "#D4AF37",
      accent_color: "#E8D5C4",
      font_family: "Georgia, serif",
      logo_url: "",
      favicon_url: "",
      custom_css: "",
      hide_powered_by: false,
      support_email: "",
      support_phone: "",
      terms_url: "",
      privacy_url: "",
    },
  },
  {
    id: "barber-classic",
    name: "Barber Classic",
    description: "Traditional barbershop aesthetic",
    category: "barber",
    branding: {
      company_name: "Classic Barber",
      tagline: "Premium Grooming",
      primary_color: "#1a1a1a",
      secondary_color: "#DC143C",
      accent_color: "#FFD700",
      font_family: "Courier New, monospace",
      logo_url: "",
      favicon_url: "",
      custom_css: "",
      hide_powered_by: false,
      support_email: "",
      support_phone: "",
      terms_url: "",
      privacy_url: "",
    },
  },
  {
    id: "salon-modern",
    name: "Salon Modern",
    description: "Contemporary and vibrant salon design",
    category: "salon",
    branding: {
      company_name: "Modern Salon",
      tagline: "Your Style, Your Way",
      primary_color: "#FF6B9D",
      secondary_color: "#C44569",
      accent_color: "#FFA502",
      font_family: "Poppins, sans-serif",
      logo_url: "",
      favicon_url: "",
      custom_css: "",
      hide_powered_by: false,
      support_email: "",
      support_phone: "",
      terms_url: "",
      privacy_url: "",
    },
  },
  {
    id: "tech-modern",
    name: "Tech Modern",
    description: "Sleek and professional tech-inspired design",
    category: "modern",
    branding: {
      company_name: "Tech Beauty",
      tagline: "Innovation in Beauty",
      primary_color: "#0066CC",
      secondary_color: "#00D4FF",
      accent_color: "#FF00FF",
      font_family: "Inter, sans-serif",
      logo_url: "",
      favicon_url: "",
      custom_css: "",
      hide_powered_by: false,
      support_email: "",
      support_phone: "",
      terms_url: "",
      privacy_url: "",
    },
  },
  {
    id: "classic-elegant",
    name: "Classic Elegant",
    description: "Timeless and sophisticated design",
    category: "classic",
    branding: {
      company_name: "Elegant Beauty",
      tagline: "Timeless Beauty",
      primary_color: "#2C3E50",
      secondary_color: "#E74C3C",
      accent_color: "#ECF0F1",
      font_family: "Garamond, serif",
      logo_url: "",
      favicon_url: "",
      custom_css: "",
      hide_powered_by: false,
      support_email: "",
      support_phone: "",
      terms_url: "",
      privacy_url: "",
    },
  },
];

export function TemplateSelector({
  templates = DEFAULT_TEMPLATES,
  onApplyTemplate,
  onSaveAsTemplate,
  currentBranding,
  useHooks = false,
}: TemplateSelectorProps) {
  const { showToast } = useToast();
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [savingTemplate, setSavingTemplate] = useState(false);
  const [templateName, setTemplateName] = useState("");

  const handleApplyTemplate = (template: ThemeTemplate) => {
    setSelectedTemplate(template.id);
    onApplyTemplate(template);
  };

  const handleSaveAsTemplate = async () => {
    if (!templateName.trim() || !currentBranding || !onSaveAsTemplate) return;

    try {
      setSavingTemplate(true);
      await onSaveAsTemplate(templateName, currentBranding);
      setTemplateName("");
      setShowSaveForm(false);
    } catch (error) {
      console.error("Failed to save template:", error);
      showToast({
        title: "Error",
        description: "Failed to save template. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSavingTemplate(false);
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      spa: "bg-purple-100 text-purple-800",
      barber: "bg-gray-100 text-gray-800",
      salon: "bg-pink-100 text-pink-800",
      modern: "bg-blue-100 text-blue-800",
      classic: "bg-amber-100 text-amber-800",
    };
    return colors[category] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Theme Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((template) => (
            <Card
              key={template.id}
              className={`p-4 cursor-pointer transition-all ${
                selectedTemplate === template.id
                  ? "ring-2 ring-blue-500 bg-blue-50"
                  : "hover:shadow-lg"
              }`}
              onClick={() => handleApplyTemplate(template)}
            >
              {/* Preview Box */}
              <div
                className="w-full h-32 rounded-lg mb-3 flex items-center justify-center text-white font-semibold text-lg"
                style={{
                  background: `linear-gradient(135deg, ${template.branding.primary_color} 0%, ${template.branding.secondary_color} 100%)`,
                }}
              >
                {template.branding.company_name}
              </div>

              {/* Template Info */}
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="font-semibold text-sm">{template.name}</h4>
                    <p className="text-xs text-gray-600 mt-1">
                      {template.description}
                    </p>
                  </div>
                  {selectedTemplate === template.id && (
                    <Check className="h-5 w-5 text-blue-500 flex-shrink-0" />
                  )}
                </div>

                {/* Category Badge */}
                <Badge
                  className={`w-fit text-xs ${getCategoryColor(template.category)}`}
                >
                  {template.category}
                </Badge>

                {/* Color Preview */}
                <div className="flex gap-2 mt-3">
                  <div
                    className="w-6 h-6 rounded border"
                    style={{ backgroundColor: template.branding.primary_color }}
                    title="Primary"
                  />
                  <div
                    className="w-6 h-6 rounded border"
                    style={{
                      backgroundColor: template.branding.secondary_color,
                    }}
                    title="Secondary"
                  />
                  <div
                    className="w-6 h-6 rounded border"
                    style={{ backgroundColor: template.branding.accent_color }}
                    title="Accent"
                  />
                </div>

                {/* Apply Button */}
                <Button
                  size="sm"
                  className="w-full mt-3"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleApplyTemplate(template);
                  }}
                >
                  {selectedTemplate === template.id
                    ? "Applied"
                    : "Apply Template"}
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Save Current as Template */}
      {currentBranding && onSaveAsTemplate && (
        <Card className="p-4 bg-gray-50">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-semibold">Save Current Branding</h4>
              <p className="text-sm text-gray-600 mt-1">
                Save your current branding configuration as a reusable template
              </p>
            </div>
            <Button
              variant="outline"
              onClick={() => setShowSaveForm(!showSaveForm)}
            >
              {showSaveForm ? "Cancel" : "Save as Template"}
            </Button>
          </div>

          {showSaveForm && (
            <div className="mt-4 space-y-3 pt-4 border-t">
              <div>
                <label className="text-sm font-medium">Template Name</label>
                <input
                  type="text"
                  value={templateName}
                  onChange={(e) => setTemplateName(e.target.value)}
                  placeholder="e.g., My Custom Salon Theme"
                  className="w-full mt-1 px-3 py-2 border rounded-lg text-sm"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setShowSaveForm(false);
                    setTemplateName("");
                  }}
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleSaveAsTemplate}
                  disabled={!templateName.trim() || savingTemplate}
                >
                  {savingTemplate ? "Saving..." : "Save Template"}
                </Button>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
