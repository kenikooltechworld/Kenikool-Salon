import React, { useState, useEffect } from 'react';

interface ScheduledReport {
  id: string;
  reportId: string;
  reportName: string;
  schedule: 'daily' | 'weekly' | 'monthly';
  recipients: string[];
  format: 'pdf' | 'excel' | 'csv';
  status: 'active' | 'paused' | 'completed';
  nextRun: string;
  lastRun?: string;
  createdAt: string;
}

interface ReportSchedulerProps {
  reportId?: string;
  reportName?: string;
  onScheduleCreated?: (schedule: ScheduledReport) => void;
}

export const ReportScheduler: React.FC<ReportSchedulerProps> = ({
  reportId,
  reportName,
  onScheduleCreated,
}) => {
  const [schedules, setSchedules] = useState<ScheduledReport[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [schedule, setSchedule] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [format, setFormat] = useState<'pdf' | 'excel' | 'csv'>('pdf');
  const [recipients, setRecipients] = useState<string[]>([]);
  const [recipientEmail, setRecipientEmail] = useState('');

  useEffect(() => {
    loadSchedules();
  }, []);

  const loadSchedules = () => {
    try {
      const stored = localStorage.getItem('scheduled_reports');
      if (stored) {
        setSchedules(JSON.parse(stored));
      }
    } catch (error) {
      console.error('Error loading schedules:', error);
    }
  };

  const calculateNextRun = (scheduleType: string): string => {
    let nextRun = new Date();

    if (scheduleType === 'daily') {
      nextRun.setDate(nextRun.getDate() + 1);
      nextRun.setHours(9, 0, 0, 0);
    } else if (scheduleType === 'weekly') {
      nextRun.setDate(nextRun.getDate() + 7);
      nextRun.setHours(9, 0, 0, 0);
    } else if (scheduleType === 'monthly') {
      nextRun.setMonth(nextRun.getMonth() + 1);
      nextRun.setDate(1);
      nextRun.setHours(9, 0, 0, 0);
    }

    return nextRun.toISOString();
  };

  const createSchedule = () => {
    if (!reportId || !reportName || recipients.length === 0) {
      alert('Please select a report and add at least one recipient');
      return;
    }

    const newSchedule: ScheduledReport = {
      id: `schedule_${Date.now()}`,
      reportId,
      reportName,
      schedule,
      recipients,
      format,
      status: 'active',
      nextRun: calculateNextRun(schedule),
      createdAt: new Date().toISOString(),
    };

    const updatedSchedules = [...schedules, newSchedule];
    setSchedules(updatedSchedules);
    localStorage.setItem('scheduled_reports', JSON.stringify(updatedSchedules));

    onScheduleCreated?.(newSchedule);

    setRecipients([]);
    setRecipientEmail('');
    setShowForm(false);
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

  const pauseSchedule = (scheduleId: string) => {
    const updatedSchedules = schedules.map((s) =>
      s.id === scheduleId ? { ...s, status: 'paused' as const } : s
    );
    setSchedules(updatedSchedules);
    localStorage.setItem('scheduled_reports', JSON.stringify(updatedSchedules));
  };

  const resumeSchedule = (scheduleId: string) => {
    const updatedSchedules = schedules.map((s) =>
      s.id === scheduleId ? { ...s, status: 'active' as const } : s
    );
    setSchedules(updatedSchedules);
    localStorage.setItem('scheduled_reports', JSON.stringify(updatedSchedules));
  };

  const deleteSchedule = (scheduleId: string) => {
    const updatedSchedules = schedules.filter((s) => s.id !== scheduleId);
    setSchedules(updatedSchedules);
    localStorage.setItem('scheduled_reports', JSON.stringify(updatedSchedules));
  };

  const getScheduleLabel = (scheduleType: string): string => {
    switch (scheduleType) {
      case 'daily':
        return 'Every day at 9:00 AM';
      case 'weekly':
        return 'Every Monday at 9:00 AM';
      case 'monthly':
        return 'First day of month at 9:00 AM';
      default:
        return scheduleType;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Report Scheduling</h3>
        {reportId && (
          <button
            onClick={() => setShowForm(!showForm)}
            className="text-sm px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {showForm ? 'Cancel' : 'Schedule Report'}
          </button>
        )}
      </div>

      {showForm && reportId && (
        <div className="mb-6 p-4 bg-gray-50 rounded border border-gray-200 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Schedule</label>
            <select
              value={schedule}
              onChange={(e) => setSchedule(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">{getScheduleLabel(schedule)}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Format</label>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="pdf">PDF</option>
              <option value="excel">Excel</option>
              <option value="csv">CSV</option>
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
                  <div
                    key={email}
                    className="flex items-center justify-between bg-white p-2 rounded border border-gray-200"
                  >
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

          <button
            onClick={createSchedule}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Create Schedule
          </button>
        </div>
      )}

      {/* Scheduled Reports List */}
      {schedules.length > 0 ? (
        <div className="space-y-2">
          {schedules.map((sched) => (
            <div
              key={sched.id}
              className="flex items-start justify-between p-3 bg-gray-50 rounded border border-gray-200 hover:bg-gray-100"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-gray-900">{sched.reportName}</h4>
                  <span
                    className={`text-xs px-2 py-1 rounded font-medium ${
                      sched.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : sched.status === 'paused'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {sched.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {getScheduleLabel(sched.schedule)} • Format: {sched.format.toUpperCase()}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Recipients: {sched.recipients.join(', ')}
                </p>
                <p className="text-xs text-gray-500">
                  Next run: {new Date(sched.nextRun).toLocaleString()}
                </p>
                {sched.lastRun && (
                  <p className="text-xs text-gray-500">
                    Last run: {new Date(sched.lastRun).toLocaleString()}
                  </p>
                )}
              </div>
              <div className="flex gap-1 ml-2">
                {sched.status === 'active' ? (
                  <button
                    onClick={() => pauseSchedule(sched.id)}
                    className="text-xs px-2 py-1 bg-yellow-600 text-white rounded hover:bg-yellow-700"
                  >
                    Pause
                  </button>
                ) : (
                  <button
                    onClick={() => resumeSchedule(sched.id)}
                    className="text-xs px-2 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    Resume
                  </button>
                )}
                <button
                  onClick={() => deleteSchedule(sched.id)}
                  className="text-xs px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-center py-6 text-gray-500">No scheduled reports yet</p>
      )}
    </div>
  );
};
