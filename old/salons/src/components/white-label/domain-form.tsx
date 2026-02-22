"use client";

import {
  WhiteLabelDomain,
  useGetDNSInstructions,
  useVerifyDomain,
} from "@/lib/api/hooks/useWhiteLabel";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { CheckIcon, AlertCircleIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";

interface DomainFormProps {
  domain: WhiteLabelDomain;
  onChange: (domain: WhiteLabelDomain) => void;
}

export function DomainForm({ domain, onChange }: DomainFormProps) {
  const { data: dnsInstructions = [] } = useGetDNSInstructions();
  const verifyMutation = useVerifyDomain();

  const handleChange = (field: keyof WhiteLabelDomain, value: any) => {
    onChange({ ...domain, [field]: value });
  };

  const handleVerify = async () => {
    try {
      const result = await verifyMutation.mutateAsync();
      if (result.verified) {
        showToast(result.message, "success");
      } else {
        showToast(result.message, "error");
      }
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to verify domain",
        "error"
      );
    }
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Custom Domain</h3>
      <div className="space-y-4">
        <div>
          <Label htmlFor="custom_domain">Domain</Label>
          <Input
            id="custom_domain"
            value={domain.custom_domain || ""}
            onChange={(e) => handleChange("custom_domain", e.target.value)}
            placeholder="booking.yoursalon.com"
          />
        </div>

        <div className="flex items-center justify-between p-3 bg-[var(--muted)] rounded-[var(--radius-md)]">
          <div>
            <p className="font-semibold">SSL Enabled</p>
            <p className="text-sm text-[var(--muted-foreground)]">
              Secure your custom domain with SSL
            </p>
          </div>
          <Switch
            checked={domain.ssl_enabled}
            onCheckedChange={(checked) => handleChange("ssl_enabled", checked)}
          />
        </div>

        {domain.custom_domain && (
          <>
            <div className="p-4 bg-blue-50 rounded-[var(--radius-md)]">
              <div className="flex items-start gap-2 mb-3">
                <AlertCircleIcon size={20} className="text-blue-600 mt-0.5" />
                <div>
                  <p className="font-semibold text-blue-900">
                    DNS Configuration Required
                  </p>
                  <p className="text-sm text-blue-800 mt-1">
                    Add these DNS records to your domain provider:
                  </p>
                </div>
              </div>

              {dnsInstructions.map((instruction, index) => (
                <div key={index} className="mt-3 p-3 bg-white rounded border">
                  <div className="grid grid-cols-4 gap-2 text-sm mb-2">
                    <div>
                      <p className="font-semibold">Type</p>
                      <p>{instruction.record_type}</p>
                    </div>
                    <div>
                      <p className="font-semibold">Host</p>
                      <p className="font-mono text-xs">{instruction.host}</p>
                    </div>
                    <div>
                      <p className="font-semibold">Value</p>
                      <p className="font-mono text-xs">{instruction.value}</p>
                    </div>
                    <div>
                      <p className="font-semibold">TTL</p>
                      <p>{instruction.ttl}</p>
                    </div>
                  </div>
                  <p className="text-xs text-[var(--muted-foreground)]">
                    {instruction.instructions}
                  </p>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-3">
              <Button
                onClick={handleVerify}
                disabled={verifyMutation.isPending}
                variant="outline"
              >
                Verify DNS Configuration
              </Button>
              {domain.dns_configured && (
                <div className="flex items-center gap-2 text-green-600">
                  <CheckIcon size={20} />
                  <span className="text-sm font-semibold">Verified</span>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </Card>
  );
}
