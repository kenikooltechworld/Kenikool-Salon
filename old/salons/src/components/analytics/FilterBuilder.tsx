import React, { useState } from 'react';

interface Filter {
  id: string;
  field: string;
  operator: string;
  value: string | number | boolean | string[];
  logicalOperator?: 'AND' | 'OR';
}



interface FilterBuilderProps {
  onFiltersChange?: (filters: Filter[]) => void;
  onApply?: (filters: Filter[]) => void;
}

export const FilterBuilder: React.FC<FilterBuilderProps> = ({ onFiltersChange, onApply }) => {
  const [filters, setFilters] = useState<Filter[]>([]);
  const [newFilter, setNewFilter] = useState<Partial<Filter>>({});
  const [logicalOperator, setLogicalOperator] = useState<'AND' | 'OR'>('AND');
  const [advancedMode, setAdvancedMode] = useState(false);

  const availableFields = [
    { id: 'revenue', label: 'Revenue', type: 'number' },
    { id: 'bookings', label: 'Bookings', type: 'number' },
    { id: 'clients', label: 'Clients', type: 'number' },
    { id: 'staff', label: 'Staff', type: 'text' },
    { id: 'location', label: 'Location', type: 'text' },
    { id: 'date', label: 'Date', type: 'date' },
    { id: 'service_type', label: 'Service Type', type: 'text' },
    { id: 'status', label: 'Status', type: 'select' },
    { id: 'payment_method', label: 'Payment Method', type: 'select' },
  ];

  const operators = [
    { id: 'equals', label: 'Equals', types: ['text', 'number', 'date', 'select'] },
    { id: 'not_equals', label: 'Not Equals', types: ['text', 'number', 'date', 'select'] },
    { id: 'greater_than', label: 'Greater Than', types: ['number', 'date'] },
    { id: 'less_than', label: 'Less Than', types: ['number', 'date'] },
    { id: 'greater_equal', label: 'Greater or Equal', types: ['number', 'date'] },
    { id: 'less_equal', label: 'Less or Equal', types: ['number', 'date'] },
    { id: 'contains', label: 'Contains', types: ['text'] },
    { id: 'not_contains', label: 'Does Not Contain', types: ['text'] },
    { id: 'starts_with', label: 'Starts With', types: ['text'] },
    { id: 'ends_with', label: 'Ends With', types: ['text'] },
    { id: 'between', label: 'Between', types: ['number', 'date'] },
    { id: 'in', label: 'In List', types: ['text', 'number', 'select'] },
    { id: 'not_in', label: 'Not In List', types: ['text', 'number', 'select'] },
    { id: 'is_empty', label: 'Is Empty', types: ['text', 'number', 'date'] },
    { id: 'is_not_empty', label: 'Is Not Empty', types: ['text', 'number', 'date'] },
  ];

  const statusOptions = ['Active', 'Completed', 'Cancelled', 'Pending'];
  const paymentMethods = ['Cash', 'Card', 'Check', 'Bank Transfer', 'Gift Card'];

  const getApplicableOperators = (fieldId: string) => {
    const field = availableFields.find((f) => f.id === fieldId);
    if (!field) return operators;
    return operators.filter((op) => op.types.includes(field.type));
  };

  const getFieldType = (fieldId: string) => {
    return availableFields.find((f) => f.id === fieldId)?.type || 'text';
  };

  const addFilter = () => {
    if (newFilter.field && newFilter.operator && (newFilter.value !== undefined || ['is_empty', 'is_not_empty'].includes(newFilter.operator as string))) {
      const filter: Filter = {
        id: `filter_${Date.now()}`,
        field: newFilter.field,
        operator: newFilter.operator,
        value: newFilter.value || '',
        logicalOperator: filters.length > 0 ? logicalOperator : undefined,
      };
      const updatedFilters = [...filters, filter];
      setFilters(updatedFilters);
      setNewFilter({});
      onFiltersChange?.(updatedFilters);
    }
  };

  const removeFilter = (filterId: string) => {
    const updatedFilters = filters.filter((f) => f.id !== filterId);
    setFilters(updatedFilters);
    onFiltersChange?.(updatedFilters);
  };

  const handleApply = () => {
    onApply?.(filters);
  };

  const renderValueInput = () => {
    if (!newFilter.field) return null;

    const fieldType = getFieldType(newFilter.field);
    const field = availableFields.find((f) => f.id === newFilter.field);

    if (['is_empty', 'is_not_empty'].includes(newFilter.operator as string)) {
      return null;
    }

    if (newFilter.operator === 'between') {
      return (
        <div className="flex gap-2">
          <input
            type={fieldType === 'date' ? 'date' : 'text'}
            placeholder="From"
            className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type={fieldType === 'date' ? 'date' : 'text'}
            placeholder="To"
            className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      );
    }

    if (field?.id === 'status') {
      return (
        <select
          value={String(newFilter.value || '')}
          onChange={(e) => setNewFilter({ ...newFilter, value: e.target.value })}
          className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Select status...</option>
          {statusOptions.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
      );
    }

    if (field?.id === 'payment_method') {
      return (
        <select
          value={String(newFilter.value || '')}
          onChange={(e) => setNewFilter({ ...newFilter, value: e.target.value })}
          className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Select method...</option>
          {paymentMethods.map((method) => (
            <option key={method} value={method}>
              {method}
            </option>
          ))}
        </select>
      );
    }

    return (
      <input
        type={fieldType === 'date' ? 'date' : fieldType === 'number' ? 'number' : 'text'}
        value={String(newFilter.value || '')}
        onChange={(e) => setNewFilter({ ...newFilter, value: e.target.value })}
        placeholder="Enter value"
        className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    );
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Advanced Filters</h3>

      <div className="space-y-4">
        {/* Mode Toggle */}
        <div className="flex items-center gap-2">
          <label className="flex items-center text-sm">
            <input
              type="checkbox"
              checked={advancedMode}
              onChange={(e) => setAdvancedMode(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="ml-2 text-gray-700">Advanced Mode</span>
          </label>
        </div>

        {/* Filter Input */}
        <div className="grid grid-cols-1 gap-2">
          <div className="grid grid-cols-4 gap-2">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Field</label>
              <select
                value={newFilter.field || ''}
                onChange={(e) => setNewFilter({ ...newFilter, field: e.target.value })}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select field...</option>
                {availableFields.map((field) => (
                  <option key={field.id} value={field.id}>
                    {field.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Operator</label>
              <select
                value={newFilter.operator || ''}
                onChange={(e) => setNewFilter({ ...newFilter, operator: e.target.value })}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select operator...</option>
                {getApplicableOperators(newFilter.field || '').map((op) => (
                  <option key={op.id} value={op.id}>
                    {op.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Value</label>
              {renderValueInput()}
            </div>

            <div className="flex items-end">
              <button
                onClick={addFilter}
                className="w-full px-2 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                Add Filter
              </button>
            </div>
          </div>

          {/* Logical Operator Selection */}
          {filters.length > 0 && (
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">Combine with:</label>
              <select
                value={logicalOperator}
                onChange={(e) => setLogicalOperator(e.target.value as 'AND' | 'OR')}
                className="px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="AND">AND (all conditions must match)</option>
                <option value="OR">OR (any condition can match)</option>
              </select>
            </div>
          )}
        </div>

        {/* Active Filters */}
        {filters.length > 0 && (
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Active Filters</h4>
            <div className="space-y-2">
              {filters.map((filter, idx) => {
                const field = availableFields.find((f) => f.id === filter.field);
                const operator = operators.find((o) => o.id === filter.operator);
                return (
                  <div key={filter.id} className="flex items-center gap-2">
                    {idx > 0 && (
                      <span className="text-xs font-semibold text-gray-600 px-2 py-1 bg-gray-100 rounded">
                        {filter.logicalOperator || logicalOperator}
                      </span>
                    )}
                    <div className="flex-1 flex items-center justify-between bg-gray-50 p-2 rounded border border-gray-200">
                      <span className="text-sm text-gray-700">
                        {field?.label} {operator?.label} {filter.value}
                      </span>
                      <button
                        onClick={() => removeFilter(filter.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 pt-4 border-t">
          <button
            onClick={handleApply}
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
          >
            Apply Filters
          </button>
          <button
            onClick={() => {
              setFilters([]);
              onFiltersChange?.([]);
            }}
            className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 text-sm"
          >
            Clear All
          </button>
        </div>
      </div>
    </div>
  );
};
