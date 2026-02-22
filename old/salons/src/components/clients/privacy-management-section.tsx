"use client";

import React, { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Loader2Icon,
  DownloadIcon,
  TrashIcon,
  CheckCircle2Icon,
  AlertTriangleIcon,
} from "@/components/icons";
import { useToast } from "@/hooks/use-toast";

interface ConsentRecord {
  id: string;
  consent_type: string;
  granted: boolean;
  recorded_at: string;
  ip_address?: string;
}

interface PrivacyManagementSectionProps {
  clientId: string;
  tenantId: string;
}

export function PrivacyManagementSection({
  clientId,
  tenantId,
}: PrivacyManagementSectionProps) {
  const { toast } = useToast();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showExportConfirm, setShowExportConfirm] = useState(false);

  // Fetch consent history
  const { data: consentData } = useQuery({
    queryKey: ["consent-history", clientId],
    queryFn: async () => {
      const response = await fetch(
        `/api/privacy/clients/${clientId}/consent-history`,
        {
          headers: { "X-Tenant-ID": tenantId },
        },
      );
      if (!response.ok) throw new Error("Failed to fetch consent history");
      return response.json();
    },
  });

  // Export data mutation
  const exportMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(
        `/api/privacy/clients/${clientId}/export-data`,
        {
          headers: { "X-Tenant-ID": tenantId },
        },
      );
      if (!response.ok) throw new Error("Failed to export data");
      return response.blob();
    },
    onSuccess: (blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `client_${clientId}_data.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast({
        title: "Success",
        description: "Data exported successfully",
      });
      setShowExportConfirm(false);
    },
    onError: (error) => {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to export data",
        variant: "destructive",
      });
    },
  });

  // Delete data mutation
  const deleteMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(
        `/api/privacy/clients/${clientId}/anonymize`,
        {
          method: "POST",
          headers: { "X-Tenant-ID": tenantId },
        },
      );
      if (!response.ok) throw new Error("Failed to delete data");
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Client data has been anonymized",
      });
      setShowDeleteConfirm(false);
    },
    onError: (error) => {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to delete data",
        variant: "destructive",
      });
    },
  });

  const consents = consentData?.consents || [];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Privacy & Consent Management</CardTitle>
          <CardDescription>
            Manage client data privacy preferences and GDPR compliance
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Consent Status */}
          <div>
            <h3 className="font-semibold mb-4">Consent Status</h3>
            <div className="grid grid-cols-2 gap-4">
              {["marketing", "analytics", "data_processing"].map((type) => {
                const consent = consents.find((c) => c.consent_type === type);
                return (
                  <div key={type} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <p className="font-medium capitalize">
                        {type.replace("_", " ")}
                      </p>
                      <Badge
                        variant={consent?.granted ? "default" : "secondary"}
                      >
                        {consent?.granted ? "Granted" : "Not Granted"}
                      </Badge>
                    </div>
                    {consent && (
                      <p className="text-sm text-gray-600 mt-2">
                        {new Date(consent.recorded_at).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Consent History */}
          {consents.length > 0 && (
            <div>
              <h3 className="font-semibold mb-4">Consent History</h3>
              <div className="space-y-2">
                {consents.map((consent) => (
                  <div
                    key={consent.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div>
                      <p className="font-medium capitalize">
                        {consent.consent_type.replace("_", " ")}
                      </p>
                      <p className="text-sm text-gray-600">
                        {new Date(consent.recorded_at).toLocaleString()}
                      </p>
                    </div>
                    <Badge
                      variant={consent.granted ? "default" : "destructive"}
                    >
                      {consent.granted ? "Granted" : "Denied"}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Data Actions */}
          <div className="border-t pt-6">
            <h3 className="font-semibold mb-4">Data Management</h3>
            <div className="space-y-3">
              <Button
                onClick={() => setShowExportConfirm(true)}
                variant="outline"
                className="w-full justify-start"
                disabled={exportMutation.isPending}
              >
                <DownloadIcon className="mr-2 h-4 w-4" />
                Export My Data
              </Button>
              <Button
                onClick={() => setShowDeleteConfirm(true)}
                variant="destructive"
                className="w-full justify-start"
                disabled={deleteMutation.isPending}
              >
                <TrashIcon className="mr-2 h-4 w-4" />
                Delete My Data
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Export Confirmation Dialog */}
      <Dialog open={showExportConfirm} onOpenChange={setShowExportConfirm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Export Your Data</DialogTitle>
            <DialogDescription>
              Download all your personal data in a machine-readable format
              (JSON)
            </DialogDescription>
          </DialogHeader>
          <Alert>
            <CheckCircle2Icon className="h-4 w-4" />
            <AlertDescription>
              Your data export will include all bookings, payments,
              communications, and other information associated with your
              account.
            </AlertDescription>
          </Alert>
          <div className="flex gap-4 justify-end">
            <Button
              variant="outline"
              onClick={() => setShowExportConfirm(false)}
              disabled={exportMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              onClick={() => exportMutation.mutate()}
              disabled={exportMutation.isPending}
            >
              {exportMutation.isPending && (
                <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />
              )}
              Download Data
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Your Data</DialogTitle>
            <DialogDescription>
              This action will anonymize your personal information
            </DialogDescription>
          </DialogHeader>
          <Alert variant="destructive">
            <AlertTriangleIcon className="h-4 w-4" />
            <AlertDescription>
              Your personal information (name, phone, email, address) will be
              permanently anonymized. However, your booking history and
              analytics data will be preserved for business records. This action
              cannot be undone.
            </AlertDescription>
          </Alert>
          <div className="flex gap-4 justify-end">
            <Button
              variant="outline"
              onClick={() => setShowDeleteConfirm(false)}
              disabled={deleteMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => deleteMutation.mutate()}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending && (
                <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />
              )}
              Confirm Deletion
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
