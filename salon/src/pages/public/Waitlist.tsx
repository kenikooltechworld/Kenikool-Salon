import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Card,
  Button,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui";
import WaitlistJoin from "@/components/public/WaitlistJoin";
import WaitlistStatus from "@/components/public/WaitlistStatus";
import { ArrowLeftIcon } from "@/components/icons";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

interface Service {
  id: string;
  name: string;
}

interface Staff {
  id: string;
  name: string;
}

export default function Waitlist() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState("join");

  const serviceId = searchParams.get("service");
  const staffId = searchParams.get("staff");

  // Fetch service details if serviceId is provided
  const { data: service } = useQuery({
    queryKey: ["service", serviceId],
    queryFn: async () => {
      if (!serviceId) return null;
      const { data } = await apiClient.get<Service>(
        `/public/services/${serviceId}`,
      );
      return data;
    },
    enabled: !!serviceId,
  });

  // Fetch staff details if staffId is provided
  const { data: staff } = useQuery({
    queryKey: ["staff", staffId],
    queryFn: async () => {
      if (!staffId) return null;
      const { data } = await apiClient.get<Staff>(`/public/staff/${staffId}`);
      return data;
    },
    enabled: !!staffId,
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate("/public")}
            className="mb-4"
          >
            <ArrowLeftIcon className="w-4 h-4 mr-2" />
            Back to Booking
          </Button>

          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Waitlist Management
          </h1>
          <p className="text-gray-600">
            Join our waitlist or check your current position
          </p>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="join">Join Waitlist</TabsTrigger>
            <TabsTrigger value="status">Check Status</TabsTrigger>
          </TabsList>

          <TabsContent value="join">
            {serviceId && service ? (
              <WaitlistJoin
                serviceId={serviceId}
                serviceName={service.name}
                staffId={staffId || undefined}
                staffName={staff?.name}
                onSuccess={() => setActiveTab("status")}
              />
            ) : (
              <div className="space-y-4">
                <Card className="p-6 bg-blue-50 border-blue-200">
                  <h3 className="font-semibold text-blue-900 mb-2">
                    How the Waitlist Works
                  </h3>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Select your desired service and staff member</li>
                    <li>
                      • We'll notify you when a time slot becomes available
                    </li>
                    <li>• You'll receive updates via email and SMS</li>
                    <li>• Cancel anytime if your plans change</li>
                  </ul>
                </Card>

                <p className="text-center text-gray-600">
                  To join the waitlist, please start a booking from the{" "}
                  <button
                    onClick={() => navigate("/public")}
                    className="text-blue-600 hover:underline font-medium"
                  >
                    main booking page
                  </button>
                  . The waitlist option will appear if no time slots are
                  available.
                </p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="status">
            <WaitlistStatus />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
