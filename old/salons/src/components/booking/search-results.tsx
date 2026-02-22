import React, { useState } from "react";
import { format } from "date-fns";

interface SearchResult {
  id: string;
  clientName: string;
  serviceName: string;
  stylistName: string;
  date: string;
  time: string;
  status: string;
  price: number;
}

interface SearchResultsProps {
  results: SearchResult[];
  loading?: boolean;
  onResultClick?: (result: SearchResult) => void;
  sortBy?: "date" | "status" | "client" | "stylist";
  onSortChange?: (sortBy: string) => void;
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  loading = false,
  onResultClick,
  sortBy = "date",
  onSortChange,
}) => {
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  if (loading) {
    return <div className="text-sm text-gray-500">Searching...</div>;
  }

  if (!results || results.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-center text-sm text-gray-600">
        No results found
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Sort Options */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600">Sort by:</span>
        <select
          value={sortBy}
          onChange={(e) => onSortChange?.(e.target.value)}
          className="rounded border border-gray-300 px-2 py-1 text-sm"
        >
          <option value="date">Date</option>
          <option value="status">Status</option>
          <option value="client">Client</option>
          <option value="stylist">Stylist</option>
        </select>
        <button
          onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
          className="text-sm text-gray-600 hover:text-gray-900"
        >
          {sortOrder === "asc" ? "↑" : "↓"}
        </button>
      </div>

      {/* Results Table */}
      <div className="rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-900">
                Client
              </th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-900">
                Service
              </th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-900">
                Stylist
              </th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-900">
                Date & Time
              </th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-900">
                Status
              </th>
              <th className="px-4 py-2 text-right text-sm font-medium text-gray-900">
                Price
              </th>
            </tr>
          </thead>
          <tbody>
            {results.map((result) => (
              <tr
                key={result.id}
                onClick={() => onResultClick?.(result)}
                className="border-b border-gray-200 hover:bg-blue-50 cursor-pointer"
              >
                <td className="px-4 py-3 text-sm text-gray-900">
                  {result.clientName}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {result.serviceName}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {result.stylistName}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {result.date} {result.time}
                </td>
                <td className="px-4 py-3 text-sm">
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      result.status === "confirmed"
                        ? "bg-green-100 text-green-700"
                        : result.status === "cancelled"
                          ? "bg-red-100 text-red-700"
                          : result.status === "completed"
                            ? "bg-blue-100 text-blue-700"
                            : "bg-gray-100 text-gray-700"
                    }`}
                  >
                    {result.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-sm font-medium text-gray-900">
                  ${result.price.toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Results Count */}
      <div className="text-sm text-gray-600">
        Showing {results.length} result{results.length !== 1 ? "s" : ""}
      </div>
    </div>
  );
};
