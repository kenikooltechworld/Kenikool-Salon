import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table } from "@/components/ui/table";
import {
  ChevronUpIcon,
  ChevronDownIcon,
  EditIcon,
  TrashIcon,
} from "@/components/icons";
import type { Booking } from "@/lib/api/types";

interface BookingListViewProps {
  bookings: Booking[];
  onBookingClick?: (booking: Booking) => void;
  onEdit?: (booking: Booking) => void;
  onDelete?: (booking: Booking) => void;
}

type SortField = "date" | "client" | "status" | "price";
type SortOrder = "asc" | "desc";

export function BookingListView({
  bookings,
  onBookingClick,
  onEdit,
  onDelete,
}: BookingListViewProps) {
  const [sortField, setSortField] = useState<SortField>("date");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("asc");
    }
  };

  const sortedBookings = [...bookings].sort((a, b) => {
    let aVal: any = a[sortField as keyof Booking];
    let bVal: any = b[sortField as keyof Booking];

    if (sortField === "date") {
      aVal = new Date(a.booking_date).getTime();
      bVal = new Date(b.booking_date).getTime();
    }

    if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
    if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
    return 0;
  });

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

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return sortOrder === "asc" ? (
      <ChevronUpIcon size={16} />
    ) : (
      <ChevronDownIcon size={16} />
    );
  };

  return (
    <div className="space-y-3 sm:space-y-4">
      <div className="overflow-x-auto -mx-3 sm:-mx-4 md:mx-0">
        <div className="px-3 sm:px-4 md:px-0">
          <Table>
            <thead>
              <tr>
                <th className="text-xs sm:text-sm">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort("client")}
                    className="flex items-center gap-1 text-xs sm:text-sm p-0 h-auto"
                  >
                    Client
                    <SortIcon field="client" />
                  </Button>
                </th>
                <th className="text-xs sm:text-sm">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort("date")}
                    className="flex items-center gap-1 text-xs sm:text-sm p-0 h-auto"
                  >
                    Date
                    <SortIcon field="date" />
                  </Button>
                </th>
                <th className="text-xs sm:text-sm hidden sm:table-cell">
                  Service
                </th>
                <th className="text-xs sm:text-sm hidden md:table-cell">
                  Stylist
                </th>
                <th className="text-xs sm:text-sm">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort("status")}
                    className="flex items-center gap-1 text-xs sm:text-sm p-0 h-auto"
                  >
                    Status
                    <SortIcon field="status" />
                  </Button>
                </th>
                <th className="text-xs sm:text-sm text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort("price")}
                    className="flex items-center gap-1 text-xs sm:text-sm p-0 h-auto ml-auto"
                  >
                    Price
                    <SortIcon field="price" />
                  </Button>
                </th>
                <th className="text-xs sm:text-sm text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedBookings.map((booking) => (
                <tr
                  key={booking.id}
                  onClick={() => onBookingClick?.(booking)}
                  className="cursor-pointer text-xs sm:text-sm"
                >
                  <td className="font-medium truncate">
                    {booking.client_name}
                  </td>
                  <td className="text-xs sm:text-sm whitespace-nowrap">
                    {new Date(booking.booking_date).toLocaleDateString()}
                  </td>
                  <td className="hidden sm:table-cell text-xs sm:text-sm truncate">
                    {booking.service_name}
                  </td>
                  <td className="hidden md:table-cell text-xs sm:text-sm truncate">
                    {booking.stylist_name}
                  </td>
                  <td>
                    <Badge
                      variant={getStatusVariant(booking.status)}
                      className="text-xs"
                    >
                      {booking.status}
                    </Badge>
                  </td>
                  <td className="text-right font-medium text-xs sm:text-sm whitespace-nowrap">
                    ₦{(booking.service_price || 0).toLocaleString()}
                  </td>
                  <td className="text-right">
                    <div className="flex gap-1 justify-end">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onEdit?.(booking);
                        }}
                        className="p-1 h-auto"
                      >
                        <EditIcon size={14} />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete?.(booking);
                        }}
                        className="p-1 h-auto"
                      >
                        <TrashIcon size={14} />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      </div>

      {sortedBookings.length === 0 && (
        <Card className="p-6 sm:p-8 text-center text-xs sm:text-sm text-muted-foreground">
          No bookings found
        </Card>
      )}
    </div>
  );
}
