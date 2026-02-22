import { useState } from "react";
import { useStaff } from "@/hooks/useStaff";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Modal } from "@/components/ui/modal";
import { UserIcon, XIcon } from "@/components/icons";

interface StaffSelectorProps {
  onSelect: (staffId: string, staffName: string) => void;
  selectedStaffId?: string;
  selectedStaffName?: string;
}

export default function StaffSelector({
  onSelect,
  selectedStaffId,
  selectedStaffName,
}: StaffSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { data: staffData, isLoading } = useStaff({ pageSize: 50 });

  const staff = staffData?.staff || [];

  const handleSelect = (staffId: string, staffName: string) => {
    onSelect(staffId, staffName);
    setIsOpen(false);
  };

  const handleClear = () => {
    onSelect("", "");
  };

  return (
    <>
      <div className="flex gap-2">
        <Button
          variant="outline"
          onClick={() => setIsOpen(true)}
          className="flex-1 justify-start text-left"
        >
          <UserIcon size={16} className="mr-2" />
          {selectedStaffName || "Select Staff"}
        </Button>
        {selectedStaffId && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClear}
            className="text-destructive hover:text-destructive"
          >
            <XIcon size={16} />
          </Button>
        )}
      </div>

      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Select Staff Member</h2>

          <div className="max-h-96 overflow-y-auto space-y-2">
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : staff.length === 0 ? (
              <Card className="p-4 text-center text-muted-foreground">
                No staff members found
              </Card>
            ) : (
              staff.map((member) => (
                <Card
                  key={member.id}
                  className="p-3 cursor-pointer hover:bg-muted transition"
                  onClick={() => handleSelect(member.id, member.name)}
                >
                  <p className="font-medium text-foreground">{member.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {member.email}
                  </p>
                  {member.phone && (
                    <p className="text-sm text-muted-foreground">
                      {member.phone}
                    </p>
                  )}
                </Card>
              ))
            )}
          </div>

          <Button
            variant="outline"
            onClick={() => setIsOpen(false)}
            className="w-full"
          >
            Close
          </Button>
        </div>
      </Modal>
    </>
  );
}
