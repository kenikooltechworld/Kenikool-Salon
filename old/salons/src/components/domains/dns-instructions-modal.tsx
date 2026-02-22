import { useGetDNSRecords, DNSRecord } from "@/lib/api/hooks/useDomains";
import { XIcon, CopyIcon, CheckIcon } from "@/components/icons";
import { useState } from "react";
import { showToast } from "@/lib/utils/toast";

interface DNSInstructionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  domainId: string | null;
}

export function DNSInstructionsModal({
  isOpen,
  onClose,
  domainId,
}: DNSInstructionsModalProps) {
  const { data: records, isLoading } = useGetDNSRecords(domainId || "");
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const handleCopy = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    showToast("Copied to clipboard", "success");
    setTimeout(() => setCopiedField(null), 2000);
  };

  if (!isOpen || !domainId) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-[var(--radius-lg)] w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-card border-b border-border p-6 flex items-center justify-between">
          <h2 className="text-xl font-bold">DNS Configuration Instructions</h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <XIcon size={24} />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-[var(--radius-md)]">
            <p className="text-sm text-blue-600 font-medium mb-2">
              Configure these DNS records with your domain provider
            </p>
            <p className="text-xs text-blue-600">
              Changes may take up to 48 hours to propagate. Click "Verify
              Domain" after configuration.
            </p>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : records && records.length > 0 ? (
            <div className="space-y-4">
              {records.map((record, index) => (
                <div
                  key={index}
                  className="bg-muted rounded-[var(--radius-lg)] p-4 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-foreground">
                      Record {index + 1}
                    </span>
                    <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded-full font-medium">
                      {record.type}
                    </span>
                  </div>

                  <div className="space-y-2">
                    <div>
                      <label className="text-xs text-muted-foreground font-medium">
                        Type
                      </label>
                      <div className="flex items-center gap-2 mt-1">
                        <input
                          type="text"
                          value={record.type}
                          readOnly
                          className="flex-1 px-3 py-2 bg-background border border-border rounded-[var(--radius-md)] text-sm"
                        />
                        <button
                          onClick={() =>
                            handleCopy(record.type, `type-${index}`)
                          }
                          className="p-2 bg-primary/10 text-primary rounded-[var(--radius-md)] hover:bg-primary/20 transition-colors"
                        >
                          {copiedField === `type-${index}` ? (
                            <CheckIcon size={16} />
                          ) : (
                            <CopyIcon size={16} />
                          )}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="text-xs text-muted-foreground font-medium">
                        Name/Host
                      </label>
                      <div className="flex items-center gap-2 mt-1">
                        <input
                          type="text"
                          value={record.name}
                          readOnly
                          className="flex-1 px-3 py-2 bg-background border border-border rounded-[var(--radius-md)] text-sm"
                        />
                        <button
                          onClick={() =>
                            handleCopy(record.name, `name-${index}`)
                          }
                          className="p-2 bg-primary/10 text-primary rounded-[var(--radius-md)] hover:bg-primary/20 transition-colors"
                        >
                          {copiedField === `name-${index}` ? (
                            <CheckIcon size={16} />
                          ) : (
                            <CopyIcon size={16} />
                          )}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="text-xs text-muted-foreground font-medium">
                        Value/Points To
                      </label>
                      <div className="flex items-center gap-2 mt-1">
                        <input
                          type="text"
                          value={record.value}
                          readOnly
                          className="flex-1 px-3 py-2 bg-background border border-border rounded-[var(--radius-md)] text-sm font-mono"
                        />
                        <button
                          onClick={() =>
                            handleCopy(record.value, `value-${index}`)
                          }
                          className="p-2 bg-primary/10 text-primary rounded-[var(--radius-md)] hover:bg-primary/20 transition-colors"
                        >
                          {copiedField === `value-${index}` ? (
                            <CheckIcon size={16} />
                          ) : (
                            <CopyIcon size={16} />
                          )}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="text-xs text-muted-foreground font-medium">
                        TTL
                      </label>
                      <input
                        type="text"
                        value={record.ttl}
                        readOnly
                        className="w-full px-3 py-2 bg-background border border-border rounded-[var(--radius-md)] text-sm mt-1"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No DNS records available
            </div>
          )}

          <div className="p-4 bg-muted rounded-[var(--radius-md)]">
            <p className="text-sm font-semibold mb-2">Common DNS Providers:</p>
            <ul className="text-xs text-muted-foreground space-y-1 list-disc list-inside">
              <li>GoDaddy: DNS Management → Add Record</li>
              <li>Namecheap: Advanced DNS → Add New Record</li>
              <li>Cloudflare: DNS → Add Record</li>
              <li>Google Domains: DNS → Custom Records</li>
            </ul>
          </div>

          <div className="flex gap-3 pt-4 border-t border-border">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-[var(--radius-md)] hover:bg-primary/90 transition-colors font-medium"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
