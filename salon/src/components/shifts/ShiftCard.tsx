import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Shift } from "@/hooks/useShifts";
import { formatDate, formatTime } from "@/lib/utils/format";

interface ShiftCardProps {
  shift: Shift;
  staffName: string;
  onEdit?: (shift: Shift) => void;
  onDelete?: (shiftId: string) => void;
}

const statusColors: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-800",
  in_progress: "bg-yellow-100 text-yellow-800",
  completed: "bg-green-100 text-green-800",
  cancelled: "bg-red-100 text-red-800",
};

export function ShiftCard({
  shift,
  staffName,
  onEdit,
  onDelete,
}: ShiftCardProps) {
  const startDate = new Date(shift.start_time);
  const endDate = new Date(shift.end_time);

  return (
    <Card className="p-4">
      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-lg">{staffName}</h3>
            <p className="text-sm text-gray-600">
              {formatDate(startDate)} - {formatTime(startDate)} to{" "}
              {formatTime(endDate)}
            </p>
          </div>
          <Badge className={statusColors[shift.status]}>
            {shift.status.replace("_", " ")}
          </Badge>
        </div>

        <div className="flex items-center justify-between border-t pt-3">
          <div>
            <p className="text-sm text-gray-600">Labor Cost</p>
            <p className="font-semibold">
              ₦{shift.labor_cost.toLocaleString()}
            </p>
          </div>
          <div className="flex gap-2">
            {onEdit && (
              <Button variant="outline" size="sm" onClick={() => onEdit(shift)}>
                Edit
              </Button>
            )}
            {onDelete && (
              <Button
                variant="destructive"
                size="sm"
                onClick={() => onDelete(shift.id)}
              >
                Delete
              </Button>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
