import React, { useState, useRef } from 'react';
import { useCreateCustomReport, useScheduleReport } from '@/lib/api/hooks/useAnalytics';
import { FilterBuilder } from './FilterBuilder';
import { FilterPresets } from './FilterPresets';

interface Filter {
  id: string;
  field: string;
  operator: string;
  value: string | number | boolean;
}

interface Widget {
  id: string;
  type: 'chart' | 'metric' | 'table' | 'text';
  title: string;
  config: Record<string, any>;
  position: { x: number; y: number };
  size: { width: number; height: number };
}

interface ReportBuilderProps {
  onReportCreated?: (reportId: string) => void;
}

export const ReportBuilder: React.FC<ReportBuilderProps> = ({ onReportCreated }) => {
  const [reportName, setReportName] = useState('');
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [granularity, setGranularity] = useState('daily');
  const [schedule, setSchedule] = useState('');
  const [recipients, setRecipients] = useState<string[]>([]);
  const [recipientEmail, setRecipientEmail] = useState('');
  const [enableScheduling, setEnableScheduling] = useState(false);
  const [filters, setFilters] = useState<Filter[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [showWidgetLibrary, setShowWidgetLibrary] = useState(false);
  const [draggedWidget, setDraggedWidget] = useState<Widget | null>(null);
  const [selectedWidget, setSelectedWidget] = useState<string | null>(null);
  const canvasRef = useRef<HTMLDivElement>(null);
  const createReport = useCreateCustomReport();
  const scheduleReport = useScheduleReport();

  const availableMetrics = [
    { id: 'revenue', label: 'Revenue' },
    { id: 'bookings', label: 'Bookings' },
    { id: 'clients', label: 'Clients' },
    { id: 'inventory', label: 'Inventory' },
    { id: 'staff', label: 'Staff Utilization' },
  ];

  const widgetLibrary = [
    { type: 'chart', title: 'Line Chart', icon: '📈' },
    { type: 'chart', title: 'Bar Chart', icon: '📊' },
    { type: 'chart', title: 'Pie Chart', icon: '🥧' },
    { type: 'metric', title: 'KPI Card', icon: '📌' },
    { type: 'table', title: 'Data Table', icon: '📋' },
    { type: 'text', title: 'Text Block', icon: '📝' },
  ];

  const toggleMetric = (metricId: string) => {
    setSelectedMetrics((prev) =>
      prev.includes(metricId) ? prev.filter((m) => m !== metricId) : [...prev, metricId]
    );
  };

  const addWidget = (widgetType: string, title: string) => {
    const newWidget: Widget = {
      id: `widget_${Date.now()}`,
      type: widgetType as any,
      title,
      config: {},
      position: { x: 0, y: widgets.length * 100 },
      size: { width: 300, height: 200 },
    };
    setWidgets([...widgets, newWidget]);
    setShowWidgetLibrary(false);
  };

  const removeWidget = (widgetId: string) => {
    setWidgets(widgets.filter((w) => w.id !== widgetId));
    if (selectedWidget === widgetId) {
      setSelectedWidget(null);
    }
  };

  const updateWidgetSize = (widgetId: string, width: number, height: number) => {
    setWidgets(
      widgets.map((w) =>
        w.id === widgetId ? { ...w, size: { width, height } } : w
      )
    );
  };

  const handleDragStart = (e: React.DragEvent, widget: Widget) => {
    setDraggedWidget(widget);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (draggedWidget && canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      setWidgets(
        widgets.map((w) =>
          w.id === draggedWidget.id ? { ...w, position: { x, y } } : w
        )
      );
    }
    setDraggedWidget(null);
  };

  const addRecipient = () => {
    if (recipientEmail && !recipients.includes(recipientEmail)) {
      setRecipients([...recipients, recipientEmail]);
      setRecipientEmail('');
    }
  };

  const removeRecipient = (email: string) => {
    setRecipients(recipients.filter((r) => r !== email));
  };

  const handleCreateReport = async () => {
    if (!reportName || selectedMetrics.length === 0) {
      alert('Please enter a report name and select at least one metric');
      return;
    }

    if (enableScheduling && (!schedule || recipients.length === 0)) {
      alert('Please select a schedule and add at least one recipient');
      return;
    }

    const reportData = {
      name: reportName,
      metrics: selectedMetrics,
      filters: filters,
      widgets: widgets,
      date_range: {
        start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        end: new Date().toISOString(),
      },
      granularity: granularity,
    };

    createReport.mutate(reportData, {
      onSuccess: (data) => {
        if (enableScheduling && data.report_id) {
          scheduleReport.mutate(
            {
              reportId: data.report_id,
              schedule: schedule,
              recipients: recipients,
            },
            {
              onSuccess: () => {
                setReportName('');
                setSelectedMetrics([]);
                setSchedule('');
                setRecipients([]);
                setRecipientEmail('');
                setEnableScheduling(false);
                setFilters([]);
                setShowFilters(false);
                setWidgets([]);
                if (onReportCreated) {
                  onReportCreated(data.report_id);
                }
              },
            }
          );
        } else {
          setReportName('');
          setSelectedMetrics([]);
          setSchedule('');
          setRecipients([]);
          setRecipientEmail('');
          setEnableScheduling(false);
          setFilters([]);
          setShowFilters(false);
          setWidgets([]);
          if (onReportCreated && data.report_id) {
            onReportCreated(data.report_id);
          }
        }
      },
    });
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Create Custom Report</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Report Name</label>
          <input
            type="text"
            value={reportName}
            onChange={(e) => setReportName(e.target.value)}
            placeholder="e.g., Monthly Revenue Report"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Metrics</label>
          <div className="grid grid-cols-2 gap-2">
            {availableMetrics.map((metric) => (
              <label key={metric.id} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedMetrics.includes(metric.id)}
                  onChange={() => toggleMetric(metric.id)}
                  className="rounded border-gray-300"
                />
                <span className="ml-2 text-sm text-gray-700">{metric.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Granularity</label>
          <select
            value={granularity}
            onChange={(e) => setGranularity(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="hourly">Hourly</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>

        {/* Widget Library and Canvas */}
        <div className="border-t pt-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-gray-900">Report Layout</h3>
            <button
              onClick={() => setShowWidgetLibrary(!showWidgetLibrary)}
              className="text-sm px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              {showWidgetLibrary ? 'Hide' : 'Add Widget'}
            </button>
          </div>

          {showWidgetLibrary && (
            <div className="mb-4 p-3 bg-gray-50 rounded border border-gray-200">
              <p className="text-xs text-gray-600 mb-2">Click to add widget to report</p>
              <div className="grid grid-cols-3 gap-2">
                {widgetLibrary.map((widget, idx) => (
                  <button
                    key={idx}
                    onClick={() => addWidget(widget.type, widget.title)}
                    className="p-2 bg-white border border-gray-300 rounded hover:bg-gray-50 text-center"
                  >
                    <div className="text-lg mb-1">{widget.icon}</div>
                    <div className="text-xs text-gray-700">{widget.title}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Canvas */}
          <div
            ref={canvasRef}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className="relative w-full h-96 bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg overflow-auto"
          >
            {widgets.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-400">
                <p className="text-sm">Drag widgets here or click "Add Widget"</p>
              </div>
            ) : (
              widgets.map((widget) => (
                <div
                  key={widget.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, widget)}
                  onClick={() => setSelectedWidget(widget.id)}
                  className={`absolute p-3 bg-white border-2 rounded cursor-move transition-all ${
                    selectedWidget === widget.id
                      ? 'border-blue-500 shadow-lg'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  style={{
                    left: `${widget.position.x}px`,
                    top: `${widget.position.y}px`,
                    width: `${widget.size.width}px`,
                    height: `${widget.size.height}px`,
                  }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-gray-700">{widget.title}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        removeWidget(widget.id);
                      }}
                      className="text-red-600 hover:text-red-800 text-xs"
                    >
                      ✕
                    </button>
                  </div>
                  {selectedWidget === widget.id && (
                    <div className="text-xs text-gray-500 space-y-1">
                      <div>
                        <label className="block">Width:</label>
                        <input
                          type="number"
                          value={widget.size.width}
                          onChange={(e) =>
                            updateWidgetSize(widget.id, parseInt(e.target.value), widget.size.height)
                          }
                          className="w-full px-1 py-0.5 border border-gray-300 rounded text-xs"
                        />
                      </div>
                      <div>
                        <label className="block">Height:</label>
                        <input
                          type="number"
                          value={widget.size.height}
                          onChange={(e) =>
                            updateWidgetSize(widget.id, widget.size.width, parseInt(e.target.value))
                          }
                          className="w-full px-1 py-0.5 border border-gray-300 rounded text-xs"
                        />
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        <div className="border-t pt-4">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="text-sm font-medium text-blue-600 hover:text-blue-800"
          >
            {showFilters ? '▼ Hide Filters' : '▶ Show Filters'}
          </button>
        </div>

        {showFilters && (
          <div className="space-y-4 bg-gray-50 p-4 rounded-md">
            <FilterBuilder
              onFiltersChange={setFilters}
              onApply={(appliedFilters) => {
                setFilters(appliedFilters);
              }}
            />
            <FilterPresets
              currentFilters={filters}
              onLoadPreset={(loadedFilters) => {
                setFilters(loadedFilters);
              }}
            />
          </div>
        )}

        <div className="border-t pt-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={enableScheduling}
              onChange={(e) => setEnableScheduling(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="ml-2 text-sm font-medium text-gray-700">Enable Scheduling</span>
          </label>
        </div>

        {enableScheduling && (
          <div className="space-y-4 bg-gray-50 p-4 rounded-md">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Schedule</label>
              <select
                value={schedule}
                onChange={(e) => setSchedule(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select schedule...</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Recipients</label>
              <div className="flex gap-2 mb-2">
                <input
                  type="email"
                  value={recipientEmail}
                  onChange={(e) => setRecipientEmail(e.target.value)}
                  placeholder="Enter email address"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={addRecipient}
                  className="px-3 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Add
                </button>
              </div>
              {recipients.length > 0 && (
                <div className="space-y-1">
                  {recipients.map((email) => (
                    <div key={email} className="flex items-center justify-between bg-white p-2 rounded border border-gray-200">
                      <span className="text-sm text-gray-700">{email}</span>
                      <button
                        onClick={() => removeRecipient(email)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        <button
          onClick={handleCreateReport}
          disabled={createReport.isPending || scheduleReport.isPending}
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {createReport.isPending || scheduleReport.isPending ? 'Creating...' : 'Create Report'}
        </button>

        {(createReport.isError || scheduleReport.isError) && (
          <div className="text-red-600 text-sm">Error creating report</div>
        )}
        {createReport.isSuccess && !enableScheduling && (
          <div className="text-green-600 text-sm">Report created successfully!</div>
        )}
        {scheduleReport.isSuccess && (
          <div className="text-green-600 text-sm">Report created and scheduled successfully!</div>
        )}
      </div>
    </div>
  );
};
