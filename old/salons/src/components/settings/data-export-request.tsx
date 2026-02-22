import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckIcon,
  AlertTriangleIcon,
  DownloadIcon,
} from "@/components/icons";
import { useRequestDataExport } from "@/lib/api/hooks/useSettings";
import { useQueryClient } from "@tanstack/react-query";

export function DataExportRequest() {
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [selectedCategories, setSelectedCategories] = useState({
    include_bookings: true,
    include_clients: true,
    include_payments: true,
    include_settings: true,
  });
  const queryClient = useQueryClient();

  const exportMutation = useRequestDataExport({
    onSuccess: () => {
      setSuccessMessage(
        "Data export requested successfully! You'll receive an email with the download link shortly."
      );
      queryClient.invalidateQueries({ queryKey: ["data-exports"] });
      setTimeout(() => setSuccessMessage(""), 5000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to request data export"
      );
    },
  });

  const handleToggle = (key: string) => {
    setSelectedCategories((prev) => ({
      ...prev,
      [key]: !prev[key as keyof typeof prev],
    }));
  };

  const handleExport = () => {
    exportMutation.mutate(selectedCategories);
  };

  const categories = [
    {
      key: "include_bookings",
      label: "Bookings",
      description: "All your booking history and details",
    },
    {
      key: "include_clients",
      label: "Clients",
      description: "Client information and relationships",
    },
    {
      key: "include_payments",
      label: "Payments",
      description: "Payment history and transactions",
    },
    {
      key: "include_settings",
      label: "Settings",
      description: "Your account settings and preferences",
    },
  ];

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-6">
        Export Your Data
      </h2>

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

      <div className="space-y-4 mb-6">
        <p className="text-sm text-muted-foreground">
          Select the data categories you want to export:
        </p>

        {categories.map((category) => (
          <div
            key={category.key}
            className="flex items-start gap-3 p-3 bg-muted rounded-lg"
          >
            <Checkbox
              id={category.key}
              checked={
                selectedCategories[category.key as keyof typeof selectedCategories]
              }
              onChange={() => handleToggle(category.key)}
              disabled={exportMutation.isPending}
              className="mt-1"
            />
            <div className="flex-1">
              <Label
                htmlFor={category.key}
                className="font-medium text-foreground cursor-pointer"
              >
                {category.label}
              </Label>
              <p className="text-xs text-muted-foreground mt-1">
                {category.description}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 p-4 rounded-lg mb-6">
        <p className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
          ℹ️ About Data Export
        </p>
        <ul className="text-xs text-blue-800 dark:text-blue-200 space-y-1">
          <li>• Your data will be exported as a JSON file</li>
          <li>• A download link will be sent to your email</li>
          <li>• The link will expire after 7 days</li>
          <li>• You can request multiple exports</li>
        </ul>
      </div>

      <Button
        onClick={handleExport}
        disabled={exportMutation.isPending}
        className="w-full"
      >
        {exportMutation.isPending ? (
          <>
            <Spinner size="sm" />
            Requesting Export...
          </>
        ) : (
          <>
            <DownloadIcon size={16} className="mr-2" />
            Request Data Export
          </>
        )}
      </Button>
    </Card>
  );
}
