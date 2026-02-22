'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { AlertCircle, CheckCircle2, Trash2 } from 'lucide-react';

interface Alert {
  id: string;
  type: string;
  title: string;
  message: string;
  severity: string;
  status: string;
  created_at: string;
  product_id: string;
}

interface AlertsListProps {
  productId?: string;
  alertType?: string;
  status?: string;
}

export function AlertsList({
  productId,
  alertType,
  status,
}: AlertsListProps) {
  const queryClient = useQueryClient();

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts', productId, alertType, status],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (productId) params.append('product_id', productId);
      if (alertType) params.append('alert_type', alertType);
      if (status) params.append('status', status);

      const res = await fetch(`/api/inventory/alerts?${params}`);
      if (!res.ok) throw new Error('Failed to fetch alerts');
      return res.json();
    },
  });

  const dismissMutation = useMutation({
    mutationFn: async (alertId: string) => {
      const res = await fetch(`/api/inventory/alerts/${alertId}/dismiss`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: 'Dismissed by user' }),
      });
      if (!res.ok) throw new Error('Failed to dismiss alert');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      toast.success('Alert dismissed');
    },
    onError: () => {
      toast.error('Failed to dismiss alert');
    },
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const getStatusIcon = (status: string) => {
    return status === 'sent' ? (
      <CheckCircle2 className="w-4 h-4 text-green-600" />
    ) : (
      <AlertCircle className="w-4 h-4 text-yellow-600" />
    );
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading alerts...</div>;
  }

  const alertList = alerts?.data || [];

  if (alertList.length === 0) {
    return <div className="text-center py-8 text-gray-500">No alerts</div>;
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Title</TableHead>
            <TableHead>Message</TableHead>
            <TableHead>Severity</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Created</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {alertList.map((alert: Alert) => (
            <TableRow key={alert.id}>
              <TableCell className="font-medium">{alert.title}</TableCell>
              <TableCell className="text-sm text-gray-600">
                {alert.message}
              </TableCell>
              <TableCell>
                <Badge className={getSeverityColor(alert.severity)}>
                  {alert.severity}
                </Badge>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  {getStatusIcon(alert.status)}
                  <span className="capitalize text-sm">{alert.status}</span>
                </div>
              </TableCell>
              <TableCell className="text-sm">
                {format(new Date(alert.created_at), 'MMM dd, HH:mm')}
              </TableCell>
              <TableCell>
                {alert.status !== 'dismissed' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => dismissMutation.mutate(alert.id)}
                    disabled={dismissMutation.isPending}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
