import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  CheckIcon,
  ArrowLeftIcon,
  EyeIcon,
  RefreshCwIcon,
} from "@/components/icons";
import { useToast } from "@/components/ui/toast";
import { useNavigate } from "react-router-dom";
import {
  useGetCustomerWelcomeTemplate,
  useUpdateCustomerWelcomeTemplate,
  useResetCustomerWelcomeTemplate,
  usePreviewCustomerWelcomeTemplate,
} from "@/hooks/useEmailTemplates";

export default function EmailTemplates() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const { data: templateData, isLoading } = useGetCustomerWelcomeTemplate();
  const updateTemplate = useUpdateCustomerWelcomeTemplate();
  const resetTemplate = useResetCustomerWelcomeTemplate();
  const previewTemplate = usePreviewCustomerWelcomeTemplate();

  const [template, setTemplate] = useState("");
  const [previewHtml, setPreviewHtml] = useState("");
  const [showPreview, setShowPreview] = useState(false);
  const [selectedVariable, setSelectedVariable] = useState("");

  useEffect(() => {
    if (templateData) {
      setTemplate(templateData.template);
    }
  }, [templateData]);

  const handleSave = async () => {
    try {
      await updateTemplate.mutateAsync(template);
      addToast({
        title: "Success",
        description: "Email template saved successfully!",
        variant: "success",
      });
    } catch (error) {
      addToast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to save template",
        variant: "error",
      });
    }
  };

  const handleReset = async () => {
    if (
      !confirm(
        "Are you sure you want to reset to the default template? This will discard your custom template.",
      )
    ) {
      return;
    }

    try {
      const result = await resetTemplate.mutateAsync();
      setTemplate(result.template);
      addToast({
        title: "Success",
        description: "Template reset to default!",
        variant: "success",
      });
    } catch (error) {
      addToast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to reset template",
        variant: "error",
      });
    }
  };

  const handlePreview = async () => {
    try {
      const result = await previewTemplate.mutateAsync(template);
      setPreviewHtml(result.html);
      setShowPreview(true);
    } catch (error) {
      addToast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to preview template",
        variant: "error",
      });
    }
  };

  const insertVariable = (variable: string) => {
    const textarea = document.getElementById(
      "template-editor",
    ) as HTMLTextAreaElement;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = template;
    const before = text.substring(0, start);
    const after = text.substring(end);
    const variableText = `{{ ${variable} }}`;

    setTemplate(before + variableText + after);

    // Set cursor position after inserted variable
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(
        start + variableText.length,
        start + variableText.length,
      );
    }, 0);
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-muted rounded animate-pulse w-1/3" />
        <div className="h-96 bg-muted rounded animate-pulse" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/settings")}
          className="gap-2 cursor-pointer"
        >
          <ArrowLeftIcon size={18} />
          Back
        </Button>
        <div>
          <h2 className="text-2xl font-bold text-foreground">
            Email Templates
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Customize email templates sent to your customers
          </p>
        </div>
      </div>

      {/* Customer Welcome Email Section */}
      <div className="bg-card border border-border rounded-lg p-4 md:p-6 space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-2">
            Customer Welcome Email
          </h3>
          <p className="text-sm text-muted-foreground">
            This email is sent when a new customer is created in your system.
            Customize it to match your brand and include the information you
            want.
          </p>
        </div>

        {/* Template Variables */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-foreground">
            Available Variables
          </label>
          <div className="flex flex-wrap gap-2">
            {templateData?.available_variables &&
              Object.entries(templateData.available_variables).map(
                ([key, description]) => (
                  <button
                    key={key}
                    onClick={() => insertVariable(key)}
                    className="px-3 py-1.5 text-xs font-mono bg-muted hover:bg-muted/80 text-foreground border border-border rounded-md transition-colors cursor-pointer"
                    title={description}
                  >
                    {`{{ ${key} }}`}
                  </button>
                ),
              )}
          </div>
          <p className="text-xs text-muted-foreground">
            Click a variable to insert it at your cursor position
          </p>
        </div>

        {/* Template Editor */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-foreground">
            Template HTML
          </label>
          <textarea
            id="template-editor"
            value={template}
            onChange={(e) => setTemplate(e.target.value)}
            className="w-full h-96 px-3 py-2 border border-border rounded-lg bg-background text-foreground font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary resize-y"
            placeholder="Enter your HTML template here..."
          />
          <p className="text-xs text-muted-foreground">
            Use Jinja2 template syntax. Variables: {`{{ variable_name }}`},
            Conditionals: {`{% if condition %} ... {% endif %}`}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3">
          <Button
            onClick={handlePreview}
            disabled={previewTemplate.isPending || !template.trim()}
            variant="outline"
            className="gap-2 cursor-pointer"
          >
            <EyeIcon size={18} />
            {previewTemplate.isPending ? "Generating..." : "Preview"}
          </Button>

          <Button
            onClick={handleReset}
            disabled={resetTemplate.isPending}
            variant="outline"
            className="gap-2 cursor-pointer"
          >
            <RefreshCwIcon size={18} />
            {resetTemplate.isPending ? "Resetting..." : "Reset to Default"}
          </Button>

          <Button
            onClick={handleSave}
            disabled={updateTemplate.isPending || !template.trim()}
            className="gap-2 ml-auto cursor-pointer"
          >
            <CheckIcon size={18} />
            {updateTemplate.isPending ? "Saving..." : "Save Template"}
          </Button>
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowPreview(false)}
        >
          <div
            className="bg-card border border-border rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-4 border-b border-border">
              <h3 className="text-lg font-semibold text-foreground">
                Email Preview
              </h3>
              <button
                onClick={() => setShowPreview(false)}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 overflow-auto p-4 bg-muted">
              <div
                className="bg-white rounded-lg shadow-lg"
                dangerouslySetInnerHTML={{ __html: previewHtml }}
              />
            </div>
            <div className="p-4 border-t border-border flex justify-end">
              <Button
                onClick={() => setShowPreview(false)}
                variant="outline"
                className="cursor-pointer"
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
