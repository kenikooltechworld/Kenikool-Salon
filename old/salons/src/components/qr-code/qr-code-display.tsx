import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { DownloadIcon, AlertTriangleIcon, CheckIcon } from "@/components/icons";
import {
  generateQRCode,
  downloadQRCode,
  getBookingPageUrl,
} from "@/lib/utils/qr-code";

interface QRCodeDisplayProps {
  subdomain: string;
  salonName: string;
  salonLogo?: string;
  brandColor?: string;
}

export function QRCodeDisplay({
  subdomain,
  salonName,
  salonLogo,
  brandColor = "#6366f1",
}: QRCodeDisplayProps) {
  const [qrCodeUrl, setQrCodeUrl] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [copied, setCopied] = useState(false);

  const bookingUrl = getBookingPageUrl(subdomain);

  useEffect(() => {
    generateQR();
  }, [subdomain, brandColor]);

  const generateQR = async () => {
    setIsLoading(true);
    setError("");

    try {
      const dataUrl = await generateQRCode(bookingUrl, {
        width: 400,
        margin: 2,
        color: {
          dark: brandColor,
          light: "#FFFFFF",
        },
      });
      setQrCodeUrl(dataUrl);
    } catch (err) {
      setError("Failed to generate QR code. Please try again.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (qrCodeUrl) {
      downloadQRCode(qrCodeUrl, `${subdomain}-booking-qr.png`);
    }
  };

  const handleCopyUrl = () => {
    navigator.clipboard.writeText(bookingUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <p>Failed to generate QR code</p>
        </Alert>
      )}

      {copied && (
        <Alert variant="success">
          <CheckIcon size={20} />
          <p>URL copied!</p>
        </Alert>
      )}

      <Card className="p-8">
        <div className="text-center">
          {salonLogo && (
            <img
              src={salonLogo}
              alt={salonName}
              className="w-24 h-24 mx-auto mb-4 rounded-lg object-cover"
            />
          )}
          <h2 className="text-2xl font-bold text-foreground mb-2">
            {salonName}
          </h2>
          <p className="text-muted-foreground mb-6">Scan to Book</p>

          {isLoading ? (
            <div className="flex justify-center py-12">
              <Spinner />
            </div>
          ) : qrCodeUrl ? (
            <div className="inline-block p-6 bg-white rounded-lg">
              <img
                src={qrCodeUrl}
                alt="Booking QR Code"
                className="w-full max-w-md mx-auto"
              />
            </div>
          ) : null}

          <div className="mt-6 p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground mb-2">Booking URL:</p>
            <p className="font-mono text-sm text-foreground break-all">
              {bookingUrl}
            </p>
          </div>

          <div className="flex flex-wrap gap-3 justify-center mt-6">
            <Button onClick={handleDownload} disabled={!qrCodeUrl}>
              <DownloadIcon size={16} />
              Download
            </Button>
            <Button variant="outline" onClick={handleCopyUrl}>
              Copy URL
            </Button>
            <Button variant="outline" onClick={handlePrint}>
              Print
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
