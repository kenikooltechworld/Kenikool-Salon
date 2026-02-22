import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { Spinner } from "@/components/ui/spinner";
import {
  CheckIcon,
  AlertTriangleIcon,
  TrashIcon,
  KeyIcon,
  CalendarIcon,
} from "@/components/icons";
import {
  useAPIKeys,
  useRevokeAPIKey,
  useCreateAPIKey,
} from "@/lib/api/hooks/useSettings";
import { useQueryClient } from "@tanstack/react-query";
import { APIKeyCreateModal } from "./api-key-create-modal";
import { APIKeyDisplayModal } from "./api-key-display-modal";

export function APIKeyList() {
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [displayedKey, setDisplayedKey] = useState<{
    key: string;
    metadata: any;
  } | null>(null);
  const queryClient = useQueryClient();

  const { data: apiKeys = [], isLoading } = useAPIKeys();

  const revokeKeyMutation = useRevokeAPIKey({
    onSuccess: () => {
      setSuccessMessage("API key revoked successfully");
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
      setTimeout(() => setSuccessMessage(""), 3000);
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to revoke API key"
      );
    },
  });

  const createKeyMutation = useCreateAPIKey({
    onSuccess: (data) => {
      setDisplayedKey(data);
      setShowCreateModal(false);
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
    },
    onError: (error: any) => {
      setErrorMessage(
        error.response?.data?.detail || "Failed to create API key"
      );
    },
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const isExpired = (expiresAt?: string) => {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
  };

  return (
    <>
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold text-foreground">
              API Keys
            </h2>
            <p className="text-sm text-muted-foreground">
              Manage API keys for external integrations
            </p>
          </div>
          <Button onClick={() => setShowCreateModal(true)}>
            Create API Key
          </Button>
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

        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : apiKeys.length === 0 ? (
          <div className="text-center py-8">
            <KeyIcon size={48} className="mx-auto text-muted-foreground mb-3" />
            <p className="text-muted-foreground mb-4">
              No API keys yet. Create one to get started.
            </p>
            <Button onClick={() => setShowCreateModal(true)}>
              Create Your First API Key
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {apiKeys.map((key) => (
              <div
                key={key.id}
                className={`flex items-start justify-between p-4 rounded-lg border ${
                  isExpired(key.expires_at)
                    ? "bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800"
                    : "bg-muted border-border"
                }`}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <KeyIcon size={18} className="text-muted-foreground" />
                    <div>
                      <p className="font-medium text-foreground">{key.name}</p>
                      <p className="text-xs text-muted-foreground font-mono">
                        {key.key_prefix}...
                      </p>
                    </div>
                    {isExpired(key.expires_at) && (
                      <span className="ml-auto px-2 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-100 text-xs rounded-full font-medium">
                        Expired
                      </span>
                    )}
                  </div>

                  <div className="space-y-1 text-xs text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <CalendarIcon size={14} />
                      <span>Created: {formatDate(key.created_at)}</span>
                    </div>
                    {key.last_used && (
                      <div className="flex items-center gap-2">
                        <span>Last used: {formatDate(key.last_used)}</span>
                      </div>
                    )}
                    {key.expires_at && (
                      <div className="flex items-center gap-2">
                        <span>Expires: {formatDate(key.expires_at)}</span>
                      </div>
                    )}
                  </div>
                </div>

                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => revokeKeyMutation.mutate(key.id)}
                  disabled={revokeKeyMutation.isPending}
                  className="ml-4"
                >
                  {revokeKeyMutation.isPending ? (
                    <Spinner size="sm" />
                  ) : (
                    <TrashIcon size={18} className="text-destructive" />
                  )}
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Create Modal */}
      {showCreateModal && (
        <APIKeyCreateModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSubmit={(data) => createKeyMutation.mutate(data)}
          isLoading={createKeyMutation.isPending}
        />
      )}

      {/* Display Modal */}
      {displayedKey && (
        <APIKeyDisplayModal
          isOpen={!!displayedKey}
          onClose={() => setDisplayedKey(null)}
          apiKey={displayedKey.key}
          metadata={displayedKey.metadata}
        />
      )}
    </>
  );
}
