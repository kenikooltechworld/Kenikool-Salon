"use client";

import { useState, useCallback } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { ArrowUpDownIcon } from "@/components/icons";

export type SortBy = "created_at" | "rating" | "status" | "helpful_votes";
export type SortOrder = "asc" | "desc";

interface ReviewSortProps {
  onSortChange: (sortBy: SortBy, sortOrder: SortOrder) => void;
  currentSortBy?: SortBy;
  currentSortOrder?: SortOrder;
}

const SORT_OPTIONS: Array<{
  value: SortBy;
  label: string;
  description: string;
}> = [
  {
    value: "created_at",
    label: "Date",
    description: "Sort by review date",
  },
  {
    value: "rating",
    label: "Rating",
    description: "Sort by star rating",
  },
  {
    value: "status",
    label: "Status",
    description: "Sort by approval status",
  },
  {
    value: "helpful_votes",
    label: "Helpfulness",
    description: "Sort by helpful votes",
  },
];

const ORDER_OPTIONS: Array<{
  value: SortOrder;
  label: string;
  description: string;
}> = [
  {
    value: "desc",
    label: "Descending",
    description: "Highest to lowest",
  },
  {
    value: "asc",
    label: "Ascending",
    description: "Lowest to highest",
  },
];

export function ReviewSort({
  onSortChange,
  currentSortBy = "created_at",
  currentSortOrder = "desc",
}: ReviewSortProps) {
  const [sortBy, setSortBy] = useState<SortBy>(currentSortBy);
  const [sortOrder, setSortOrder] = useState<SortOrder>(currentSortOrder);

  const handleSortByChange = useCallback(
    (value: string) => {
      const newSortBy = value as SortBy;
      setSortBy(newSortBy);
      onSortChange(newSortBy, sortOrder);
    },
    [sortOrder, onSortChange]
  );

  const handleSortOrderChange = useCallback(
    (value: string) => {
      const newSortOrder = value as SortOrder;
      setSortOrder(newSortOrder);
      onSortChange(sortBy, newSortOrder);
    },
    [sortBy, onSortChange]
  );

  const currentSortLabel = SORT_OPTIONS.find(
    (opt) => opt.value === sortBy
  )?.label;
  const currentOrderLabel = ORDER_OPTIONS.find(
    (opt) => opt.value === sortOrder
  )?.label;

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        <ArrowUpDownIcon className="h-4 w-4 text-muted-foreground" />
        <Label htmlFor="sort-by" className="text-sm font-medium">
          Sort by:
        </Label>
      </div>

      <Select value={sortBy} onValueChange={handleSortByChange}>
        <SelectTrigger id="sort-by" className="w-[150px]">
          <SelectValue placeholder="Select sort field" />
        </SelectTrigger>
        <SelectContent>
          {SORT_OPTIONS.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              <div className="flex flex-col">
                <span>{option.label}</span>
                <span className="text-xs text-muted-foreground">
                  {option.description}
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={sortOrder} onValueChange={handleSortOrderChange}>
        <SelectTrigger className="w-[150px]">
          <SelectValue placeholder="Select order" />
        </SelectTrigger>
        <SelectContent>
          {ORDER_OPTIONS.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              <div className="flex flex-col">
                <span>{option.label}</span>
                <span className="text-xs text-muted-foreground">
                  {option.description}
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Display current sort */}
      <div className="text-sm text-muted-foreground">
        {currentSortLabel} ({currentOrderLabel})
      </div>
    </div>
  );
}
