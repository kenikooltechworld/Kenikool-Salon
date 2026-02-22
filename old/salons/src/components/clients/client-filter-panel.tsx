import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ClientFilter } from "@/lib/api/types";
import { XIcon } from "@/components/icons";

interface ClientFilterPanelProps {
  filters: Omit<ClientFilter, "offset" | "limit">;
  onFilterChange: (filters: Omit<ClientFilter, "offset" | "limit">) => void;
}

export function ClientFilterPanel({
  filters,
  onFilterChange,
}: ClientFilterPanelProps) {
  const [localFilters, setLocalFilters] = useState(filters);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleApply = () => {
    onFilterChange(localFilters);
  };

  const handleClear = () => {
    const emptyFilters: Omit<ClientFilter, "offset" | "limit"> = {};
    setLocalFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  const hasActiveFilters = Object.keys(localFilters).some(
    (key) => localFilters[key as keyof typeof localFilters] !== undefined
  );

  return (
    <div className="border border-border rounded-lg p-4 space-y-4 bg-muted/30">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-foreground">Filters</h3>
        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={handleClear}>
            <XIcon size={16} />
            Clear All
          </Button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Segment Filter */}
        <div className="space-y-2">
          <Label htmlFor="segment">Segment</Label>
          <select
            id="segment"
            className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
            value={localFilters.segment || ""}
            onChange={(e) =>
              setLocalFilters({
                ...localFilters,
                segment: e.target.value || undefined,
              })
            }
          >
            <option value="">All Segments</option>
            <option value="new">New</option>
            <option value="regular">Regular</option>
            <option value="vip">VIP</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>

        {/* Min Spent */}
        <div className="space-y-2">
          <Label htmlFor="min_spent">Min Spent (₦)</Label>
          <Input
            id="min_spent"
            type="number"
            placeholder="0"
            value={localFilters.min_spent || ""}
            onChange={(e) =>
              setLocalFilters({
                ...localFilters,
                min_spent: e.target.value
                  ? parseFloat(e.target.value)
                  : undefined,
              })
            }
          />
        </div>

        {/* Max Spent */}
        <div className="space-y-2">
          <Label htmlFor="max_spent">Max Spent (₦)</Label>
          <Input
            id="max_spent"
            type="number"
            placeholder="1000000"
            value={localFilters.max_spent || ""}
            onChange={(e) =>
              setLocalFilters({
                ...localFilters,
                max_spent: e.target.value
                  ? parseFloat(e.target.value)
                  : undefined,
              })
            }
          />
        </div>

        {/* Last Visit Start */}
        <div className="space-y-2">
          <Label htmlFor="last_visit_start">Last Visit From</Label>
          <Input
            id="last_visit_start"
            type="date"
            value={localFilters.last_visit_start || ""}
            onChange={(e) =>
              setLocalFilters({
                ...localFilters,
                last_visit_start: e.target.value || undefined,
              })
            }
          />
        </div>

        {/* Last Visit End */}
        <div className="space-y-2">
          <Label htmlFor="last_visit_end">Last Visit To</Label>
          <Input
            id="last_visit_end"
            type="date"
            value={localFilters.last_visit_end || ""}
            onChange={(e) =>
              setLocalFilters({
                ...localFilters,
                last_visit_end: e.target.value || undefined,
              })
            }
          />
        </div>

        {/* Birthday Month */}
        <div className="space-y-2">
          <Label htmlFor="birthday_month">Birthday Month</Label>
          <select
            id="birthday_month"
            className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
            value={localFilters.birthday_month || ""}
            onChange={(e) =>
              setLocalFilters({
                ...localFilters,
                birthday_month: e.target.value
                  ? parseInt(e.target.value)
                  : undefined,
              })
            }
          >
            <option value="">All Months</option>
            <option value="1">January</option>
            <option value="2">February</option>
            <option value="3">March</option>
            <option value="4">April</option>
            <option value="5">May</option>
            <option value="6">June</option>
            <option value="7">July</option>
            <option value="8">August</option>
            <option value="9">September</option>
            <option value="10">October</option>
            <option value="11">November</option>
            <option value="12">December</option>
          </select>
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={handleClear}>
          Clear
        </Button>
        <Button onClick={handleApply}>Apply Filters</Button>
      </div>
    </div>
  );
}
