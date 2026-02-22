import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalBody,
  ModalFooter,
} from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ScannedProduct {
  barcode: string;
  product: any;
  quantity_change: number;
}

interface BarcodeScannerProps {
  isOpen: boolean;
  onClose: () => void;
  onProductScanned?: (product: any) => void;
}

export function BarcodeScanner({
  isOpen,
  onClose,
  onProductScanned,
}: BarcodeScannerProps) {
  const { toast } = useToast();
  const [barcodeInput, setBarcodeInput] = useState("");
  const [scannedProducts, setScannedProducts] = useState<ScannedProduct[]>([]);
  const [useCamera, setUseCamera] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scanMutation = useMutation({
    mutationFn: async (barcode: string) => {
      const res = await apiClient.get(`/api/inventory/scan/${barcode}`);
      return res.data;
    },
    onSuccess: (data) => {
      const product = data.product;
      setScannedProducts([
        ...scannedProducts,
        {
          barcode: barcodeInput,
          product,
          quantity_change: 1,
        },
      ]);
      toast(`Scanned: ${product.name}`, "success");
      setBarcodeInput("");
      onProductScanned?.(product);
      inputRef.current?.focus();
    },
    onError: (error: any) => {
      toast(
        error.response?.data?.detail || "Product not found",
        "error"
      );
      setBarcodeInput("");
    },
  });

  const handleScan = async () => {
    if (!barcodeInput.trim()) {
      toast("Please enter or scan a barcode", "error");
      return;
    }

    await scanMutation.mutateAsync(barcodeInput);
  };

  const handleRemoveProduct = (index: number) => {
    setScannedProducts(scannedProducts.filter((_, i) => i !== index));
  };

  const handleQuantityChange = (index: number, newQuantity: number) => {
    const updated = [...scannedProducts];
    updated[index].quantity_change = Math.max(1, newQuantity);
    setScannedProducts(updated);
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setUseCamera(true);
      }
    } catch (error) {
      toast("Camera access denied", "error");
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach((track) => track.stop());
      setUseCamera(false);
    }
  };

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <ModalHeader>
        <ModalTitle>Barcode Scanner</ModalTitle>
      </ModalHeader>

      <ModalBody className="space-y-6">
        {/* Scan Input */}
        <div className="space-y-2">
          <Label>Barcode/SKU</Label>
          <div className="flex gap-2">
            <Input
              ref={inputRef}
              value={barcodeInput}
              onChange={(e) => setBarcodeInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter") {
                  handleScan();
                }
              }}
              placeholder="Scan or enter barcode"
              disabled={scanMutation.isPending}
            />
            <Button
              onClick={handleScan}
              disabled={scanMutation.isPending || !barcodeInput.trim()}
            >
              {scanMutation.isPending ? "Scanning..." : "Scan"}
            </Button>
          </div>
        </div>

        {/* Camera Option */}
        <div>
          <Button
            onClick={useCamera ? stopCamera : startCamera}
            variant="outline"
            className="w-full"
          >
            {useCamera ? "Stop Camera" : "Use Camera"}
          </Button>
          {useCamera && (
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full mt-2 rounded border border-[var(--border)]"
            />
          )}
        </div>

        {/* Scanned Products */}
        {scannedProducts.length > 0 && (
          <div className="space-y-3">
            <h3 className="font-semibold text-[var(--foreground)]">
              Scanned Products ({scannedProducts.length})
            </h3>
            {scannedProducts.map((item, index) => (
              <Card key={index}>
                <CardContent className="pt-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-medium text-[var(--foreground)]">
                        {item.product.name}
                      </h4>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        SKU: {item.product.sku}
                      </p>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        Current Stock: {item.product.quantity}
                      </p>
                    </div>
                    <Badge variant="secondary">{item.barcode}</Badge>
                  </div>

                  <div className="flex items-center gap-2">
                    <Label className="text-xs">Qty:</Label>
                    <Input
                      type="number"
                      value={item.quantity_change}
                      onChange={(e) =>
                        handleQuantityChange(index, parseInt(e.target.value) || 1)
                      }
                      min="1"
                      className="w-20"
                    />
                    <Button
                      onClick={() => handleRemoveProduct(index)}
                      variant="destructive"
                      size="sm"
                    >
                      Remove
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </ModalBody>

      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          Close
        </Button>
        <Button
          onClick={() => {
            toast(`${scannedProducts.length} products ready for processing`, "success");
            onClose();
          }}
          disabled={scannedProducts.length === 0}
        >
          Done ({scannedProducts.length})
        </Button>
      </ModalFooter>
    </Modal>
  );
}
