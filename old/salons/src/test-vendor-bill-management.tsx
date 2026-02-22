import React, { useState } from 'react';
import { 
  useGetVendors, 
  useCreateVendor, 
  useUpdateVendor, 
  useDeleteVendor,
  useGetBills,
  useCreateBill,
  useUpdateBill,
  useDeleteBill,
  useRecordBillPayment,
  useGetAPAgingReport
} from '@/lib/api/hooks/useAccounting';
import { VendorFormModal } from '@/components/accounting/vendor-form-modal';
import { BillFormModal } from '@/components/accounting/bill-form-modal';

export function TestVendorBillManagement() {
  const { data: vendors = [], isLoading: vendorsLoading } = useGetVendors();
  const { data: bills = [], isLoading: billsLoading } = useGetBills();
  const { data: agingReport } = useGetAPAgingReport();
  
  const deleteVendor = useDeleteVendor();
  const deleteBill = useDeleteBill();
  const recordPayment = useRecordBillPayment();
  
  const [selectedVendor, setSelectedVendor] = useState(null);
  const [selectedBill, setSelectedBill] = useState(null);
  const [isVendorModalOpen, setIsVendorModalOpen] = useState(false);
  const [isBillModalOpen, setIsBillModalOpen] = useState(false);
  const [isCreateMode, setIsCreateMode] = useState(true);

  const handleCreateVendor = () => {
    setSelectedVendor(null);
    setIsCreateMode(true);
    setIsVendorModalOpen(true);
  };

  const handleEditVendor = (vendor) => {
    setSelectedVendor(vendor);
    setIsCreateMode(false);
    setIsVendorModalOpen(true);
  };

  const handleDeleteVendor = async (vendorId) => {
    if (confirm('Are you sure you want to delete this vendor?')) {
      try {
        await deleteVendor.mutateAsync(vendorId);
        console.log('Vendor deleted successfully');
      } catch (error) {
        console.error('Error deleting vendor:', error);
      }
    }
  };

  const handleCreateBill = () => {
    setSelectedBill(null);
    setIsCreateMode(true);
    setIsBillModalOpen(true);
  };

  const handleEditBill = (bill) => {
    setSelectedBill(bill);
    setIsCreateMode(false);
    setIsBillModalOpen(true);
  };

  const handleDeleteBill = async (billId) => {
    if (confirm('Are you sure you want to delete this bill?')) {
      try {
        await deleteBill.mutateAsync(billId);
        console.log('Bill deleted successfully');
      } catch (error) {
        console.error('Error deleting bill:', error);
      }
    }
  };

  const handleRecordPayment = async (billId, amount) => {
    const paymentAmount = prompt(`Enter payment amount (max: ₦${amount}):`);
    if (paymentAmount && parseFloat(paymentAmount) > 0) {
      try {
        await recordPayment.mutateAsync({
          id: billId,
          payment: {
            bill_id: billId,
            amount: parseFloat(paymentAmount),
            payment_date: new Date().toISOString().split('T')[0],
            payment_method: 'cash',
            reference: `Payment-${Date.now()}`
          }
        });
        console.log('Payment recorded successfully');
      } catch (error) {
        console.error('Error recording payment:', error);
      }
    }
  };

  const closeVendorModal = () => {
    setIsVendorModalOpen(false);
    setSelectedVendor(null);
  };

  const closeBillModal = () => {
    setIsBillModalOpen(false);
    setSelectedBill(null);
  };

  if (vendorsLoading || billsLoading) return <div>Loading...</div>;

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-2xl font-bold">Vendor & Bill Management Test</h1>
      
      {/* AP Aging Report Summary */}
      {agingReport && (
        <div className="bg-white p-4 rounded-lg border">
          <h2 className="text-lg font-semibold mb-4">AP Aging Summary</h2>
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                ₦{agingReport.aging_summary?.current?.toFixed(2) || '0.00'}
              </div>
              <div className="text-sm text-gray-600">Current</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                ₦{agingReport.aging_summary?.['30_days']?.toFixed(2) || '0.00'}
              </div>
              <div className="text-sm text-gray-600">1-30 Days</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                ₦{agingReport.aging_summary?.['60_days']?.toFixed(2) || '0.00'}
              </div>
              <div className="text-sm text-gray-600">31-60 Days</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                ₦{agingReport.aging_summary?.['90_plus']?.toFixed(2) || '0.00'}
              </div>
              <div className="text-sm text-gray-600">60+ Days</div>
            </div>
          </div>
          <div className="mt-4 text-center">
            <div className="text-xl font-bold">
              Total Outstanding: ₦{agingReport.total_outstanding?.toFixed(2) || '0.00'}
            </div>
          </div>
        </div>
      )}

      {/* Vendors Section */}
      <div className="bg-white p-4 rounded-lg border">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Vendors ({vendors.length})</h2>
          <button 
            onClick={handleCreateVendor}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Add Vendor
          </button>
        </div>
        
        {vendors.length > 0 ? (
          <div className="space-y-2">
            {vendors.map((vendor) => (
              <div key={vendor.id} className="p-3 border rounded flex justify-between items-center">
                <div>
                  <strong>{vendor.name}</strong> ({vendor.vendor_number})
                  <p className="text-sm text-gray-600">
                    Status: {vendor.status} | Outstanding: ₦{vendor.total_outstanding?.toFixed(2) || '0.00'}
                  </p>
                  {vendor.contact_person && (
                    <p className="text-sm text-gray-500">Contact: {vendor.contact_person}</p>
                  )}
                </div>
                <div className="space-x-2">
                  <button 
                    onClick={() => handleEditVendor(vendor)}
                    className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    Edit
                  </button>
                  <button 
                    onClick={() => handleDeleteVendor(vendor.id)}
                    className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                    disabled={deleteVendor.isPending}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No vendors found. Create your first vendor!</p>
        )}
      </div>

      {/* Bills Section */}
      <div className="bg-white p-4 rounded-lg border">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Bills ({bills.length})</h2>
          <button 
            onClick={handleCreateBill}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            disabled={vendors.length === 0}
          >
            Create Bill
          </button>
        </div>
        
        {bills.length > 0 ? (
          <div className="space-y-2">
            {bills.map((bill) => (
              <div key={bill.id} className="p-3 border rounded flex justify-between items-center">
                <div>
                  <strong>{bill.bill_number}</strong> - {bill.vendor_name}
                  <p className="text-sm text-gray-600">
                    Total: ₦{bill.total?.toFixed(2)} | Due: ₦{bill.amount_due?.toFixed(2)} | Status: {bill.status}
                  </p>
                  <p className="text-sm text-gray-500">
                    Due Date: {bill.due_date}
                  </p>
                </div>
                <div className="space-x-2">
                  <button 
                    onClick={() => handleEditBill(bill)}
                    className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                    disabled={bill.status !== 'draft'}
                  >
                    Edit
                  </button>
                  {bill.amount_due > 0 && (
                    <button 
                      onClick={() => handleRecordPayment(bill.id, bill.amount_due)}
                      className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                      disabled={recordPayment.isPending}
                    >
                      Pay
                    </button>
                  )}
                  <button 
                    onClick={() => handleDeleteBill(bill.id)}
                    className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                    disabled={deleteBill.isPending}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No bills found. Create your first bill!</p>
        )}
      </div>

      {/* Modals */}
      <VendorFormModal
        isOpen={isVendorModalOpen}
        onClose={closeVendorModal}
        vendor={isCreateMode ? undefined : selectedVendor}
      />

      <BillFormModal
        isOpen={isBillModalOpen}
        onClose={closeBillModal}
        bill={isCreateMode ? undefined : selectedBill}
      />
    </div>
  );
}