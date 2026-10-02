import { useState } from "react";
import {
  useResourceMaintenance,
  useScheduleMaintenance,
  useCompleteMaintenance,
} from "@/hooks/useResourceOperations";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CalendarIcon } from "@/components/icons";

interface ResourceMaintenanceScheduleProps {
  resourceId?: string;
}

export default function ResourceMaintenanceSchedule({
  resourceId,
}: ResourceMaintenanceScheduleProps) {
  const { data: maintenanceRecords = [], isLoading } = useResourceMaintenance(resourceId);
  const scheduleMaintenance = useScheduleMaintenance();
  const completeMaintenance = useCompleteMaintenance();

  const [formData, setFormData] = useState({
    resource_id: resourceId || "",
    maintenance_type: "cleaning",
    scheduled_date: "",
    estimated_duration_hours: 1,
    description: "",
    cost: 0,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    scheduleMaintenance.mutate(formData, {
      onSuccess: () => {
        setFormData({
          resource_id: resourceId || "",
          maintenance_type: "cleaning",
          scheduled_date: "",
          estimated_duration_hours: 1,
          description: "",
          cost: 0,
        });
      },
    });
  };

  const handleComplete = (maintenanceId: string) => {
    completeMaintenance.mutate(maintenanceId);
  };

  return (
    <div className="space-y-4">
      {!resourceId && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base sm:text-lg">Schedule Maintenance</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4">
              <div>
                <Label>Resource ID</Label>
                <Input
                  value={formData.resource_id}
                  onChange={(e) =>
                    setFormData({ ...formData, resource_id: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <Label>Maintenance Type</Label>
                <Select
                  value={formData.maintenance_type}
                  onValueChange={(value) =>
                    setFormData({ ...formData, maintenance_type: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="cleaning">Cleaning</SelectItem>
                    <SelectItem value="repair">Repair</SelectItem>
                    <SelectItem value="inspection">Inspection</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Scheduled Date</Label>
                <Input
                  type="datetime-local"
                  value={formData.scheduled_date}
                  onChange={(e) =>
                    setFormData({ ...formData, scheduled_date: e.target.value })
                  }
                  required
                />
              </div>
              <div>
                <Label>Estimated Duration (hours)</Label>
                <Input
                  type="number"
                  min="1"
                  value={formData.estimated_duration_hours}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      estimated_duration_hours: Number(e.target.value),
                    })
                  }
                />
              </div>
              <div>
                <Label>Description</Label>
                <Input
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                />
              </div>
              <div>
                <Label>Cost (₦)</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.cost}
                  onChange={(e) =>
                    setFormData({ ...formData, cost: Number(e.target.value) })
                  }
                />
              </div>
              <Button type="submit" disabled={scheduleMaintenance.isPending}>
                Schedule Maintenance
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="space-y-2">
        {maintenanceRecords.map((record) => (
          <Card key={record.id}>
            <CardContent className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 py-3 sm:py-4">
              <div>
                <p className="font-medium text-sm sm:text-base">{record.maintenance_type}</p>
                <p className="text-sm text-muted-foreground">
                  {new Date(record.scheduled_date).toLocaleString()} | Status: {record.status}
                </p>
                {record.description && (
                  <p className="text-xs text-muted-foreground">{record.description}</p>
                )}
              </div>
              {record.status !== "completed" && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleComplete(record.id)}
                  className="w-full sm:w-auto"
                >
                  Complete
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
