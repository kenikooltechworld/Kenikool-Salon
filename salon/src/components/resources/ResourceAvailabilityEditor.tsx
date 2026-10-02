import { useState } from "react";
import { useResourceAvailability, useCreateResourceAvailability, useUpdateResourceAvailability, useDeleteResourceAvailability } from "@/hooks/useResourceOperations";
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
import { Trash2Icon, PlusIcon } from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface ResourceAvailabilityEditorProps {
  resourceId: string;
}

const DAYS = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

export default function ResourceAvailabilityEditor({
  resourceId,
}: ResourceAvailabilityEditorProps) {
  const { data: availabilities = [], isLoading } = useResourceAvailability(resourceId);
  const createAvailability = useCreateResourceAvailability();
  const updateAvailability = useUpdateResourceAvailability();
  const deleteAvailability = useDeleteResourceAvailability();

  const [newSlot, setNewSlot] = useState({
    day_of_week: "monday",
    start_time: "09:00",
    end_time: "17:00",
    is_recurring: true,
    is_active: true,
  });

  const handleAdd = () => {
    createAvailability.mutate(
      {
        resource_id: resourceId,
        ...newSlot,
      },
      {
        onSuccess: () => {
          setNewSlot({
            day_of_week: "monday",
            start_time: "09:00",
            end_time: "17:00",
            is_recurring: true,
            is_active: true,
          });
        },
      }
    );
  };

  const handleRemove = (id: string) => {
    deleteAvailability.mutate(id);
  };

  if (isLoading) {
    return <div className="space-y-3">Loading availability...</div>;
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base sm:text-lg">Add Availability Slot</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 sm:gap-4">
            <div>
              <Label>Day</Label>
              <Select
                value={newSlot.day_of_week}
                onValueChange={(value) =>
                  setNewSlot({ ...newSlot, day_of_week: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DAYS.map((day) => (
                    <SelectItem key={day} value={day}>
                      {day.charAt(0).toUpperCase() + day.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Start Time</Label>
              <Input
                type="time"
                value={newSlot.start_time}
                onChange={(e) =>
                  setNewSlot({ ...newSlot, start_time: e.target.value })
                }
              />
            </div>
            <div>
              <Label>End Time</Label>
              <Input
                type="time"
                value={newSlot.end_time}
                onChange={(e) =>
                  setNewSlot({ ...newSlot, end_time: e.target.value })
                }
              />
            </div>
            <div className="flex items-end sm:col-span-2 md:col-span-1">
              <Button onClick={handleAdd} className="w-full">
                <PlusIcon className="w-4 h-4 mr-2" />
                Add
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-2">
        {availabilities.map((slot) => (
          <Card key={slot.id}>
            <CardContent className="flex items-center justify-between py-3 sm:py-4">
              <div>
                <p className="font-medium text-sm sm:text-base">
                  {slot.day_of_week?.charAt(0).toUpperCase() + (slot.day_of_week?.slice(1) || "")}
                </p>
                <p className="text-sm text-muted-foreground">
                  {slot.start_time} - {slot.end_time}
                </p>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => handleRemove(slot.id)}
              >
                <Trash2Icon className="w-4 h-4" />
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
