import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface AuditLogFiltersProps {
  onFilterChange: (filters: {
    startDate?: string;
    endDate?: string;
    user?: string;
    action?: string;
  }) => void;
}

const ACTION_TYPES = [
  "created",
  "updated",
  "cancelled",
  "completed",
  "rescheduled",
  "marked_no_show",
];

export const AuditLogFilters: React.FC<AuditLogFiltersProps> = ({
  onFilterChange,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [user, setUser] = useState("");
  const [action, setAction] = useState("");

  const handleApplyFilters = () => {
    onFilterChange({
      startDate: startDate || undefined,
      endDate: endDate || undefined,
      user: user || undefined,
      action: action || undefined,
    });
  };

  const handleClearFilters = () => {
    setStartDate("");
    setEndDate("");
    setUser("");
    setAction("");
    onFilterChange({});
  };

  const hasFilters = startDate || endDate || user || action;

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

          {/* User */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-900">User</label>
            <Input
              type="text"
              value={user}
              onChange={(e) => setUser(e.target.value)}
              placeholder="Filter by user name or email"
            />
          </div>

          {/* Action Type */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-900">
              Action Type
            </label>
            <select
              value={action}
              onChange={(e) => setAction(e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
            >
              <option value="">All actions</option>
              {ACTION_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type.replace(/_/g, " ")}
                </option>
              ))}
            </select>
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
