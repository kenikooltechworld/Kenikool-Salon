import React, { useState, useEffect } from 'react';

interface Template {
  id: string;
  name: string;
  description: string;
  metrics: string[];
  filters: any[];
  widgets: any[];
  granularity: string;
  isShared: boolean;
  sharedWith: string[];
  createdAt: string;
  createdBy: string;
}

interface ReportTemplatesProps {
  onLoadTemplate?: (template: Template) => void;
  onSaveTemplate?: (template: Omit<Template, 'id' | 'createdAt' | 'createdBy'>) => void;
  currentReport?: {
    name: string;
    metrics: string[];
    filters: any[];
    widgets: any[];
    granularity: string;
  };
}

export const ReportTemplates: React.FC<ReportTemplatesProps> = ({
  onLoadTemplate,
  onSaveTemplate,
  currentReport,
}) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [templateName, setTemplateName] = useState('');
  const [templateDescription, setTemplateDescription] = useState('');
  const [shareWith, setShareWith] = useState<string[]>([]);
  const [shareEmail, setShareEmail] = useState('');
  const [activeTab, setActiveTab] = useState<'my' | 'shared'>('my');

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = () => {
    try {
      const stored = localStorage.getItem('report_templates');
      if (stored) {
        setTemplates(JSON.parse(stored));
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    }
  };

  const saveTemplate = () => {
    if (!templateName.trim() || !currentReport) {
      alert('Please enter a template name');
      return;
    }

    const newTemplate: Template = {
      id: `template_${Date.now()}`,
      name: templateName,
      description: templateDescription,
      metrics: currentReport.metrics,
      filters: currentReport.filters,
      widgets: currentReport.widgets,
      granularity: currentReport.granularity,
      isShared: shareWith.length > 0,
      sharedWith: shareWith,
      createdAt: new Date().toISOString(),
      createdBy: 'current_user', // In real app, get from auth context
    };

    const updatedTemplates = [...templates, newTemplate];
    setTemplates(updatedTemplates);
    localStorage.setItem('report_templates', JSON.stringify(updatedTemplates));

    onSaveTemplate?.(newTemplate);

    setTemplateName('');
    setTemplateDescription('');
    setShareWith([]);
    setShareEmail('');
    setShowSaveForm(false);
  };

  const loadTemplate = (template: Template) => {
    onLoadTemplate?.(template);
  };

  const deleteTemplate = (templateId: string) => {
    const updatedTemplates = templates.filter((t) => t.id !== templateId);
    setTemplates(updatedTemplates);
    localStorage.setItem('report_templates', JSON.stringify(updatedTemplates));
  };

  const addShareEmail = () => {
    if (shareEmail && !shareWith.includes(shareEmail)) {
      setShareWith([...shareWith, shareEmail]);
      setShareEmail('');
    }
  };

  const removeShareEmail = (email: string) => {
    setShareWith(shareWith.filter((e) => e !== email));
  };

  const duplicateTemplate = (template: Template) => {
    const newTemplate: Template = {
      ...template,
      id: `template_${Date.now()}`,
      name: `${template.name} (Copy)`,
      createdAt: new Date().toISOString(),
    };

    const updatedTemplates = [...templates, newTemplate];
    setTemplates(updatedTemplates);
    localStorage.setItem('report_templates', JSON.stringify(updatedTemplates));
  };

  const myTemplates = templates.filter((t) => t.createdBy === 'current_user');
  const sharedTemplates = templates.filter((t) => t.isShared && t.createdBy !== 'current_user');

  const displayTemplates = activeTab === 'my' ? myTemplates : sharedTemplates;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Report Templates</h3>
        {currentReport && (
          <button
            onClick={() => setShowSaveForm(!showSaveForm)}
            className="text-sm px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {showSaveForm ? 'Cancel' : 'Save as Template'}
          </button>
        )}
      </div>

      {showSaveForm && currentReport && (
        <div className="mb-6 p-4 bg-gray-50 rounded border border-gray-200 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Template Name</label>
            <input
              type="text"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              placeholder="e.g., Monthly Revenue Report"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={templateDescription}
              onChange={(e) => setTemplateDescription(e.target.value)}
              placeholder="Describe what this template is for..."
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Share With</label>
            <div className="flex gap-2 mb-2">
              <input
                type="email"
                value={shareEmail}
                onChange={(e) => setShareEmail(e.target.value)}
                placeholder="Enter email to share"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={addShareEmail}
                className="px-3 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
              >
                Add
              </button>
            </div>
            {shareWith.length > 0 && (
              <div className="space-y-1">
                {shareWith.map((email) => (
                  <div
                    key={email}
                    className="flex items-center justify-between bg-white p-2 rounded border border-gray-200"
                  >
                    <span className="text-sm text-gray-700">{email}</span>
                    <button
                      onClick={() => removeShareEmail(email)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={saveTemplate}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Save Template
          </button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-4 border-b">
        <button
          onClick={() => setActiveTab('my')}
          className={`px-4 py-2 font-medium text-sm ${
            activeTab === 'my'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          My Templates ({myTemplates.length})
        </button>
        <button
          onClick={() => setActiveTab('shared')}
          className={`px-4 py-2 font-medium text-sm ${
            activeTab === 'shared'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Shared with Me ({sharedTemplates.length})
        </button>
      </div>

      {/* Templates List */}
      {displayTemplates.length > 0 ? (
        <div className="space-y-2">
          {displayTemplates.map((template) => (
            <div
              key={template.id}
              className="flex items-start justify-between p-3 bg-gray-50 rounded border border-gray-200 hover:bg-gray-100"
            >
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{template.name}</h4>
                {template.description && (
                  <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                )}
                <div className="flex gap-2 mt-2">
                  {template.metrics.slice(0, 3).map((metric, idx) => (
                    <span
                      key={idx}
                      className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded"
                    >
                      {metric}
                    </span>
                  ))}
                  {template.metrics.length > 3 && (
                    <span className="text-xs text-gray-600">
                      +{template.metrics.length - 3} more
                    </span>
                  )}
                </div>
                {template.isShared && (
                  <p className="text-xs text-gray-500 mt-1">
                    Shared with {template.sharedWith.length} user(s)
                  </p>
                )}
              </div>
              <div className="flex gap-1 ml-2">
                <button
                  onClick={() => loadTemplate(template)}
                  className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Load
                </button>
                {activeTab === 'my' && (
                  <>
                    <button
                      onClick={() => duplicateTemplate(template)}
                      className="text-xs px-2 py-1 bg-gray-600 text-white rounded hover:bg-gray-700"
                    >
                      Copy
                    </button>
                    <button
                      onClick={() => deleteTemplate(template.id)}
                      className="text-xs px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Delete
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-center py-6 text-gray-500">
          {activeTab === 'my'
            ? 'No templates saved yet. Create a report and save it as a template!'
            : 'No templates shared with you yet.'}
        </p>
      )}
    </div>
  );
};
