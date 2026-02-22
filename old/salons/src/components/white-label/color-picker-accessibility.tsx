"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AlertCircle, CheckCircle, Lightbulb } from "lucide-react";
import { useState, useMemo } from "react";

interface ColorPickerAccessibilityProps {
  primaryColor: string;
  secondaryColor: string;
  onPrimaryChange: (color: string) => void;
  onSecondaryChange: (color: string) => void;
}

interface ContrastResult {
  ratio: number;
  level: "AAA" | "AA" | "fail";
  isCompliant: boolean;
}

// Calculate relative luminance
function getLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map((x) => {
    x = x / 255;
    return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

// Calculate contrast ratio
function getContrastRatio(color1: string, color2: string): number {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);

  if (!rgb1 || !rgb2) return 0;

  const lum1 = getLuminance(rgb1.r, rgb1.g, rgb1.b);
  const lum2 = getLuminance(rgb2.r, rgb2.g, rgb2.b);

  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);

  return (lighter + 0.05) / (darker + 0.05);
}

// Convert hex to RGB
function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

// Convert RGB to hex
function rgbToHex(r: number, g: number, b: number): string {
  return (
    "#" +
    [r, g, b]
      .map((x) => {
        const hex = x.toString(16);
        return hex.length === 1 ? "0" + hex : hex;
      })
      .join("")
      .toUpperCase()
  );
}

// Generate complementary color
function getComplementaryColor(hex: string): string {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  return rgbToHex(255 - rgb.r, 255 - rgb.g, 255 - rgb.b);
}

// Generate analogous colors
function getAnalogousColors(hex: string): string[] {
  const rgb = hexToRgb(hex);
  if (!rgb) return [];

  // Simple analogous color generation
  const colors = [];
  for (let i = -30; i <= 30; i += 30) {
    const hue = ((Math.atan2(rgb.g - 128, rgb.r - 128) * 180) / Math.PI + 360 + i) % 360;
    const angle = (hue * Math.PI) / 180;
    const r = Math.round(128 + 127 * Math.cos(angle));
    const g = Math.round(128 + 127 * Math.sin(angle));
    const b = Math.round(128 - 127 * Math.cos(angle));
    colors.push(rgbToHex(r, g, b));
  }
  return colors;
}

// Suggest accessible alternative
function suggestAccessibleAlternative(
  color: string,
  targetColor: string,
  targetRatio: number = 4.5
): string {
  const rgb = hexToRgb(color);
  if (!rgb) return color;

  // Try to adjust brightness to meet contrast ratio
  for (let brightness = 0; brightness <= 255; brightness += 5) {
    const testColor = rgbToHex(
      Math.min(255, rgb.r + brightness),
      Math.min(255, rgb.g + brightness),
      Math.min(255, rgb.b + brightness)
    );
    const ratio = getContrastRatio(testColor, targetColor);
    if (ratio >= targetRatio) {
      return testColor;
    }
  }

  return color;
}

