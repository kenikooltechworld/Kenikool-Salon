'use client';

import { useRef } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Download, Mail, X } from 'lucide-react';
import { formatCurrency } from '@/lib/utils/currency';
import jsPDF from 'jspdf';

interface ServiceItem {
  service_name: string;
  quantity: number;
  price: number;
}

interface PackageReceiptProps {
  isOpen: boolean;
  onClose: () => void;
  purchase: {
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
    services: ServiceItem[];
    is_gift?: boolean;
    gift_message?: string;
    gift_from_name?: string;
    payment_method: string;
  };
  onEmailReceipt?: (email: string) => void;
}

export function PackageReceipt({
  isOpen,
  onClose,
  purchase,
  onEmailReceipt,
}: PackageReceiptProps) {
  const receiptRef = useRef<HTMLDivElement>(null);

  const totalValue = purchase.services.reduce(
    (sum, s) => sum + s.price * s.quantity,
    0
  );
  const savings = totalValue - purchase.amount_paid;

  const handleDownloadPDF = () => {
    try {
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4',
      });

      let yPosition = 20;
      const pageWidth = pdf.internal.pageSize.getWidth();
      const margin = 15;
      const contentWidth = pageWidth - 2 * margin;

      // Helper function to add text with wrapping
      const addWrappedText = (text: string, x: number, y: number, maxWidth: number, fontSize: number = 10) => {
        pdf.setFontSize(fontSize);
        const lines = pdf.splitTextToSize(text, maxWidth) as string[];
        pdf.text(lines, x, y);
        return y + (lines.length * fontSize * 0.35);
      };

      // Header
      pdf.setFontSize(20);
      pdf.text('RECEIPT', margin, yPosition);
      yPosition += 10;

      pdf.setFontSize(10);
      pdf.setTextColor(100, 100, 100);
      pdf.text('Package Purchase Confirmation', margin, yPosition);
      yPosition += 5;
      pdf.text(`Receipt #${purchase._id.slice(-8).toUpperCase()}`, margin, yPosition);
      yPosition += 10;

      // Separator
      pdf.setDrawColor(200, 200, 200);
      pdf.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 8;

      // Purchase Info
      pdf.setTextColor(0, 0, 0);
      pdf.setFontSize(10);
      pdf.text('Purchase Date:', margin, yPosition);
      pdf.text(new Date(purchase.purchase_date).toLocaleDateString(), margin + 50, yPosition);
      yPosition += 7;

      pdf.text('Expiration Date:', margin, yPosition);
      pdf.text(new Date(purchase.expiration_date).toLocaleDateString(), margin + 50, yPosition);
      yPosition += 10;

      // Client Info
      pdf.setFontSize(11);
      pdf.setFont(undefined, 'bold');
      pdf.text('Client Information', margin, yPosition);
      yPosition += 7;

      pdf.setFont(undefined, 'normal');
      pdf.setFontSize(10);
      pdf.text(purchase.client_name, margin, yPosition);
      yPosition += 5;
      pdf.setTextColor(100, 100, 100);
      pdf.text(purchase.client_email, margin, yPosition);
      yPosition += 10;

      // Gift Info
      if (purchase.is_gift) {
        pdf.setTextColor(0, 0, 0);
        pdf.setFont(undefined, 'bold');
        pdf.text('Gift Package', margin, yPosition);
        yPosition += 5;
        pdf.setFont(undefined, 'normal');
        if (purchase.gift_from_name) {
          pdf.text(`From: ${purchase.gift_from_name}`, margin, yPosition);
          yPosition += 5;
        }
        if (purchase.gift_message) {
          yPosition = addWrappedText(`"${purchase.gift_message}"`, margin, yPosition, contentWidth, 9);
        }
        yPosition += 5;
      }

      // Separator
      pdf.setDrawColor(200, 200, 200);
      pdf.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 8;

      // Package Details
      pdf.setTextColor(0, 0, 0);
      pdf.setFont(undefined, 'bold');
      pdf.setFontSize(11);
      pdf.text(purchase.package_name, margin, yPosition);
      yPosition += 6;

      pdf.setFont(undefined, 'normal');
      pdf.setFontSize(9);
      pdf.setTextColor(100, 100, 100);
      yPosition = addWrappedText(purchase.package_description, margin, yPosition, contentWidth, 9);
      yPosition += 5;

      // Services Table
      pdf.setTextColor(0, 0, 0);
      pdf.setFont(undefined, 'bold');
      pdf.setFontSize(10);

      const colWidths = [contentWidth * 0.4, contentWidth * 0.15, contentWidth * 0.2, contentWidth * 0.25];
      const headers = ['Service', 'Qty', 'Price', 'Total'];

      // Header row
      let xPos = margin;
      headers.forEach((header, i) => {
        pdf.text(header, xPos, yPosition);
        xPos += colWidths[i];
      });

      yPosition += 6;
      pdf.setDrawColor(200, 200, 200);
      pdf.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 5;

      // Data rows
      pdf.setFont(undefined, 'normal');
      pdf.setFontSize(9);
      purchase.services.forEach((service) => {
        xPos = margin;
        pdf.text(service.service_name, xPos, yPosition);
        xPos += colWidths[0];
        pdf.text(service.quantity.toString(), xPos, yPosition);
        xPos += colWidths[1];
        pdf.text(formatCurrency(service.price), xPos, yPosition);
        xPos += colWidths[2];
        pdf.text(formatCurrency(service.price * service.quantity), xPos, yPosition);
        yPosition += 5;
      });

      yPosition += 3;
      pdf.setDrawColor(200, 200, 200);
      pdf.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 8;

      // Pricing Summary
      pdf.setFont(undefined, 'normal');
      pdf.setFontSize(10);
      pdf.setTextColor(0, 0, 0);

      pdf.text('Original Value:', margin, yPosition);
      pdf.text(formatCurrency(purchase.original_price), pageWidth - margin - 30, yPosition);
      yPosition += 5;

      pdf.text(`Discount (${purchase.discount_percentage}%):`, margin, yPosition);
      pdf.setTextColor(200, 0, 0);
      pdf.text(`-${formatCurrency(savings)}`, pageWidth - margin - 30, yPosition);
      yPosition += 5;

      pdf.setTextColor(0, 0, 0);
      pdf.setFont(undefined, 'bold');
      pdf.text('Package Price:', margin, yPosition);
      pdf.setTextColor(0, 128, 0);
      pdf.text(formatCurrency(purchase.amount_paid), pageWidth - margin - 30, yPosition);
      yPosition += 7;

      pdf.setTextColor(0, 0, 0);
      pdf.text('Client Savings:', margin, yPosition);
      pdf.setTextColor(0, 128, 0);
      pdf.text(formatCurrency(savings), pageWidth - margin - 30, yPosition);
      yPosition += 10;

      // Payment Method
      pdf.setTextColor(0, 0, 0);
      pdf.setFont(undefined, 'bold');
      pdf.text('Payment Method:', margin, yPosition);
      pdf.setFont(undefined, 'normal');
      pdf.text(purchase.payment_method.charAt(0).toUpperCase() + purchase.payment_method.slice(1), margin + 50, yPosition);
      yPosition += 10;

      // Footer
      pdf.setDrawColor(200, 200, 200);
      pdf.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 5;

      pdf.setFontSize(9);
      pdf.setTextColor(100, 100, 100);
      pdf.text('Thank you for your purchase!', pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 5;
      pdf.text(
        `This package is valid until ${new Date(purchase.expiration_date).toLocaleDateString()}`,
        pageWidth / 2,
        yPosition,
        { align: 'center' }
      );
      yPosition += 5;
      pdf.text('For questions, please contact our salon', pageWidth / 2, yPosition, { align: 'center' });

      pdf.save(`package-receipt-${purchase._id}.pdf`);
    } catch (error) {
      console.error('Failed to generate PDF:', error);
    }
  };

  const handleEmailReceipt = () => {
    onEmailReceipt?.(purchase.client_email);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Package Purchase Receipt</DialogTitle>
        </DialogHeader>

        {/* Receipt Content */}
        <div
          ref={receiptRef}
          className="p-8 bg-white space-y-6"
          style={{ width: '100%' }}
        >
          {/* Header */}
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold">RECEIPT</h1>
            <p className="text-gray-600">Package Purchase Confirmation</p>
            <p className="text-sm text-gray-500">
              Receipt #{purchase._id.slice(-8).toUpperCase()}
            </p>
          </div>

          <Separator />

          {/* Purchase Info */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-xs text-gray-600 uppercase font-semibold">
                Purchase Date
              </p>
              <p className="text-lg font-semibold">
                {new Date(purchase.purchase_date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600 uppercase font-semibold">
                Expiration Date
              </p>
              <p className="text-lg font-semibold">
                {new Date(purchase.expiration_date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
          </div>

          <Separator />

          {/* Client Info */}
          <div>
            <p className="text-xs text-gray-600 uppercase font-semibold mb-2">
              Client Information
            </p>
            <div className="space-y-1">
              <p className="font-semibold text-lg">{purchase.client_name}</p>
              <p className="text-gray-600">{purchase.client_email}</p>
            </div>
          </div>

          {/* Gift Info */}
          {purchase.is_gift && (
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <p className="text-sm font-semibold text-purple-900 mb-2">
                Gift Package
              </p>
              {purchase.gift_from_name && (
                <p className="text-sm text-purple-800">
                  <span className="font-semibold">From:</span>{' '}
                  {purchase.gift_from_name}
                </p>
              )}
              {purchase.gift_message && (
                <p className="text-sm text-purple-800 italic mt-2">
                  "{purchase.gift_message}"
                </p>
              )}
            </div>
          )}

          <Separator />

          {/* Package Details */}
          <div>
            <p className="text-xs text-gray-600 uppercase font-semibold mb-3">
              Package Details
            </p>
            <div className="space-y-2 mb-4">
              <h3 className="text-xl font-bold">{purchase.package_name}</h3>
              <p className="text-gray-600 text-sm">
                {purchase.package_description}
              </p>
            </div>

            {/* Services Table */}
            <div className="border border-gray-300 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-2 text-left text-sm font-semibold">
                      Service
                    </th>
                    <th className="px-4 py-2 text-center text-sm font-semibold">
                      Qty
                    </th>
                    <th className="px-4 py-2 text-right text-sm font-semibold">
                      Price
                    </th>
                    <th className="px-4 py-2 text-right text-sm font-semibold">
                      Total
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {purchase.services.map((service, index) => (
                    <tr
                      key={index}
                      className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                    >
                      <td className="px-4 py-3 text-sm">
                        {service.service_name}
                      </td>
                      <td className="px-4 py-3 text-center text-sm">
                        {service.quantity}
                      </td>
                      <td className="px-4 py-3 text-right text-sm">
                        {formatCurrency(service.price)}
                      </td>
                      <td className="px-4 py-3 text-right text-sm font-semibold">
                        {formatCurrency(service.price * service.quantity)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <Separator />

          {/* Pricing Summary */}
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Original Value:</span>
              <span className="font-semibold">
                {formatCurrency(purchase.original_price)}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Discount ({purchase.discount_percentage}%):</span>
              <span className="font-semibold text-red-600">
                -{formatCurrency(savings)}
              </span>
            </div>
            <div className="flex justify-between text-sm border-t pt-3">
              <span className="font-semibold">Package Price:</span>
              <span className="font-bold text-lg">
                {formatCurrency(purchase.amount_paid)}
              </span>
            </div>
            <div className="flex justify-between text-sm bg-green-50 p-3 rounded">
              <span className="font-semibold text-green-900">Client Savings:</span>
              <span className="font-bold text-green-700">
                {formatCurrency(savings)}
              </span>
            </div>
          </div>

          <Separator />

          {/* Payment Info */}
          <div>
            <p className="text-xs text-gray-600 uppercase font-semibold mb-2">
              Payment Method
            </p>
            <p className="text-lg font-semibold capitalize">
              {purchase.payment_method}
            </p>
          </div>

          {/* Footer */}
          <div className="text-center space-y-2 pt-4 border-t">
            <p className="text-sm text-gray-600">
              Thank you for your purchase!
            </p>
            <p className="text-xs text-gray-500">
              This package is valid until{' '}
              {new Date(purchase.expiration_date).toLocaleDateString()}
            </p>
            <p className="text-xs text-gray-500">
              For questions, please contact our salon
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 justify-end mt-6">
          <Button
            variant="outline"
            onClick={handleEmailReceipt}
            className="gap-2"
          >
            <Mail className="w-4 h-4" />
            Email Receipt
          </Button>
          <Button
            variant="outline"
            onClick={handleDownloadPDF}
            className="gap-2"
          >
            <Download className="w-4 h-4" />
            Download PDF
          </Button>
          <Button onClick={onClose} className="gap-2">
            <X className="w-4 h-4" />
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
