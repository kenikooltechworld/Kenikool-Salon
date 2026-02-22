import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  SearchIcon,
  DownloadIcon,
  AlertTriangleIcon,
  EyeIcon,
} from "@/components/icons";
import { usePayments } from "@/lib/api/hooks/usePayments";
import { format } from "date-fns";
import { ReceiptModal } from "@/components/payments/receipt-modal";
import type { ReceiptData } from "@/lib/utils/receipt";

export default function ReceiptsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedReceipt, setSelectedReceipt] = useState<ReceiptData | null>(
    null
  );

  const {
    data: payments,
    isLoading,
    error,
  } = usePayments({
    status: "completed",
  });

  const filteredPayments = payments?.filter(
    (payment) =>
      payment.reference.toLowerCase().includes(searchQuery.toLowerCase()) ||
      payment.booking_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleViewReceipt = (payment: any) => {
    // Transform payment data to receipt data
    const receiptData: ReceiptData = {
      receipt_number: payment.reference,
      booking_id: payment.booking_id,
      client_name: "Client Name", // TODO: Get from booking
      client_phone: "Client Phone", // TODO: Get from booking
      service_name: "Service Name", // TODO: Get from booking
      service_price: payment.amount,
      stylist_name: "Stylist Name", // TODO: Get from booking
      booking_date: payment.created_at,
      payment_method: payment.gateway,
      amount_paid: payment.amount,
      salon_name: "Kenikool Salon", // TODO: Get from tenant
      salon_address: "Salon Address", // TODO: Get from tenant
      salon_phone: "Salon Phone", // TODO: Get from tenant
      salon_email: "Salon Email", // TODO: Get from tenant
    };

    setSelectedReceipt(receiptData);
  };

  if (error) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Error loading receipts</h3>
          <p className="text-sm">{error.message}</p>
        </div>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Receipts</h1>
          <p className="text-muted-foreground">
            View and manage payment receipts
          </p>
        </div>
      </div>

      {/* Search */}
      <Card className="p-4">
        <div className="relative">
          <SearchIcon
            size={20}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by receipt number or booking ID..."
            className="pl-10"
          />
        </div>
      </Card>

      {/* Receipts List */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : filteredPayments && filteredPayments.length > 0 ? (
        <div className="grid grid-cols-1 gap-4">
          {filteredPayments.map((payment) => (
            <Card key={payment.id} className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-foreground">
                      Receipt #{payment.reference.slice(0, 12)}
                    </h3>
                    <Badge
                      className={
                        payment.status === "completed"
                          ? "bg-[var(--success)] text-white"
                          : "bg-muted text-muted-foreground"
                      }
                    >
                      {payment.status}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Booking ID</span>
                      <p className="font-medium text-foreground">
                        {payment.booking_id.slice(0, 8)}
                      </p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Amount</span>
                      <p className="font-medium text-foreground">
                        ₦{payment.amount.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Gateway</span>
                      <p className="font-medium text-foreground capitalize">
                        {payment.gateway}
                      </p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Date</span>
                      <p className="font-medium text-foreground">
                        {format(new Date(payment.created_at), "dd/MM/yyyy")}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleViewReceipt(payment)}
                  >
                    <EyeIcon size={16} />
                    View
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="p-12">
          <div className="text-center">
            <DownloadIcon
              size={48}
              className="mx-auto text-muted-foreground mb-4"
            />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              No receipts found
            </h3>
            <p className="text-muted-foreground">
              {searchQuery
                ? "Try adjusting your search"
                : "Receipts will appear here after payments are completed"}
            </p>
          </div>
        </Card>
      )}

      {/* Receipt Modal */}
      {selectedReceipt && (
        <ReceiptModal
          open={!!selectedReceipt}
          onClose={() => setSelectedReceipt(null)}
          receiptData={selectedReceipt}
        />
      )}
    </div>
  );
}
