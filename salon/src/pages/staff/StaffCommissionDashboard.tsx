import { useState } from "react";
import { useStaff } from "@/hooks/useStaff";
import { StaffCommissionDashboard } from "@/components/staff/StaffCommissionDashboard";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";

export default function StaffCommissionDashboardPage() {
  const [selectedStaffId, setSelectedStaffId] = useState<string>("");
  const { data: staffData, isLoading: staffLoading } = useStaff();

  const staff = staffData?.staff || [];
  const selectedStaff = staff.find((s: any) => s.id === selectedStaffId);

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-foreground">
          Staff Commissions
        </h1>
        <p className="text-muted-foreground mt-2">
          Track and manage staff commission earnings
        </p>
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
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 md:gap-3">
            {staff.map((member: any) => (
              <Button
                key={member.id}
                variant={selectedStaffId === member.id ? "primary" : "outline"}
                onClick={() => setSelectedStaffId(member.id)}
                className="justify-start text-sm md:text-base"
              >
                {member.firstName} {member.lastName}
              </Button>
            ))}
          </div>
        )}
      </Card>

      {/* Commission Dashboard */}
      {selectedStaffId && selectedStaff && (
        <StaffCommissionDashboard
          staffId={selectedStaffId}
          staffName={`${selectedStaff.firstName} ${selectedStaff.lastName}`}
        />
      )}
    </div>
  );
}
