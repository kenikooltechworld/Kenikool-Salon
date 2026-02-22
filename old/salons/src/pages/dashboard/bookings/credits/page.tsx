import React, { useState } from "react";
import { CreditBalanceDisplay } from "@/components/booking/credit-balance-display";
import { CreditTransactionLog } from "@/components/booking/credit-transaction-log";
import { CreditExpirationWarning } from "@/components/booking/credit-expiration-warning";
import { PackageCreditRedemption } from "@/components/booking/package-credit-redemption";
import { usePackageCredits } from "@/lib/api/hooks/usePackageCredits";

export default function CreditsPage() {
  const [activeTab, setActiveTab] = useState<
    "balance" | "transactions" | "redemption"
  >("balance");
  const { credits, loading } = usePackageCredits();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Package Credits</h1>
      </div>

      <CreditExpirationWarning />

      <div className="flex gap-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab("balance")}
          className={`px-4 py-2 font-medium ${
            activeTab === "balance"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Balance
        </button>
        <button
          onClick={() => setActiveTab("transactions")}
          className={`px-4 py-2 font-medium ${
            activeTab === "transactions"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Transactions
        </button>
        <button
          onClick={() => setActiveTab("redemption")}
          className={`px-4 py-2 font-medium ${
            activeTab === "redemption"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Redemption
        </button>
      </div>

      {activeTab === "balance" && (
        <CreditBalanceDisplay credits={credits} loading={loading} />
      )}
      {activeTab === "transactions" && (
        <CreditTransactionLog credits={credits} loading={loading} />
      )}
      {activeTab === "redemption" && (
        <PackageCreditRedemption
          availableCredits={credits?.balance || 0}
          bookingTotal={0}
          onCreditsApply={() => {}}
        />
      )}
    </div>
  );
}
