import { QRCodeDisplay } from "@/components/qr-code/qr-code-display";
import { Spinner } from "@/components/ui/spinner";
import { useTenant } from "@/lib/api/hooks/useTenant";

export default function QRCodePage() {
  const { data: tenant, isLoading } = useTenant();

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner />
      </div>
    );
  }

  if (!tenant) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">
          Unable to load salon information
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Booking QR Code</h1>
        <p className="text-muted-foreground">
          Share your booking page with customers using a QR code
        </p>
      </div>

      {/* QR Code Display */}
      <QRCodeDisplay
        subdomain={tenant.subdomain}
        salonName={tenant.salon_name}
        salonLogo={tenant.logo_url}
        brandColor={tenant.brand_color}
      />
    </div>
  );
}
