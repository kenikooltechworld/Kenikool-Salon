'use client';

import React from 'react';
import { usePackageRecommendations } from '@/lib/api/hooks/usePackageRecommendations';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, TrendingUp } from 'lucide-react';

interface PackageRecommendationsProps {
  clientId: string;
  limit?: number;
  onPurchase?: (packageId: string) => void;
}

export const PackageRecommendations: React.FC<PackageRecommendationsProps> = ({
  clientId,
  limit = 5,
  onPurchase,
}) => {
  const { data, isLoading, error } = usePackageRecommendations(clientId, limit);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recommended Packages</CardTitle>
          <CardDescription>Loading recommendations...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recommended Packages</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-4 w-4" />
            <p>Failed to load recommendations</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.count === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recommended Packages</CardTitle>
          <CardDescription>No recommendations available at this time</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600">
            Book more services to get personalized package recommendations
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recommended Packages</CardTitle>
        <CardDescription>
          Based on your booking history, we recommend these packages
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.recommendations.map((recommendation) => (
            <div
              key={recommendation.package_id}
              className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg">{recommendation.package_name}</h3>
                  <p className="text-sm text-gray-600">{recommendation.description}</p>
                </div>
                <Badge variant="secondary" className="ml-2">
                  {recommendation.discount_percentage}% off
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-500 uppercase">Package Price</p>
                  <p className="text-lg font-bold">${recommendation.package_price.toFixed(2)}</p>
                  <p className="text-xs text-gray-400 line-through">
                    ${recommendation.original_price.toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase">Potential Savings</p>
                  <div className="flex items-center gap-1">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    <p className="text-lg font-bold text-green-600">
                      ${recommendation.potential_savings.toFixed(2)}
                    </p>
                  </div>
                </div>
              </div>

              {recommendation.validity_days && (
                <p className="text-xs text-gray-600 mb-3">
                  Valid for {recommendation.validity_days} days after purchase
                </p>
              )}

              <div className="mb-4">
                <p className="text-xs font-semibold text-gray-700 mb-2">Includes:</p>
                <div className="flex flex-wrap gap-2">
                  {recommendation.services.map((service) => (
                    <Badge key={service.service_id} variant="outline">
                      {service.quantity}x Service
                    </Badge>
                  ))}
                </div>
              </div>

              {recommendation.matching_services.length > 0 && (
                <div className="mb-4 p-2 bg-blue-50 rounded">
                  <p className="text-xs font-semibold text-blue-900 mb-1">
                    Why we recommend this:
                  </p>
                  <p className="text-xs text-blue-800">
                    You've booked {recommendation.matching_services.length} of the services
                    in this package {recommendation.matching_services.reduce((sum, s) => sum + s.frequency, 0)} times
                  </p>
                </div>
              )}

              <Button
                onClick={() => onPurchase?.(recommendation.package_id)}
                className="w-full"
              >
                Purchase Package
              </Button>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
