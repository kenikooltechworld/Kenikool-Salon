'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, Plus, Filter, Download, Search } from 'lucide-react';
import { useGiftCardDashboard } from '@/lib/api/hooks/useGiftCardDashboard';
import GiftCardList from './gift-card-list';
import GiftCardDetailModal from './gift-card-detail-modal';
import GiftCardCreateModal from './gift-card-create-modal';

interface DashboardProps {
  tenantId: string;
}

interface Metrics {
  totalSold: number;
  totalRedeemed: number;
  outstandingLiability: number;
  expirationRate: number;
}

export default function GiftCardDashboard({ tenantId }: DashboardProps) {
  const { listCards, loading, error, cards, total } = useGiftCardDashboard();
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedCard, setSelectedCard] = useState<any>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [metrics, setMetrics] = useState<Metrics>({
    totalSold: 0,
    totalRedeemed: 0,
    outstandingLiability: 0,
    expirationRate: 0,
  });

  useEffect(() => {
    loadCards();
    loadMetrics();
  }, [page, statusFilter, typeFilter, searchQuery]);

  const loadCards = async () => {
    try {
      await listCards({
        tenantId,
        page,
        limit: 20,
        status: statusFilter || undefined,
        cardType: typeFilter || undefined,
      });
    } catch (err) {
      // Error handled by hook
    }
  };

  const loadMetrics = async () => {
    try {
      const response = await fetch(
        `/api/pos/gift-cards/analytics?tenant_id=${tenantId}`
      );
      if (response.ok) {
        const data = await response.json();
        setMetrics({
          totalSold: data.total_sold || 0,
          totalRedeemed: data.total_redeemed || 0,
          outstandingLiability: data.outstanding_liability || 0,
          expirationRate: data.expiration_rate || 0,
        });
      }
    } catch (err) {
      console.error('Failed to load metrics:', err);
    }
  };

  const handleCardClick = (card: any) => {
    setSelectedCard(card);
    setShowDetailModal(true);
  };

  const handleRefresh = () => {
    setPage(1);
    loadCards();
    loadMetrics();
  };

  const handleExportCSV = async () => {
    try {
      const response = await fetch(
        `/api/pos/gift-cards/export?tenant_id=${tenantId}&format=csv`
      );
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gift-cards-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Failed to export CSV:', err);
    }
  };

  const handleExportPDF = async () => {
    try {
      const response = await fetch(
        `/api/pos/gift-cards/export?tenant_id=${tenantId}&format=pdf`
      );
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gift-cards-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Failed to export PDF:', err);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
    }).format(amount);
  };

  const totalPages = Math.ceil(total / 20);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gift Cards</h1>
          <p className="text-gray-600 mt-1">Manage and monitor gift cards</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportCSV}>
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
          <Button variant="outline" onClick={handleExportPDF}>
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Create Gift Card
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Total Sold</p>
            <p className="text-2xl font-bold text-gray-900 mt-2">
              {formatCurrency(metrics.totalSold)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Total Redeemed</p>
            <p className="text-2xl font-bold text-green-600 mt-2">
              {formatCurrency(metrics.totalRedeemed)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Outstanding Liability</p>
            <p className="text-2xl font-bold text-orange-600 mt-2">
              {formatCurrency(metrics.outstandingLiability)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-600">Expiration Rate</p>
            <p className="text-2xl font-bold text-red-600 mt-2">
              {metrics.expirationRate.toFixed(1)}%
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Filters & Search</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Card number, name, email..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setPage(1);
                  }}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(1);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
              >
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="expired">Expired</option>
                <option value="voided">Voided</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type
              </label>
              <select
                value={typeFilter}
                onChange={(e) => {
                  setTypeFilter(e.target.value);
                  setPage(1);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
              >
                <option value="">All Types</option>
                <option value="digital">Digital</option>
                <option value="physical">Physical</option>
              </select>
            </div>

            <div className="flex items-end">
              <Button variant="outline" onClick={handleRefresh} className="w-full">
                <Filter className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {/* Gift Cards List */}
      <GiftCardList
        cards={cards}
        loading={loading}
        onCardClick={handleCardClick}
      />

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1 || loading}
          >
            Previous
          </Button>
          <span className="text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages || loading}
          >
            Next
          </Button>
        </div>
      )}

      {/* Modals */}
      {showDetailModal && selectedCard && (
        <GiftCardDetailModal
          card={selectedCard}
          tenantId={tenantId}
          onClose={() => {
            setShowDetailModal(false);
            handleRefresh();
          }}
        />
      )}

      {showCreateModal && (
        <GiftCardCreateModal
          tenantId={tenantId}
          onClose={() => {
            setShowCreateModal(false);
            handleRefresh();
          }}
        />
      )}
    </div>
  );
}
