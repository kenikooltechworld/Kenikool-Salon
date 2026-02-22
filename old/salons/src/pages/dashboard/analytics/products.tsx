import React from 'react';
import { ProductSalesChart } from '@/components/analytics/ProductSalesChart';

export default function ProductAnalyticsPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Product & Retail Analytics</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Sales by Category</h2>
          <ProductSalesChart />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600">Top Product</h3>
            <p className="text-2xl font-bold text-gray-900 mt-2">Shampoo Pro</p>
            <p className="text-sm text-gray-500 mt-1">$8,500 revenue</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600">Product Mix</h3>
            <p className="text-2xl font-bold text-gray-900 mt-2">8 Products</p>
            <p className="text-sm text-gray-500 mt-1">4 Categories</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600">Avg Price</h3>
            <p className="text-2xl font-bold text-gray-900 mt-2">$48.50</p>
            <p className="text-sm text-gray-500 mt-1">Per product</p>
          </div>
        </div>
      </div>
    </div>
  );
}
