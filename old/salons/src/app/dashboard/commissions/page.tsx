import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { CommissionDashboard } from "@/components/marketplace/admin/commission-dashboard";
import { CommissionTransactions } from "@/components/marketplace/admin/commission-transactions";
import { CommissionRateManager } from "@/components/marketplace/admin/commission-rate-manager";
import { DownloadIcon } from "@/components/icons";

type Tab = "overview" | "transactions" | "rates";

export default function CommissionsPage() {
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  const handleExportCSV = () => {
    // TODO: Implement CSV export
    console.log("Exporting commission report as CSV");
  };

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <motion.div
        className="flex items-center justify-between"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div>
          <h1 className="text-3xl font-bold text-[var(--foreground)]">
            Commission Management
          </h1>
          <p className="text-[var(--muted-foreground)] mt-1">
            Track and manage marketplace commissions
          </p>
        </div>
        <Button
          onClick={handleExportCSV}
          variant="outline"
          className="flex items-center gap-2"
        >
          <DownloadIcon size={18} />
          Export Report
        </Button>
      </motion.div>

      {/* Tabs */}
      <motion.div
        className="flex gap-2 border-b border-[var(--border)]"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        {[
          { id: "overview", label: "Overview" },
          { id: "transactions", label: "Transactions" },
          { id: "rates", label: "Commission Rates" },
        ].map((tab) => (
          <motion.button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as Tab)}
            className={`px-4 py-3 font-medium transition-colors border-b-2 ${
              activeTab === tab.id
                ? "border-[var(--primary)] text-[var(--primary)]"
                : "border-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {tab.label}
          </motion.button>
        ))}
      </motion.div>

      {/* Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {activeTab === "overview" && <CommissionDashboard />}
        {activeTab === "transactions" && <CommissionTransactions />}
        {activeTab === "rates" && <CommissionRateManager />}
      </motion.div>
    </motion.div>
  );
}
