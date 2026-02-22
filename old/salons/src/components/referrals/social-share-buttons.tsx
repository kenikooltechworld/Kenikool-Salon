'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircleIcon } from '@/components/icons';

interface SocialShareButtonsProps {
  referralLink: string;
  referralCode: string;
  salonName?: string;
}

/**
 * Social share buttons for referral link
 * Validates: REQ-8
 */
export function SocialShareButtons({
  referralLink,
  referralCode,
  salonName = 'our salon',
}: SocialShareButtonsProps) {
  const [copied, setCopied] = useState(false);

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(referralLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy link:', err);
    }
  };

  const handleWhatsAppShare = () => {
    const message = `Hey! I found this amazing salon - ${salonName}. Use my referral link to book and we both get rewards! ${referralLink}`;
    const encodedMessage = encodeURIComponent(message);
    window.open(
      `https://wa.me/?text=${encodedMessage}`,
      '_blank',
      'noopener,noreferrer'
    );
  };

  const handleFacebookShare = () => {
    const url = new URL('https://www.facebook.com/sharer/sharer.php');
    url.searchParams.append('u', referralLink);
    url.searchParams.append('quote', `Check out ${salonName}! Book using my link and get rewards: ${referralLink}`);
    window.open(url.toString(), '_blank', 'noopener,noreferrer');
  };

  const handleTwitterShare = () => {
    const text = `Just discovered ${salonName}! Book with my referral link and get rewards: ${referralLink}`;
    const encodedText = encodeURIComponent(text);
    window.open(
      `https://twitter.com/intent/tweet?text=${encodedText}`,
      '_blank',
      'noopener,noreferrer'
    );
  };

  return (
    <div className="space-y-3">
      {/* Copy Link Success Message */}
      {copied && (
        <Alert className="bg-green-500/10 border-green-500/20">
          <CheckCircleIcon className="h-4 w-4 text-green-500" />
          <AlertDescription className="text-green-700">
            Link copied to clipboard!
          </AlertDescription>
        </Alert>
      )}

      {/* Share Buttons */}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {/* WhatsApp */}
        <Button
          variant="outline"
          onClick={handleWhatsAppShare}
          className="flex items-center justify-center gap-2"
        >
          <svg
            className="h-4 w-4"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.67-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.076 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421-7.403h-.004a9.87 9.87 0 00-4.255.949c-1.238.503-2.39 1.242-3.286 2.138-1.604 1.603-2.504 3.756-2.504 6.035 0 1.631.266 3.15.748 4.545L1 23.135l4.773-1.285c1.592.887 3.402 1.357 5.228 1.357 2.279 0 4.428-.9 6.035-2.507 1.605-1.605 2.507-3.754 2.507-6.035 0-1.863-.505-3.623-1.461-5.149-1.384-2.165-3.814-3.6-6.514-3.6zm3.829 11.81c-.256-.134-1.51-.745-1.74-.83-.23-.084-.397-.126-.565.126-.168.252-.65.829-.797 1.001-.148.172-.295.193-.55.061-.256-.132-1.082-.399-2.061-1.271-.762-.684-1.277-1.529-1.425-1.785-.148-.256-.016-.394.111-.522.111-.111.297-.291.446-.437.149-.146.198-.248.297-.414.099-.167.05-.31-.025-.435-.075-.125-.565-1.36-.774-1.86-.204-.487-.408-.42-.565-.427-.148-.005-.31-.005-.472-.005-.161 0-.423.06-.645.298-.222.24-.847.829-.847 2.02 0 1.192.868 2.344 1.017 2.5.149.156 2.096 3.2 5.076 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z" />
          </svg>
          <span className="hidden sm:inline">WhatsApp</span>
        </Button>

        {/* Facebook */}
        <Button
          variant="outline"
          onClick={handleFacebookShare}
          className="flex items-center justify-center gap-2"
        >
          <svg
            className="h-4 w-4"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
          </svg>
          <span className="hidden sm:inline">Facebook</span>
        </Button>

        {/* Twitter */}
        <Button
          variant="outline"
          onClick={handleTwitterShare}
          className="flex items-center justify-center gap-2"
        >
          <svg
            className="h-4 w-4"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M23.953 4.57a10 10 0 002.856-3.915 10 10 0 01-2.866.853c1.007-.6 1.78-1.555 2.14-2.697a10 10 0 01-3.127 1.195 4.982 4.982 0 00-8.526 4.55A14.14 14.14 0 011.671 3.149a4.982 4.982 0 001.541 6.657 4.936 4.936 0 01-2.261-.556v.06a4.983 4.983 0 003.995 4.882 4.914 4.914 0 01-2.254.085 4.985 4.985 0 004.644 3.459A9.98 9.98 0 010 19.54a14.11 14.11 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
          </svg>
          <span className="hidden sm:inline">Twitter</span>
        </Button>

        {/* Copy Link */}
        <Button
          variant="outline"
          onClick={handleCopyLink}
          className="flex items-center justify-center gap-2"
        >
          <svg
            className="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
          <span className="hidden sm:inline">Copy</span>
        </Button>
      </div>

      {/* Referral Code Display */}
      <div className="bg-muted/50 rounded-lg p-3 text-center">
        <p className="text-xs text-muted-foreground mb-1">Your Referral Code</p>
        <p className="font-mono font-bold text-sm">{referralCode}</p>
      </div>
    </div>
  );
}
