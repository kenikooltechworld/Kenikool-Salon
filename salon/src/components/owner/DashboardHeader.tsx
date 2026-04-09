import { Button } from "@/components/ui/button";
import { SettingsIcon } from "@/components/icons";
import { useNavigate } from "react-router-dom";

interface DashboardHeaderProps {
  onSettingsClick?: () => void;
}

export function DashboardHeader({ onSettingsClick }: DashboardHeaderProps) {
  const navigate = useNavigate();

  const handleSettingsClick = () => {
    if (onSettingsClick) {
      onSettingsClick();
    } else {
      navigate("/settings");
    }
  };

  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's your business overview.
        </p>
      </div>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="icon"
          onClick={handleSettingsClick}
          title="Settings"
          className="cursor-pointer"
        >
          <SettingsIcon size={20} />
        </Button>
      </div>
    </div>
  );
}
