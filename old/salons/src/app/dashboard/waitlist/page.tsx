'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useWaitlistEntries, useWaitlistFilters, WaitlistEntry } from '@/lib/api/hooks/useWaitlist';
import { WaitlistFiltersComponent } from '@/components/waitlist/waitlist-filters';
import { WaitlistAdminList } from '@/components/waitlist/waitlist-admin-list';
import { BookingFromWaitlistModal } from '@/components/waitlist/booking-from-waitlist-modal';
import { NotificationTemplateManager } from '@/components/waitlist/notification-template-manager';
import Link from 'next/link';

export default function WaitlistPage() {
  const { filters, updateFilter, resetFilters } = useWaitlistFilters();
  const { data: entries, isLoading } = useWaitlistEntries(filters);
  const [selectedEntry, setSelectedEntry] = useState<WaitlistEntry | null>(null);
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);
  const [showTemplateManager, setShowTemplateManager] = useState(false);

  const handleCreateBooking = (entry: WaitlistEntry) => {
    setSelectedEntry(entry);
    setIsBookingModalOpen(true);
  };

  const handleBookingSuccess = () => {
    setIsBookingModalOpen(false);
    setSelectedEntry(null);
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Waitlist Management</h1>
          <p className="text-gray-600 mt-1">Manage and track client waitlist requests</p>
        </div>
        <div className="flex gap-2">
          <Link href="/dashboard/waitlist/analytics">
            <Button variant="outline">View Analytics</Button>
          </Link>
          <Button onClick={() => setShowTemplateManager(!showTemplateManager)} variant="outline">
            {showTemplateManager ? 'Hide' : 'Manage'} Templates
          </Button>
        </div>
      </div>

      {/* Template Manager */}
      {showTemplateManager && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Notification Templates</h2>
          <NotificationTemplateManager />
        </Card>
      )}

      {/* Filters */}
      <WaitlistFiltersComponent
        onFiltersChange={(newFilters) => {
          Object.entries(newFilters).forEach(([key, value]) => {
            updateFilter(key as any, value);
          });
        }}
        onReset={resetFilters}
      />

      {/* Waitlist List */}
      <WaitlistAdminList
        entries={entries?.items || []}
        isLoading={isLoading}
        onCreateBooking={handleCreateBooking}
      />

      {/* Booking Modal */}
      <BookingFromWaitlistModal
        entry={selectedEntry}
        isOpen={isBookingModalOpen}
        onClose={() => {
          setIsBookingModalOpen(false);
          setSelectedEntry(null);
        }}
        onSuccess={handleBookingSuccess}
      />
    </div>
  );
}
