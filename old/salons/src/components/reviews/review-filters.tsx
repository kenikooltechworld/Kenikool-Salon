"use client";

import { useState, useCallback } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  FilterIcon,
  XIcon,
  ChevronDownIcon,
  StarIcon,
} from "@/components/icons";

export interface ReviewFilters {
  status?: "pending" | "approved" | "rejected";
  rating?: number[];
  serviceId?: string;
  stylistId?: string;
  dateRange?: { start: string; end: string };
  hasResponse?: boolean;
  hasPhotos?: boolean;
  isFlagged?: boolean;
}

export interface FilterStats {
  totalReviews: number;
  byStatus: Record<string, number>;
  byRating: Record<number, number>;
  byService: Record<string, number>;
  byStylist: Record<string, number>;
  withResponse: number;
  withPhotos: number;
  flagged: number;
}

interface ReviewFiltersProps {
  onFilterChange: (filters: ReviewFilters) => void;
  stats: FilterStats;
  services?: Array<{ id: string; name: string }>;
  stylists?: Array<{ id: string; name: string }>;
  currentFilters?: ReviewFilters;
}

export function ReviewFilters({
  onFilterChange,
  stats,
  services = [],
  stylists = [],
  currentFilters = {},
}: ReviewFiltersProps) {
  const [filters, setFilters] = useState<ReviewFilters>(currentFilters);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleStatusChange = useCallback(
    (status: "pending" | "approved" | "rejected" | "") => {
      const newFilters = {
        ...filters,
        status: status || undefined,
      };
      setFilters(newFilters);
      onFilterChange(newFilters);
    },
    [filters, onFilterChange]
  );

  const handleRatingToggle = useCallback(
    (rating: number) => {
      const currentRatings = filters.rating || [];
      const newRatings = currentRatings.includes(rating)
        ? currentRatings.filter((r) => r !== rating)
        : [...currentRatings, rating];

      const newFilters = {
        ...filters,
        rating: newRatings.length > 0 ? newRatings : undefined,
      };
      setFilters(newFilters);
      onFilterChange(newFilters);
    },
    [filters, onFilterChange]
  );

  const handleServiceChange = useCallback(
    (serviceId: string) => {
      const newFilters = {
        ...filters,
        serviceId: serviceId || undefined,
      };
      setFilters(newFilters);
      onFilterChange(newFilters);
    },
    [filters, onFilterChange]
  );

  const handleStylistChange = useCallback(
    (stylistId: string) => {
      const newFilters = {
        ...filters,
        stylistId: stylistId || undefined,
      };
      setFilters(newFilters);
      onFilterChange(newFilters);
    },
    [filters, onFilterChange]
  );

  const handleDateRangeChange = useCallback(
    (type: "start" | "end", value: string) => {
      const currentRange = filters.dateRange || { start: "", end: "" };
      const newRange = {
        ...currentRange,
        [type]: value,
      };

      const newFilters = {
        ...filters,
        dateRange:
          newRange.start || newRange.end
            ? newRange
            : undefined,
      };
      setFilters(newFilters);
      onFilterChange(newFilters);
    },
    [filters, onFilterChange]
  );

  const handleToggleChange = useCallback(
    (key: "hasResponse" | "hasPhotos" | "isFlagged", value: boolean) => {
      const newFilters = {
        ...filters,
        [key]: value || undefined,
      };
      setFilters(newFilters);
      onFilterChange(newFilters);
    },
    [filters, onFilterChange]
  );

  const handleClearAll = useCallback(() => {
    const emptyFilters: ReviewFilters = {};
    setFilters(emptyFilters);
    onFilterChange(emptyFilters);
  }, [onFilterChange]);

  const activeFilterCount = Object.values(filters).filter(
    (v) => v !== undefined
  ).length;

  const getStatusCount = (status: string): number => {
    return stats.byStatus?.[status] || 0;
  };

  const getRatingCount = (rating: number): number => {
    return stats.byRating?.[rating] || 0;
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <FilterIcon size={20} className="text-foreground" />
          <h2 className="text-lg font-semibold text-foreground">Filters</h2>
          {activeFilterCount > 0 && (
            <Badge variant="secondary" className="ml-2">
              {activeFilterCount} active
            </Badge>
          )}
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ChevronDownIcon
            size={16}
            className={`transition-transform ${
              isExpanded ? "rotate-180" : ""
            }`}
          />
          {isExpanded ? "Hide" : "Show"}
        </button>
      </div>

      {isExpanded && (
        <div className="space-y-6">
          {/* Status Filter */}
          <div>
            <Label className="text-sm font-medium mb-3 block">Status</Label>
            <div className="flex flex-wrap gap-2">
              {["pending", "approved", "rejected"].map((status) => (
                <button
                  key={status}
                  onClick={() =>
                    handleStatusChange(
                      filters.status === status
                        ? ""
                        : (status as "pending" | "approved" | "rejected")
                    )
                  }
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    filters.status === status
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground hover:bg-muted/80"
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                  <span className="ml-2 text-xs opacity-75">
                    ({getStatusCount(status)})
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Rating Filter */}
          <div>
            <Label className="text-sm font-medium mb-3 block">Rating</Label>
            <div className="flex flex-wrap gap-2">
              {[5, 4, 3, 2, 1].map((rating) => (
                <button
                  key={rating}
                  onClick={() => handleRatingToggle(rating)}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1 ${
                    filters.rating?.includes(rating)
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground hover:bg-muted/80"
                  }`}
                >
                  <div className="flex items-center gap-0.5">
                    {[...Array(rating)].map((_, i) => (
                      <StarIcon
                        key={i}
                        size={14}
                        className="fill-current"
                      />
                    ))}
                  </div>
                  <span className="ml-1">({getRatingCount(rating)})</span>
                </button>
              ))}
            </div>
          </div>

          {/* Service Filter */}
          {services.length > 0 && (
            <div>
              <Label htmlFor="service-select" className="text-sm font-medium mb-3 block">
                Service
              </Label>
              <Select value={filters.serviceId || ""} onValueChange={handleServiceChange}>
                <SelectTrigger id="service-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Services</SelectItem>
                  {services.map((service) => (
                    <SelectItem key={service.id} value={service.id}>
                      {service.name}
                      <span className="ml-2 text-xs opacity-75">
                        ({stats.byService?.[service.id] || 0})
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Stylist Filter */}
          {stylists.length > 0 && (
            <div>
              <Label htmlFor="stylist-select" className="text-sm font-medium mb-3 block">
                Stylist
              </Label>
              <Select value={filters.stylistId || ""} onValueChange={handleStylistChange}>
                <SelectTrigger id="stylist-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Stylists</SelectItem>
                  {stylists.map((stylist) => (
                    <SelectItem key={stylist.id} value={stylist.id}>
                      {stylist.name}
                      <span className="ml-2 text-xs opacity-75">
                        ({stats.byStylist?.[stylist.id] || 0})
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Date Range Filter */}
          <div>
            <Label className="text-sm font-medium mb-3 block">Date Range</Label>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">
                  From
                </label>
                <Input
                  type="date"
                  value={filters.dateRange?.start || ""}
                  onChange={(e) => handleDateRangeChange("start", e.target.value)}
                  className="text-sm"
                />
              </div>
              <div>
                <label className="text-xs text-muted-foreground mb-1 block">
                  To
                </label>
                <Input
                  type="date"
                  value={filters.dateRange?.end || ""}
                  onChange={(e) => handleDateRangeChange("end", e.target.value)}
                  className="text-sm"
                />
              </div>
            </div>
          </div>

          {/* Toggle Filters */}
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <Checkbox
                id="has-response"
                checked={filters.hasResponse || false}
                onCheckedChange={(checked) =>
                  handleToggleChange("hasResponse", checked as boolean)
                }
              />
              <Label
                htmlFor="has-response"
                className="text-sm font-medium cursor-pointer"
              >
                Has Response
                <span className="ml-2 text-xs text-muted-foreground">
                  ({stats.withResponse || 0})
                </span>
              </Label>
            </div>

            <div className="flex items-center gap-3">
              <Checkbox
                id="has-photos"
                checked={filters.hasPhotos || false}
                onCheckedChange={(checked) =>
                  handleToggleChange("hasPhotos", checked as boolean)
                }
              />
              <Label
                htmlFor="has-photos"
                className="text-sm font-medium cursor-pointer"
              >
                Has Photos
                <span className="ml-2 text-xs text-muted-foreground">
                  ({stats.withPhotos || 0})
                </span>
              </Label>
            </div>

            <div className="flex items-center gap-3">
              <Checkbox
                id="is-flagged"
                checked={filters.isFlagged || false}
                onCheckedChange={(checked) =>
                  handleToggleChange("isFlagged", checked as boolean)
                }
              />
              <Label
                htmlFor="is-flagged"
                className="text-sm font-medium cursor-pointer"
              >
                Flagged
                <span className="ml-2 text-xs text-muted-foreground">
                  ({stats.flagged || 0})
                </span>
              </Label>
            </div>
          </div>

          {/* Clear All Button */}
          {activeFilterCount > 0 && (
            <Button
              onClick={handleClearAll}
              variant="outline"
              className="w-full"
            >
              <XIcon size={16} className="mr-2" />
              Clear All Filters
            </Button>
          )}
        </div>
      )}

      {/* Active Filters Display */}
      {activeFilterCount > 0 && !isExpanded && (
        <div className="flex flex-wrap gap-2 mt-4">
          {filters.status && (
            <Badge variant="secondary" className="flex items-center gap-1">
              Status: {filters.status}
              <button
                onClick={() => handleStatusChange("")}
                className="ml-1 hover:opacity-70"
              >
                <XIcon size={14} />
              </button>
            </Badge>
          )}
          {filters.rating && filters.rating.length > 0 && (
            <Badge variant="secondary" className="flex items-center gap-1">
              Rating: {filters.rating.join(", ")} ★
              <button
                onClick={() => {
                  const newFilters = { ...filters, rating: undefined };
                  setFilters(newFilters);
                  onFilterChange(newFilters);
                }}
                className="ml-1 hover:opacity-70"
              >
                <XIcon size={14} />
              </button>
            </Badge>
          )}
          {filters.serviceId && (
            <Badge variant="secondary" className="flex items-center gap-1">
              Service: {services.find((s) => s.id === filters.serviceId)?.name}
              <button
                onClick={() => handleServiceChange("")}
                className="ml-1 hover:opacity-70"
              >
                <XIcon size={14} />
              </button>
            </Badge>
          )}
          {filters.stylistId && (
            <Badge variant="secondary" className="flex items-center gap-1">
              Stylist: {stylists.find((s) => s.id === filters.stylistId)?.name}
              <button
                onClick={() => handleStylistChange("")}
                className="ml-1 hover:opacity-70"
              >
                <XIcon size={14} />
              </button>
            </Badge>
          )}
          {filters.hasResponse && (
            <Badge variant="secondary" className="flex items-center gap-1">
              Has Response
              <button
                onClick={() => handleToggleChange("hasResponse", false)}
                className="ml-1 hover:opacity-70"
              >
                <XIcon size={14} />
              </button>
            </Badge>
          )}
          {filters.hasPhotos && (
            <Badge variant="secondary" className="flex items-center gap-1">
              Has Photos
              <button
                onClick={() => handleToggleChange("hasPhotos", false)}
                className="ml-1 hover:opacity-70"
              >
                <XIcon size={14} />
              </button>
            </Badge>
          )}
          {filters.isFlagged && (
            <Badge variant="secondary" className="flex items-center gap-1">
              Flagged
              <button
                onClick={() => handleToggleChange("isFlagged", false)}
                className="ml-1 hover:opacity-70"
              >
                <XIcon size={14} />
              </button>
            </Badge>
          )}
        </div>
      )}
    </Card>
  );
}
