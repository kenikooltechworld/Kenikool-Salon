"use client";

import React, { useState, useEffect } from "react";
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
  Loader2Icon,
  AlertTriangleIcon,
  CheckCircle2Icon,
} from "@/components/icons";
import { useToast } from "@/hooks/use-toast";

interface DuplicatePair {
  client1_id: string;
  client1_name: string;
  client1_phone?: string;
  client1_email?: string;
  client2_id: string;
  client2_name: string;
  client2_phone?: string;
  client2_email?: string;
  similarity_score: number;
  name_match: number;
  phone_match: number;
  email_match: number;
}

interface DuplicateDetectionPageProps {
  tenantId: string;
}

export function DuplicateDetectionPage({
  tenantId,
}: DuplicateDetectionPageProps) {
  const { toast } = useToast();
  const [selectedPair, setSelectedPair] = useState<DuplicatePair | null>(null);
  const [mergeInProgress, setMergeInProgress] = useState(false);

  // Fetch duplicates
  const {
    data: duplicatesData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["duplicates", tenantId],
    queryFn: async () => {
      const response = await fetch(`/api/clients/duplicates?limit=100`, {
        headers: {
          "X-Tenant-ID": tenantId,
        },
      });
      if (!response.ok) throw new Error("Failed to fetch duplicates");
      return response.json();
    },
  });

  // Merge mutation
  const mergeMutation = useMutation({
    mutationFn: async (pair: DuplicatePair) => {
      const response = await fetch("/api/clients/merge", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Tenant-ID": tenantId,
        },
        body: JSON.stringify({
          primary_client_id: pair.client1_id,
          secondary_client_id: pair.client2_id,
        }),
      });
      if (!response.ok) throw new Error("Failed to merge clients");
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Clients merged successfully",
      });
      setSelectedPair(null);
      refetch();
    },
    onError: (error) => {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to merge clients",
        variant: "destructive",
      });
    },
  });

  const duplicates = duplicatesData?.duplicates || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Duplicate Detection</h1>
        <p className="text-gray-600 mt-2">
          Identify and merge duplicate client records to maintain data quality
        </p>
      </div>

      {isLoading ? (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <Loader2Icon className="h-8 w-8 animate-spin text-gray-400" />
          </CardContent>
        </Card>
      ) : duplicates.length === 0 ? (
        <Alert>
          <CheckCircle2Icon className="h-4 w-4" />
          <AlertDescription>
            No duplicate clients detected. Your client database is clean!
          </AlertDescription>
        </Alert>
      ) : (
        <div className="space-y-4">
          <Alert>
            <AlertTriangleIcon className="h-4 w-4" />
            <AlertDescription>
              Found {duplicates.length} potential duplicate pairs. Review and
              merge as needed.
            </AlertDescription>
          </Alert>

          {duplicates.map((pair, index) => (
            <Card
              key={index}
              className="cursor-pointer hover:shadow-lg transition-shadow"
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4">
                      <div>
                        <p className="font-semibold">{pair.client1_name}</p>
                        <p className="text-sm text-gray-600">
                          {pair.client1_phone}
                        </p>
                        <p className="text-sm text-gray-600">
                          {pair.client1_email}
                        </p>
                      </div>
                      <div className="text-center">
                        <Badge variant="secondary" className="text-lg">
                          {(pair.similarity_score * 100).toFixed(0)}%
                        </Badge>
                        <p className="text-xs text-gray-600 mt-1">Match</p>
                      </div>
                      <div>
                        <p className="font-semibold">{pair.client2_name}</p>
                        <p className="text-sm text-gray-600">
                          {pair.client2_phone}
                        </p>
                        <p className="text-sm text-gray-600">
                          {pair.client2_email}
                        </p>
                      </div>
                    </div>
                  </div>
                  <Button
                    onClick={() => setSelectedPair(pair)}
                    variant="outline"
                  >
                    Review & Merge
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Name Match</p>
                    <p className="font-semibold">
                      {(pair.name_match * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Phone Match</p>
                    <p className="font-semibold">
                      {(pair.phone_match * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Email Match</p>
                    <p className="font-semibold">
                      {(pair.email_match * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Merge Modal */}
      {selectedPair && (
        <MergeModal
          pair={selectedPair}
          onClose={() => setSelectedPair(null)}
          onMerge={() => {
            setMergeInProgress(true);
            mergeMutation.mutate(selectedPair);
            setMergeInProgress(false);
          }}
          isLoading={mergeInProgress}
        />
      )}
    </div>
  );
}

interface MergeModalProps {
  pair: DuplicatePair;
  onClose: () => void;
  onMerge: () => void;
  isLoading: boolean;
}

function MergeModal({ pair, onClose, onMerge, isLoading }: MergeModalProps) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>Merge Duplicate Clients</CardTitle>
          <CardDescription>
            Review the details and confirm the merge. You can undo this within
            24 hours.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Client 1 */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-4">Keep (Primary)</h3>
              <div className="space-y-2">
                <div>
                  <p className="text-sm text-gray-600">Name</p>
                  <p className="font-semibold">{pair.client1_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Phone</p>
                  <p className="font-semibold">{pair.client1_phone || "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="font-semibold">{pair.client1_email || "N/A"}</p>
                </div>
              </div>
            </div>

            {/* Client 2 */}
            <div className="border rounded-lg p-4 bg-gray-50">
              <h3 className="font-semibold mb-4">Merge Into Primary</h3>
              <div className="space-y-2">
                <div>
                  <p className="text-sm text-gray-600">Name</p>
                  <p className="font-semibold">{pair.client2_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Phone</p>
                  <p className="font-semibold">{pair.client2_phone || "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="font-semibold">{pair.client2_email || "N/A"}</p>
                </div>
              </div>
            </div>
          </div>

          <Alert>
            <AlertTriangleIcon className="h-4 w-4" />
            <AlertDescription>
              All bookings, payments, and communications from the secondary
              client will be merged into the primary client. This action can be
              undone within 24 hours.
            </AlertDescription>
          </Alert>

          <div className="flex gap-4 justify-end">
            <Button variant="outline" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button onClick={onMerge} disabled={isLoading}>
              {isLoading && (
                <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />
              )}
              Confirm Merge
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
