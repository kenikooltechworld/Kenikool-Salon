import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface SearchFilters {
  dateFrom?: string;
  dateTo?: string;
  status?: string;
  location?: string;
  stylist?: string;
  client?: string;
}

interface AdvancedSearchFormProps {
  onSearch: (filters: SearchFilters) => void;
  onClear?: () => void;
}

const STATUS_OPTIONS = [
  "confirmed",
  "cancelled",
  "completed",
  "no-show",
  "pending",
];

export const AdvancedSearchForm: React.FC<AdvancedSearchFormProps> = ({
  onSearch,
  onClear,
}) => {
  const [filters, setFilters] = useState<SearchFilters>({});

  const handleSearch = () => {
    onSearch(filters);
  };

  const handleClear = () => {
    setFilters({});
    onClear?.();
  };

  const hasFilters = Object.values(filters).some((v) => v);

  return (
    <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="font-medium text-gray-900">Advanced Search</h3>

      <div className="grid grid-cols-2 gap-3">
        {/* Date Range */}
        <div className="space-y-1">
          <label className="text-xs font-medium text-gray-900">From Date</label>
          <Input
            type="date"
            value={filters.dateFrom || ""}
            onChange={(e) =>
              setFilters({ ...filters, dateFrom: e.target.value })
            }
          />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-medium text-gray-900">To Date</label>
          <Input
            type="date"
            value={filters.dateTo || ""}
            onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
          />
        </div>

        {/* Status */}
        <div className="space-y-1">
          <label className="text-xs font-medium text-gray-900">Status</label>
          <select
            value={filters.status || ""}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
          >
            <option value="">All statuses</option>
            {STATUS_OPTIONS.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        {/* Location */}
        <div className="space-y-1">
          <label className="text-xs font-medium text-gray-900">Location</label>
          <Input
            type="text"
            value={filters.location || ""}
            onChange={(e) =>
              setFilters({ ...filters, location: e.target.value })
            }
            placeholder="Filter by location"
          />
        </div>

        {/* Stylist */}
        <div className="space-y-1">
          <label className="text-xs font-medium text-gray-900">Stylist</label>
          <Input
            type="text"
            value={filters.stylist || ""}
            onChange={(e) =>
              setFilters({ ...filters, stylist: e.target.value })
            }
            placeholder="Filter by stylist"
          />
        </div>

        {/* Client */}
        <div className="space-y-1">
          <label className="text-xs font-medium text-gray-900">Client</label>
          <Input
            type="text"
            value={filters.client || ""}
            onChange={(e) => setFilters({ ...filters, client: e.target.value })}
            placeholder="Name or phone"
          />
        </div>
      </div>

      {/* Buttons */}
      <div className="flex gap-2 border-t border-gray-200 pt-3">
        <Button onClick={handleSearch} className="flex-1">
          Search
        </Button>
        {hasFilters && (
          <Button onClick={handleClear} variant="outline" className="flex-1">
            Clear
          </Button>
        )}
      </div>
    </div>
  );
};
