import { useState } from "react";
import { useGetAccounts } from "@/lib/api/hooks/useAccounting";
import {
  ChartOfAccounts,
  AccountFormModal,
  JournalEntryForm,
  FinancialReports,
} from "@/components/accounting";
import { DollarSignIcon, PlusIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function AccountingPage() {
  const { data: accounts = [], isLoading } = useGetAccounts();
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);

  const handleEdit = (account: any) => {
    setSelectedAccount(account);
    setIsFormOpen(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <DollarSignIcon size={32} className="text-[var(--primary)]" />
            Accounting
          </h1>
          <p className="text-[var(--muted-foreground)] mt-1">
            Manage your general ledger and financial records
          </p>
        </div>
      </div>

      <Tabs defaultValue="accounts" className="space-y-6">
        <TabsList>
          <TabsTrigger value="accounts">Chart of Accounts</TabsTrigger>
          <TabsTrigger value="journal">Journal Entries</TabsTrigger>
          <TabsTrigger value="reports">Financial Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="accounts" className="space-y-4">
          <div className="flex justify-end">
            <Button
              onClick={() => {
                setSelectedAccount(null);
                setIsFormOpen(true);
              }}
            >
              <PlusIcon size={20} />
              Add Account
            </Button>
          </div>
          <Card className="p-6">
            <ChartOfAccounts accounts={accounts} onEdit={handleEdit} />
          </Card>
        </TabsContent>

        <TabsContent value="journal">
          <JournalEntryForm />
        </TabsContent>

        <TabsContent value="reports">
          <FinancialReports />
        </TabsContent>
      </Tabs>

      <AccountFormModal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setSelectedAccount(null);
        }}
        account={selectedAccount}
      />
    </div>
  );
}
