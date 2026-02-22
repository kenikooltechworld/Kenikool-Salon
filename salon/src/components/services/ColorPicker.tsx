import { useState } from "react";
import { ChevronDownIcon } from "@/components/icons";

const PRESET_COLORS = [
  { name: "Blue", value: "#3B82F6" },
  { name: "Red", value: "#EF4444" },
  { name: "Green", value: "#10B981" },
  { name: "Amber", value: "#F59E0B" },
  { name: "Purple", value: "#8B5CF6" },
  { name: "Pink", value: "#EC4899" },
  { name: "Cyan", value: "#06B6D4" },
  { name: "Indigo", value: "#6366F1" },
  { name: "Teal", value: "#14B8A6" },
  { name: "Orange", value: "#F97316" },
  { name: "Slate", value: "#64748B" },
  { name: "Black", value: "#000000" },
];

interface ColorPickerProps {
  value: string;
  onChange: (color: string) => void;
}

export function ColorPicker({ value, onChange }: ColorPickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const selectedColor = PRESET_COLORS.find((c) => c.value === value);

  return (
    <div className="relative w-full">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary appearance-none cursor-pointer flex items-center justify-between"
      >
        <div className="flex items-center gap-2">
          {selectedColor && (
            <div
              className="w-5 h-5 rounded border border-border"
              style={{ backgroundColor: selectedColor.value }}
            />
          )}
          <span className="text-sm">
            {selectedColor?.name || "Select color"}
          </span>
        </div>
        <ChevronDownIcon
          size={16}
          className={`text-muted-foreground transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-background border border-border rounded-lg shadow-lg z-50">
          <div className="grid grid-cols-4 gap-2 p-3">
            {PRESET_COLORS.map((color) => (
              <button
                key={color.value}
                type="button"
                onClick={() => {
                  onChange(color.value);
                  setIsOpen(false);
                }}
                className="flex flex-col items-center gap-1 p-2 rounded-lg hover:bg-muted transition-colors"
                title={color.name}
              >
                <div
                  className={`w-8 h-8 rounded border-2 ${
                    value === color.value
                      ? "border-foreground"
                      : "border-border"
                  }`}
                  style={{ backgroundColor: color.value }}
                />
                <span className="text-xs text-center text-foreground">
                  {color.name}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
