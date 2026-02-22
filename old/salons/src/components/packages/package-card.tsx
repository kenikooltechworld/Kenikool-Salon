'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, CheckCircle, Clock, Gift } from 'lucide-react';
import { PackagePurchase } from '@/lib/api/hooks/useClientPackages';

interface PackageCardProps {
  package: PackagePurchase;
  daysRemaining: number;
  isExpiringsoon: boolean;
  onViewDetails: (packageId: string) => void;
}

export function PackageCard({
  package: pkg,
  daysRemaining,
  isExpiringoon,
  onViewDetails,
}: PackageCardProps) {
  const totalCredits = pkg.credits.reduce((sum, c) => sum + c.initial_quantity, 0);
  const usedCredits = pkg.credits.reduce((sum, c) => sum + (c.initial_quantity - c.remaining_quantity), 0);
  const progressPercent = totalCredits > 0 ? (usedCredits / totalCredits) * 100 : 0;

  const getStatusColor = () => {
    switch (pkg.status) {
      case 'active':
        return 'bg-green-50 border-green-200';
      case 'expired':
        return 'bg-red-50 border-red-200';
      case 'fully_redeemed':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getStatusBadge = () => {
    switch (pkg.status) {
      case 'active':
        return <Badge className="bg-green-600">Active</Badge>;
      case 'expired':
        return <Badge className="bg-red-600">Expired</Badge>;
      case 'fully_redeemed':
        return <Badge className="bg-blue-600">Fully Redeemed</Badge>;
      case 'cancelled':
        return <Badge className="bg-gray-600">Cancelled</Badge>;
      default:
        return null;
    }
  };

  return (
    <Card className={`cursor-pointer transition-shadow hover:shadow-lg ${getStatusColor()}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">{pkg.package_name}</CardTitle>
            <p className="text-sm text-gray-600 mt-1">{pkg.package_description}</p>
          </div>
          {pkg.is_gift && (
            <Gift className="w-5 h-5 text-purple-600 ml-2 flex-shrink-0" />
          )}
        </div>
        <div className="flex items-center gap-2 mt-2">
          {getStatusBadge()}
          {isExpiringoon && pkg.status === 'active' && (
            <Badge variant="outline" className="border-orange-300 text-orange-700">
              <AlertCircle className="w-3 h-3 mr-1" />
              Expiring Soon
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Expiration Info */}
        {pkg.status === 'active' && (
          <div className="flex items-center gap-2 text-sm">
            <Clock className="w-4 h-4 text-gray-500" />
            <span className="text-gray-700">
              {daysRemaining} days remaining
            </span>
            <span className="text-gray-500">
              (Expires {new Date(pkg.expiration_date).toLocaleDateString()})
            </span>
          </div>
        )}

        {pkg.status === 'expired' && (
          <div className="flex items-center gap-2 text-sm text-red-600">
            <AlertCircle className="w-4 h-4" />
            <span>Expired on {new Date(pkg.expiration_date).toLocaleDateString()}</span>
          </div>
        )}

        {/* Credit Progress */}
        {pkg.status !== 'cancelled' && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Credits Used</span>
              <span className="font-medium">
                {usedCredits} / {totalCredits}
              </span>
            </div>
            <Progress value={progressPercent} className="h-2" />
          </div>
        )}

        {/* Service Credits Summary */}
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">Services</p>
          <div className="space-y-1">
            {pkg.credits.map((credit) => (
              <div key={credit._id} className="flex justify-between text-sm">
                <span className="text-gray-600">{credit.service_name}</span>
                <span className="font-medium">
                  {credit.remaining_quantity} / {credit.initial_quantity}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Purchase Info */}
        <div className="pt-2 border-t border-gray-200">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Purchased</span>
            <span className="text-gray-700">
              {new Date(pkg.purchase_date).toLocaleDateString()}
            </span>
          </div>
          <div className="flex justify-between text-sm mt-1">
            <span className="text-gray-600">Price Paid</span>
            <span className="font-medium">${pkg.amount_paid.toFixed(2)}</span>
          </div>
        </div>

        {/* View Details Button */}
        <button
          onClick={() => onViewDetails(pkg._id)}
          className="w-full mt-3 px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
        >
          View Details
        </button>
      </CardContent>
    </Card>
  );
}
