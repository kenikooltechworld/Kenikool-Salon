import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EditIcon, TrashIcon, PrinterIcon } from "@/components/icons";
import type { Booking } from "@/lib/api/types";

interface BookingDetailsModalProps {
  booking: Booking | null;
  isOpen: boolean;
  onClose: () => void;
  onEdit?: (booking: Booking) => void;
  onDelete?: (booking: Booking) => void;
}

export function BookingDetailsModal({
  booking,
  isOpen,
  onClose,
  onEdit,
  onDelete,
}: BookingDetailsModalProps) {
  if (!booking) return null;

  const getStatusVariant = (
    status: string,
  ): "default" | "secondary" | "destructive" | "outline" | "accent" => {
    switch (status) {
      case "confirmed":
        return "default";
      case "pending":
        return "accent";
      case "cancelled":
        return "destructive";
      case "completed":
        return "secondary";
      default:
        return "outline";
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Booking Details</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">{booking.client_name}</h3>
              <p className="text-sm text-muted-foreground">
                Booking ID: {booking.id}
              </p>
            </div>
            <Badge variant={getStatusVariant(booking.status)}>
              {booking.status}
            </Badge>
          </div>

          {/* Client Information */}
          <Card className="p-4">
            <h4 className="font-semibold mb-3">Client Information</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Name</p>
                <p className="font-medium">{booking.client_name}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Phone</p>
                <p className="font-medium">{booking.client_phone || "N/A"}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Email</p>
                <p className="font-medium">{booking.client_phone || "N/A"}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Booking Type</p>
                <p className="font-medium capitalize">Individual</p>
              </div>
            </div>
          </Card>

          {/* Service Information */}
          <Card className="p-4">
            <h4 className="font-semibold mb-3">Service Information</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Service</p>
                <p className="font-medium">{booking.service_name}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Stylist</p>
                <p className="font-medium">{booking.stylist_name}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Date & Time</p>
                <p className="font-medium">
                  {new Date(booking.booking_date).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Duration</p>
                <p className="font-medium">
                  {booking.duration_minutes || "N/A"} minutes
                </p>
              </div>
            </div>
          </Card>

          {/* Pricing Information */}
          <Card className="p-4">
            <h4 className="font-semibold mb-3">Pricing</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Service Price</span>
                <span className="font-medium">
                  ₦{(booking.service_price || 0).toLocaleString()}
                </span>
              </div>
              {booking.variant_name && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Variant</span>
                  <span className="font-medium">{booking.variant_name}</span>
                </div>
              )}
              <div className="flex justify-between border-t pt-2 font-semibold">
                <span>Total</span>
                <span>₦{(booking.service_price || 0).toLocaleString()}</span>
              </div>
            </div>
          </Card>

          {/* Notes */}
          {booking.notes && (
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Notes</h4>
              <p className="text-sm text-muted-foreground">{booking.notes}</p>
            </Card>
          )}

          {/* Actions */}
          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            <Button
              variant="outline"
              onClick={() => window.print()}
              className="flex items-center gap-2"
            >
              <PrinterIcon size={16} />
              Print
            </Button>
            {onEdit && (
              <Button
                onClick={() => {
                  onEdit(booking);
                  onClose();
                }}
                className="flex items-center gap-2"
              >
                <EditIcon size={16} />
                Edit
              </Button>
            )}
            {onDelete && (
              <Button
                variant="destructive"
                onClick={() => {
                  onDelete(booking);
                  onClose();
                }}
                className="flex items-center gap-2"
              >
                <TrashIcon size={16} />
                Delete
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
