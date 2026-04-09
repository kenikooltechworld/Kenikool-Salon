import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { CheckIcon } from "@/components/icons";
import { useToast } from "@/components/ui/toast";
import { useAuthStore } from "@/stores/auth";
import {
  useStaffSettings,
  useUpdateStaffSettings,
} from "@/hooks/staff/useStaffSettings";

export default function StaffProfileForm() {
  const { addToast } = useToast();
  const user = useAuthStore((state) => state.user);
  const { data: staffSettings, isLoading } = useStaffSettings();
  const { mutate: updateSettings, isPending } = useUpdateStaffSettings();
  const [profile, setProfile] = useState({
    firstName: "",
    lastName: "",
    email: user?.email || "",
    phone: "",
  });

  useEffect(() => {
    if (staffSettings) {
      setProfile({
        firstName: staffSettings.first_name || "",
        lastName: staffSettings.last_name || "",
        email: user?.email || "",
        phone: staffSettings.phone || "",
      });
    }
  }, [staffSettings, user?.email]);

  const handleSave = async () => {
    updateSettings(
      {
        first_name: profile.firstName,
        last_name: profile.lastName,
        phone: profile.phone,
      },
      {
        onSuccess: () => {
          addToast({
            title: "Success",
            description: "Profile updated successfully!",
            variant: "success",
          });
        },
        onError: (error) => {
          addToast({
            title: "Error",
            description:
              error instanceof Error
                ? error.message
                : "Failed to update profile",
            variant: "error",
          });
        },
      },
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-foreground">Profile Settings</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Manage your personal profile information
        </p>
      </div>

      {/* Profile Form */}
      <div className="bg-card border border-border rounded-lg p-4 md:p-6 space-y-6">
        {isLoading ? (
          <div className="space-y-4">
            <div className="h-10 bg-muted rounded animate-pulse" />
            <div className="h-10 bg-muted rounded animate-pulse" />
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  First Name
                </label>
                <input
                  type="text"
                  value={profile.firstName}
                  onChange={(e) =>
                    setProfile({ ...profile, firstName: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Last Name
                </label>
                <input
                  type="text"
                  value={profile.lastName}
                  onChange={(e) =>
                    setProfile({ ...profile, lastName: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={profile.email}
                  disabled
                  className="w-full px-3 py-2 border border-border rounded-lg bg-muted text-foreground opacity-60"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Phone
                </label>
                <input
                  type="tel"
                  value={profile.phone}
                  onChange={(e) =>
                    setProfile({ ...profile, phone: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>

            <div className="flex flex-col sm:flex-row justify-end gap-3 border-t border-border pt-6">
              <Button
                onClick={handleSave}
                disabled={isPending}
                className="gap-2 w-full sm:w-auto cursor-pointer"
              >
                <CheckIcon size={18} />
                {isPending ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
