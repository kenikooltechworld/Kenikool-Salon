/**
 * AddressAutocomplete Component
 *
 * Provides real-time address suggestions using backend Mapbox Places API.
 * Features:
 * - Debounced input (300ms) to reduce API calls
 * - Dropdown suggestions with formatted addresses
 * - Selection handler to populate address field
 * - Comprehensive error handling with retry logic
 * - Loading states and error boundaries
 * - Keyboard navigation support
 * - Theme-aware UI using custom component library
 *
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 6.1, 6.2, 6.3, 6.4, 6.5
 */

import React, { useState, useCallback, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils/cn";

/**
 * Simple debounce utility function
 */
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Retry logic with exponential backoff
 */
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  initialDelayMs: number = 1000,
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (attempt < maxRetries - 1) {
        const delayMs = initialDelayMs * Math.pow(2, attempt);
        await new Promise((resolve) => setTimeout(resolve, delayMs));
      }
    }
  }

  throw lastError || new Error("Max retries exceeded");
}

interface AddressSuggestion {
  formatted_address: string;
  place_id: string;
  place_type: string[];
  latitude?: number;
  longitude?: number;
}

interface AddressAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect: (suggestion: AddressSuggestion) => void;
  placeholder?: string;
  country?: string;
  disabled?: boolean;
  className?: string;
  error?: boolean;
  errorMessage?: string;
  proximity?: { latitude: number; longitude: number };
  bbox?: { minLon: number; minLat: number; maxLon: number; maxLat: number };
}

