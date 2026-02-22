import { useState } from "react";
import WaitingRoomQueue from "@/components/waiting-room/WaitingRoomQueue";
import CheckInForm from "@/components/waiting-room/CheckInForm";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function WaitingRoomManagement() {
  const [activeTab, setActiveTab] = useState("queue");

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        Waiting Room
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        Manage customer queue and check-ins
      </p>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="queue">Queue Management</TabsTrigger>
          <TabsTrigger value="checkin">Customer Check-In</TabsTrigger>
        </TabsList>

        <TabsContent value="queue" className="mt-6">
          <WaitingRoomQueue />
        </TabsContent>

        <TabsContent value="checkin" className="mt-6">
          <CheckInForm />
        </TabsContent>
      </Tabs>
    </div>
  );
}
