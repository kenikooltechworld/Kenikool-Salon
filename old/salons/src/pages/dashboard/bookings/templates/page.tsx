import React, { useState } from "react";
import { TemplateManager } from "@/components/booking/template-manager";
import { TemplateLibrary } from "@/components/booking/template-library";
import { useBookingTemplates } from "@/lib/api/hooks/useBookingTemplates";

export default function BookingTemplatesPage() {
  const [activeTab, setActiveTab] = useState<"manage" | "library">("manage");
  const { templates, loading } = useBookingTemplates();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Booking Templates</h1>
      </div>

      <div className="flex gap-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab("manage")}
          className={`px-4 py-2 font-medium ${
            activeTab === "manage"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Manage Templates
        </button>
        <button
          onClick={() => setActiveTab("library")}
          className={`px-4 py-2 font-medium ${
            activeTab === "library"
              ? "border-b-2 border-blue-600 text-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Template Library
        </button>
      </div>

      {activeTab === "manage" && <TemplateManager />}
      {activeTab === "library" && <TemplateLibrary />}
    </div>
  );
}
