"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState, useEffect } from "react";
import { Check } from "lucide-react";

interface FontOption {
  name: string;
  family: string;
  weights: number[];
  category: string;
}

interface FontPickerProps {
  fontFamily: string;
  onFontChange: (font: string) => void;
  onFontWeightChange?: (weight: number) => void;
  currentWeight?: number;
}

const GOOGLE_FONTS: FontOption[] = [
  {
    name: "Inter",
    family: "Inter, sans-serif",
    weights: [400, 500, 600, 700],
    category: "sans-serif",
  },
  {
    name: "Poppins",
    family: "Poppins, sans-serif",
    weights: [400, 500, 600, 700, 800],
    category: "sans-serif",
  },
  {
    name: "Roboto",
    family: "Roboto, sans-serif",
    weights: [400, 500, 700],
    category: "sans-serif",
  },
  {
    name: "Open Sans",
    family: "'Open Sans', sans-serif",
    weights: [400, 600, 700],
    category: "sans-serif",
  },
  {
    name: "Lato",
    family: "Lato, sans-serif",
    weights: [400, 700],
    category: "sans-serif",
  },
  {
    name: "Montserrat",
    family: "Montserrat, sans-serif",
    weights: [400, 600, 700],
    category: "sans-serif",
  },
  {
    name: "Playfair Display",
    family: "'Playfair Display', serif",
    weights: [400, 700],
    category: "serif",
  },
  {
    name: "Georgia",
    family: "Georgia, serif",
    weights: [400, 700],
    category: "serif",
  },
  {
    name: "Garamond",
    family: "Garamond, serif",
    weights: [400, 700],
    category: "serif",
  },
  {
    name: "Courier New",
    family: "'Courier New', monospace",
    weights: [400, 700],
    category: "monospace",
  },
];

const SYSTEM_FONTS: FontOption[] = [
  {
    name: "System Default",
    family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    weights: [400, 700],
    category: "system",
  },
  {
    name: "Arial",
    family: "Arial, sans-serif",
    weights: [400, 700],
    category: "sans-serif",
  },
  {
    name: "Helvetica",
    family: "Helvetica, sans-serif",
    weights: [400, 700],
    category: "sans-serif",
  },
  {
    name: "Times New Roman",
    family: "'Times New Roman', serif",
    weights: [400, 700],
    category: "serif",
  },
];

export function FontPicker({
  fontFamily,
  onFontChange,
  onFontWeightChange,
  currentWeight = 400,
}: FontPickerProps) {
  const [showFontList, setShowFontList] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedWeight, setSelectedWeight] = useState(currentWeight);
  const [fontsLoaded, setFontsLoaded] = useState(false);

  const allFonts = [...SYSTEM_FONTS, ...GOOGLE_FONTS];

  const filteredFonts = allFonts.filter((font) =>
    font.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const currentFont = allFonts.find((f) => f.family === fontFamily);

  // Load Google Fonts
  useEffect(() => {
    const loadGoogleFonts = () => {
      const fontNames = GOOGLE_FONTS.map((f) => f.name.replace(/\s+/g, "+")).join(
        "&family="
      );
      const link = document.createElement("link");
      link.href = `https://fonts.googleapis.com/css2?family=${fontNames}:wght@400;500;600;700;800&display=swap`;
      link.rel = "stylesheet";
      document.head.appendChild(link);
      setFontsLoaded(true);
    };

    loadGoogleFonts();
  }, []);

  const handleFontSelect = (font: FontOption) => {
    onFontChange(font.family);
    setShowFontList(false);
    setSearchTerm("");
  };

  const handleWeightChange = (weight: number) => {
    setSelectedWeight(weight);
    onFontWeightChange?.(weight);
  };

  const availableWeights = currentFont?.weights || [400, 700];

  return (
    <Card className="p-4">
      <h3 className="font-semibold mb-4">Font Picker</h3>

      <div className="space-y-4">
        {/* Font Selection */}
        <div>
          <Label htmlFor="font_family">Font Family</Label>
          <div className="relative mt-2">
            <Button
              variant="outline"
              className="w-full justify-between"
              onClick={() => setShowFontList(!showFontList)}
            >
              <span style={{ fontFamily: fontFamily }}>
                {currentFont?.name || "Select a font"}
              </span>
              <span className="text-gray-400">▼</span>
            </Button>

            {showFontList && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border rounded-lg shadow-lg z-50">
                {/* Search */}
                <div className="p-2 border-b sticky top-0 bg-white">
                  <Input
                    placeholder="Search fonts..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="text-sm"
                  />
                </div>

                {/* Font List */}
                <div className="max-h-64 overflow-y-auto">
                  {filteredFonts.length > 0 ? (
                    filteredFonts.map((font) => (
                      <button
                        key={font.family}
                        onClick={() => handleFontSelect(font)}
                        className="w-full text-left px-3 py-2 hover:bg-gray-100 flex items-center justify-between group"
                      >
                        <div>
                          <div
                            style={{ fontFamily: font.family }}
                            className="font-medium"
                          >
                            {font.name}
                          </div>
                          <div className="text-xs text-gray-500">{font.category}</div>
                        </div>
                        {fontFamily === font.family && (
                          <Check className="h-4 w-4 text-blue-500" />
                        )}
                      </button>
                    ))
                  ) : (
                    <div className="px-3 py-2 text-sm text-gray-500">
                      No fonts found
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Font Preview */}
        {currentFont && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="text-sm font-semibold mb-2">Preview</h4>
            <div
              style={{
                fontFamily: fontFamily,
                fontSize: "16px",
                lineHeight: "1.5",
              }}
            >
              <p className="mb-2">The quick brown fox jumps over the lazy dog</p>
              <p className="text-sm text-gray-600">
                ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789
              </p>
            </div>
          </div>
        )}

        {/* Font Weight Selection */}
        {currentFont && currentFont.weights.length > 1 && (
          <div>
            <Label>Font Weight</Label>
            <div className="flex gap-2 mt-2 flex-wrap">
              {availableWeights.map((weight) => (
                <Button
                  key={weight}
                  variant={selectedWeight === weight ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleWeightChange(weight)}
                  style={{
                    fontFamily: fontFamily,
                    fontWeight: weight,
                  }}
                >
                  {weight === 400
                    ? "Regular"
                    : weight === 500
                      ? "Medium"
                      : weight === 600
                        ? "Semibold"
                        : weight === 700
                          ? "Bold"
                          : weight === 800
                            ? "Extra Bold"
                            : weight}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Font Info */}
        {currentFont && (
          <div className="bg-blue-50 p-3 rounded-lg text-sm text-blue-900">
            <p>
              <strong>Category:</strong> {currentFont.category}
            </p>
            <p className="mt-1">
              <strong>Available weights:</strong> {currentFont.weights.join(", ")}
            </p>
          </div>
        )}

        {/* Font Categories */}
        <div className="pt-4 border-t">
          <h4 className="text-sm font-semibold mb-3">Font Categories</h4>
          <div className="grid grid-cols-2 gap-2">
            {["system", "sans-serif", "serif", "monospace"].map((category) => {
              const fontsInCategory = allFonts.filter(
                (f) => f.category === category
              );
              return (
                <div key={category} className="text-xs">
                  <p className="font-semibold capitalize mb-1">{category}</p>
                  <p className="text-gray-600">
                    {fontsInCategory.length} fonts
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </Card>
  );
}
