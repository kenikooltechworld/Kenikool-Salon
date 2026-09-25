import { useState, useCallback } from "react";
import { RefreshCwIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";

interface RefreshButtonProps {
  onClick: () => void | Promise<void>;
  label?: string;
}

export function RefreshButton({ onClick, label = "Refresh" }: RefreshButtonProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = useCallback(async () => {
    setIsLoading(true);
    try {
      await onClick();
    } finally {
      setIsLoading(false);
    }
  }, [onClick]);

  return (
    <Button
      onClick={handleClick}
      variant="outline"
      size="sm"
      className="gap-2"
      disabled={isLoading}
    >
      <RefreshCwIcon size={16} className={isLoading ? "animate-spin" : ""} />
      {label}
    </Button>
  );
}
