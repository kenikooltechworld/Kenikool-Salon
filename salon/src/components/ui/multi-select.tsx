import { useState, useRef, useEffect } from "react";
import { XIcon } from "@/components/icons";

interface MultiSelectOption {
  id: string;
  label: string;
  description?: string;
}

interface MultiSelectProps {
  options: MultiSelectOption[];
  selectedIds: string[];
  onChange: (selectedIds: string[]) => void;
  placeholder?: string;
  label?: string;
  disabled?: boolean;
}

export function MultiSelect({
  options,
  selectedIds,
  onChange,
  placeholder = "Select items...",
  label,
  disabled = false,
}: MultiSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const selectedOptions = options.filter((opt) => selectedIds.includes(opt.id));
  const availableOptions = options.filter(
    (opt) => !selectedIds.includes(opt.id),
  );

  const handleSelect = (optionId: string) => {
    if (!selectedIds.includes(optionId)) {
      onChange([...selectedIds, optionId]);
    }
    setIsOpen(false);
  };

  const handleRemove = (optionId: string) => {
    onChange(selectedIds.filter((id) => id !== optionId));
  };

  return (
    <div ref={containerRef} className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-foreground">
          {label}
        </label>
      )}

      <div className="space-y-2">
        {/* Display selected items as badges */}
        {selectedIds.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {selectedOptions.map((option) => (
              <div
                key={option.id}
                className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 border border-primary/20 rounded-full text-sm text-primary"
              >
                <span>{option.label}</span>
                <button
                  type="button"
                  onClick={() => handleRemove(option.id)}
                  disabled={disabled}
                  className="hover:bg-primary/20 rounded-full p-0.5 transition cursor-pointer disabled:opacity-50"
                  aria-label={`Remove ${option.label}`}
                >
                  <XIcon size={14} />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Dropdown trigger */}
        <div className="relative">
          <button
            type="button"
            onClick={() => !disabled && setIsOpen(!isOpen)}
            disabled={disabled}
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary text-sm text-left flex items-center justify-between disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span
              className={
                selectedIds.length === 0 ? "text-muted-foreground" : ""
              }
            >
              {selectedIds.length === 0
                ? placeholder
                : `${selectedIds.length} selected`}
            </span>
            <svg
              className={`w-4 h-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 14l-7 7m0 0l-7-7m7 7V3"
              />
            </svg>
          </button>

          {/* Dropdown menu */}
          {isOpen && availableOptions.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-border rounded-lg shadow-lg z-50 max-h-48 overflow-y-auto">
              {availableOptions.map((option) => (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => handleSelect(option.id)}
                  className="w-full px-3 py-2 text-left hover:bg-muted transition text-sm text-foreground flex flex-col"
                >
                  <span className="font-medium">{option.label}</span>
                  {option.description && (
                    <span className="text-xs text-muted-foreground">
                      {option.description}
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}

          {/* Empty state */}
          {isOpen && availableOptions.length === 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-border rounded-lg shadow-lg z-50 p-3 text-center text-sm text-muted-foreground">
              All items selected
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
