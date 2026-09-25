import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/toast";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  SettingsIcon,
  SaveIcon,
  UserIcon,
  ClockIcon,
  MessageSquareIcon,
  GlobeIcon,
} from "@/components/icons";
import {
  useCustomerPreferences,
  useUpdateCustomerPreferences,
} from "@/hooks/useCustomerPreferences";
import { useServices } from "@/hooks/useServices";
import { useStaff } from "@/hooks/useStaff";

interface CustomerPreferencesPanelProps {
  customerId: string;
  customerName: string;
}

const TIME_SLOTS = [
  { value: "morning", label: "Morning (6AM - 12PM)" },
  { value: "afternoon", label: "Afternoon (12PM - 6PM)" },
  { value: "evening", label: "Evening (6PM - 12AM)" },
];

const COMMUNICATION_METHODS = [
  { value: "email", label: "Email" },
  { value: "sms", label: "SMS" },
  { value: "phone", label: "Phone" },
];

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "es", label: "Spanish" },
  { value: "fr", label: "French" },
  { value: "de", label: "German" },
  { value: "it", label: "Italian" },
  { value: "pt", label: "Portuguese" },
];

export function CustomerPreferencesPanel({
  customerId,
  customerName,
}: CustomerPreferencesPanelProps) {
  const { showToast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    preferred_staff_ids: [] as string[],
    preferred_service_ids: [] as string[],
    communication_methods: ["email"] as string[],
    preferred_time_slots: [] as string[],
    language: "en",
    notes: "",
  });

  const { data: preferences, isLoading, refetch } = useCustomerPreferences(customerId);
  const { data: services } = useServices();
  const { data: staff } = useStaff();
  const updatePreferences = useUpdateCustomerPreferences();

  useEffect(() => {
    if (preferences) {
      setFormData({
        preferred_staff_ids: preferences.preferred_staff_ids || [],
        preferred_service_ids: preferences.preferred_service_ids || [],
        communication_methods: preferences.communication_methods || ["email"],
        preferred_time_slots: preferences.preferred_time_slots || [],
        language: preferences.language || "en",
        notes: preferences.notes || "",
      });
    }
  }, [preferences]);

  const handleSave = async () => {
    try {
      await updatePreferences.mutateAsync({
        customerId,
        ...formData,
      });
      await refetch();
      setIsEditing(false);
      showToast({
        title: "Preferences Saved",
        description: "Customer preferences have been updated successfully.",
        variant: "success",
      });
    } catch (error: any) {
      showToast({
        title: "Save Failed",
        description: error.message || "Failed to save preferences.",
        variant: "error",
      });
    }
  };

  const handleCancel = () => {
    if (preferences) {
      setFormData({
        preferred_staff_ids: preferences.preferred_staff_ids || [],
        preferred_service_ids: preferences.preferred_service_ids || [],
        communication_methods: preferences.communication_methods || ["email"],
        preferred_time_slots: preferences.preferred_time_slots || [],
        language: preferences.language || "en",
        notes: preferences.notes || "",
      });
    }
    setIsEditing(false);
  };

  const toggleArrayValue = (array: string[], value: string) => {
    return array.includes(value)
      ? array.filter((item) => item !== value)
      : [...array, value];
  };

  if (isLoading) {
    return (
      <Card className="p-4 sm:p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-9 w-20" />
          </div>
          <div className="space-y-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="space-y-3">
                <Skeleton className="h-5 w-40" />
                <Skeleton className="h-20 w-full" />
              </div>
            ))}
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4 sm:p-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <SettingsIcon size={20} className="text-blue-600" />
            <h3 className="text-lg font-semibold text-foreground">Preferences</h3>
          </div>
          <div className="flex gap-2">
            {isEditing ? (
              <>
                <Button variant="outline" size="sm" onClick={handleCancel}>
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleSave}
                  disabled={updatePreferences.isPending}
                  className="gap-2"
                >
                  <SaveIcon size={16} />
                  Save
                </Button>
              </>
            ) : (
              <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
                Edit
              </Button>
            )}
          </div>
        </div>

        {/* Preferred Staff */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <UserIcon size={16} className="text-muted-foreground" />
            <h4 className="text-sm font-medium text-foreground">Preferred Staff</h4>
          </div>
          {isEditing ? (
            <div className="space-y-2">
              {staff?.map((member: any) => (
                <label
                  key={member.id}
                  className="flex items-center gap-3 p-3 rounded-lg border cursor-pointer hover:bg-muted"
                >
                  <input
                    type="checkbox"
                    checked={formData.preferred_staff_ids.includes(member.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFormData({
                          ...formData,
                          preferred_staff_ids: [...formData.preferred_staff_ids, member.id],
                        });
                      } else {
                        setFormData({
                          ...formData,
                          preferred_staff_ids: formData.preferred_staff_ids.filter(
                            (id) => id !== member.id
                          ),
                        });
                      }
                    }}
                    className="rounded"
                  />
                  <span className="text-sm text-foreground">
                    {member.firstName} {member.lastName}
                  </span>
                </label>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              {formData.preferred_staff_ids.length > 0 ? (
                formData.preferred_staff_ids.map((staffId) => {
                  const member = staff?.find((s: any) => s.id === staffId);
                  return member ? (
                    <Badge key={staffId} variant="secondary">
                      {member.firstName} {member.lastName}
                    </Badge>
                  ) : null;
                })
              ) : (
                <span className="text-sm text-muted-foreground">No preferences set</span>
              )}
            </div>
          )}
        </div>

        {/* Preferred Services */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <SettingsIcon size={16} className="text-muted-foreground" />
            <h4 className="text-sm font-medium text-foreground">Preferred Services</h4>
          </div>
          {isEditing ? (
            <div className="space-y-2">
              {services?.map((service: any) => (
                <label
                  key={service.id}
                  className="flex items-center gap-3 p-3 rounded-lg border cursor-pointer hover:bg-muted"
                >
                  <input
                    type="checkbox"
                    checked={formData.preferred_service_ids.includes(service.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFormData({
                          ...formData,
                          preferred_service_ids: [...formData.preferred_service_ids, service.id],
                        });
                      } else {
                        setFormData({
                          ...formData,
                          preferred_service_ids: formData.preferred_service_ids.filter(
                            (id) => id !== service.id
                          ),
                        });
                      }
                    }}
                    className="rounded"
                  />
                  <div>
                    <span className="text-sm text-foreground">{service.name}</span>
                    <p className="text-xs text-muted-foreground">{service.description}</p>
                  </div>
                </label>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              {formData.preferred_service_ids.length > 0 ? (
                formData.preferred_service_ids.map((serviceId) => {
                  const service = services?.find((s: any) => s.id === serviceId);
                  return service ? (
                    <Badge key={serviceId} variant="secondary">
                      {service.name}
                    </Badge>
                  ) : null;
                })
              ) : (
                <span className="text-sm text-muted-foreground">No preferences set</span>
              )}
            </div>
          )}
        </div>

        {/* Preferred Time Slots */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <ClockIcon size={16} className="text-muted-foreground" />
            <h4 className="text-sm font-medium text-foreground">Preferred Time Slots</h4>
          </div>
          {isEditing ? (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {TIME_SLOTS.map((slot) => (
                <label
                  key={slot.value}
                  className="flex items-center gap-3 p-3 rounded-lg border cursor-pointer hover:bg-muted"
                >
                  <input
                    type="checkbox"
                    checked={formData.preferred_time_slots.includes(slot.value)}
                    onChange={() =>
                      setFormData({
                        ...formData,
                        preferred_time_slots: toggleArrayValue(
                          formData.preferred_time_slots,
                          slot.value
                        ),
                      })
                    }
                    className="rounded"
                  />
                  <span className="text-sm text-foreground">{slot.label}</span>
                </label>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              {formData.preferred_time_slots.length > 0 ? (
                formData.preferred_time_slots.map((slot) => {
                  const timeSlot = TIME_SLOTS.find((ts) => ts.value === slot);
                  return timeSlot ? (
                    <Badge key={slot} variant="secondary">
                      {timeSlot.label}
                    </Badge>
                  ) : null;
                })
              ) : (
                <span className="text-sm text-muted-foreground">No preferences set</span>
              )}
            </div>
          )}
        </div>

        {/* Communication Methods */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <MessageSquareIcon size={16} className="text-muted-foreground" />
            <h4 className="text-sm font-medium text-foreground">Communication Methods</h4>
          </div>
          {isEditing ? (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {COMMUNICATION_METHODS.map((method) => (
                <label
                  key={method.value}
                  className="flex items-center gap-3 p-3 rounded-lg border cursor-pointer hover:bg-muted"
                >
                  <input
                    type="checkbox"
                    checked={formData.communication_methods.includes(method.value)}
                    onChange={() =>
                      setFormData({
                        ...formData,
                        communication_methods: toggleArrayValue(
                          formData.communication_methods,
                          method.value
                        ),
                      })
                    }
                    className="rounded"
                  />
                  <span className="text-sm text-foreground">{method.label}</span>
                </label>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              {formData.communication_methods.map((method) => {
                const commMethod = COMMUNICATION_METHODS.find((cm) => cm.value === method);
                return commMethod ? (
                  <Badge key={method} variant="secondary">
                    {commMethod.label}
                  </Badge>
                ) : null;
              })}
            </div>
          )}
        </div>

        {/* Language */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <GlobeIcon size={16} className="text-muted-foreground" />
            <h4 className="text-sm font-medium text-foreground">Language</h4>
          </div>
          {isEditing ? (
            <Select
              value={formData.language}
              onValueChange={(value) => setFormData({ ...formData, language: value })}
            >
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LANGUAGES.map((lang) => (
                  <SelectItem key={lang.value} value={lang.value}>
                    {lang.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            <Badge variant="secondary">
              {LANGUAGES.find((lang) => lang.value === formData.language)?.label || "English"}
            </Badge>
          )}
        </div>

        {/* Notes */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-foreground">Notes</h4>
          {isEditing ? (
            <Textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="Add any special notes or preferences..."
              rows={3}
            />
          ) : formData.notes ? (
            <p className="text-sm text-foreground p-3 bg-muted rounded-lg">
              {formData.notes}
            </p>
          ) : (
            <span className="text-sm text-muted-foreground">No notes added</span>
          )}
        </div>
      </div>
    </Card>
  );
}