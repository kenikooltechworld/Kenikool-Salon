import React, { useState } from "react";
import { useFamilyAccounts } from "@/lib/api/hooks/useFamilyAccounts";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";

interface FamilyMemberSelectorProps {
  onMemberSelect: (memberId: string, memberName: string) => void;
  selectedMemberId?: string;
}

export const FamilyMemberSelector: React.FC<FamilyMemberSelectorProps> = ({
  onMemberSelect,
  selectedMemberId,
}) => {
  const { data: familyAccounts = [], isLoading: loading } = useFamilyAccounts();
  const [expanded, setExpanded] = useState(false);

  // Flatten all family members from all accounts
  const allMembers = familyAccounts.flatMap((account) => account.members || []);

  if (loading) {
    return (
      <div className="text-sm text-muted-foreground">
        Loading family members...
      </div>
    );
  }

  if (!allMembers || allMembers.length === 0) {
    return (
      <div className="text-sm text-muted-foreground">
        No family members found
      </div>
    );
  }

  const selectedMember = allMembers.find(
    (m) => m.client_id === selectedMemberId,
  );

  return (
    <div className="space-y-3">
      <Button
        onClick={() => setExpanded(!expanded)}
        variant="outline"
        className="w-full justify-between"
      >
        <span className="font-medium text-sm">
          Booking For
          {selectedMember && (
            <span className="ml-2 text-xs bg-accent text-accent-foreground px-2 py-1 rounded">
              {selectedMember.name}
            </span>
          )}
        </span>
        <span className="text-muted-foreground">{expanded ? "▼" : "▶"}</span>
      </Button>

      {expanded && (
        <div className="space-y-3 p-3 border rounded bg-muted">
          <RadioGroup
            value={selectedMemberId || ""}
            onValueChange={(value) => {
              const member = allMembers.find((m) => m.client_id === value);
              if (member) {
                onMemberSelect(member.client_id, member.name);
                setExpanded(false);
              }
            }}
          >
            {allMembers.map((member) => (
              <div
                key={member.client_id}
                className="flex items-center space-x-2"
              >
                <RadioGroupItem
                  value={member.client_id}
                  id={`member-${member.client_id}`}
                />
                <Label
                  htmlFor={`member-${member.client_id}`}
                  className="text-sm cursor-pointer flex-1"
                >
                  <div className="font-medium">{member.name}</div>
                  <div className="text-xs text-muted-foreground">
                    Family member
                  </div>
                </Label>
              </div>
            ))}
          </RadioGroup>
        </div>
      )}
    </div>
  );
};
