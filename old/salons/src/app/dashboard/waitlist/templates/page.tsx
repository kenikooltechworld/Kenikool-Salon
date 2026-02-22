'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { NotificationTemplateManager } from '@/components/waitlist/notification-template-manager';
import Link from 'next/link';

export default function WaitlistTemplatesPage() {
  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Notification Templates</h1>
          <p className="text-gray-600 mt-1">Create and manage notification templates for your waitlist</p>
        </div>
        <Link href="/dashboard/waitlist">
          <Button variant="outline">Back to Waitlist</Button>
        </Link>
      </div>

      {/* Template Manager */}
      <NotificationTemplateManager />
    </div>
  );
}
