import React from 'react';
import { useGetTaxRates, useCreateTaxRate } from '@/lib/api/hooks/useAccounting';

export function TestTaxRates() {
  const { data: taxRates, isLoading, error } = useGetTaxRates(true);
  const createTaxRate = useCreateTaxRate();

  const handleCreateTestTaxRate = async () => {
    try {
      await createTaxRate.mutateAsync({
        name: 'VAT',
        rate: 7.5,
        description: 'Value Added Tax'
      });
      console.log('Tax rate created successfully');
    } catch (error) {
      console.error('Error creating tax rate:', error);
    }
  };

  if (isLoading) return <div>Loading tax rates...</div>;
  if (error) return <div>Error loading tax rates: {error.message}</div>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Tax Rates Test</h2>
      
      <button 
        onClick={handleCreateTestTaxRate}
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        disabled={createTaxRate.isPending}
      >
        {createTaxRate.isPending ? 'Creating...' : 'Create Test Tax Rate'}
      </button>

      <div>
        <h3 className="text-lg font-semibold mb-2">Current Tax Rates:</h3>
        {taxRates && taxRates.length > 0 ? (
          <ul className="space-y-2">
            {taxRates.map((rate) => (
              <li key={rate.id} className="p-2 border rounded">
                <strong>{rate.name}</strong> - {rate.rate}%
                {rate.description && <p className="text-sm text-gray-600">{rate.description}</p>}
              </li>
            ))}
          </ul>
        ) : (
          <p>No tax rates found</p>
        )}
      </div>
    </div>
  );
}