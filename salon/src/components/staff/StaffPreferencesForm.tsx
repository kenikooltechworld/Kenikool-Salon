import { useState, useEffect } from "react";
import {
  useStaffSettings,
  useUpdateStaffSettings,
} from "@/hooks/staff/useStaffSettings";
import { useServices } from "@/hooks/useServices";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";
import { MultiSelect } from "@/components/ui/multi-select";

const CUSTOMER_TYPES = [
  { value: "walk-in", label: "Walk-in" },
  { value: "regular", label: "Regular" },
  { value: "vip", label: "VIP" },
  { value: "new", label: "New Customer" },
  { value: "returning", label: "Returning Customer" },
];

export default function StaffPreferencesForm() {
  const { data: settings, isLoading: settingsLoading } = useStaffSettings();
  const { data: services = [], isLoading: servicesLoading } = useServices();
  const updateSettings = useUpdateStaffSettings();
  const { addToast } = useToast();

  const [serviceSpecializations, setServiceSpecializations] = useState<
    string[]
  >([]);
  const [preferredCustomerTypes, setPreferredCustomerTypes] = useState<
    string[]
  >([]);
  const [emergencyContactName, setEmergencyContactName] = useState("");
  const [emergencyContactPhone, setEmergencyContactPhone] = useState("");
  const [emergencyContactRelationship, setEmergencyContactRelationship] =
    useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (settings) {
      setServiceSpecializations(settings.service_specializations || []);
      setPreferredCustomerTypes(settings.preferred_customer_types || []);
      setEmergencyContactName(settings.emergency_contact_name || "");
      setEmergencyContactPhone(settings.emergency_contact_phone || "");
      setEmergencyContactRelationship(
        settings.emergency_contact_relationship || "",
      );
    }
  }, [settings]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Validate phone format if provided
    if (
      emergencyContactPhone &&
      !/^[\d\s\-\+\(\)]+$/.test(emergencyContactPhone)
    ) {
      newErrors.emergencyContactPhone = "Invalid phone number format";
    }

    // If any emergency contact field is filled, require name and phone
    if (
      emergencyContactName ||
      emergencyContactPhone ||
      emergencyContactRelationship
    ) {
      if (!emergencyContactName) {
        newErrors.emergencyContactName = "Emergency contact name is required";
      }
      if (!emergencyContactPhone) {
        newErrors.emergencyContactPhone = "Emergency contact phone is required";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      await updateSettings.mutateAsync({
        service_specializations: serviceSpecializations,
        preferred_customer_types: preferredCustomerTypes,
        emergency_contact_name: emergencyContactName || undefined,
        emergency_contact_phone: emergencyContactPhone || undefined,
        emergency_contact_relationship:
          emergencyContactRelationship || undefined,
      });

      addToast({
        title: "Success",
        description: "Work preferences updated successfully",
        variant: "success",
      });
    } catch (error: any) {
      addToast({
        title: "Error",
        description: error.message || "Failed to update work preferences",
        variant: "error",
      });
    }
  };

  if (settingsLoading || servicesLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Spinner size="lg" />
        </CardContent>
      </Card>
    );
  }

  // Convert services to options for MultiSelect
  const serviceOptions = services.map((service) => ({
    value: service.id,
    label: service.name,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Work Preferences</CardTitle>
        <CardDescription>
          Set your service specializations and customer preferences
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Service Specializations */}
          <div className="space-y-2">
            <Label htmlFor="serviceSpecializations">
              Service Specializations
            </Label>
            <MultiSelect
              options={serviceOptions}
              selected={serviceSpecializations}
              onChange={setServiceSpecializations}
              placeholder="Select services you specialize in"
            />
            <p className="text-xs text-muted-foreground">
              Select the services you are most skilled at providing
            </p>
          </div>

          {/* Preferred Customer Types */}
          <div className="space-y-2">
            <Label htmlFor="preferredCustomerTypes">
              Preferred Customer Types
            </Label>
            <MultiSelect
              options={CUSTOMER_TYPES}
              selected={preferredCustomerTypes}
              onChange={setPreferredCustomerTypes}
              placeholder="Select preferred customer types"
            />
            <p className="text-xs text-muted-foreground">
              Select the types of customers you prefer to work with
            </p>
          </div>

          {/* Emergency Contact Section */}
          <div className="space-y-4 pt-4 border-t">
            <h3 className="text-sm font-medium">Emergency Contact</h3>

            <div className="space-y-2">
              <Label htmlFor="emergencyContactName">Contact Name</Label>
              <Input
                id="emergencyContactName"
                value={emergencyContactName}
                onChange={(e) => setEmergencyContactName(e.target.value)}
                placeholder="John Doe"
              />
              {errors.emergencyContactName && (
                <p className="text-sm text-destructive">
                  {errors.emergencyContactName}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="emergencyContactPhone">Contact Phone</Label>
              <Input
                id="emergencyContactPhone"
                value={emergencyContactPhone}
                onChange={(e) => setEmergencyContactPhone(e.target.value)}
                placeholder="+1 (555) 123-4567"
              />
              {errors.emergencyContactPhone && (
                <p className="text-sm text-destructive">
                  {errors.emergencyContactPhone}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="emergencyContactRelationship">Relationship</Label>
              <Input
                id="emergencyContactRelationship"
                value={emergencyContactRelationship}
                onChange={(e) =>
                  setEmergencyContactRelationship(e.target.value)
                }
                placeholder="Spouse, Parent, Sibling, etc."
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <Button type="submit" disabled={updateSettings.isPending}>
              {updateSettings.isPending ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Saving...
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
