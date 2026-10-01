import { useState } from "react";
import {
  useResourceAssignments,
  useAssignResource,
  useReleaseResourceAssignment,
} from "@/hooks/useResourceOperations";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { useResources } from "@/hooks/useResources";

interface ResourceAssignmentsProps {
  appointmentId: string;
}

export default function ResourceAssignments({ appointmentId }: ResourceAssignmentsProps) {
  const { data: assignments = [], isLoading } = useResourceAssignments(appointmentId);
  const { data: resources = [] } = useResources();
  const assignResource = useAssignResource();
  const releaseAssignment = useReleaseResourceAssignment();

  const [selectedResourceId, setSelectedResourceId] = useState("");
  const [quantity, setQuantity] = useState(1);

  const handleAssign = () => {
    if (!selectedResourceId) return;
    assignResource.mutate(
      {
        appointment_id: appointmentId,
        resource_id: selectedResourceId,
        quantity_used: Number(quantity),
      },
      {
        onSuccess: () => {
          setSelectedResourceId("");
          setQuantity(1);
        },
      }
    );
  };

  const handleRelease = (assignmentId: string) => {
    releaseAssignment.mutate(assignmentId);
  };

  const availableResources = resources.filter(
    (r) => r.status === "active" && r.is_active && r.available_quantity >= quantity
  );

  if (isLoading) {
    return <div className="space-y-3">Loading assignments...</div>;
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Assign Resource</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>Resource</Label>
              <Select value={selectedResourceId} onValueChange={setSelectedResourceId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select resource" />
                </SelectTrigger>
                <SelectContent>
                  {availableResources.map((resource) => (
                    <SelectItem key={resource.id} value={resource.id}>
                      {resource.name} ({resource.available_quantity} available)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Quantity</Label>
              <Input
                type="number"
                min="1"
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
              />
            </div>
            <div className="flex items-end">
              <Button
                onClick={handleAssign}
                disabled={!selectedResourceId || assignResource.isPending}
                className="w-full"
              >
                Assign
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-2">
        {assignments.map((assignment) => (
          <Card key={assignment.id}>
            <CardContent className="flex items-center justify-between py-4">
              <div>
                <p className="font-medium">Resource ID: {assignment.resource_id}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Quantity: {assignment.quantity_used} | Status: {assignment.status}
                </p>
              </div>
              {assignment.status !== "released" && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleRelease(assignment.id)}
                >
                  Release
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
