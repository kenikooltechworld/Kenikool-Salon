"use client";

import { useState, useCallback, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SearchIcon, XIcon } from "@/components/icons";

interface ReviewSearchProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  resultCount?: number;
  isLoading?: boolean;
}

export function ReviewSearch({
  onSearch,
  placeholder = "Search reviews by client name, comment, service, or stylist...",
  resultCount,
  isLoading = false,
}: ReviewSearchProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");

  // Debounce search query (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
      onSearch(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery, onSearch]);

  const handleClear = useCallback(() => {
    setSearchQuery("");
    setDebouncedQuery("");
    onSearch("");
  }, [onSearch]);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setSearchQuery(e.target.value);
    },
    []
  );

  return (
    <div className="w-full space-y-2">
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <SearchIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="text"
            placeholder={placeholder}
            value={searchQuery}
            onChange={handleInputChange}
            className="pl-10 pr-10"
            disabled={isLoading}
          />
          {searchQuery && (
            <button
              onClick={handleClear}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              aria-label="Clear search"
              disabled={isLoading}
            >
              <XIcon className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Search result count */}
      {debouncedQuery && resultCount !== undefined && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>
            Found <Badge variant="outline">{resultCount}</Badge> review
            {resultCount !== 1 ? "s" : ""}
          </span>
          {searchQuery && (
            <span className="text-xs">
              matching "{searchQuery}"
            </span>
          )}
        </div>
      )}

      {/* Loading indicator */}
      {isLoading && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-muted-foreground border-t-foreground" />
          <span>Searching...</span>
        </div>
      )}
    </div>
  );
}
