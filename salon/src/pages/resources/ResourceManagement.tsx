import { useState } from "react";
import ResourceList from "@/components/resources/ResourceList";
import ResourceForm from "@/components/resources/ResourceForm";
import ResourceAvailabilityEditor from "@/components/resources/ResourceAvailabilityEditor";
import ResourceAssignments from "@/components/resources/ResourceAssignments";
import ResourceMaintenanceSchedule from "@/components/resources/ResourceMaintenanceSchedule";
import ResourceUtilization from "@/components/resources/ResourceUtilization";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function ResourceManagement() {
  const [activeTab, setActiveTab] = useState("list");
  const [editingResourceId, setEditingResourceId] = useState<
    string | undefined
  >();
  const [selectedResourceId, setSelectedResourceId] = useState<string>("");
  const [selectedAppointmentId, setSelectedAppointmentId] = useState<string>("");

  const handleEdit = (resourceId: string) => {
    setEditingResourceId(resourceId);
    setActiveTab("edit");
  };

  const handleFormSuccess = () => {
    setEditingResourceId(undefined);
    setActiveTab("list");
  };

  return (
    <div className="max-w-6xl mx-auto p-3 sm:p-4 md:p-6">
      <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-foreground mb-1 sm:mb-2">
        Resource Management
      </h1>
      <p className="text-xs sm:text-sm md:text-base text-muted-foreground mb-4 sm:mb-6">
        Manage physical resources, equipment, and supplies
      </p>

      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        defaultValue="list"
        className="w-full"
      >
        <TabsList className="flex w-full overflow-x-auto snap-x snap-mandatory gap-1 rounded-lg bg-muted p-1 sm:grid sm:grid-cols-4 md:grid-cols-7">
          <TabsTrigger
            value="list"
            className="flex-shrink-0 snap-start text-xs sm:text-sm"
          >
            Resources
          </TabsTrigger>
          <TabsTrigger
            value="create"
            className="flex-shrink-0 snap-start text-xs sm:text-sm"
          >
            Create
          </TabsTrigger>
          {editingResourceId && (
            <TabsTrigger
              value="edit"
              className="flex-shrink-0 snap-start text-xs sm:text-sm"
            >
              Edit
            </TabsTrigger>
          )}
          <TabsTrigger
            value="availability"
            className="flex-shrink-0 snap-start text-xs sm:text-sm"
          >
            Availability
          </TabsTrigger>
          <TabsTrigger
            value="assignments"
            className="flex-shrink-0 snap-start text-xs sm:text-sm"
          >
            Assignments
          </TabsTrigger>
          <TabsTrigger
            value="maintenance"
            className="flex-shrink-0 snap-start text-xs sm:text-sm"
          >
            Maintenance
          </TabsTrigger>
          <TabsTrigger
            value="utilization"
            className="flex-shrink-0 snap-start text-xs sm:text-sm"
          >
            Utilization
          </TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="mt-4 sm:mt-6">
          <ResourceList onEdit={handleEdit} />
        </TabsContent>

        <TabsContent value="create" className="mt-4 sm:mt-6">
          <ResourceForm onSuccess={handleFormSuccess} />
        </TabsContent>

        {editingResourceId && (
          <TabsContent value="edit" className="mt-4 sm:mt-6">
            <ResourceForm
              resourceId={editingResourceId}
              onSuccess={handleFormSuccess}
            />
          </TabsContent>
        )}

        <TabsContent value="availability" className="mt-4 sm:mt-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Select Resource
              </label>
              <input
                type="text"
                value={selectedResourceId}
                onChange={(e) => setSelectedResourceId(e.target.value)}
                placeholder="Enter Resource ID"
                className="w-full px-3 py-2 sm:px-4 sm:py-2 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground"
              />
            </div>
            {selectedResourceId && (
              <ResourceAvailabilityEditor resourceId={selectedResourceId} />
            )}
          </div>
        </TabsContent>

        <TabsContent value="assignments" className="mt-4 sm:mt-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Appointment ID
              </label>
              <input
                type="text"
                value={selectedAppointmentId}
                onChange={(e) => setSelectedAppointmentId(e.target.value)}
                placeholder="Enter Appointment ID"
                className="w-full px-3 py-2 sm:px-4 sm:py-2 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground"
              />
            </div>
            {selectedAppointmentId && (
              <ResourceAssignments appointmentId={selectedAppointmentId} />
            )}
          </div>
        </TabsContent>

        <TabsContent value="maintenance" className="mt-4 sm:mt-6">
          <ResourceMaintenanceSchedule resourceId={selectedResourceId || undefined} />
        </TabsContent>

        <TabsContent value="utilization" className="mt-4 sm:mt-6">
          <ResourceUtilization resourceId={selectedResourceId || undefined} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
