'use client';

import { useMemo } from 'react';
import { ReferralHistoryItem } from "@/lib/api/hooks/useReferrals";
import {
  UsersIcon,
  CheckCircleIcon,
  ClockIcon,
  XCircleIcon,
  ChevronDownIcon,
} from "@/components/icons";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface ReferralListProps {
  referrals: ReferralHistoryItem[];
  sortBy?: 'recent' | 'reward' | 'status';
}

/**
 * Enhanced referral list with detailed information
 * Validates: REQ-5
 */
export function ReferralList({ referrals, sortBy = 'recent' }: ReferralListProps) {
  // Sort referrals based on sortBy parameter
  const sortedReferrals = useMemo(() => {
    const sorted = [...referrals];
    
    switch (sortBy) {
      case 'reward':
        return sorted.sort((a, b) => b.reward_amount - a.reward_amount);
      case 'status':
        return sorted.sort((a, b) => a.status.localeCompare(b.status));
      case 'recent':
      default:
        return sorted.sort(
          (a, b) =>
            new Date(b.referred_at).getTime() -
            new Date(a.referred_at).getTime()
        );
    }
  }, [referrals, sortBy]);

  if (referrals.length === 0) {
    return (
      <div className="text-center py-12">
        <UsersIcon size={48} className="mx-auto text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold mb-2">No referrals yet</h3>
        <p className="text-muted-foreground">
          Start referring clients to earn rewards
        </p>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircleIcon size={16} className="text-green-500" />;
      case "pending":
        return <ClockIcon size={16} className="text-yellow-500" />;
      case "expired":
        return <XCircleIcon size={16} className="text-red-500" />;
      default:
        return <ClockIcon size={16} className="text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500/10 text-green-700";
      case "pending":
        return "bg-yellow-500/10 text-yellow-700";
      case "expired":
        return "bg-red-500/10 text-red-700";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  return (
    <div className="border border-border rounded-[var(--radius-lg)] overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-muted/50">
            <TableHead>Referred Client</TableHead>
            <TableHead>Reward Amount</TableHead>
            <TableHead>Referred Date</TableHead>
            <TableHead>Completion Date</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedReferrals.map((referral, idx) => (
            <TableRow key={idx} className="hover:bg-muted/50 transition-colors">
              <TableCell className="font-medium">
                {referral.referred_client_name}
              </TableCell>
              <TableCell className="font-semibold">
                ₦{referral.reward_amount.toFixed(2)}
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {new Date(referral.referred_at).toLocaleDateString()}
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {referral.completed_at
                  ? new Date(referral.completed_at).toLocaleDateString()
                  : '-'}
              </TableCell>
              <TableCell>
                <div
                  className={`inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full font-medium ${getStatusColor(
                    referral.status
                  )}`}
                >
                  {getStatusIcon(referral.status)}
                  {referral.status.charAt(0).toUpperCase() +
                    referral.status.slice(1)}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
