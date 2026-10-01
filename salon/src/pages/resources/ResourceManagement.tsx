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
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        Resource Management
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        Manage physical resources, equipment, and supplies
      </p>

      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        defaultValue="list"
        className="w-full"
      >
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="list">Resources</TabsTrigger>
          <TabsTrigger value="create">Create</TabsTrigger>
          {editingResourceId && (
            <TabsTrigger value="edit">Edit</TabsTrigger>
          )}
          <TabsTrigger value="availability">Availability</TabsTrigger>
          <TabsTrigger value="assignments">Assignments</TabsTrigger>
          <TabsTrigger value="maintenance">Maintenance</TabsTrigger>
          <TabsTrigger value="utilization">Utilization</TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="mt-6">
          <ResourceList onEdit={handleEdit} />
        </TabsContent>

        <TabsContent value="create" className="mt-6">
          <ResourceForm onSuccess={handleFormSuccess} />
        </TabsContent>

        {editingResourceId && (
          <TabsContent value="edit" className="mt-6">
            <ResourceForm
              resourceId={editingResourceId}
              onSuccess={handleFormSuccess}
            />
          </TabsContent>
        )}

        <TabsContent value="availability" className="mt-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Resource
              </label>
              <input
                type="text"
                value={selectedResourceId}
                onChange={(e) => setSelectedResourceId(e.target.value)}
                placeholder="Enter Resource ID"
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            {selectedResourceId && (
              <ResourceAvailabilityEditor resourceId={selectedResourceId} />
            )}
          </div>
        </TabsContent>

        <TabsContent value="assignments" className="mt-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Appointment ID
              </label>
              <input
                type="text"
                value={selectedAppointmentId}
                onChange={(e) => setSelectedAppointmentId(e.target.value)}
                placeholder="Enter Appointment ID"
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            {selectedAppointmentId && (
              <ResourceAssignments appointmentId={selectedAppointmentId} />
            )}
          </div>
        </TabsContent>

        <TabsContent value="maintenance" className="mt-6">
          <ResourceMaintenanceSchedule resourceId={selectedResourceId || undefined} />
        </TabsContent>

        <TabsContent value="utilization" className="mt-6">
          <ResourceUtilization resourceId={selectedResourceId || undefined} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
