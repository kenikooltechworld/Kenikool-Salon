import { useState } from "react";
import { Button } from "@/components/ui/button";
import { CheckIcon } from "@/components/icons";
import { useToast } from "@/components/ui/toast";
import { post } from "@/lib/utils/api";

export default function StaffPasswordForm() {
  const { addToast } = useToast();
  const [passwords, setPasswords] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    if (passwords.newPassword !== passwords.confirmPassword) {
      addToast({
        title: "Error",
        description: "Passwords do not match",
        variant: "error",
      });
      return;
    }

    if (passwords.newPassword.length < 8) {
      addToast({
        title: "Error",
        description: "Password must be at least 8 characters",
        variant: "error",
      });
      return;
    }

    setIsSaving(true);
    try {
      await post("/auth/change-password", {
        current_password: passwords.currentPassword,
        new_password: passwords.newPassword,
      });
      addToast({
        title: "Success",
        description: "Password changed successfully!",
        variant: "success",
      });
      setPasswords({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
    } catch (error) {
      addToast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to change password",
        variant: "error",
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-foreground">Change Password</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Update your password to keep your account secure
        </p>
      </div>

      {/* Password Form */}
      <div className="bg-card border border-border rounded-lg p-4 md:p-6 space-y-6 max-w-md">
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Current Password
          </label>
          <input
            type="password"
            value={passwords.currentPassword}
            onChange={(e) =>
              setPasswords({ ...passwords, currentPassword: e.target.value })
            }
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            New Password
          </label>
          <input
            type="password"
            value={passwords.newPassword}
            onChange={(e) =>
              setPasswords({ ...passwords, newPassword: e.target.value })
            }
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <p className="text-xs text-muted-foreground mt-1">
            Must be at least 8 characters
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Confirm Password
          </label>
          <input
            type="password"
            value={passwords.confirmPassword}
            onChange={(e) =>
              setPasswords({ ...passwords, confirmPassword: e.target.value })
            }
            className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="flex flex-col sm:flex-row justify-end gap-3 border-t border-border pt-6">
          <Button
            onClick={handleSave}
            disabled={isSaving}
            className="gap-2 w-full sm:w-auto cursor-pointer"
          >
            <CheckIcon size={18} />
            {isSaving ? "Saving..." : "Change Password"}
          </Button>
        </div>
      </div>
    </div>
  );
}
