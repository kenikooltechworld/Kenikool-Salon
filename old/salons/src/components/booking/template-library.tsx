/**
 * TemplateLibrary Component
 * Displays available booking templates organized by category
 * Validates: Requirements 4.1
 */
import React, { useMemo } from "react";
import { BookOpen, Clock, DollarSign } from "lucide-react";

interface BookingTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  duration: number;
  pricing: number;
  usage_count: number;
}

interface TemplateLibraryProps {
  templates: BookingTemplate[];
  onTemplateSelect: (template: BookingTemplate) => void;
  loading?: boolean;
}

/**
 * Component for displaying and selecting booking templates
 */
export const TemplateLibrary: React.FC<TemplateLibraryProps> = ({
  templates,
  onTemplateSelect,
  loading = false,
}) => {
  const groupedByCategory = useMemo(() => {
    const groups: Record<string, BookingTemplate[]> = {};
    templates.forEach((template) => {
      if (!groups[template.category]) {
        groups[template.category] = [];
      }
      groups[template.category].push(template);
    });
    return groups;
  }, [templates]);

  if (templates.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center">
        <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 font-semibold text-gray-900">
          No templates available
        </h3>
        <p className="mt-1 text-sm text-gray-600">
          Create your first booking template to get started
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {Object.entries(groupedByCategory).map(
        ([category, categoryTemplates]) => (
          <div key={category}>
            <h3 className="mb-3 text-lg font-semibold text-gray-900">
              {category}
            </h3>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {categoryTemplates.map((template) => (
                <button
                  key={template.id}
                  onClick={() => onTemplateSelect(template)}
                  disabled={loading}
                  className="rounded-lg border border-gray-200 bg-white p-4 text-left transition-all hover:border-blue-300 hover:shadow-md disabled:opacity-50"
                >
                  <h4 className="font-semibold text-gray-900">
                    {template.name}
                  </h4>
                  <p className="mt-1 text-sm text-gray-600">
                    {template.description}
                  </p>

                  <div className="mt-3 space-y-2 border-t border-gray-200 pt-3 text-sm">
                    <div className="flex items-center gap-2 text-gray-600">
                      <Clock className="h-4 w-4" />
                      <span>{template.duration} minutes</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <DollarSign className="h-4 w-4" />
                      <span>${template.pricing.toFixed(2)}</span>
                    </div>
                    <div className="text-xs text-gray-500">
                      Used {template.usage_count} times
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ),
      )}
    </div>
  );
};

export default TemplateLibrary;
