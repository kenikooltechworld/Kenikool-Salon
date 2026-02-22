import { useState } from "react";
import { useCreateDomain } from "@/lib/api/hooks/useDomains";
import { XIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";

interface DomainFormModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function DomainFormModal({ isOpen, onClose }: DomainFormModalProps) {
  const createMutation = useCreateDomain();
  const [domain, setDomain] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Basic domain validation
    const domainRegex =
      /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$/;
    if (!domainRegex.test(domain)) {
      showToast("Please enter a valid domain name", "error");
      return;
    }

    try {
      await createMutation.mutateAsync({ domain });
      showToast(
        "Domain added successfully. Please configure DNS records.",
        "success"
      );
      setDomain("");
      onClose();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail ||
          "Failed to add domain. Make sure you're on the Enterprise plan.",
        "error"
      );
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-[var(--radius-lg)] w-full max-w-md">
        <div className="border-b border-border p-6 flex items-center justify-between">
          <h2 className="text-xl font-bold">Add Custom Domain</h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <XIcon size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-[var(--radius-md)]">
            <p className="text-sm text-blue-600 font-medium mb-2">
              Enterprise Feature
            </p>
            <p className="text-xs text-blue-600">
              Custom domains are only available for Enterprise plan subscribers.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Domain Name *
            </label>
            <input
              type="text"
              value={domain}
              onChange={(e) => setDomain(e.target.value.toLowerCase())}
              placeholder="example.com"
              className="w-full px-3 py-2 bg-background border border-border rounded-[var(--radius-md)] focus:outline-none focus:ring-2 focus:ring-primary"
              required
            />
            <p className="text-xs text-muted-foreground mt-2">
              Enter your domain without www (e.g., example.com)
            </p>
          </div>

          <div className="p-4 bg-muted rounded-[var(--radius-md)]">
            <p className="text-sm font-semibold mb-2">Next Steps:</p>
            <ol className="text-xs text-muted-foreground space-y-1 list-decimal list-inside">
              <li>Add your domain here</li>
              <li>Configure DNS records with your domain provider</li>
              <li>Click "Verify Domain" to complete setup</li>
              <li>SSL certificate will be automatically provisioned</li>
            </ol>
          </div>

          <div className="flex gap-3 pt-4 border-t border-border">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-muted text-foreground rounded-[var(--radius-md)] hover:bg-muted/80 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-[var(--radius-md)] hover:bg-primary/90 transition-colors font-medium disabled:opacity-50"
            >
              {createMutation.isPending ? "Adding..." : "Add Domain"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
