import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import { CheckIcon, AlertTriangleIcon, LockIcon } from "@/components/icons";
import { useChangePassword } from "@/lib/api/hooks/useSettings";
import { PasswordStrengthIndicator } from "./password-strength-indicator";

export function PasswordChangeForm() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [formData, setFormData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const changePasswordMutation = useChangePassword({
    onSuccess: () => {
      setSuccessMessage("Password changed successfully!");
      setFormData({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
      setIsExpanded(false);
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to change password"
      );
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    // Validation
    if (!formData.current_password) {
      setErrorMessage("Current password is required");
      return;
    }

    if (!formData.new_password) {
      setErrorMessage("New password is required");
      return;
    }

    if (formData.new_password.length < 8) {
      setErrorMessage("Password must be at least 8 characters");
      return;
    }

    if (formData.new_password !== formData.confirm_password) {
      setErrorMessage("New passwords do not match");
      return;
    }

    if (formData.current_password === formData.new_password) {
      setErrorMessage("New password must be different from current password");
      return;
    }

    changePasswordMutation.mutate({
      current_password: formData.current_password,
      new_password: formData.new_password,
    });
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Change Password
          </h2>
          <p className="text-sm text-muted-foreground">
            Update your password regularly for better security
          </p>
        </div>
        {!isExpanded && (
          <Button onClick={() => setIsExpanded(true)}>Change Password</Button>
        )}
      </div>

      {successMessage && (
        <Alert variant="success" className="mb-4">
          <CheckIcon size={20} />
          <p>{successMessage}</p>
        </Alert>
      )}

      {errorMessage && (
        <Alert variant="error" className="mb-4">
          <AlertTriangleIcon size={20} />
          <p>{errorMessage}</p>
        </Alert>
      )}

      {isExpanded && (
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Current Password */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              <LockIcon size={16} className="inline mr-2" />
              Current Password *
            </label>
            <Input
              type="password"
              value={formData.current_password}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  current_password: e.target.value,
                })
              }
              placeholder="Enter current password"
              disabled={changePasswordMutation.isPending}
            />
          </div>

          {/* New Password */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              New Password *
            </label>
            <Input
              type="password"
              value={formData.new_password}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  new_password: e.target.value,
                })
              }
              placeholder="Enter new password"
              disabled={changePasswordMutation.isPending}
            />
          </div>

          {/* Password Strength Indicator */}
          {formData.new_password && (
            <PasswordStrengthIndicator password={formData.new_password} />
          )}

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Confirm New Password *
            </label>
            <Input
              type="password"
              value={formData.confirm_password}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  confirm_password: e.target.value,
                })
              }
              placeholder="Confirm new password"
              disabled={changePasswordMutation.isPending}
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setIsExpanded(false);
                setFormData({
                  current_password: "",
                  new_password: "",
                  confirm_password: "",
                });
                setErrorMessage("");
              }}
              disabled={changePasswordMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={changePasswordMutation.isPending}
            >
              {changePasswordMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Updating...
                </>
              ) : (
                "Update Password"
              )}
            </Button>
          </div>
        </form>
      )}
    </Card>
  );
}
