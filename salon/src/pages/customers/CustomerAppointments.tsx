import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeftIcon } from "@/components/icons";
import { useCustomer } from "@/hooks/useCustomers";
import { useCustomerHistory } from "@/hooks/useCustomerHistory";
import { useState } from "react";

export default function CustomerAppointments() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 20;

  const { data: customer, isLoading: customerLoading } = useCustomer(id || "");
  const { data: history, isLoading: historyLoading } = useCustomerHistory(
    id || "",
    { page, page_size: PAGE_SIZE },
  );

  if (customerLoading) {
    return (
      <div className="space-y-4 sm:space-y-6">
        <div className="flex items-center gap-2 sm:gap-4">
          <Skeleton className="h-10 w-10 rounded" />
          <Skeleton className="h-8 w-48" />
        </div>
        <Card className="p-4 sm:p-6">
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-40" />
                <Skeleton className="h-4 w-32" />
              </div>
            ))}
          </div>
        </Card>
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-muted-foreground">Customer not found</div>
      </div>
    );
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2 sm:gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate(`/customers/${id}`)}
          className="gap-2 cursor-pointer"
        >
          <ArrowLeftIcon size={18} />
          <span className="hidden sm:inline">Back</span>
        </Button>
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-foreground">
            {customer.firstName} {customer.lastName}
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            Appointment History
          </p>
        </div>
      </div>

      {/* Appointments List */}
      <Card className="p-4 sm:p-6">
        {historyLoading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="space-y-2 pb-4 border-b border-border last:border-0"
              >
                <Skeleton className="h-4 w-40" />
                <Skeleton className="h-4 w-32" />
              </div>
            ))}
          </div>
        ) : history && history.length > 0 ? (
          <div className="space-y-4">
            {history.map((appointment) => (
              <div
                key={appointment.id}
                className="border-b border-border pb-4 last:border-0 cursor-pointer hover:bg-muted/50 p-3 rounded transition-colors"
                onClick={() =>
                  navigate(`/customers/${id}/appointments/${appointment.id}`)
                }
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm sm:text-base font-medium text-foreground">
                      {appointment.service_name}
                    </p>
                    <p className="text-xs sm:text-sm text-muted-foreground mt-1">
                      with {appointment.staff_name}
                    </p>
                    {appointment.notes && (
                      <p className="text-xs text-muted-foreground mt-2">
                        {appointment.notes}
                      </p>
                    )}
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <p className="text-xs sm:text-sm text-muted-foreground whitespace-nowrap">
                      {new Date(
                        appointment.appointment_date,
                      ).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {appointment.appointment_time}
                    </p>
                  </div>
                </div>
                {appointment.rating > 0 && (
                  <div className="mt-2">
                    <Badge variant="secondary">
                      Rating: {appointment.rating}/5
                    </Badge>
                  </div>
                )}
              </div>
            ))}

            {/* Pagination */}
            <div className="flex items-center justify-between mt-6 pt-4 border-t border-border">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">Page {page}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(page + 1)}
                disabled={history.length < PAGE_SIZE}
              >
                Next
              </Button>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-muted-foreground">No appointments found</p>
          </div>
        )}
      </Card>
    </div>
  );
}
