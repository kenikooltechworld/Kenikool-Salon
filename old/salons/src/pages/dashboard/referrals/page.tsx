import { useState } from "react";
import {
  useGetReferrals,
  useGetReferralStats,
} from "@/lib/api/hooks/useReferrals";
import { ReferralList, ReferralStatsComponent } from "@/components/referrals";
import { UsersIcon, CopyIcon, CheckIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";
import { useTenant } from "@/lib/api/hooks/useTenant";

export default function ReferralsPage() {
  const { data: referrals, isLoading: referralsLoading } = useGetReferrals();
  const { data: stats, isLoading: statsLoading } = useGetReferralStats();
  const { data: tenant } = useTenant();

  const [copied, setCopied] = useState(false);

  const referralLink = tenant?.subdomain
    ? `https://${tenant.subdomain}.yourdomain.com/book?ref=${tenant._id}`
    : "";

  const handleCopyLink = () => {
    if (referralLink) {
      navigator.clipboard.writeText(referralLink);
      setCopied(true);
      showToast("Referral link copied to clipboard", "success");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (referralsLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <UsersIcon size={32} className="text-primary" />
          Referral Program
        </h1>
        <p className="text-muted-foreground mt-1">
          Track your referrals and earn rewards
        </p>
      </div>

      {/* Stats */}
      {stats && <ReferralStatsComponent stats={stats} />}

      {/* Referral Link Generator */}
      <div className="bg-card border border-border rounded-[var(--radius-lg)] p-6">
        <h2 className="text-xl font-bold mb-4">Your Referral Link</h2>
        <p className="text-muted-foreground mb-4">
          Share this link with your friends and earn rewards when they book
          services
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            value={referralLink}
            readOnly
            className="flex-1 px-4 py-2 bg-background border border-border rounded-[var(--radius-md)] text-foreground"
          />
          <button
            onClick={handleCopyLink}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-[var(--radius-md)] hover:bg-primary/90 transition-colors font-medium"
          >
            {copied ? (
              <>
                <CheckIcon size={20} />
                Copied!
              </>
            ) : (
              <>
                <CopyIcon size={20} />
                Copy Link
              </>
            )}
          </button>
        </div>
      </div>

      {/* Referral List */}
      <div className="bg-card border border-border rounded-[var(--radius-lg)] p-6">
        <h2 className="text-xl font-bold mb-4">Referral History</h2>
        <ReferralList referrals={referrals || []} />
      </div>
    </div>
  );
}
