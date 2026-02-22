import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Stylist } from "@/lib/api/types";

interface ScheduleTabProps {
  stylist: Stylist;
}

export function ScheduleTab({ stylist }: ScheduleTabProps) {
  if (
    !stylist.schedule?.working_hours ||
    stylist.schedule.working_hours.length === 0
  ) {
    return (
      <Card className="p-4 sm:p-6">
        <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4">
          Schedule
        </h2>
        <p className="text-muted-foreground">
          No schedule information available
        </p>
      </Card>
    );
  }

  return (
    <Card className="p-4 sm:p-6">
      <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4">
        Schedule
      </h2>
      <div className="space-y-3">
        {stylist.schedule.working_hours.map((wh: any, idx: number) => (
          <div key={idx} className="p-3 border border-border rounded-lg">
            <div className="flex justify-between items-center">
              <p className="font-medium capitalize">{wh.day}</p>
              {wh.is_working ? (
                <p className="text-sm text-muted-foreground">
                  {wh.start_time} - {wh.end_time}
                </p>
              ) : (
                <Badge variant="destructive">Off</Badge>
              )}
            </div>
          </div>
        ))}
        {stylist.schedule.break_start && stylist.schedule.break_end && (
          <div className="p-3 border border-border rounded-lg bg-muted/50">
            <p className="text-sm">
              <span className="font-medium">Break:</span>{" "}
              {stylist.schedule.break_start} - {stylist.schedule.break_end}
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}
