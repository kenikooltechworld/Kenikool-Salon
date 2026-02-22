import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { apiClient } from "@/lib/api/client";
import { useToast } from "@/components/ui/toast";

interface WaitlistFormProps {
  serviceId?: string;
  onSuccess?: () => void;
}

export function WaitlistForm({ serviceId, onSuccess }: WaitlistFormProps) {
  const { addToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    clientName: "",
    clientPhone: "",
    clientEmail: "",
    preferredDate: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await apiClient.post("/api/waitlist", {
        ...formData,
        service_id: serviceId,
      });

      addToast({
        title: "Success",
        description: "Added to waitlist successfully",
        variant: "success",
      });

      setFormData({
        clientName: "",
        clientPhone: "",
        clientEmail: "",
        preferredDate: "",
      });

      onSuccess?.();
    } catch (error) {
      addToast({
        title: "Error",
        description: "Failed to add to waitlist",
        variant: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Join Waitlist</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          placeholder="Full Name"
          value={formData.clientName}
          onChange={(e) =>
            setFormData({ ...formData, clientName: e.target.value })
          }
          required
        />
        <Input
          placeholder="Phone Number"
          value={formData.clientPhone}
          onChange={(e) =>
            setFormData({ ...formData, clientPhone: e.target.value })
          }
          required
        />
        <Input
          placeholder="Email"
          type="email"
          value={formData.clientEmail}
          onChange={(e) =>
            setFormData({ ...formData, clientEmail: e.target.value })
          }
          required
        />
        <Input
          placeholder="Preferred Date"
          type="date"
          value={formData.preferredDate}
          onChange={(e) =>
            setFormData({ ...formData, preferredDate: e.target.value })
          }
          required
        />
        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Adding..." : "Add to Waitlist"}
        </Button>
      </form>
    </Card>
  );
}
