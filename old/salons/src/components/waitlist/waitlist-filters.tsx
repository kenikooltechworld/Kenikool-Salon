'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { WaitlistFilters } from '@/lib/api/hooks/useWaitlist';

interface WaitlistFiltersProps {
  onFiltersChange: (filters: WaitlistFilters) => void;
  onReset: () => void;
}

export const WaitlistFiltersComponent: React.FC<WaitlistFiltersProps> = ({ onFiltersChange, onReset }) => {
  const [status, setStatus] = useState<string>('');
  const [serviceId, setServiceId] = useState<string>('');
  const [stylistId, setStylistId] = useState<string>('');
  const [locationId, setLocationId] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [sortBy, setSortBy] = useState<'priority' | 'created_at' | 'updated_at'>('priority');

  const handleApplyFilters = () => {
    const filters: WaitlistFilters = {
      sort_by: sortBy,
      limit: 100,
      offset: 0,
    };

    if (status) filters.status = status;
    if (serviceId) filters.service_id = serviceId;
    if (stylistId) filters.stylist_id = stylistId;
    if (locationId) filters.location_id = locationId;
    if (searchQuery) filters.search_query = searchQuery;
    if (dateFrom) filters.date_from = dateFrom;
    if (dateTo) filters.date_to = dateTo;

    onFiltersChange(filters);
  };

  const handleReset = () => {
    setStatus('');
    setServiceId('');
    setStylistId('');
    setLocationId('');
    setSearchQuery('');
    setDateFrom('');
    setDateTo('');
    setSortBy('priority');
    onReset();
  };

  return (
    <Card className="p-6 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium mb-2">Status</label>
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger>
              <SelectValue placeholder="All statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All statuses</SelectItem>
              <SelectItem value="waiting">Waiting</SelectItem>
              <SelectItem value="notified">Notified</SelectItem>
              <SelectItem value="booked">Booked</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
              <SelectItem value="expired">Expired</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Service Filter */}
        <div>
          <label className="block text-sm font-medium mb-2">Service</label>
          <Input
            placeholder="Service ID"
            value={serviceId}
            onChange={(e) => setServiceId(e.target.value)}
          />
        </div>

        {/* Stylist Filter */}
        <div>
          <label className="block text-sm font-medium mb-2">Stylist</label>
          <Input
            placeholder="Stylist ID"
            value={stylistId}
            onChange={(e) => setStylistId(e.target.value)}
          />
        </div>

        {/* Location Filter */}
        <div>
          <label className="block text-sm font-medium mb-2">Location</label>
          <Input
            placeholder="Location ID"
            value={locationId}
            onChange={(e) => setLocationId(e.target.value)}
          />
        </div>

        {/* Search Query */}
        <div>
          <label className="block text-sm font-medium mb-2">Search</label>
          <Input
            placeholder="Client name or phone"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Date From */}
        <div>
          <label className="block text-sm font-medium mb-2">From Date</label>
          <Input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
          />
        </div>

        {/* Date To */}
        <div>
          <label className="block text-sm font-medium mb-2">To Date</label>
          <Input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
          />
        </div>

        {/* Sort By */}
        <div>
          <label className="block text-sm font-medium mb-2">Sort By</label>
          <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="priority">Priority</SelectItem>
              <SelectItem value="created_at">Created Date</SelectItem>
              <SelectItem value="updated_at">Updated Date</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <Button onClick={handleApplyFilters} className="bg-blue-600 hover:bg-blue-700">
          Apply Filters
        </Button>
        <Button onClick={handleReset} variant="outline">
          Reset
        </Button>
      </div>
    </Card>
  );
};
