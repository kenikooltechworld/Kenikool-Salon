import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { CustomerPreference } from "@/hooks/useCustomerPreferences";

interface CustomerPreferencesProps {
  customerId: string;
  preferences: CustomerPreference | null;
  staffOptions: Array<{ id: string; name: string }>;
  serviceOptions: Array<{ id: string; name: string }>;
  onUpdate: (preferences: Partial<CustomerPreference>) => void;
  isLoading?: boolean;
}

export function CustomerPreferences({
  customerId,
  preferences,
  staffOptions,
  serviceOptions,
  onUpdate,
  isLoading = false,
}: CustomerPreferencesProps) {
  const [formData, setFormData] = useState({
    preferred_staff_ids: preferences?.preferred_staff_ids || [],
    preferred_service_ids: preferences?.preferred_service_ids || [],
    communication_methods: preferences?.communication_methods || [],
    preferred_time_slots: preferences?.preferred_time_slots || [],
    language: preferences?.language || "en",
    notes: preferences?.notes || "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onUpdate(formData);
  };

  const toggleStaff = (staffId: string) => {
    setFormData((prev) => ({
      ...prev,
      preferred_staff_ids: prev.preferred_staff_ids.includes(staffId)
        ? prev.preferred_staff_ids.filter((id) => id !== staffId)
        : [...prev.preferred_staff_ids, staffId],
    }));
  };

  const toggleService = (serviceId: string) => {
    setFormData((prev) => ({
      ...prev,
      preferred_service_ids: prev.preferred_service_ids.includes(serviceId)
        ? prev.preferred_service_ids.filter((id) => id !== serviceId)
        : [...prev.preferred_service_ids, serviceId],
    }));
  };

  const toggleCommunication = (method: "email" | "sms" | "phone") => {
    setFormData((prev) => ({
      ...prev,
      communication_methods: prev.communication_methods.includes(method)
        ? prev.communication_methods.filter((m) => m !== method)
        : [...prev.communication_methods, method],
    }));
  };

  const toggleTimeSlot = (slot: "morning" | "afternoon" | "evening") => {
    setFormData((prev) => ({
      ...prev,
      preferred_time_slots: prev.preferred_time_slots.includes(slot)
        ? prev.preferred_time_slots.filter((s) => s !== slot)
        : [...prev.preferred_time_slots, slot],
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <Label className="text-base font-semibold mb-3 block">
          Preferred Staff
        </Label>
        <div className="space-y-2">
          {staffOptions.map((staff) => (
            <div key={staff.id} className="flex items-center">
              <Checkbox
                id={`staff-${staff.id}`}
                checked={formData.preferred_staff_ids.includes(staff.id)}
                onCheckedChange={() => toggleStaff(staff.id)}
              />
              <Label
                htmlFor={`staff-${staff.id}`}
                className="ml-2 cursor-pointer"
              >
                {staff.name}
              </Label>
            </div>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-base font-semibold mb-3 block">
          Preferred Services
        </Label>
        <div className="space-y-2">
          {serviceOptions.map((service) => (
            <div key={service.id} className="flex items-center">
              <Checkbox
                id={`service-${service.id}`}
                checked={formData.preferred_service_ids.includes(service.id)}
                onCheckedChange={() => toggleService(service.id)}
              />
              <Label
                htmlFor={`service-${service.id}`}
                className="ml-2 cursor-pointer"
              >
                {service.name}
              </Label>
            </div>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-base font-semibold mb-3 block">
          Communication Methods
        </Label>
        <div className="space-y-2">
          {(["email", "sms", "phone"] as const).map((method) => (
            <div key={method} className="flex items-center">
              <Checkbox
                id={`comm-${method}`}
                checked={formData.communication_methods.includes(method)}
                onCheckedChange={() => toggleCommunication(method)}
              />
              <Label htmlFor={`comm-${method}`} className="ml-2 cursor-pointer">
                {method.charAt(0).toUpperCase() + method.slice(1)}
              </Label>
            </div>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-base font-semibold mb-3 block">
          Preferred Time Slots
        </Label>
        <div className="space-y-2">
          {(["morning", "afternoon", "evening"] as const).map((slot) => (
            <div key={slot} className="flex items-center">
              <Checkbox
                id={`slot-${slot}`}
                checked={formData.preferred_time_slots.includes(slot)}
                onCheckedChange={() => toggleTimeSlot(slot)}
              />
              <Label htmlFor={`slot-${slot}`} className="ml-2 cursor-pointer">
                {slot.charAt(0).toUpperCase() + slot.slice(1)}
              </Label>
            </div>
          ))}
        </div>
      </div>

      <div>
        <Label htmlFor="language">Language</Label>
        <Select
          value={formData.language}
          onValueChange={(value) =>
            setFormData({ ...formData, language: value })
          }
        >
          <option value="en">English</option>
          <option value="fr">French</option>
          <option value="es">Spanish</option>
          <option value="pt">Portuguese</option>
        </Select>
      </div>

      <div>
        <Label htmlFor="notes">Additional Notes</Label>
        <Textarea
          id="notes"
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          placeholder="Any additional preferences or notes"
        />
      </div>

      <Button type="submit" disabled={isLoading} className="w-full">
        {isLoading ? "Saving..." : "Save Preferences"}
      </Button>
    </form>
  );
}
