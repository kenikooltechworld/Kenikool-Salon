import { useState } from "react";
import {
  useCommissions,
  useCommissionPayouts,
  useCreateCommissionPayout,
} from "@/hooks/useCommissions";
import { useStaff } from "@/hooks/useStaff";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

export default function CommissionDashboard() {
  const [selectedStaffId, setSelectedStaffId] = useState<string>("");
  const [page, setPage] = useState(1);
  const [payoutPeriod, setPayoutPeriod] = useState("monthly");
  const { data: staffData, isLoading: staffLoading } = useStaff();
  const { data: commissionsData, isLoading: commissionsLoading } =
    useCommissions(selectedStaffId, { page, pageSize: 20 });
  const { data: payoutsData, isLoading: payoutsLoading } = useCommissionPayouts(
    {
      staffId: selectedStaffId,
      page: 1,
      pageSize: 10,
    },
  );
  const createPayout = useCreateCommissionPayout();
  const { showToast } = useToast();

  const staff = staffData?.staff || [];
  const commissions = commissionsData?.commissions || [];
  const payouts = payoutsData?.payouts || [];
  const totalCommissions = commissionsData?.total || 0;

  const totalEarned = commissions.reduce(
    (sum, c) => sum + c.commissionAmount,
    0,
  );
  const avgCommission =
    commissions.length > 0 ? totalEarned / commissions.length : 0;

  const handleProcessPayout = async () => {
    if (!selectedStaffId) {
      showToast({
        title: "Error",
        description: "Please select a staff member",
        variant: "error",
      });
      return;
    }

    try {
      await createPayout.mutateAsync({
        staffId: selectedStaffId,
        period: payoutPeriod,
      });
      showToast({
        title: "Success",
        description: "Commission payout processed successfully",
        variant: "success",
      });
    } catch (error) {
      showToast({
        title: "Error",
        description: "Failed to process payout",
        variant: "error",
      });
    }
  };

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 md:gap-4">
        <Card className="p-4 md:p-6">
          <p className="text-xs md:text-sm text-muted-foreground mb-2">
            Total Commissions
          </p>
          <p className="text-2xl md:text-3xl font-bold text-foreground">
            ₦{totalEarned.toLocaleString("en-NG", { maximumFractionDigits: 2 })}
          </p>
        </Card>
        <Card className="p-4 md:p-6">
          <p className="text-xs md:text-sm text-muted-foreground mb-2">
            Average Commission
          </p>
          <p className="text-2xl md:text-3xl font-bold text-foreground">
            ₦
            {avgCommission.toLocaleString("en-NG", {
              maximumFractionDigits: 2,
            })}
          </p>
        </Card>
        <Card className="p-4 md:p-6">
          <p className="text-xs md:text-sm text-muted-foreground mb-2">
            Transactions
          </p>
          <p className="text-2xl md:text-3xl font-bold text-foreground">
            {commissions.length}
          </p>
        </Card>
      </div>

      {/* Staff Selection */}
      <Card className="p-4 md:p-6">
        <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">
          Select Staff Member
        </h3>
        {staffLoading ? (
          <div className="flex justify-center py-4">
            <Spinner />
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 md:gap-3">
            {staff.map((member: any) => (
              <Button
                key={member.id}
                variant={selectedStaffId === member.id ? "primary" : "outline"}
                onClick={() => {
                  setSelectedStaffId(member.id);
                  setPage(1);
                }}
                className="justify-start text-sm md:text-base"
              >
                {member.firstName} {member.lastName}
              </Button>
            ))}
          </div>
        )}
      </Card>

      {selectedStaffId && (
        <>
          {/* Commissions List */}
          <Card className="p-4 md:p-6">
            <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">
              Commission Breakdown
            </h3>
            {commissionsLoading ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : commissions.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                No commissions yet
              </p>
            ) : (
              <div className="space-y-2 md:space-y-3">
                {commissions.map((commission) => (
                  <div
                    key={commission.id}
                    className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 p-3 md:p-4 bg-muted rounded-lg"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm md:text-base text-foreground truncate">
                        Transaction {commission.transactionId.slice(0, 8)}
                      </p>
                      <p className="text-xs md:text-sm text-muted-foreground">
                        {new Date(commission.calculatedAt).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <p className="font-bold text-sm md:text-base text-foreground">
                        ₦
                        {commission.commissionAmount.toLocaleString("en-NG", {
                          maximumFractionDigits: 2,
                        })}
                      </p>
                      <Badge variant="secondary" className="text-xs mt-1">
                        {commission.commissionRate}% {commission.commissionType}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalCommissions > 20 && (
              <div className="flex justify-between items-center mt-6 pt-6 border-t border-border gap-2 flex-wrap">
                <Button
                  variant="outline"
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="text-sm"
                >
                  Previous
                </Button>
                <span className="text-xs md:text-sm text-muted-foreground">
                  Page {page} of {Math.ceil(totalCommissions / 20)}
                </span>
                <Button
                  variant="outline"
                  onClick={() => setPage(page + 1)}
                  disabled={page >= Math.ceil(totalCommissions / 20)}
                  className="text-sm"
                >
                  Next
                </Button>
              </div>
            )}
          </Card>

          {/* Payouts History */}
          <Card className="p-4 md:p-6">
            <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">
              Payout History
            </h3>
            {payoutsLoading ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : payouts.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">
                No payouts yet
              </p>
            ) : (
              <div className="space-y-2 md:space-y-3">
                {payouts.map((payout) => (
                  <div
                    key={payout.id}
                    className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 p-3 md:p-4 bg-muted rounded-lg"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm md:text-base text-foreground capitalize truncate">
                        {payout.period}
                      </p>
                      <p className="text-xs md:text-sm text-muted-foreground">
                        {new Date(payout.payoutDate).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <p className="font-bold text-sm md:text-base text-foreground">
                        ₦
                        {payout.payoutAmount.toLocaleString("en-NG", {
                          maximumFractionDigits: 2,
                        })}
                      </p>
                      <Badge
                        variant={
                          payout.status === "processed"
                            ? "default"
                            : payout.status === "failed"
                              ? "destructive"
                              : "secondary"
                        }
                        className="text-xs mt-1"
                      >
                        {payout.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Process Payout */}
          <Card className="p-4 md:p-6">
            <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">
              Process Payout
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Payout Period
                </label>
                <select
                  value={payoutPeriod}
                  onChange={(e) => setPayoutPeriod(e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm"
                >
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <Button
                onClick={handleProcessPayout}
                disabled={createPayout.isPending}
                className="w-full text-sm md:text-base"
              >
                {createPayout.isPending ? "Processing..." : "Process Payout"}
              </Button>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
