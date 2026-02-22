import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectItem } from "@/components/ui/select";
import { FilterIcon, XIcon } from "@/components/icons";

export interface ExpenseFiltersData {
  start_date?: string;
  end_date?: string;
  category?: string;
}

interface ExpenseFiltersProps {
  filters: ExpenseFiltersData;
  onFiltersChange: (filters: ExpenseFiltersData) => void;
}

const EXPENSE_CATEGORIES = [
  "Rent",
  "Utilities",
  "Supplies",
  "Salaries",
  "Marketing",
  "Equipment",
  "Maintenance",
  "Insurance",
  "Other",
];

export function ExpenseFilters({
  filters,
  onFiltersChange,
}: ExpenseFiltersProps) {
  const handleStartDateChange = (value: string) => {
    onFiltersChange({ ...filters, start_date: value });
  };

  const handleEndDateChange = (value: string) => {
    onFiltersChange({ ...filters, end_date: value });
  };

  const handleCategoryChange = (value: string) => {
    onFiltersChange({ ...filters, category: value });
  };

  const handleClearFilters = () => {
    onFiltersChange({});
  };

  const hasActiveFilters =
    filters.start_date || filters.end_date || filters.category;

  return (
    <div className="space-y-4 p-4 bg-[var(--muted)] rounded-[var(--radius-md)]">
      <div className="flex items-center gap-2 mb-4">
        <FilterIcon size={20} className="text-[var(--primary)]" />
        <h3 className="font-semibold">Filters</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <Label htmlFor="start_date">Start Date</Label>
          <Input
            id="start_date"
            type="date"
            value={filters.start_date || ""}
            onChange={(e) => handleStartDateChange(e.target.value)}
          />
        </div>

        <div>
          <Label htmlFor="end_date">End Date</Label>
          <Input
            id="end_date"
            type="date"
            value={filters.end_date || ""}
            onChange={(e) => handleEndDateChange(e.target.value)}
          />
        </div>

        <div>
          <Label htmlFor="category">Category</Label>
          <Select
            id="category"
            value={filters.category || ""}
            onValueChange={handleCategoryChange}
          >
            <SelectItem value="">All Categories</SelectItem>
            {EXPENSE_CATEGORIES.map((cat) => (
              <SelectItem key={cat} value={cat}>
                {cat}
              </SelectItem>
            ))}
          </Select>
        </div>
      </div>

      {hasActiveFilters && (
        <div className="flex justify-end">
          <Button
            variant="outline"
            size="sm"
            onClick={handleClearFilters}
            className="gap-2"
          >
            <XIcon size={16} />
            Clear Filters
          </Button>
        </div>
      )}
    </div>
  );
}
