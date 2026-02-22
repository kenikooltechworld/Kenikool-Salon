import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useLookupBarcode } from "@/lib/api/hooks/usePOS";
import { toast } from "sonner";
import { ScanIcon, KeyboardIcon } from "@/components/icons";

interface BarcodeScannerProps {
  onItemScanned: (item: {
    id: string;
    name: string;
    price: number;
    type?: string;
    quantity?: number;
  }) => void;
}

export function BarcodeScanner({ onItemScanned }: BarcodeScannerProps) {
  const [barcode, setBarcode] = useState("");
  const [scanMode, setScanMode] = useState<"scanner" | "manual">("scanner");
  const [isListening, setIsListening] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);
  const lookupBarcode = useLookupBarcode();

  // Listen for barcode scanner input
  useEffect(() => {
    if (scanMode !== "scanner" || !isListening) return;

    let buffer = "";
    let timeout: NodeJS.Timeout;

    const handleKeyPress = (e: KeyboardEvent) => {
      // Ignore if user is typing in an input field
      if (
        document.activeElement?.tagName === "INPUT" ||
        document.activeElement?.tagName === "TEXTAREA"
      ) {
        return;
      }

      // Clear timeout
      clearTimeout(timeout);

      // Enter key indicates end of barcode scan
      if (e.key === "Enter") {
        if (buffer.length > 0) {
          handleBarcodeScanned(buffer);
          buffer = "";
        }
        return;
      }

      // Add character to buffer
      if (e.key.length === 1) {
        buffer += e.key;

        // Auto-submit after 100ms of no input (typical scanner behavior)
        timeout = setTimeout(() => {
          if (buffer.length > 0) {
            handleBarcodeScanned(buffer);
            buffer = "";
          }
        }, 100);
      }
    };

    window.addEventListener("keypress", handleKeyPress);

    return () => {
      window.removeEventListener("keypress", handleKeyPress);
      clearTimeout(timeout);
    };
  }, [scanMode, isListening]);

  const handleBarcodeScanned = async (scannedBarcode: string) => {
    try {
      const item = await lookupBarcode.mutateAsync(scannedBarcode);

      if (item) {
        onItemScanned(item);
        toast.success(`Added ${item.name} to cart`);
      } else {
        toast.error(`No item found for barcode: ${scannedBarcode}`);
      }
    } catch (error) {
      toast.error("Failed to lookup barcode");
    }
  };

  const handleManualSubmit = () => {
    if (barcode.trim()) {
      handleBarcodeScanned(barcode.trim());
      setBarcode("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleManualSubmit();
    }
  };

  return (
    <div className="space-y-3 p-4 border rounded-lg bg-card">
      <div className="flex items-center justify-between">
        <Label className="flex items-center gap-2">
          <ScanIcon className="h-4 w-4" />
          Barcode Scanner
        </Label>
        <Button
          variant="ghost"
          size="sm"
          onClick={() =>
            setScanMode(scanMode === "scanner" ? "manual" : "scanner")
          }
        >
          {scanMode === "scanner" ? (
            <>
              <KeyboardIcon className="h-4 w-4 mr-2" />
              Manual Entry
            </>
          ) : (
            <>
              <ScanIcon className="h-4 w-4 mr-2" />
              Scanner Mode
            </>
          )}
        </Button>
      </div>

      {scanMode === "scanner" ? (
        <div className="space-y-2">
          <div className="flex items-center gap-2 p-3 bg-muted rounded-md">
            <div className="flex-1">
              <p className="text-sm font-medium">
                {isListening ? "🟢 Scanner Ready" : "🔴 Scanner Paused"}
              </p>
              <p className="text-xs text-muted-foreground">
                Scan barcode with your scanner device
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsListening(!isListening)}
            >
              {isListening ? "Pause" : "Resume"}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            💡 Tip: Point scanner at barcode and press trigger
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex gap-2">
            <Input
              ref={inputRef}
              type="text"
              value={barcode}
              onChange={(e) => setBarcode(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter barcode manually..."
              className="flex-1"
            />
            <Button
              onClick={handleManualSubmit}
              disabled={!barcode.trim() || lookupBarcode.isPending}
            >
              {lookupBarcode.isPending ? "Looking up..." : "Scan"}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            💡 Tip: Type or paste barcode and press Enter
          </p>
        </div>
      )}
    </div>
  );
}
