'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { GiftIcon } from '@/components/icons';

interface ClientRegistrationReferralProps {
  onReferralCodeChange?: (code: string) => void;
}

/**
 * Referral code capture component for client registration
 * Validates: REQ-9
 */
export function ClientRegistrationReferral({
  onReferralCodeChange,
}: ClientRegistrationReferralProps) {
  const searchParams = useSearchParams();
  const [referralCode, setReferralCode] = useState<string>('');
  const [showBonus, setShowBonus] = useState(false);

  // Capture referral code from URL parameter on mount
  useEffect(() => {
    const refParam = searchParams?.get('ref');
    if (refParam) {
      setReferralCode(refParam);
      setShowBonus(true);
      onReferralCodeChange?.(refParam);
    }
  }, [searchParams, onReferralCodeChange]);

  return (
    <>
      {/* Hidden field for referral code */}
      <input
        type="hidden"
        name="referral_code"
        value={referralCode}
        data-testid="referral-code-input"
      />

      {/* Referral bonus message */}
      {showBonus && referralCode && (
        <Alert className="bg-green-500/10 border-green-500/20 mb-4">
          <GiftIcon className="h-4 w-4 text-green-500" />
          <AlertDescription className="text-green-700">
            Great! You'll receive a referral bonus when you complete your first booking.
            Your referrer will also earn a reward!
          </AlertDescription>
        </Alert>
      )}
    </>
  );
}
