'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth/auth-context';
import {
  useGenerateReferralLink,
  useGetReferralDashboard,
  useGetReferralAnalytics,
} from '@/lib/api/hooks/useReferrals';
import { ReferralStatsComponent } from '@/components/referrals/referral-stats';
import { ReferralList } from '@/components/referrals/referral-list';
import { SocialShareButtons } from '@/components/referrals/social-share-buttons';
import { RedeemRewardsModal } from '@/components/referrals/redeem-rewards-modal';
import { ReferralAnalyticsDashboard } from '@/components/referrals/referral-analytics';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import { GiftIcon, BarChart3Icon } from '@/components/icons';

/**
 * Referrals dashboard page
 * Validates: REQ-1, REQ-4, REQ-8, REQ-11
 */
export default function ReferralsPage() {
  const { user, tenant } = useAuth();
  const [showRedeemModal, setShowRedeemModal] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);

  // Generate referral link on page load
  const generateLinkMutation = useGenerateReferralLink();
  useEffect(() => {
    if (user?.id && !generateLinkMutation.isPending) {
      generateLinkMutation.mutate({ client_id: user.id });
    }
  }, [user?.id]);

  // Fetch dashboard data
  const { data: dashboard, isLoading: dashboardLoading } =
    useGetReferralDashboard(user?.id || '');

  // Fetch analytics data (for salon owners)
  const { data: analytics, isLoading: analyticsLoading } =
    useGetReferralAnalytics();

  const isSalonOwner = tenant?.role === 'owner' || tenant?.role === 'admin';

  if (dashboardLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Referral Program</h1>
          <p className="text-muted-foreground mt-1">
            Share your referral link and earn rewards
          </p>
        </div>
        <div className="flex gap-2">
          {isSalonOwner && (
            <Button
              variant="outline"
              onClick={() => setShowAnalytics(!showAnalytics)}
              className="flex items-center gap-2"
            >
              <BarChart3Icon size={18} />
              {showAnalytics ? 'Hide' : 'Show'} Analytics
            </Button>
          )}
          <Button
            onClick={() => setShowRedeemModal(true)}
            className="flex items-center gap-2"
          >
            <GiftIcon size={18} />
            Redeem Rewards
          </Button>
        </div>
      </div>

      {/* Analytics Section (for salon owners) */}
      {isSalonOwner && showAnalytics && analytics && !analyticsLoading && (
        <div className="border-t pt-6">
          <h2 className="text-2xl font-bold mb-4">Program Analytics</h2>
          <ReferralAnalyticsDashboard analytics={analytics} />
        </div>
      )}

      {/* Client Referral Section */}
      <div className="space-y-6">
        {/* Referral Stats */}
        {dashboard && (
          <ReferralStatsComponent
            stats={{
              total_referrals: dashboard.total_referrals || 0,
              successful_referrals: dashboard.successful_referrals || 0,
              pending_referrals:
                (dashboard.total_referrals || 0) -
                (dashboard.successful_referrals || 0),
              total_rewards: dashboard.total_rewards_earned || 0,
            }}
            dashboard={dashboard}
          />
        )}

        {/* Social Share Section */}
        {dashboard && (
          <Card>
            <CardHeader>
              <CardTitle>Share Your Referral Link</CardTitle>
            </CardHeader>
            <CardContent>
              <SocialShareButtons
                referralLink={dashboard.referral_link || ''}
                referralCode={dashboard.referral_code || ''}
                salonName={tenant?.name || 'our salon'}
              />
            </CardContent>
          </Card>
        )}

        {/* Referral History */}
        {dashboard && dashboard.referral_history.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Referral History</CardTitle>
            </CardHeader>
            <CardContent>
              <ReferralList
                referrals={dashboard.referral_history}
                sortBy="recent"
              />
            </CardContent>
          </Card>
        )}

        {/* Empty State */}
        {dashboard && dashboard.referral_history.length === 0 && (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-8">
                <GiftIcon size={48} className="mx-auto text-muted-foreground mb-3" />
                <h3 className="font-semibold mb-1">No referrals yet</h3>
                <p className="text-muted-foreground text-sm">
                  Share your referral link to start earning rewards
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Redeem Rewards Modal */}
      <RedeemRewardsModal
        isOpen={showRedeemModal}
        onClose={() => setShowRedeemModal(false)}
        clientId={user?.id || ''}
        availableBalance={dashboard?.pending_rewards || 0}
      />
    </div>
  );
}
