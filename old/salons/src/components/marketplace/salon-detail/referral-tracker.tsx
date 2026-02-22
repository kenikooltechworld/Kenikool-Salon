import { useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { ShareIcon, LinkIcon } from "@/components/icons";
import { useTrackReferral } from "@/lib/api/hooks/useMarketplaceQueries";

interface ReferralTrackerProps {
  salonId: string;
  salonName: string;
  salonWebsite?: string;
}

export function ReferralTracker({
  salonId,
  salonName,
  salonWebsite,
}: ReferralTrackerProps) {
  const trackReferralMutation = useTrackReferral();

  // Generate referral code
  const generateReferralCode = () => {
    return `ref_${salonId}_${Date.now()}`;
  };

  const referralCode = generateReferralCode();
  const referralUrl = `${window.location.origin}/marketplace/salon/${salonId}?ref=${referralCode}`;

  // Track referral on component mount
  useEffect(() => {
    const trackReferral = async () => {
      try {
        await trackReferralMutation.mutateAsync({
          tenantId: salonId,
          visitorData: {
            referral_code: referralCode,
            user_agent: navigator.userAgent,
            ip_address: "", // This would be set by backend
            timestamp: new Date().toISOString(),
          },
        });

        // Track analytics event
        if (window.gtag) {
          window.gtag("event", "referral_click", {
            salon_id: salonId,
            salon_name: salonName,
            referral_code: referralCode,
          });
        }
      } catch (error) {
        console.error("Error tracking referral:", error);
      }
    };

    trackReferral();
  }, [salonId, referralCode, salonName, trackReferralMutation]);

  const handleVisitSalon = () => {
    // Track button click
    if (window.gtag) {
      window.gtag("event", "visit_salon_site", {
        salon_id: salonId,
        salon_name: salonName,
        referral_code: referralCode,
      });
    }

    // Open salon website
    if (salonWebsite) {
      window.open(salonWebsite, "_blank");
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(referralUrl);
    // Show toast notification
    if (window.showToast) {
      window.showToast("Referral link copied to clipboard!");
    }
  };

  const handleShareReferral = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Check out ${salonName}`,
          text: `Visit ${salonName} and get exclusive offers!`,
          url: referralUrl,
        });

        // Track share event
        if (window.gtag) {
          window.gtag("event", "share_referral", {
            salon_id: salonId,
            salon_name: salonName,
            referral_code: referralCode,
          });
        }
      } catch (error) {
        console.error("Error sharing:", error);
      }
    }
  };

  return (
    <motion.div
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Visit Salon Button */}
      {salonWebsite && (
        <motion.button
          onClick={handleVisitSalon}
          className="w-full px-4 py-3 bg-[var(--primary)] hover:bg-[var(--primary-dark)] text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <LinkIcon size={18} />
          Visit Salon Site
        </motion.button>
      )}

      {/* Referral Section */}
      <motion.div
        className="bg-[var(--muted)] p-4 rounded-lg space-y-3"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h4 className="font-semibold text-[var(--foreground)]">
          Share & Earn
        </h4>
        <p className="text-sm text-[var(--muted-foreground)]">
          Share this salon with friends and earn referral rewards
        </p>

        {/* Referral Link */}
        <div className="bg-white p-3 rounded-lg border border-[var(--border)]">
          <p className="text-xs text-[var(--muted-foreground)] mb-2">
            Referral Link
          </p>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={referralUrl}
              readOnly
              className="flex-1 text-xs px-2 py-1 bg-[var(--muted)] rounded border-0 focus:outline-none"
            />
            <motion.button
              onClick={handleCopyLink}
              className="p-2 hover:bg-[var(--muted)] rounded transition-colors"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              title="Copy link"
            >
              <LinkIcon size={16} className="text-[var(--primary)]" />
            </motion.button>
          </div>
        </div>

        {/* Share Button */}
        <motion.button
          onClick={handleShareReferral}
          className="w-full px-3 py-2 bg-[var(--primary)]/10 hover:bg-[var(--primary)]/20 text-[var(--primary)] font-medium rounded-lg transition-colors flex items-center justify-center gap-2 text-sm"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <ShareIcon size={16} />
          Share Referral
        </motion.button>
      </motion.div>

      {/* Info Box */}
      <motion.div
        className="bg-blue-50 border border-blue-200 p-3 rounded-lg text-xs text-blue-800"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <p className="font-semibold mb-1">💰 Referral Rewards:</p>
        <p>
          Earn commission when your referral books an appointment. Share your
          unique link to start earning!
        </p>
      </motion.div>
    </motion.div>
  );
}
