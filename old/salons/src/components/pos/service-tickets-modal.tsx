import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  useListServiceTickets,
  useUpdateTicketStatus,
  type ServiceTicket,
} from "@/lib/api/hooks/usePOS";
import { ClipboardListIcon, CheckCircleIcon, ClockIcon } from "@/components/icons";
import { toast } from "sonner";
import { formatCurrency } from "@/lib/utils/currency";

interface ServiceTicketsModalProps {
  open: boolean;
  onClose: () => void;
}

export function ServiceTicketsModal({
  open,
  onClose,
}: ServiceTicketsModalProps) {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [stylistFilter, setStylistFilter] = useState<string>("all");

  // Queries
  const { data: tickets, isLoading } = useListServiceTickets({
    status: statusFilter === "all" ? undefined : statusFilter,
  });

  // Mutations
  const updateStatus = useUpdateTicketStatus();

  const handleUpdateStatus = async (ticketId: string, newStatus: string) => {
    try {
      await updateStatus.mutateAsync({
        ticket_id: ticketId,
        status: newStatus,
      });
      toast.success("Ticket status updated");
    } catch (error) {
      toast.error("Failed to update ticket status");
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return <Badge variant="outline">Pending</Badge>;
      case "in_progress":
        return <Badge className="bg-blue-500">In Progress</Badge>;
      case "completed":
        return <Badge className="bg-green-500">Completed</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pending":
        return <ClockIcon className="h-4 w-4 text-[var(--accent)]" />;
      case "in_progress":
        return <ClipboardListIcon className="h-4 w-4 text-[var(--primary)]" />;
      case "completed":
        return <CheckCircleIcon className="h-4 w-4 text-[var(--primary)]" />;
      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Service Tickets</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Filters */}
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">Status</label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="in_progress">In Progress</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Tickets List */}
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading tickets...
            </div>
          ) : !tickets || tickets.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No service tickets found
            </div>
          ) : (
            <div className="space-y-3">
              {tickets.map((ticket: ServiceTicket) => (
                <div
                  key={ticket.id}
                  className="border rounded-lg p-4 space-y-3"
                >
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(ticket.status)}
                        <span className="font-semibold">
                          {ticket.ticket_number}
                        </span>
                        {getStatusBadge(ticket.status)}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Transaction: {ticket.transaction_number}
                      </div>
                    </div>
                    <div className="text-right text-sm">
                      <div className="font-medium">{ticket.client_name}</div>
                      {ticket.client_phone && (
                        <div className="text-muted-foreground">
                          {ticket.client_phone}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Items */}
                  <div className="space-y-1">
                    <div className="text-sm font-medium">Items:</div>
                    <div className="space-y-1">
                      {ticket.items.map((item, idx) => (
                        <div
                          key={idx}
                          className="text-sm text-muted-foreground flex justify-between"
                        >
                          <span>
                            {item.item_name} x{item.quantity}
                          </span>
                          <span>
                            {formatCurrency(item.price * item.quantity)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Stylist */}
                  {ticket.stylist_name && (
                    <div className="text-sm">
                      <span className="font-medium">Stylist:</span>{" "}
                      {ticket.stylist_name}
                    </div>
                  )}

                  {/* Notes */}
                  {ticket.notes && (
                    <div className="text-sm">
                      <span className="font-medium">Notes:</span> {ticket.notes}
                    </div>
                  )}

                  {/* Status Update */}
                  {ticket.status !== "completed" && (
                    <div className="flex gap-2 pt-2 border-t">
                      {ticket.status === "pending" && (
                        <Button
                          size="sm"
                          onClick={() =>
                            handleUpdateStatus(ticket.id, "in_progress")
                          }
                          disabled={updateStatus.isPending}
                        >
                          Start Work
                        </Button>
                      )}
                      {ticket.status === "in_progress" && (
                        <Button
                          size="sm"
                          onClick={() =>
                            handleUpdateStatus(ticket.id, "completed")
                          }
                          disabled={updateStatus.isPending}
                        >
                          Mark Complete
                        </Button>
                      )}
                    </div>
                  )}

                  {/* Completed timestamp */}
                  {ticket.completed_at && (
                    <div className="text-xs text-muted-foreground">
                      Completed:{" "}
                      {new Date(ticket.completed_at).toLocaleString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
