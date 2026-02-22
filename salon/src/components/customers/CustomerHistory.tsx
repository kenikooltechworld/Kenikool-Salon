import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AppointmentHistory } from "@/hooks/useCustomerHistory";
import { formatDate, formatTime } from "@/lib/utils/format";

interface CustomerHistoryProps {
  customerId: string;
  history: AppointmentHistory[];
  isLoading?: boolean;
  onViewDetails?: (historyId: string) => void;
}

export function CustomerHistory({
  customerId,
  history,
  isLoading = false,
  onViewDetails,
}: CustomerHistoryProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-gray-500">Loading history...</p>
      </div>
    );
  }

  if (!history || history.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-gray-500">No appointment history</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {history.map((item) => {
        const appointmentDate = new Date(item.appointment_date);
        const ratingPercentage = (item.rating / 5) * 100;

        return (
          <Card key={item.id} className="p-4">
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-lg">{item.service_name}</h3>
                  <p className="text-sm text-gray-600">
                    with {item.staff_name}
                  </p>
                </div>
                {item.rating > 0 && (
                  <div className="text-right">
                    <div className="flex items-center gap-1">
                      <span className="text-lg font-semibold">
                        {item.rating.toFixed(1)}
                      </span>
                      <span className="text-yellow-500">★</span>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>
                  {formatDate(appointmentDate)} at {formatTime(appointmentDate)}
                </span>
              </div>

              {item.notes && (
                <div className="bg-gray-50 p-3 rounded">
                  <p className="text-sm font-medium text-gray-700">Notes</p>
                  <p className="text-sm text-gray-600">{item.notes}</p>
                </div>
              )}

              {item.feedback && (
                <div className="bg-blue-50 p-3 rounded">
                  <p className="text-sm font-medium text-blue-700">Feedback</p>
                  <p className="text-sm text-blue-600">{item.feedback}</p>
                </div>
              )}

              {onViewDetails && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onViewDetails(item.id)}
                  className="w-full"
                >
                  View Details
                </Button>
              )}
            </div>
          </Card>
        );
      })}
    </div>
  );
}
