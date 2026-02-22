'use client';

import React, { useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { WaitlistEntry, useBulkUpdateWaitlist, useBulkDeleteWaitlist, useBulkNotifyWaitlist } from '@/lib/api/hooks/useWaitlist';
import { format } from 'date-fns';

interface WaitlistAdminListProps {
  entries: WaitlistEntry[];
  isLoading: boolean;
  onCreateBooking: (entry: WaitlistEntry) => void;
}

const statusColors: Record<string, string> = {
  waiting: 'bg-yellow-100 text-yellow-800',
  notified: 'bg-blue-100 text-blue-800',
  booked: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
  expired: 'bg-gray-100 text-gray-800',
};

export const WaitlistAdminList: React.FC<WaitlistAdminListProps> = ({
  entries,
  isLoading,
  onCreateBooking,
}) => {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const bulkUpdateMutation = useBulkUpdateWaitlist();
  const bulkDeleteMutation = useBulkDeleteWaitlist();
  const bulkNotifyMutation = useBulkNotifyWaitlist();

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedIds(new Set(entries.map((e) => e.id)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleSelectEntry = (id: string, checked: boolean) => {
    const newSelected = new Set(selectedIds);
    if (checked) {
      newSelected.add(id);
    } else {
      newSelected.delete(id);
    }
    setSelectedIds(newSelected);
  };

  const handleBulkStatusUpdate = (status: string) => {
    if (selectedIds.size === 0) return;
    bulkUpdateMutation.mutate({
      waitlist_ids: Array.from(selectedIds),
      status,
    });
    setSelectedIds(new Set());
  };

  const handleBulkDelete = () => {
    if (selectedIds.size === 0) return;
    if (confirm(`Delete ${selectedIds.size} entries?`)) {
      bulkDeleteMutation.mutate(Array.from(selectedIds));
      setSelectedIds(new Set());
    }
  };

  const handleBulkNotify = (templateId?: string) => {
    if (selectedIds.size === 0) return;
    bulkNotifyMutation.mutate({
      waitlist_ids: Array.from(selectedIds),
      template_id: templateId,
    });
    setSelectedIds(new Set());
  };

  const handleExportCSV = () => {
    const headers = ['Name', 'Phone', 'Email', 'Service', 'Status', 'Priority', 'Created'];
    const rows = entries.map((e) => [
      e.client_name,
      e.client_phone,
      e.client_email || '',
      e.service_name,
      e.status,
      e.priority_score.toFixed(2),
      format(new Date(e.created_at), 'yyyy-MM-dd HH:mm'),
    ]);

    const csv = [headers, ...rows].map((row) => row.map((cell) => `"${cell}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `waitlist-${format(new Date(), 'yyyy-MM-dd')}.csv`;
    a.click();
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="space-y-4">
      {/* Bulk Action Toolbar */}
      {selectedIds.size > 0 && (
        <Card className="p-4 bg-blue-50">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">{selectedIds.size} selected</span>
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={() => handleBulkStatusUpdate('notified')}
                disabled={bulkUpdateMutation.isPending}
              >
                Mark Notified
              </Button>
              <Button
                size="sm"
                onClick={() => handleBulkStatusUpdate('booked')}
                disabled={bulkUpdateMutation.isPending}
              >
                Mark Booked
              </Button>
              <Button
                size="sm"
                onClick={() => handleBulkNotify()}
                disabled={bulkNotifyMutation.isPending}
              >
                Send Notification
              </Button>
              <Button
                size="sm"
                variant="destructive"
                onClick={handleBulkDelete}
                disabled={bulkDeleteMutation.isPending}
              >
                Delete
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Export Button */}
      <div className="flex justify-end">
        <Button onClick={handleExportCSV} variant="outline" size="sm">
          Export to CSV
        </Button>
      </div>

      {/* Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">
                <Checkbox
                  checked={selectedIds.size === entries.length && entries.length > 0}
                  onCheckedChange={handleSelectAll}
                />
              </TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Phone</TableHead>
              <TableHead>Service</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {entries.map((entry) => (
              <TableRow key={entry.id}>
                <TableCell>
                  <Checkbox
                    checked={selectedIds.has(entry.id)}
                    onCheckedChange={(checked) => handleSelectEntry(entry.id, checked as boolean)}
                  />
                </TableCell>
                <TableCell className="font-medium">{entry.client_name}</TableCell>
                <TableCell>{entry.client_phone}</TableCell>
                <TableCell>{entry.service_name}</TableCell>
                <TableCell>
                  <Badge className={statusColors[entry.status]}>
                    {entry.status}
                  </Badge>
                </TableCell>
                <TableCell>{entry.priority_score.toFixed(2)}</TableCell>
                <TableCell>{format(new Date(entry.created_at), 'MMM dd, yyyy')}</TableCell>
                <TableCell>
                  <Button
                    size="sm"
                    onClick={() => onCreateBooking(entry)}
                    disabled={entry.status !== 'waiting' && entry.status !== 'notified'}
                  >
                    Create Booking
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {entries.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No waitlist entries found
        </div>
      )}
    </div>
  );
};
