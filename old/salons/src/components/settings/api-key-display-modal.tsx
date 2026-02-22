import { useState } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Alert } from "@/components/ui/alert";
import { CheckIcon, CopyIcon, AlertTriangleIcon } from "@/components/icons";

interface APIKeyDisplayModalProps {
  isOpen: boolean;
  onClose: () => void;
  apiKey: string;
  metadata: {
    id: string;
    name: string;
    key_prefix: string;
    created_at: string;
  };
}

export function APIKeyDisplayModal({
  isOpen,
  onClose,
  apiKey,
  metadata,
}: APIKeyDisplayModalProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="API Key Created">
      <div className="space-y-4">
        {/* Warning */}
        <Alert variant="warning">
          <AlertTriangleIcon size={20} />
          <p>
            This is the only time your API key will be displayed. Save it now
            in a secure location. You won't be able to see it again.
          </p>
        </Alert>

        {/* Key Details */}
        <div className="bg-muted p-4 rounded-lg space-y-3">
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-1">
              Name
            </p>
            <p className="text-sm font-medium text-foreground">{metadata.name}</p>
          </div>

          <div>
            <p className="text-xs font-medium text-muted-foreground mb-1">
              Created
            </p>
            <p className="text-sm text-foreground">
              {new Date(metadata.created_at).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </p>
          </div>
        </div>

        {/* API Key Display */}
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-2">
            API Key
          </p>
          <div className="flex items-center gap-2">
            <code className="flex-1 bg-background p-3 rounded font-mono text-sm break-all">
              {apiKey}
            </code>
            <Button
              size="sm"
              variant="outline"
              onClick={handleCopy}
              className="flex-shrink-0"
            >
              {copied ? (
                <CheckIcon size={16} className="text-green-600" />
              ) : (
                <CopyIcon size={16} />
              )}
            </Button>
          </div>
        </div>

        {/* Usage Instructions */}
        <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 p-4 rounded-lg">
          <p className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
            How to use this API key:
          </p>
          <p className="text-xs text-blue-800 dark:text-blue-200 mb-2">
            Include it in the X-API-Key header of your API requests:
          </p>
          <code className="block bg-background p-2 rounded text-xs font-mono text-foreground">
            X-API-Key: {apiKey}
          </code>
        </div>

        {/* Close Button */}
        <Button onClick={onClose} className="w-full">
          I've Saved My API Key
        </Button>
      </div>
    </Modal>
  );
}
