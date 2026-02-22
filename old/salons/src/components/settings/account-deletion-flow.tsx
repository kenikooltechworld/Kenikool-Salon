import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckIcon,
  AlertTriangleIcon,
  TrashIcon,
} from "@/components/icons";
import {
  useRequestAccountDeletion,
  useCancelAccountDeletion,
} from "@/lib/api/hooks/useSettings";
import { useQueryClient } from "@tanstack/react-query";

export function AccountDeletionFlow() {
  const [step, setStep] = useState<"idle" | "confirm" | "scheduled">("idle");
  const [password, setPassword] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [scheduledFor, setScheduledFor] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const deletionMutation = useRequestAccountDeletion({
    onSuccess: (data: any) => {
      setStep("scheduled");
      setScheduledFor(data.scheduled_for);
      setSuccessMessage("Account deletion scheduled successfully");
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to request account deletion"
      );
    },
  });

  const cancelMutation = useCancelAccountDeletion({
    onSuccess: () => {
      setSuccessMessage("Account deletion cancelled successfully");
      setStep("idle");
      setPassword("");
      setScheduledFor(null);
      queryClient.invalidateQueries({ queryKey: ["user-profile"] });
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to cancel account deletion"
      );
    },
  });

  const handleRequestDeletion = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    if (!password) {
      setErrorMessage("Password is required");
      return;
    }

    deletionMutation.mutate({ password });
  };

  const handleCancelDeletion = () => {
    if (
      confirm(
        "Are you sure you want to cancel the account deletion? Your account will remain active."
      )
    ) {
      cancelMutation.mutate();
    }
  };

  return (
    <Card className="p-6 border-red-200 dark:border-red-800">
      <div className="flex items-center gap-3 mb-6">
        <TrashIcon size={24} className="text-red-600" />
        <h2 className="text-lg font-semibold text-foreground">
          Delete Account
        </h2>
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

      {step === "idle" && (
        <div className="space-y-4">
          <Alert variant="warning">
            <AlertTriangleIcon size={20} />
            <p>
              Deleting your account is permanent. All your data will be deleted
              after 30 days. This action cannot be undone.
            </p>
          </Alert>

          <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 p-4 rounded-lg">
            <p className="text-sm font-medium text-red-900 dark:text-red-100 mb-2">
              What happens when you delete your account:
            </p>
            <ul className="text-xs text-red-800 dark:text-red-200 space-y-1">
              <li>• Your account will be soft-deleted immediately</li>
              <li>• You won't be able to log in</li>
              <li>• Your data will be permanently deleted after 30 days</li>
              <li>• You can cancel the deletion within 30 days</li>
            </ul>
          </div>

          <Button
            variant="destructive"
            onClick={() => setStep("confirm")}
            className="w-full"
          >
            <TrashIcon size={16} className="mr-2" />
            Delete My Account
          </Button>
        </div>
      )}

      {step === "confirm" && (
        <form onSubmit={handleRequestDeletion} className="space-y-4">
          <Alert variant="warning">
            <AlertTriangleIcon size={20} />
            <p>
              Please enter your password to confirm account deletion. This is
              irreversible.
            </p>
          </Alert>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Password *
            </label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              disabled={deletionMutation.isPending}
            />
          </div>

          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setStep("idle");
                setPassword("");
                setErrorMessage("");
              }}
              disabled={deletionMutation.isPending}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="destructive"
              disabled={deletionMutation.isPending}
              className="flex-1"
            >
              {deletionMutation.isPending ? (
                <>
                  <Spinner size="sm" />
                  Deleting...
                </>
              ) : (
                "Confirm Deletion"
              )}
            </Button>
          </div>
        </form>
      )}

      {step === "scheduled" && scheduledFor && (
        <div className="space-y-4">
          <Alert variant="success">
            <CheckIcon size={20} />
            <p>
              Your account has been scheduled for deletion on{" "}
              {new Date(scheduledFor).toLocaleDateString("en-US", {
                month: "long",
                day: "numeric",
                year: "numeric",
              })}
              .
            </p>
          </Alert>

          <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 p-4 rounded-lg">
            <p className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
              ℹ️ You have 30 days to change your mind
            </p>
            <p className="text-xs text-blue-800 dark:text-blue-200">
              If you change your mind, you can cancel the deletion before the
              scheduled date. After that, your account and all data will be
              permanently deleted.
            </p>
          </div>

          <Button
            variant="outline"
            onClick={handleCancelDeletion}
            disabled={cancelMutation.isPending}
            className="w-full"
          >
            {cancelMutation.isPending ? (
              <>
                <Spinner size="sm" />
                Cancelling...
              </>
            ) : (
              "Cancel Deletion"
            )}
          </Button>
        </div>
      )}
    </Card>
  );
}
