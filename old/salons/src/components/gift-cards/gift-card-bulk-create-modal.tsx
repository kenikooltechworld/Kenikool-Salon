'use client';

import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { X, AlertCircle, CheckCircle, Upload, Download } from 'lucide-react';

interface BulkCreateModalProps {
  tenantId: string;
  onClose: () => void;
}

interface BulkCreateResult {
  success: boolean;
  created_count: number;
  failed_count: number;
  total: number;
  errors?: string[];
}

export default function GiftCardBulkCreateModal({
  tenantId,
  onClose,
}: BulkCreateModalProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [result, setResult] = useState<BulkCreateResult | null>(null);
  const [csvContent, setCsvContent] = useState<string>('');
  const [amount, setAmount] = useState<number>(5000);
  const [designTheme, setDesignTheme] = useState<string>('default');
  const [progress, setProgress] = useState<number>(0);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      setError('Please select a CSV file');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setCsvContent(content);
      setError(null);
    };
    reader.readAsText(file);
  };

  const downloadTemplate = () => {
    const template = `recipient_name,recipient_email,message
John Doe,john@example.com,Happy Birthday!
Jane Smith,jane@example.com,Enjoy your gift!
Bob Johnson,bob@example.com,`;

    const blob = new Blob([template], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'gift-cards-template.csv';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleBulkCreate = async () => {
    if (!csvContent.trim()) {
      setError('Please select a CSV file');
      return;
    }

    if (amount <= 0 || amount > 500000) {
      setError('Amount must be between ₦1 and ₦500,000');
      return;
    }

    setLoading(true);
    setError(null);
    setProgress(0);

    try {
      const response = await fetch('/api/pos/gift-cards/bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tenant_id: tenantId,
          csv_content: csvContent,
          amount,
          design_theme: designTheme,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create bulk gift cards');
      }

      const data: BulkCreateResult = await response.json();
      setResult(data);
      setSuccess(true);
      setProgress(100);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  if (success && result) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <Card className="w-full max-w-md mx-4">
          <CardContent className="pt-12 pb-12 text-center">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Bulk Creation Complete!
            </h2>
            <div className="space-y-2 text-gray-600 mb-6">
              <p>✓ Created: {result.created_count} cards</p>
              {result.failed_count > 0 && (
                <p className="text-orange-600">⚠ Failed: {result.failed_count} cards</p>
              )}
              <p>Total: {result.total} cards</p>
            </div>
            {result.errors && result.errors.length > 0 && (
              <div className="bg-red-50 p-3 rounded-lg mb-4 text-left max-h-32 overflow-y-auto">
                <p className="text-xs font-semibold text-red-800 mb-2">Errors:</p>
                {result.errors.map((err, idx) => (
                  <p key={idx} className="text-xs text-red-700">
                    • {err}
                  </p>
                ))}
              </div>
            )}
            <Button onClick={onClose} className="w-full">
              Close
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
      <Card className="w-full max-w-2xl mx-4 my-8">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Bulk Create Gift Cards</CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Instructions */}
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Upload a CSV file with recipient details. Maximum 100 cards per batch.
            </AlertDescription>
          </Alert>

          {/* Template Download */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm font-semibold text-blue-900 mb-2">
              CSV Format Required
            </p>
            <p className="text-sm text-blue-800 mb-3">
              Your CSV must have columns: recipient_name, recipient_email, message (optional)
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={downloadTemplate}
              className="w-full"
            >
              <Download className="w-4 h-4 mr-2" />
              Download Template
            </Button>
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              CSV File *
            </label>
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-purple-500 hover:bg-purple-50 transition-colors"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm font-medium text-gray-900">
                {csvContent ? '✓ File selected' : 'Click to select CSV file'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {csvContent ? `${csvContent.split('\n').length - 1} rows` : 'or drag and drop'}
              </p>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* Amount */}
          <div>
            <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
              Amount per Card (₦) *
            </label>
            <Input
              id="amount"
              type="number"
              min="1000"
              max="500000"
              step="100"
              value={amount}
              onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
              disabled={loading}
            />
            <p className="text-xs text-gray-500 mt-1">
              All cards will be created with this amount
            </p>
          </div>

          {/* Design Theme */}
          <div>
            <label htmlFor="designTheme" className="block text-sm font-medium text-gray-700 mb-2">
              Design Theme
            </label>
            <select
              id="designTheme"
              value={designTheme}
              onChange={(e) => setDesignTheme(e.target.value)}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
            >
              <option value="default">Default</option>
              <option value="birthday">Birthday</option>
              <option value="christmas">Christmas</option>
              <option value="valentine">Valentine</option>
            </select>
          </div>

          {/* Progress */}
          {loading && (
            <div>
              <div className="flex justify-between items-center mb-2">
                <p className="text-sm font-medium text-gray-700">Processing...</p>
                <p className="text-sm text-gray-600">{progress}%</p>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Error Alert */}
          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={onClose} className="flex-1" disabled={loading}>
              Cancel
            </Button>
            <Button
              onClick={handleBulkCreate}
              disabled={loading || !csvContent || amount <= 0}
              className="flex-1"
            >
              {loading ? 'Creating...' : 'Create Cards'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
