'use client';

import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PackageCard } from './package-card';
import { PackageDetailsModal } from './package-details-modal';
import { useClientPackages, usePackageDetails, PackagePurchase } from '@/lib/api/hooks/useClientPackages';
import { Skeleton } from '@/components/ui/skeleton';

interface ClientPackageListProps {
  clientId: string;
}

export function ClientPackageList({ clientId }: ClientPackageListProps) {
  const [selectedPackageId, setSelectedPackageId] = useState<string | null>(null);
  const { activePackages, expiredPackages, fullyRedeemedPackages, isLoading } = useClientPackages(clientId);
  const { details } = usePackageDetails(selectedPackageId || undefined);

  const calculateDaysRemaining = (expirationDate: string) => {
    const today = new Date();
    const expiration = new Date(expirationDate);
    const diffTime = expiration.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const isExpiringoon = (expirationDate: string) => {
    const daysRemaining = calculateDaysRemaining(expirationDate);
    return daysRemaining <= 7 && daysRemaining > 0;
  };

  const renderPackageGrid = (packages: PackagePurchase[]) => {
    if (packages.length === 0) {
      return (
        <div className="text-center py-12">
          <p className="text-gray-600">No packages in this category</p>
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {packages.map((pkg) => (
          <PackageCard
            key={pkg._id}
            package={pkg}
            daysRemaining={calculateDaysRemaining(pkg.expiration_date)}
            isExpiringsoon={isExpiringoon(pkg.expiration_date)}
            onViewDetails={setSelectedPackageId}
          />
        ))}
      </div>
    );
  };

  const renderSkeleton = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {[1, 2, 3].map((i) => (
        <Skeleton key={i} className="h-64 rounded-lg" />
      ))}
    </div>
  );

  if (isLoading) {
    return renderSkeleton();
  }

  const totalPackages = activePackages.length + expiredPackages.length + fullyRedeemedPackages.length;

  if (totalPackages === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 mb-4">You haven't purchased any packages yet</p>
        <a href="/packages" className="text-blue-600 hover:text-blue-700 font-medium">
          Browse available packages
        </a>
      </div>
    );
  }

  return (
    <>
      <Tabs defaultValue="active" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="active">
            Active ({activePackages.length})
          </TabsTrigger>
          <TabsTrigger value="redeemed">
            Fully Redeemed ({fullyRedeemedPackages.length})
          </TabsTrigger>
          <TabsTrigger value="expired">
            Expired ({expiredPackages.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="mt-6">
          {renderPackageGrid(activePackages)}
        </TabsContent>

        <TabsContent value="redeemed" className="mt-6">
          {renderPackageGrid(fullyRedeemedPackages)}
        </TabsContent>

        <TabsContent value="expired" className="mt-6">
          {renderPackageGrid(expiredPackages)}
        </TabsContent>
      </Tabs>

      <PackageDetailsModal
        package={details}
        isOpen={!!selectedPackageId}
        onClose={() => setSelectedPackageId(null)}
      />
    </>
  );
}
