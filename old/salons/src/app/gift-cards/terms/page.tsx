'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ArrowLeft, AlertCircle, Loader } from 'lucide-react';
import { useSearchParams } from 'next/navigation';
import { useGiftCardTerms } from '@/lib/api/hooks/useGiftCards';

export default function TermsPage() {
  const searchParams = useSearchParams();
  const tenantId = searchParams.get('tenant') || '';
  const { fetchTerms, loading, error, data: terms } = useGiftCardTerms();
  const [hasLoaded, setHasLoaded] = useState(false);

  useEffect(() => {
    if (!hasLoaded) {
      fetchTerms(tenantId || undefined);
      setHasLoaded(true);
    }
  }, [tenantId, hasLoaded, fetchTerms]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link href="/gift-cards" className="inline-flex items-center gap-2 text-purple-600 hover:text-purple-700 mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Gift Cards
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Terms & Conditions</h1>
          <p className="text-gray-600 mt-2">Gift card terms and conditions</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {loading ? (
          <Card>
            <CardContent className="pt-12 pb-12 flex items-center justify-center">
              <div className="text-center">
                <Loader className="w-8 h-8 text-purple-600 animate-spin mx-auto mb-4" />
                <p className="text-gray-600">Loading terms...</p>
              </div>
            </CardContent>
          </Card>
        ) : error ? (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : terms ? (
          <>
            <Card>
              <CardHeader>
                <CardTitle>Gift Card Terms & Conditions</CardTitle>
                <CardDescription>
                  Version {terms.version} • Effective {new Date(terms.effective_date).toLocaleDateString('en-NG', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                    {terms.content}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Default Terms */}
            {terms.version === '1.0' && terms.content === 'Default terms and conditions' && (
              <Card className="mt-8">
                <CardHeader>
                  <CardTitle className="text-base">Standard Gift Card Terms</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6 text-sm">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">1. Validity Period</h3>
                    <p className="text-gray-600">
                      Gift cards are valid for 12 months from the date of purchase. After expiration, the card cannot be used.
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">2. Balance Checking</h3>
                    <p className="text-gray-600">
                      You can check your gift card balance anytime without logging in. Simply visit our website and enter your card number.
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">3. Redemption</h3>
                    <p className="text-gray-600">
                      Gift cards can be redeemed at any of our locations or online. Present your card number at checkout or provide it during online purchase.
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">4. Non-Transferable</h3>
                    <p className="text-gray-600">
                      Gift cards are non-transferable except through our official transfer feature. Unauthorized transfers are not permitted.
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">5. No Cash Value</h3>
                    <p className="text-gray-600">
                      Gift cards have no cash value and cannot be redeemed for cash. Unused balance will be forfeited upon expiration.
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">6. Lost or Stolen Cards</h3>
                    <p className="text-gray-600">
                      We are not responsible for lost, stolen, or damaged gift cards. Please keep your card number safe and secure.
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">7. PIN Protection</h3>
                    <p className="text-gray-600">
                      You can optionally set a PIN for your gift card. This PIN is required for redemption if enabled.
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">8. Fraud Prevention</h3>
                    <p className="text-gray-600">
                      We monitor for suspicious activity. Cards may be temporarily suspended if unusual activity is detected.
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">9. Refunds</h3>
                    <p className="text-gray-600">
                      Gift cards are non-refundable. However, if you have a dispute, please contact our customer service team.
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">10. Changes to Terms</h3>
                    <p className="text-gray-600">
                      We reserve the right to modify these terms at any time. Changes will be effective immediately upon posting.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Action Buttons */}
            <div className="mt-8 flex gap-4 justify-center">
              <Link href="/gift-cards">
                <Button variant="outline">
                  Back to Gift Cards
                </Button>
              </Link>
              <Link href="/gift-cards/purchase">
                <Button>
                  Purchase Gift Card
                </Button>
              </Link>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}
