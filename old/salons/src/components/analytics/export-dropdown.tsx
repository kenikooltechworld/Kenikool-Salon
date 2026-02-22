import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { DownloadIcon } from "@/components/icons";

interface ExportOption {
  label: string;
  onClick: () => void;
}

interface ExportDropdownProps {
  options: ExportOption[];
}

export function ExportDropdown({ options }: ExportDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <Button onClick={() => setIsOpen(!isOpen)}>
        <DownloadIcon size={20} />
        Export Report
      </Button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-[var(--card)] border border-[var(--border)] rounded-lg shadow-lg z-50">
          <div className="py-1">
            {options.map((option, index) => (
              <button
                key={index}
                onClick={() => {
                  option.onClick();
                  setIsOpen(false);
                }}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm text-foreground hover:bg-muted transition-colors"
              >
                <DownloadIcon size={16} className="text-muted-foreground" />
                {option.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
