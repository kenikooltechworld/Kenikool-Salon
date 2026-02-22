import { useState } from 'react';
import { useExportAnalytics } from '@/lib/api/hooks/useAnalytics';
import { ReportBuilder } from '@/components/analytics/ReportBuilder';
import { ReportTemplates } from '@/components/analytics/ReportTemplates';
import { ReportScheduler } from '@/components/analytics/ReportScheduler';

interface CurrentReport {
  name: string;
  metrics: string[];
  filters: any[];
  widgets: any[];
  granularity: string;
}

export default function ReportsPage() {
  const [exportFormat, setExportFormat] = useState<'csv' | 'json' | 'excel' | 'pdf'>('csv');
  const [currentReport, setCurrentReport] = useState<CurrentReport | undefined>();
  const [currentReportId, setCurrentReportId] = useState<string | undefined>();
  const exportMutation = useExportAnalytics();

  const handleExport = async () => {
    exportMutation.mutate({
      format: exportFormat,
      filters: [],
      date_range: {
        start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        end: new Date(),
      },
    });
  };

  const handleLoadTemplate = (template: any) => {
    setCurrentReport({
      name: template.name,
      metrics: template.metrics,
      filters: template.filters,
      widgets: template.widgets,
      granularity: template.granularity,
    });
  };

  const handleReportCreated = (reportId: string) => {
    setCurrentReportId(reportId);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Reports & Exports</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <ReportBuilder onReportCreated={handleReportCreated} />
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Export Data</h2>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Format</label>
                <select
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="csv">CSV</option>
                  <option value="json">JSON</option>
                  <option value="excel">Excel</option>
                  <option value="pdf">PDF</option>
                </select>
              </div>
              <button
                onClick={handleExport}
                disabled={exportMutation.isPending}
                className="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700 disabled:bg-gray-400"
              >
                {exportMutation.isPending ? 'Exporting...' : 'Export'}
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div>
            <ReportTemplates
              currentReport={currentReport}
              onLoadTemplate={handleLoadTemplate}
            />
          </div>
          <div>
            <ReportScheduler
              reportId={currentReportId}
              reportName={currentReport?.name}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
