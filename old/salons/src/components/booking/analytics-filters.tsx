import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface AnalyticsFiltersProps {
  onFilterChange: (filters: {
    startDate?: string;
    endDate?: string;
    location?: string;
    stylist?: string;
    service?: string;
  }) => void;
}

export const AnalyticsFilters: React.FC<AnalyticsFiltersProps> = ({
  onFilterChange,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [location, setLocation] = useState("");
  const [stylist, setStylist] = useState("");
  const [service, setService] = useState("");

  const handleApplyFilters = () => {
    onFilterChange({
      startDate: startDate || undefined,
      endDate: endDate || undefined,
      location: location || undefined,
      stylist: stylist || undefined,
      service: service || undefined,
    });
  };

  const handleClearFilters = () => {
    setStartDate("");
    setEndDate("");
    setLocation("");
    setStylist("");
    setService("");
    onFilterChange({});
  };

  const hasFilters = startDate || endDate || location || stylist || service;

  return (
    <div className="space-y-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full p-2 border rounded hover:bg-gray-50"
      >
        <span className="font-medium text-sm">
          Filters
          {hasFilters && (
            <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
              Active
            </span>
          )}
        </span>
        <span className="text-gray-500">{expanded ? "▼" : "▶"}</span>
      </button>

      {expanded && (
        <div className="space-y-3 p-3 border rounded bg-gray-50">
          {/* Date Range */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-900">
              Date Range
            </label>
            <div className="flex gap-2">
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                placeholder="Start date"
                className="flex-1"
              />
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                placeholder="End date"
                className="flex-1"
              />
            </div>
          </div>

          {/* Location */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-900">
              Location
            </label>
            <Input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Filter by location"
            />
          </div>

          {/* Stylist */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-900">Stylist</label>
            <Input
              type="text"
              value={stylist}
              onChange={(e) => setStylist(e.target.value)}
              placeholder="Filter by stylist name"
            />
          </div>

          {/* Service */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-900">Service</label>
            <Input
              type="text"
              value={service}
              onChange={(e) => setService(e.target.value)}
              placeholder="Filter by service"
            />
          </div>

          {/* Buttons */}
          <div className="flex gap-2">
            <Button onClick={handleApplyFilters} className="flex-1" size="sm">
              Apply Filters
            </Button>
            {hasFilters && (
              <Button
                onClick={handleClearFilters}
                variant="outline"
                className="flex-1"
                size="sm"
              >
                Clear
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
