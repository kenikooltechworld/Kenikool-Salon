import { Button } from "@/components/ui/button";

interface TabNavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const TABS = [
  { id: "performance", label: "Performance" },
  { id: "commission", label: "Commission" },
  { id: "attendance", label: "Attendance" },
  { id: "schedule", label: "Schedule" },
  { id: "services", label: "Services" },
  { id: "locations", label: "Locations" },
];

export function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
      {TABS.map((tab) => (
        <Button
          key={tab.id}
          variant={activeTab === tab.id ? "primary" : "outline"}
          size="sm"
          className="text-xs cursor-pointer"
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
        </Button>
      ))}
    </div>
  );
}
