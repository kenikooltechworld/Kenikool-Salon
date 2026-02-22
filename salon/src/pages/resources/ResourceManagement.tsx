import { useState } from "react";
import ResourceList from "@/components/resources/ResourceList";
import ResourceForm from "@/components/resources/ResourceForm";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function ResourceManagement() {
  const [activeTab, setActiveTab] = useState("list");
  const [editingResourceId, setEditingResourceId] = useState<
    string | undefined
  >();

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

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="list">Resources</TabsTrigger>
          <TabsTrigger value="create">Create Resource</TabsTrigger>
          {editingResourceId && (
            <TabsTrigger value="edit">Edit Resource</TabsTrigger>
          )}
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
      </Tabs>
    </div>
  );
}
