'use client';

import React from 'react';
import { useAuth } from '@/lib/auth/auth-context';
import { ClientPackageList } from '@/components/packages/client-package-list';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function MyPackagesPage() {
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Please log in to view your packages</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">My Packages</h1>
          <p className="text-gray-600 mt-1">
            View and manage your purchased service packages
          </p>
        </div>
        <Link href="/packages">
          <Button className="gap-2">
            Browse Packages
            <ArrowRight className="w-4 h-4" />
          </Button>
        </Link>
      </div>

      <ClientPackageList clientId={user.id} />
    </div>
  );
}
