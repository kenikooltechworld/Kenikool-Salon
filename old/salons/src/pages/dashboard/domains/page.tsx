import { useState } from "react";
import {
  useGetDomains,
  useDeleteDomain,
  useVerifyDomain,
} from "@/lib/api/hooks/useDomains";
import {
  DomainList,
  DomainFormModal,
  DNSInstructionsModal,
} from "@/components/domains";
import { GlobeIcon, PlusIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";
import { FeatureGate } from "@/components/subscriptions/feature-gate";

export default function DomainsPage() {
  const { data: domains = [], isLoading } = useGetDomains();
  const deleteMutation = useDeleteDomain();
  const verifyMutation = useVerifyDomain();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isDNSOpen, setIsDNSOpen] = useState(false);
  const [selectedDomainId, setSelectedDomainId] = useState<string | null>(null);

  const handleVerify = async (domain: string) => {
    try {
      await verifyMutation.mutateAsync(domain);
      showToast("Domain verification initiated", "success");
    } catch (error: any) {
      showToast(error.response?.data?.detail || "Verification failed", "error");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Remove this domain?")) return;
    try {
      await deleteMutation.mutateAsync(id);
      showToast("Domain removed", "success");
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to remove domain",
        "error"
      );
    }
  };

  const handleViewDNS = (id: string) => {
    setSelectedDomainId(id);
    setIsDNSOpen(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <FeatureGate feature="Custom Domains" requiredPlan="enterprise">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <GlobeIcon size={32} className="text-primary" />
              Custom Domains
            </h1>
            <p className="text-muted-foreground mt-1">
              Manage your custom domain settings (Enterprise plan)
            </p>
          </div>
          <button
            onClick={() => setIsFormOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-[var(--radius-md)] hover:bg-primary/90 transition-colors font-medium"
          >
            <PlusIcon size={20} />
            Add Domain
          </button>
        </div>

        <div className="bg-card border border-border rounded-[var(--radius-lg)] p-6">
          <DomainList
            domains={domains}
            onVerify={handleVerify}
            onDelete={handleDelete}
            onViewDNS={handleViewDNS}
          />
        </div>

        <DomainFormModal
          isOpen={isFormOpen}
          onClose={() => setIsFormOpen(false)}
        />
        <DNSInstructionsModal
          isOpen={isDNSOpen}
          onClose={() => setIsDNSOpen(false)}
          domainId={selectedDomainId}
        />
      </div>
    </FeatureGate>
  );
}
