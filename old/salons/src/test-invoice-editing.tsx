import React, { useState } from 'react';
import { useGetInvoices, useGetInvoiceById, useUpdateInvoice, useDeleteInvoice, useDownloadInvoicePDF } from '@/lib/api/hooks/useAccounting';
import { InvoiceFormModal } from '@/components/accounting/invoice-form-modal';

export function TestInvoiceEditing() {
  const { data: invoices, isLoading, error } = useGetInvoices();
  const updateInvoice = useUpdateInvoice();
  const deleteInvoice = useDeleteInvoice();
  const downloadPDF = useDownloadInvoicePDF();
  
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  const handleEdit = (invoice) => {
    setSelectedInvoice(invoice);
    setIsEditModalOpen(true);
  };

  const handleDelete = async (invoiceId) => {
    if (confirm('Are you sure you want to delete this invoice?')) {
      try {
        await deleteInvoice.mutateAsync(invoiceId);
        console.log('Invoice deleted successfully');
      } catch (error) {
        console.error('Error deleting invoice:', error);
      }
    }
  };

  const handleDownloadPDF = async (invoiceId) => {
    try {
      await downloadPDF.mutateAsync(invoiceId);
      console.log('PDF downloaded successfully');
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };

  const closeEditModal = () => {
    setIsEditModalOpen(false);
    setSelectedInvoice(null);
  };

  if (isLoading) return <div>Loading invoices...</div>;
  if (error) return <div>Error loading invoices: {error.message}</div>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Invoice Management Test</h2>
      
      <div>
        <h3 className="text-lg font-semibold mb-2">Invoices:</h3>
        {invoices && invoices.length > 0 ? (
          <div className="space-y-2">
            {invoices.map((invoice) => (
              <div key={invoice.id} className="p-4 border rounded flex justify-between items-center">
                <div>
                  <strong>{invoice.invoice_number}</strong> - {invoice.client_name}
                  <p className="text-sm text-gray-600">
                    Total: ₦{invoice.total} | Status: {invoice.status}
                  </p>
                </div>
                <div className="space-x-2">
                  <button 
                    onClick={() => handleEdit(invoice)}
                    className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                    disabled={invoice.status !== 'draft'}
                  >
                    Edit
                  </button>
                  <button 
                    onClick={() => handleDownloadPDF(invoice.id)}
                    className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                    disabled={downloadPDF.isPending}
                  >
                    PDF
                  </button>
                  <button 
                    onClick={() => handleDelete(invoice.id)}
                    className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                    disabled={deleteInvoice.isPending}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No invoices found</p>
        )}
      </div>

      <InvoiceFormModal
        isOpen={isEditModalOpen}
        onClose={closeEditModal}
        invoice={selectedInvoice}
      />
    </div>
  );
}