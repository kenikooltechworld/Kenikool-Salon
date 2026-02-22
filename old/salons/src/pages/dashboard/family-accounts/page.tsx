/**
 * Family Accounts Management Page
 * Task 2.6a
 */
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Input } from "@/components/ui/input";
import { PlusIcon, SearchIcon } from "@/components/icons";
import { useFamilyAccounts } from "@/lib/api/hooks/useFamilyAccounts";
import {
  FamilyAccountCard,
  FamilyAccountRegistrationModal,
} from "@/components/booking";

export default function FamilyAccountsPage() {
  const [isRegistrationModalOpen, setIsRegistrationModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(
    null,
  );

  const { data: familyAccounts, isLoading } = useFamilyAccounts();

  // Filter accounts based on search
  const filteredAccounts = familyAccounts?.filter(
    (account) =>
      account.account_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      account.family_account_id
        .toLowerCase()
        .includes(searchQuery.toLowerCase()),
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">
            Family Accounts
          </h1>
          <p className="text-muted-foreground">
            Manage family accounts and deferred payments
          </p>
        </div>
        <Button onClick={() => setIsRegistrationModalOpen(true)}>
          <PlusIcon size={20} />
          Register Family Account
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Total Families</div>
          <div className="text-2xl font-bold">
            {familyAccounts?.length || 0}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Total Members</div>
          <div className="text-2xl font-bold">
            {familyAccounts?.reduce(
              (sum, acc) => sum + acc.members.length,
              0,
            ) || 0}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Avg Family Size</div>
          <div className="text-2xl font-bold">
            {familyAccounts && familyAccounts.length > 0
              ? (
                  familyAccounts.reduce(
                    (sum, acc) => sum + acc.members.length,
                    0,
                  ) / familyAccounts.length
                ).toFixed(1)
              : 0}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">
            Outstanding Balance
          </div>
          <div className="text-2xl font-bold">
            $
            {familyAccounts
              ?.reduce((sum, acc) => sum + acc.outstanding_balance, 0)
              .toFixed(2) || "0.00"}
          </div>
        </Card>
      </div>

      {/* Search */}
      <Card className="p-4">
        <div className="relative">
          <SearchIcon
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground"
            size={20}
          />
          <Input
            type="text"
            placeholder="Search by family name or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </Card>

      {/* Family Accounts List */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : filteredAccounts && filteredAccounts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAccounts.map((account) => (
            <FamilyAccountCard
              key={account.id}
              account={account}
              onClick={() => setSelectedAccountId(account.id)}
            />
          ))}
        </div>
      ) : (
        <Card className="p-12 text-center">
          <p className="text-muted-foreground">
            {searchQuery
              ? "No family accounts found matching your search."
              : "No family accounts yet. Register your first family account!"}
          </p>
        </Card>
      )}

      {/* Registration Modal */}
      <FamilyAccountRegistrationModal
        isOpen={isRegistrationModalOpen}
        onClose={() => setIsRegistrationModalOpen(false)}
        onSuccess={() => {
          setIsRegistrationModalOpen(false);
        }}
      />
    </div>
  );
}
