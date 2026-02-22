import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Loader2, Plus, Trash2, Search } from 'lucide-react';

interface OptOutPreference {
  client_id: string;
  channels: {
    sms: boolean;
    whatsapp: boolean;
    email: boolean;
  };
  reason?: string;
  opted_out_at: string;
}

interface OptOutListProps {
  onAddOptOut?: () => void;
  onRemoveOptOut?: (clientId: string) => Promise<void>;
}

export const OptOutList: React.FC<OptOutListProps> = ({
  onAddOptOut,
  onRemoveOptOut,
}) => {
  const [optOuts, setOptOuts] = useState<OptOutPreference[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [removing, setRemoving] = useState<string | null>(null);

  useEffect(() => {
    fetchOptOuts();
  }, []);

  const fetchOptOuts = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/opt-outs');
      if (!response.ok) throw new Error('Failed to fetch opt-outs');
      const data = await response.json();
      setOptOuts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load opt-outs');
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (clientId: string) => {
    if (!onRemoveOptOut) return;
    try {
      setRemoving(clientId);
      await onRemoveOptOut(clientId);
      setOptOuts(prev => prev.filter(o => o.client_id !== clientId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove opt-out');
    } finally {
      setRemoving(null);
    }
  };

  const filteredOptOuts = optOuts.filter(opt =>
    opt.client_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getOptedOutChannels = (channels: OptOutPreference['channels']) => {
    return Object.entries(channels)
      .filter(([_, opted]) => opted)
      .map(([channel]) => channel.toUpperCase());
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Opt-Out Management</CardTitle>
              <CardDescription>
                Manage clients who have opted out of communications
              </CardDescription>
            </div>
            {onAddOptOut && (
              <Button onClick={onAddOptOut} size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Add Opt-Out
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          )}

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search by client ID..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Total Opt-Outs</p>
              <p className="text-2xl font-bold">{optOuts.length}</p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">SMS Opt-Outs</p>
              <p className="text-2xl font-bold">
                {optOuts.filter(o => o.channels.sms).length}
              </p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">Email Opt-Outs</p>
              <p className="text-2xl font-bold">
                {optOuts.filter(o => o.channels.email).length}
              </p>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Client ID</TableHead>
                  <TableHead>Opted Out Channels</TableHead>
                  <TableHead>Reason</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredOptOuts.length > 0 ? (
                  filteredOptOuts.map(optOut => (
                    <TableRow key={optOut.client_id}>
                      <TableCell className="font-medium">{optOut.client_id}</TableCell>
                      <TableCell>
                        <div className="flex gap-1 flex-wrap">
                          {getOptedOutChannels(optOut.channels).map(channel => (
                            <Badge key={channel} variant="secondary">
                              {channel}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell className="text-sm text-gray-600">
                        {optOut.reason || '-'}
                      </TableCell>
                      <TableCell className="text-sm">
                        {new Date(optOut.opted_out_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        {onRemoveOptOut && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleRemove(optOut.client_id)}
                            disabled={removing === optOut.client_id}
                          >
                            {removing === optOut.client_id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Trash2 className="h-4 w-4" />
                            )}
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-gray-500 py-8">
                      {searchTerm ? 'No opt-outs found' : 'No clients have opted out'}
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
