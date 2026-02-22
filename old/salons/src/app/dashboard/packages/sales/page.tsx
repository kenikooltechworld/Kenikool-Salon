'use client';

import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PackageSaleModal } from '@/components/packages/package-sale-modal';
import { PackageReceipt } from '@/components/packages/package-receipt';
import { useActivePackages } from '@/lib/api/hooks/usePackageSales';
import { formatCurrency } from '@/lib/utils/currency';
import { Search, ShoppingCart, TrendingUp } from 'lucide-react';

interface Client {
  _id: string;
  name: string;
  email: string;
}

interface PackageDefinition {
  _id: string;
  name: string;
  description: string;
  services: Array<{
    service_id: string;
    service_name: string;
    quantity: number;
    price: number;
  }>;
  original_price: number;
  package_price: number;
  discount_percentage: number;
  validity_days?: number;
  is_active: boolean;
  is_transferable: boolean;
  is_giftable: boolean;
}

interface Purchase {
  _id: string;
  package_name: string;
  package_description: string;
  client_name: string;
  client_email: string;
  purchase_date: string;
  expiration_date: string;
  amount_paid: number;
  original_price: number;
  discount_percentage: number;
  services: Array<{
    service_name: string;
    quantity: number;
    price: number;
  }>;
  is_gift?: boolean;
  gift_message?: string;
  gift_from_name?: string;
  payment_method: string;
}

export default function PackageSalesPage() {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPackage, setSelectedPackage] = useState<PackageDefinition | null>(null);
  const [showSaleModal, setShowSaleModal] = useState(false);
  const [showReceipt, setShowReceipt] = useState(false);
  const [lastPurchase, setLastPurchase] = useState<Purchase | null>(null);

  // Fetch active packages
  const { packages, isLoading: packagesLoading } = useActivePackages();

  // Fetch clients
  const { data: clientsData, isLoading: clientsLoading } = useQuery({
    queryKey: ['clients-for-sales'],
    queryFn: async () => {
      const response = await apiClient.get('/clients?limit=1000');
      return response.data;
    },
  });

  const clients: Client[] = clientsData?.clients || [];

  // Fetch sales metrics
  const { data: metricsData } = useQuery({
    queryKey: ['package-sales-metrics'],
    queryFn: async () => {
      const today = new Date();
      const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
      
      const response = await apiClient.get(
        `/packages/analytics/sales?start_date=${startOfMonth.toISOString()}&end_date=${today.toISOString()}`
      );
      return response.data;
    },
  });

  const metrics = metricsData || {};

  // Filter packages based on search
  const filteredPackages = useMemo(() => {
    return packages.filter(
      (pkg: PackageDefinition) =>
        pkg.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        pkg.description.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [packages, searchQuery]);

  const handlePackageSelect = (pkg: PackageDefinition) => {
    setSelectedPackage(pkg);
    setShowSaleModal(true);
  };

  const handleSaleSuccess = (purchase: Purchase) => {
    setLastPurchase(purchase);
    setShowSaleModal(false);
    setShowReceipt(true);
    toast('Package sold successfully!', 'success');
  };

  const handleEmailReceipt = async (email: string) => {
    try {
      await apiClient.post(`/packages/purchases/${lastPurchase?._id}/email-receipt`, {
        email,
      });
      toast('Receipt sent successfully', 'success');
    } catch (error: any) {
      toast(
        error.response?.data?.detail || 'Failed to send receipt',
        'error'
      );
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Package Sales</h1>
        <p className="text-gray-600 mt-2">
          Sell service packages to clients and generate receipts
        </p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Sales This Month
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(metrics.total_sales || 0)}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {metrics.total_packages_sold || 0} packages sold
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Average Package Value
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(metrics.average_package_price || 0)}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Per package sold
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Savings Given
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(metrics.total_savings || 0)}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Client savings this month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filter */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Search packages by name or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Packages Grid */}
      <Tabs defaultValue="all" className="w-full">
        <TabsList>
          <TabsTrigger value="all">
            All Packages ({filteredPackages.length})
          </TabsTrigger>
          <TabsTrigger value="popular">Popular</TabsTrigger>
          <TabsTrigger value="new">New</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {packagesLoading ? (
            <div className="text-center py-12">
              <p className="text-gray-600">Loading packages...</p>
            </div>
          ) : filteredPackages.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600">No packages found</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredPackages.map((pkg: PackageDefinition) => (
                <Card
                  key={pkg._id}
                  className="hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => handlePackageSelect(pkg)}
                >
                  <CardHeader>
                    <div className="flex justify-between items-start gap-2">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{pkg.name}</CardTitle>
                        <p className="text-sm text-gray-600 mt-1">
                          {pkg.description}
                        </p>
                      </div>
                      {pkg.is_giftable && (
                        <Badge variant="outline">Giftable</Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Services */}
                    <div className="space-y-2">
                      <p className="text-sm font-semibold text-gray-700">
                        Services:
                      </p>
                      <div className="space-y-1">
                        {pkg.services.map((service) => (
                          <div
                            key={service.service_id}
                            className="text-sm text-gray-600 flex justify-between"
                          >
                            <span>
                              {service.service_name} (x{service.quantity})
                            </span>
                            <span className="font-medium">
                              {formatCurrency(service.price * service.quantity)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Pricing */}
                    <div className="border-t pt-3 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Original:</span>
                        <span className="line-through text-gray-500">
                          {formatCurrency(pkg.original_price)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="font-semibold">Package Price:</span>
                        <span className="text-xl font-bold text-green-600">
                          {formatCurrency(pkg.package_price)}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Savings:</span>
                        <span className="text-green-600 font-semibold">
                          {formatCurrency(
                            pkg.original_price - pkg.package_price
                          )}
                        </span>
                      </div>
                    </div>

                    {/* Validity */}
                    {pkg.validity_days && (
                      <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                        Valid for {pkg.validity_days} days
                      </div>
                    )}

                    {/* Action Button */}
                    <Button
                      className="w-full gap-2"
                      onClick={(e) => {
                        e.stopPropagation();
                        handlePackageSelect(pkg);
                      }}
                    >
                      <ShoppingCart className="w-4 h-4" />
                      Sell Package
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="popular" className="space-y-4">
          <div className="text-center py-12">
            <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Popular packages will appear here</p>
          </div>
        </TabsContent>

        <TabsContent value="new" className="space-y-4">
          <div className="text-center py-12">
            <p className="text-gray-600">New packages will appear here</p>
          </div>
        </TabsContent>
      </Tabs>

      {/* Modals */}
      <PackageSaleModal
        package={selectedPackage}
        isOpen={showSaleModal}
        onClose={() => {
          setShowSaleModal(false);
          setSelectedPackage(null);
        }}
        onSuccess={handleSaleSuccess}
        clients={clients}
      />

      {lastPurchase && (
        <PackageReceipt
          isOpen={showReceipt}
          onClose={() => setShowReceipt(false)}
          purchase={lastPurchase}
          onEmailReceipt={handleEmailReceipt}
        />
      )}
    </div>
  );
}
