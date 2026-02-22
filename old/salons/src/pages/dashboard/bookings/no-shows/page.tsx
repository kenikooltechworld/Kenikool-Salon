import React, { useState } from "react";
import { NoShowPolicyEnforcer } from "@/components/booking/no-show-policy-enforcer";
import { NoShowTracker } from "@/components/booking/no-show-tracker";
import { NoShowFeeCalculator } from "@/components/booking/no-show-fee-calculator";
import { useNoShowTracking } from "@/lib/api/hooks/useNoShowTracking";

export default function NoShowsPage() {
  const [activeTab, setActiveTab] = useState<"tracker" | "policy" | "fees">(
    "tracker",
  );
  const { noShows, loading } = useNoShowTracking();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">No-Show Management</h1>
      </div>

      <div className="flex gap-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab("tracker")}
          className={`px-4 py-2 font-medium ${
            activeTab === "tracker"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Tracker
        </button>
        <button
          onClick={() => setActiveTab("policy")}
          className={`px-4 py-2 font-medium ${
            activeTab === "policy"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Policy
        </button>
        <button
          onClick={() => setActiveTab("fees")}
          className={`px-4 py-2 font-medium ${
            activeTab === "fees"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Fees
        </button>
      </div>

      {activeTab === "tracker" && (
        <NoShowTracker noShows={noShows} loading={loading} />
      )}
      {activeTab === "policy" && <NoShowPolicyEnforcer />}
      {activeTab === "fees" && <NoShowFeeCalculator />}
    </div>
  );
}
