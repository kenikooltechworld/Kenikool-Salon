"use client";

import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface Commission {
  _id: string;
  source_reference: string;
  base_amount: number;
  commission_rate: number;
  commission_amount: number;
  payout_status: "pending" | "paid" | "disputed";
  payout_date?: string;
  payout_method?: string;
  created_at: string;
}

interface CommissionHistoryProps {
  staffId: string;
  title?: string;
}

const STATUS_COLORS = {
  pending: "bg-yellow-100 text-yellow-800",
  paid: "bg-green-100 text-green-800",
  disputed: "bg-red-100 text-red-800",
};

export function CommissionHistory({
  staffId,
  title = "Commission History",
}: CommissionHistoryProps) {
  const { data: response, isLoading } = useQuery({
    queryKey: ["commission-history", staffId],
    queryFn: async () => {
      const res = await fetch(`/api/staff/commissions/${staffId}`);
      if (!res.ok) throw new Error("Failed to fetch commissions");
      return res.json();
    },
  });

  const commissions: Commission[] = response?.data || [];

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!commissions || commissions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No commission history found
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Source</TableHead>
                <TableHead className="text-right">Base Amount</TableHead>
                <TableHead className="text-right">Rate</TableHead>
                <TableHead className="text-right">Commission</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Payout Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {commissions.map((commission) => (
                <TableRow key={commission._id}>
                  <TableCell>
                    {format(new Date(commission.created_at), "MMM dd, yyyy")}
                  </TableCell>
                  <TableCell className="max-w-xs truncate">
                    {commission.source_reference}
                  </TableCell>
                  <TableCell className="text-right">
                    ${commission.base_amount.toFixed(2)}
                  </TableCell>
                  <TableCell className="text-right">
                    {commission.commission_rate}%
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    ${commission.commission_amount.toFixed(2)}
                  </TableCell>
                  <TableCell>
                    <Badge
                      className={
                        STATUS_COLORS[
                          commission.payout_status as keyof typeof STATUS_COLORS
                        ]
                      }
                    >
                      {commission.payout_status.charAt(0).toUpperCase() +
                        commission.payout_status.slice(1)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {commission.payout_date
                      ? format(new Date(commission.payout_date), "MMM dd, yyyy")
                      : "-"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
