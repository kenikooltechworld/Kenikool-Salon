import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  PlusIcon,
  ListIcon,
  CalendarIcon,
  PackageIcon,
} from "@/components/icons";
import { useToast } from "@/components/ui/toast";
import {
  useBookings,
  useConfirmBooking,
  useCancelBooking,
  useCompleteBooking,
  useMarkNoShow,
  useCollectPayment,
} from "@/hooks/useBookings";
import { useBookingsStore } from "@/stores/bookings";
import { BookingCard } from "@/components/bookings/BookingCard";
import { BookingList } from "@/components/bookings/BookingList";
import { BookingCalendar } from "@/components/bookings/BookingCalendar";
import { BookingDetail } from "@/pages/bookings/BookingDetail";

export default function Bookings() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [activeTab, setActiveTab] = useState(() => {
    // Load from localStorage on mount
    return localStorage.getItem("bookingsActiveTab") || "list";
  });

  // Save to localStorage whenever activeTab changes
  useEffect(() => {
    localStorage.setItem("bookingsActiveTab", activeTab);
  }, [activeTab]);

  const { filters, setFilters } = useBookingsStore();
  const { data: bookings = [], isLoading } = useBookings(filters);
  const { mutate: confirmBooking, isPending: isConfirming } =
    useConfirmBooking();
  const { mutate: cancelBooking, isPending: isCancelling } = useCancelBooking();
  const { mutate: completeBooking, isPending: isCompleting } =
    useCompleteBooking();
  const { mutate: markNoShow, isPending: isMarkingNoShow } = useMarkNoShow();
  const { mutate: collectPayment, isPending: isCollectingPayment } =
    useCollectPayment();
  const {
    isDetailModalOpen,
    setIsDetailModalOpen,
    selectedBookingId,
    setSelectedBookingId,
  } = useBookingsStore();

  const [isCollectPaymentModalOpen, setIsCollectPaymentModalOpen] =
    useState(false);
  const [selectedBookingForPayment, setSelectedBookingForPayment] =
    useState<any>(null);
  const [paymentMethod, setPaymentMethod] = useState("cash");
  const [paymentAmount, setPaymentAmount] = useState("");
  const [paymentNotes, setPaymentNotes] = useState("");

  const handleConfirm = (id: string) => {
    confirmBooking(id, {
      onSuccess: () => {
        addToast({
          title: "Success",
          description: "Appointment confirmed successfully",
          variant: "success",
        });
      },
      onError: () => {
        addToast({
          title: "Error",
          description: "Failed to confirm appointment",
          variant: "error",
        });
      },
    });
  };

  const handleCancel = (id: string) => {
    cancelBooking(
      { id, reason: "Cancelled by staff" },
      {
        onSuccess: () => {
          addToast({
            title: "Appointment Cancelled",
            description: "Appointment has been cancelled and refund initiated",
            variant: "success",
          });
        },
        onError: () => {
          addToast({
            title: "Error",
            description: "Failed to cancel appointment",
            variant: "error",
          });
        },
      },
    );
  };

  const handleComplete = (id: string) => {
    completeBooking(id, {
      onSuccess: () => {
        addToast({
          title: "Success",
          description: "Appointment marked as completed",
          variant: "success",
        });
      },
      onError: () => {
        addToast({
          title: "Error",
          description: "Failed to complete appointment",
          variant: "error",
        });
      },
    });
  };

  const handleMarkNoShow = (id: string) => {
    markNoShow(
      { id },
      {
        onSuccess: () => {
          addToast({
            title: "No-Show Recorded",
            description: "Appointment marked as no-show and refund initiated",
            variant: "success",
          });
        },
        onError: () => {
          addToast({
            title: "Error",
            description: "Failed to mark appointment as no-show",
            variant: "error",
          });
        },
      },
    );
  };

  const handleCollectPayment = (booking: any) => {
    setSelectedBookingForPayment(booking);
    setPaymentAmount(booking.price?.toString() || "");
    setPaymentMethod("cash");
    setPaymentNotes("");
    setIsCollectPaymentModalOpen(true);
  };

  const handleSubmitCollectPayment = () => {
    if (!selectedBookingForPayment) return;

    collectPayment(
      {
        id: selectedBookingForPayment.id,
        paymentMethod,
        amount: parseFloat(paymentAmount),
        notes: paymentNotes,
      },
      {
        onSuccess: () => {
          addToast({
            title: "Payment Collected",
            description: `Payment of ₦${paymentAmount} collected successfully`,
            variant: "success",
          });
          setIsCollectPaymentModalOpen(false);
          setSelectedBookingForPayment(null);
          setPaymentAmount("");
          setPaymentNotes("");
        },
        onError: () => {
          addToast({
            title: "Error",
            description: "Failed to collect payment",
            variant: "error",
          });
        },
      },
    );
  };

  const handleViewBooking = (id: string) => {
    setSelectedBookingId(id);
    setIsDetailModalOpen(true);
  };

  const isLoading_ =
    isLoading ||
    isConfirming ||
    isCancelling ||
    isCompleting ||
    isMarkingNoShow ||
    isCollectingPayment;

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-foreground">
            Bookings
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            Manage your bookings and appointments
          </p>
        </div>
        <Button
          onClick={() => navigate("/bookings/create")}
          className="gap-2 w-full sm:w-auto h-10 cursor-pointer"
        >
          <PlusIcon size={18} />
          New Booking
        </Button>
      </div>

      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="w-full"
        defaultValue="list"
      >
        <TabsList className="grid w-full grid-cols-3 h-10">
          <TabsTrigger
            value="list"
            className="text-xs sm:text-sm gap-2 cursor-pointer"
          >
            <ListIcon size={16} />
            <span className="hidden sm:inline">List View</span>
            <span className="sm:hidden">List</span>
          </TabsTrigger>
          <TabsTrigger
            value="calendar"
            className="text-xs sm:text-sm gap-2 cursor-pointer"
          >
            <CalendarIcon size={16} />
            <span className="hidden sm:inline">Calendar</span>
            <span className="sm:hidden">Cal</span>
          </TabsTrigger>
          <TabsTrigger
            value="cards"
            className="text-xs sm:text-sm gap-2 cursor-pointer"
          >
            <PackageIcon size={16} />
            <span className="hidden sm:inline">Card View</span>
            <span className="sm:hidden">Cards</span>
          </TabsTrigger>
        </TabsList>

        {/* List View */}
        <TabsContent value="list" className="space-y-4">
          <BookingList
            bookings={bookings}
            isLoading={isLoading}
            onViewBooking={handleViewBooking}
            onConfirmBooking={handleConfirm}
            onCancelBooking={handleCancel}
            filters={filters}
            onFiltersChange={setFilters}
            isConfirming={isConfirming}
            isCancelling={isCancelling}
          />
        </TabsContent>

        {/* Calendar View */}
        <TabsContent value="calendar" className="space-y-4">
          <BookingCalendar onBookingClick={handleViewBooking} />
        </TabsContent>

        {/* Card View */}
        <TabsContent value="cards" className="space-y-3 sm:space-y-4">
          {isLoading_ ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
              {[...Array(6)].map((_, i) => (
                <Card key={i} className="p-3 sm:p-4 space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-5 w-32" />
                      <Skeleton className="h-4 w-24" />
                    </div>
                    <Skeleton className="h-6 w-20 rounded-full flex-shrink-0" />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-2">
                      <Skeleton className="h-3 w-16" />
                      <Skeleton className="h-4 w-20" />
                    </div>
                    <div className="space-y-2">
                      <Skeleton className="h-3 w-16" />
                      <Skeleton className="h-4 w-20" />
                    </div>
                  </div>
                  <div className="flex gap-2 pt-2 border-t border-border">
                    <Skeleton className="flex-1 h-9" />
                    <Skeleton className="flex-1 h-9" />
                  </div>
                </Card>
              ))}
            </div>
          ) : bookings.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
               {bookings.map((booking: any) => (
                 <BookingCard
                   key={booking.id}
                   booking={booking}
                   onView={handleViewBooking}
                   onConfirm={handleConfirm}
                   onCancel={handleCancel}
                   onComplete={handleComplete}
                   onMarkNoShow={handleMarkNoShow}
                   onCollectPayment={handleCollectPayment}
                   isLoading={isLoading_}
                 />
               ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No bookings found
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Booking Detail Modal */}
      {isDetailModalOpen && selectedBookingId && (
        <BookingDetail
          bookingId={selectedBookingId}
          onClose={() => setIsDetailModalOpen(false)}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
          onComplete={handleComplete}
          onMarkNoShow={handleMarkNoShow}
        />
      )}

      {/* Collect Payment Modal */}
      {isCollectPaymentModalOpen && selectedBookingForPayment && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle>Collect Payment</CardTitle>
              <CardDescription>
                Record payment for booking #{selectedBookingForPayment.id.slice(0, 8)}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="payment-method">Payment Method</Label>
                <select
                  id="payment-method"
                  value={paymentMethod}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  className="w-full p-2 border border-border rounded-md bg-background"
                >
                  <option value="cash">Cash</option>
                  <option value="card">Card</option>
                  <option value="mobile_money">Mobile Money</option>
                  <option value="check">Check</option>
                  <option value="bank_transfer">Bank Transfer</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="payment-amount">Amount (₦)</Label>
                <Input
                  id="payment-amount"
                  type="number"
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                  placeholder="0.00"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="payment-notes">Notes (Optional)</Label>
                <textarea
                  id="payment-notes"
                  value={paymentNotes}
                  onChange={(e) => setPaymentNotes(e.target.value)}
                  placeholder="Payment notes..."
                  className="w-full p-2 border border-border rounded-md bg-background min-h-[80px]"
                />
              </div>

              <div className="flex gap-2 pt-4">
                <Button
                  onClick={handleSubmitCollectPayment}
                  disabled={isCollectingPayment || !paymentAmount}
                  className="flex-1 cursor-pointer"
                >
                  {isCollectingPayment ? "Processing..." : "Collect Payment"}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setIsCollectPaymentModalOpen(false)}
                  disabled={isCollectingPayment}
                  className="cursor-pointer"
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
