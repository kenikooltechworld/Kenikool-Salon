"use client";

import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { CheckIcon, GlobeIcon } from "@/components/icons";
import { useToast } from "@/components/ui/toast";
import { useTenant } from "@/lib/api/hooks/useTenant";

interface OnboardingData {
  profile: {
    businessName: string;
  } | null;
  service: {
    name: string;
  } | null;
  staff: {
    name: string;
  } | null;
}

interface PreviewSetupProps {
  data: OnboardingData;
  onFinish: () => void;
}

export function PreviewSetup({ data, onFinish }: PreviewSetupProps) {
  const { showToast } = useToast();
  const [copied, setCopied] = useState(false);

  // Get subdomain from localStorage (saved during registration) for instant URL
  const getSubdomain = () => {
    if (typeof window !== "undefined") {
      const userStr = localStorage.getItem("user");
      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          return user.subdomain || user.tenantId;
        } catch {
          return null;
        }
      }
    }
    return null;
  };

  const subdomain = getSubdomain();

  // Also fetch from server as backup
  const { data: tenantData } = useTenant();

  const bookingUrl = useMemo(() => {
    if (typeof window !== "undefined") {
      const sub = subdomain || tenantData?.subdomain;
      if (sub) {
        return `${window.location.origin}/book/${sub}`;
      }
    }
    return "";
  }, [subdomain, tenantData]);

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(bookingUrl);
      setCopied(true);
      showToast({
        title: "Link Copied!",
        description: "Booking page link copied to clipboard",
        variant: "success",
      });
      setTimeout(() => setCopied(false), 2000);
    } catch {
      showToast({
        title: "Copy Failed",
        description: "Failed to copy link. Please try again.",
        variant: "error",
      });
    }
  };

  // Remove loading state since we get subdomain from localStorage instantly

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[var(--foreground)] mb-2">
          You&apos;re All Set!
        </h2>
        <p className="text-[var(--muted-foreground)]">
          Your salon is ready to accept bookings
        </p>
      </div>

      {/* Success Checklist */}
      <div className="bg-[var(--success)]/10 border border-[var(--success)]/20 rounded-lg p-6">
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-full bg-[var(--success)] flex items-center justify-center">
              <CheckIcon size={14} className="text-white" />
            </div>
            <span className="text-[var(--foreground)]">
              Profile customized with your branding
            </span>
          </div>
          {data.service && (
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-full bg-[var(--success)] flex items-center justify-center">
                <CheckIcon size={14} className="text-white" />
              </div>
              <span className="text-[var(--foreground)]">
                First service created: {data.service.name}
              </span>
            </div>
          )}
          {data.staff && (
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-full bg-[var(--success)] flex items-center justify-center">
                <CheckIcon size={14} className="text-white" />
              </div>
              <span className="text-[var(--foreground)]">
                Team member added: {data.staff.name}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Booking Page Preview */}
      <div className="border-2 border-[var(--border)] rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <GlobeIcon size={20} className="text-[var(--primary)]" />
          <h3 className="text-lg font-semibold text-[var(--foreground)]">
            Your Booking Page
          </h3>
        </div>
        <div className="bg-[var(--muted)] rounded p-4 mb-4">
          <code className="text-sm text-[var(--foreground)] break-all">
            {bookingUrl || "Loading your booking page URL..."}
          </code>
        </div>
        {!bookingUrl && (
          <p className="text-sm text-[var(--muted-foreground)] mb-4">
            Please wait while we generate your booking page link...
          </p>
        )}
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => bookingUrl && window.open(bookingUrl, "_blank")}
            fullWidth
            disabled={!bookingUrl}
          >
            Preview Booking Page
          </Button>
          <Button
            variant="outline"
            onClick={handleCopyLink}
            fullWidth
            disabled={!bookingUrl}
          >
            {copied ? "Copied!" : "Copy Link"}
          </Button>
        </div>
      </div>

      {/* Next Steps */}
      <div className="bg-[var(--muted)] rounded-lg p-6">
        <h3 className="text-lg font-semibold text-[var(--foreground)] mb-3">
          What&apos;s Next?
        </h3>
        <ul className="space-y-2 text-sm text-[var(--muted-foreground)]">
          <li>• Add more services and team members</li>
          <li>• Customize your booking page further</li>
          <li>• Share your booking link with clients</li>
          <li>• Start accepting appointments</li>
          <li>• Track your business analytics</li>
        </ul>
      </div>

      <Button onClick={onFinish} fullWidth size="lg" className="cursor-pointer">
        Go to Dashboard
      </Button>
    </div>
  );
}