export const AddressAutocomplete: React.FC<AddressAutocompleteProps> = ({
  value,
  onChange,
  onSelect,
  placeholder = "Enter address...",
  country,
  disabled = false,
  className = "",
  error = false,
  errorMessage,
  proximity,
  bbox,
}) => {
  const [suggestions, setSuggestions] = useState<AddressSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [retryCount, setRetryCount] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Debounced autocomplete function with retry logic
  const fetchSuggestions = useCallback(
    debounce(async (query: string) => {
      if (!query || query.length < 2) {
        setSuggestions([]);
        setIsOpen(false);
        setApiError(null);
        return;
      }

      setIsLoading(true);
      setApiError(null);
      setRetryCount(0);

      // Cancel previous request if still pending
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      abortControllerRef.current = new AbortController();

      try {
        const result = await retryWithBackoff(
          async () => {
            const params = new URLSearchParams({
              query,
              limit: "5",
            });

            if (country) {
              params.append("country", country);
            }

            // Add proximity bias for better results
            if (proximity) {
              params.append(
                "proximity",
                `${proximity.longitude},${proximity.latitude}`,
              );
            }

            // Add bounding box to limit results to a geographic area
            if (bbox) {
              params.append(
                "bbox",
                `${bbox.minLon},${bbox.minLat},${bbox.maxLon},${bbox.maxLat}`,
              );
            }

            const response = await fetch(
              `/api/locations/autocomplete?${params}`,
              {
                method: "GET",
                headers: {
                  "Content-Type": "application/json",
                },
                signal: abortControllerRef.current?.signal,
              },
            );

            if (!response.ok) {
              if (response.status === 429) {
                throw new Error("Rate limited. Please try again in a moment.");
              } else if (response.status === 503) {
                throw new Error(
                  "Address search service temporarily unavailable",
                );
              } else if (response.status === 408 || response.status === 504) {
                throw new Error("Request timeout. Please try again.");
              } else {
                throw new Error(`Autocomplete failed: ${response.statusText}`);
              }
            }

            const data = await response.json();
            return data;
          },
          3, // max retries
          1000, // initial delay
        );

        setSuggestions(result.suggestions || []);
        setIsOpen(result.suggestions && result.suggestions.length > 0);
        setSelectedIndex(-1);
        setRetryCount(0);
      } catch (err) {
        // Don't show error if request was aborted
        if (err instanceof Error && err.name === "AbortError") {
          return;
        }

        const errorMsg =
          err instanceof Error ? err.message : "Failed to fetch suggestions";
        setApiError(errorMsg);
        setSuggestions([]);
        setIsOpen(false);
      } finally {
        setIsLoading(false);
      }
    }, 300),
    [country, proximity, bbox],
  );

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    setRetryCount(0);
    fetchSuggestions(newValue);
  };

  // Handle suggestion selection
  const handleSelectSuggestion = (suggestion: AddressSuggestion) => {
    onChange(suggestion.formatted_address);
    onSelect(suggestion);
    setSuggestions([]);
    setIsOpen(false);
    setSelectedIndex(-1);
    setApiError(null);
  };

  // Handle clear button
  const handleClear = () => {
    onChange("");
    setSuggestions([]);
    setIsOpen(false);
    setApiError(null);
    setSelectedIndex(-1);
    setRetryCount(0);
    inputRef.current?.focus();
  };

  // Handle retry
  const handleRetry = () => {
    setRetryCount(retryCount + 1);
    fetchSuggestions(value);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || suggestions.length === 0) {
      return;
    }

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : prev,
        );
        break;
      case "ArrowUp":
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case "Enter":
        e.preventDefault();
        if (selectedIndex >= 0) {
          handleSelectSuggestion(suggestions[selectedIndex]);
        }
        break;
      case "Escape":
        e.preventDefault();
        setIsOpen(false);
        setSelectedIndex(-1);
        break;
      default:
        break;
    }
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        inputRef.current &&
        !inputRef.current.contains(event.target as Node) &&
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Scroll selected item into view
  useEffect(() => {
    if (selectedIndex >= 0 && suggestionsRef.current) {
      const selectedElement = suggestionsRef.current.children[
        selectedIndex
      ] as HTMLElement;
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: "nearest" });
      }
    }
  }, [selectedIndex]);

  // Cleanup abort controller on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return (
    <div className={cn("relative w-full", className)}>
      {/* Input Field with Loading and Clear States */}
      <div className="relative flex items-center">
        <Input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => value && suggestions.length > 0 && setIsOpen(true)}
          placeholder={placeholder}
          disabled={disabled || isLoading}
          error={error || !!apiError}
          autoComplete="off"
          aria-autocomplete="list"
          aria-expanded={isOpen}
          aria-controls="address-suggestions"
          className="pr-10"
        />
        {isLoading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <Spinner size="sm" variant="primary" />
          </div>
        )}
        {value && !isLoading && (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={handleClear}
            className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8"
            aria-label="Clear address"
          >
            ✕
          </Button>
        )}
      </div>

      {/* Error Message with Retry */}
      {(apiError || errorMessage) && (
        <div
          className="mt-2 p-2 bg-[var(--error)]/10 border border-[var(--error)] rounded text-sm text-[var(--error)]"
          role="alert"
        >
          <div className="flex items-center justify-between">
            <span>{apiError || errorMessage}</span>
            {apiError && retryCount < 3 && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleRetry}
                className="text-xs"
              >
                Retry
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Suggestions Dropdown */}
      {isOpen && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          id="address-suggestions"
          className="absolute top-full left-0 right-0 mt-1 bg-[var(--card)] border-2 border-[var(--border)] rounded-[var(--radius-md)] shadow-[var(--shadow-lg)] z-50 max-h-64 overflow-y-auto animate-in fade-in-0 zoom-in-95"
          role="listbox"
        >
          {suggestions.map((suggestion, index) => (
            <Button
              key={suggestion.place_id}
              type="button"
              variant="ghost"
              onClick={() => handleSelectSuggestion(suggestion)}
              className={cn(
                "w-full justify-start text-left px-4 py-3 rounded-none border-b border-[var(--border)] last:border-b-0 hover:bg-[var(--muted)]",
                index === selectedIndex &&
                  "bg-[var(--primary)]/10 text-[var(--primary)] hover:bg-[var(--primary)]/20",
              )}
              role="option"
              aria-selected={index === selectedIndex}
            >
              <div className="flex flex-col gap-1 w-full">
                <div className="font-medium text-sm">
                  {suggestion.formatted_address}
                </div>
                {suggestion.place_type && suggestion.place_type.length > 0 && (
                  <div className="text-xs text-[var(--muted-foreground)] capitalize">
                    {suggestion.place_type[0]}
                  </div>
                )}
              </div>
            </Button>
          ))}
        </div>
      )}

      {/* No Results Message */}
      {isOpen &&
        !isLoading &&
        suggestions.length === 0 &&
        value &&
        !apiError && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-[var(--card)] border-2 border-[var(--border)] rounded-[var(--radius-md)] p-4 text-center text-sm text-[var(--muted-foreground)] z-50 animate-in fade-in-0 zoom-in-95">
            No addresses found for "{value}"
          </div>
        )}
    </div>
  );
};

export default AddressAutocomplete;
