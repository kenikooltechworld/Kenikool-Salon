import { Domain } from "@/lib/api/hooks/useDomains";
import {
  GlobeIcon,
  CheckCircleIcon,
  ClockIcon,
  XCircleIcon,
  TrashIcon,
  RefreshIcon,
} from "@/components/icons";

interface DomainListProps {
  domains: Domain[];
  onVerify: (domain: string) => void;
  onDelete: (id: string) => void;
  onViewDNS: (id: string) => void;
}

export function DomainList({
  domains,
  onVerify,
  onDelete,
  onViewDNS,
}: DomainListProps) {
  if (domains.length === 0) {
    return (
      <div className="text-center py-12">
        <GlobeIcon size={48} className="mx-auto text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold mb-2">No custom domains yet</h3>
        <p className="text-muted-foreground">
          Add a custom domain to use your own branding
        </p>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "verified":
        return <CheckCircleIcon size={16} className="text-green-500" />;
      case "pending":
        return <ClockIcon size={16} className="text-yellow-500" />;
      case "failed":
        return <XCircleIcon size={16} className="text-red-500" />;
      default:
        return <ClockIcon size={16} className="text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "verified":
        return "bg-green-500/10 text-green-500";
      case "pending":
        return "bg-yellow-500/10 text-yellow-500";
      case "failed":
        return "bg-red-500/10 text-red-500";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  return (
    <div className="space-y-3">
      {domains.map((domain) => (
        <div
          key={domain._id}
          className="bg-card border border-border rounded-[var(--radius-lg)] p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-[var(--radius-md)]">
                <GlobeIcon size={20} className="text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">{domain.domain}</h3>
                <p className="text-sm text-muted-foreground">
                  Added {new Date(domain.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            <span
              className={`flex items-center gap-1 text-xs px-3 py-1 rounded-full font-medium ${getStatusColor(
                domain.status
              )}`}
            >
              {getStatusIcon(domain.status)}
              {domain.status.charAt(0).toUpperCase() + domain.status.slice(1)}
            </span>
          </div>

          {domain.ssl_enabled && (
            <div className="mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded-[var(--radius-md)]">
              <p className="text-sm text-green-600 font-medium">
                ✓ SSL Certificate Active
              </p>
            </div>
          )}

          {domain.status === "pending" && (
            <div className="mb-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-[var(--radius-md)]">
              <p className="text-sm text-yellow-600 font-medium">
                ⚠ DNS configuration required. Click "View DNS Records" for
                instructions.
              </p>
            </div>
          )}

          {domain.status === "failed" && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-[var(--radius-md)]">
              <p className="text-sm text-red-600 font-medium">
                ✗ Verification failed. Please check your DNS configuration.
              </p>
            </div>
          )}

          <div className="flex gap-2 pt-4 border-t border-border">
            {domain.status !== "verified" && (
              <button
                onClick={() => onVerify(domain.domain)}
                className="flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-[var(--radius-md)] hover:bg-primary/20 transition-colors text-sm font-medium"
              >
                <RefreshIcon size={16} />
                Verify Domain
              </button>
            )}
            <button
              onClick={() => onViewDNS(domain._id)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500/10 text-blue-500 rounded-[var(--radius-md)] hover:bg-blue-500/20 transition-colors text-sm font-medium"
            >
              <GlobeIcon size={16} />
              View DNS Records
            </button>
            <button
              onClick={() => onDelete(domain._id)}
              className="flex items-center gap-2 px-4 py-2 bg-destructive/10 text-destructive rounded-[var(--radius-md)] hover:bg-destructive/20 transition-colors text-sm font-medium ml-auto"
            >
              <TrashIcon size={16} />
              Remove
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