export function ColorPickerAccessibility({
  primaryColor,
  secondaryColor,
  onPrimaryChange,
  onSecondaryChange,
}: ColorPickerAccessibilityProps) {
  const [showPalette, setShowPalette] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const contrastResult = useMemo((): ContrastResult => {
    const ratio = getContrastRatio(primaryColor, secondaryColor);
    return {
      ratio: Math.round(ratio * 100) / 100,
      level: ratio >= 7 ? "AAA" : ratio >= 4.5 ? "AA" : "fail",
      isCompliant: ratio >= 4.5,
    };
  }, [primaryColor, secondaryColor]);

  const suggestedSecondary = useMemo(
    () => suggestAccessibleAlternative(secondaryColor, primaryColor),
    [secondaryColor, primaryColor]
  );

  const analogousColors = useMemo(
    () => getAnalogousColors(primaryColor),
    [primaryColor]
  );

  const complementaryColor = useMemo(
    () => getComplementaryColor(primaryColor),
    [primaryColor]
  );

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <h3 className="font-semibold mb-4">Color Picker with Accessibility</h3>

        {/* Primary Color */}
        <div className="space-y-3 mb-6">
          <div>
            <Label htmlFor="primary_color">Primary Color</Label>
            <div className="flex gap-2 mt-2">
              <Input
                id="primary_color"
                value={primaryColor}
                onChange={(e) => onPrimaryChange(e.target.value)}
                placeholder="#FF6B6B"
                className="flex-1"
              />
              <input
                type="color"
                value={primaryColor}
                onChange={(e) => onPrimaryChange(e.target.value)}
                className="w-12 h-10 rounded border cursor-pointer"
              />
            </div>
          </div>

          {/* Secondary Color */}
          <div>
            <Label htmlFor="secondary_color">Secondary Color</Label>
            <div className="flex gap-2 mt-2">
              <Input
                id="secondary_color"
                value={secondaryColor}
                onChange={(e) => onSecondaryChange(e.target.value)}
                placeholder="#4ECDC4"
                className="flex-1"
              />
              <input
                type="color"
                value={secondaryColor}
                onChange={(e) => onSecondaryChange(e.target.value)}
                className="w-12 h-10 rounded border cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Contrast Ratio Display */}
        <div className="bg-gray-50 p-4 rounded-lg mb-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-sm">WCAG Contrast Ratio</h4>
            <div
              className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold ${
                contrastResult.isCompliant
                  ? "bg-green-100 text-green-800"
                  : "bg-red-100 text-red-800"
              }`}
            >
              {contrastResult.isCompliant ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <AlertCircle className="h-4 w-4" />
              )}
              {contrastResult.level}
            </div>
          </div>

          {/* Contrast Ratio Value */}
          <div className="text-2xl font-bold mb-2">{contrastResult.ratio}:1</div>

          {/* Compliance Info */}
          <div className="text-xs text-gray-600 space-y-1">
            <p>
              {contrastResult.isCompliant
                ? "✓ Meets WCAG AA standard (4.5:1 minimum)"
                : "✗ Does not meet WCAG AA standard (4.5:1 minimum)"}
            </p>
            {contrastResult.level === "AAA" && (
              <p>✓ Exceeds WCAG AAA standard (7:1 minimum)</p>
            )}
          </div>

          {/* Preview */}
          <div className="mt-4 space-y-2">
            <div
              className="p-3 rounded text-white font-semibold"
              style={{ backgroundColor: primaryColor, color: secondaryColor }}
            >
              Sample Text on Primary
            </div>
            <div
              className="p-3 rounded text-white font-semibold"
              style={{ backgroundColor: secondaryColor, color: primaryColor }}
            >
              Sample Text on Secondary
            </div>
          </div>
        </div>

        {/* Suggestions */}
        {!contrastResult.isCompliant && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
            <div className="flex gap-2">
              <Lightbulb className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-semibold text-sm text-yellow-900 mb-2">
                  Accessibility Suggestion
                </h4>
                <p className="text-sm text-yellow-800 mb-3">
                  Your color combination doesn't meet WCAG AA standards. Try this
                  alternative:
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onSecondaryChange(suggestedSecondary)}
                  className="text-yellow-900 border-yellow-300 hover:bg-yellow-100"
                >
                  Apply Suggested Color
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Color Palette Generator */}
        <div className="space-y-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowPalette(!showPalette)}
            className="w-full"
          >
            {showPalette ? "Hide" : "Show"} Color Palette Generator
          </Button>

          {showPalette && (
            <div className="bg-gray-50 p-4 rounded-lg space-y-3">
              <div>
                <h5 className="text-sm font-semibold mb-2">Complementary Color</h5>
                <div className="flex gap-2 items-center">
                  <div
                    className="w-12 h-12 rounded border"
                    style={{ backgroundColor: complementaryColor }}
                  />
                  <div className="flex-1">
                    <p className="text-sm font-mono">{complementaryColor}</p>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => onSecondaryChange(complementaryColor)}
                      className="text-xs mt-1"
                    >
                      Use as Secondary
                    </Button>
                  </div>
                </div>
              </div>

              <div>
                <h5 className="text-sm font-semibold mb-2">Analogous Colors</h5>
                <div className="flex gap-2 flex-wrap">
                  {analogousColors.map((color, idx) => (
                    <div key={idx} className="flex flex-col items-center gap-1">
                      <div
                        className="w-10 h-10 rounded border cursor-pointer hover:ring-2 ring-blue-500"
                        style={{ backgroundColor: color }}
                        onClick={() => onSecondaryChange(color)}
                        title={color}
                      />
                      <span className="text-xs text-gray-600">{color}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Color Blindness Simulation */}
        <div className="mt-4 pt-4 border-t">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSuggestions(!showSuggestions)}
            className="w-full"
          >
            {showSuggestions ? "Hide" : "Show"} Color Blindness Simulation
          </Button>

          {showSuggestions && (
            <div className="mt-3 space-y-2 text-xs">
              <p className="text-gray-600">
                Your colors should be distinguishable for users with color blindness.
                Consider using patterns or text labels in addition to colors.
              </p>
              <div className="grid grid-cols-2 gap-2">
                <div
                  className="p-2 rounded text-white text-center font-semibold"
                  style={{ backgroundColor: primaryColor }}
                >
                  Primary
                </div>
                <div
                  className="p-2 rounded text-white text-center font-semibold"
                  style={{ backgroundColor: secondaryColor }}
                >
                  Secondary
                </div>
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
