import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Keyboard } from "@/components/icons";

interface KeyboardShortcutsProps {
  onNewTransaction?: () => void;
  onSearch?: () => void;
  onPayment?: () => void;
  onDiscount?: () => void;
  onPark?: () => void;
  onQuickKeys?: () => void;
}

export function KeyboardShortcuts({
  onNewTransaction,
  onSearch,
  onPayment,
  onDiscount,
  onPark,
  onQuickKeys,
}: KeyboardShortcutsProps) {
  const [showHelp, setShowHelp] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + N: New Transaction
      if ((e.ctrlKey || e.metaKey) && e.key === "n") {
        e.preventDefault();
        onNewTransaction?.();
      }

      // Ctrl/Cmd + F: Search
      if ((e.ctrlKey || e.metaKey) && e.key === "f") {
        e.preventDefault();
        onSearch?.();
      }

      // Ctrl/Cmd + P: Payment
      if ((e.ctrlKey || e.metaKey) && e.key === "p") {
        e.preventDefault();
        onPayment?.();
      }

      // Ctrl/Cmd + D: Discount
      if ((e.ctrlKey || e.metaKey) && e.key === "d") {
        e.preventDefault();
        onDiscount?.();
      }

      // Ctrl/Cmd + H: Park Transaction
      if ((e.ctrlKey || e.metaKey) && e.key === "h") {
        e.preventDefault();
        onPark?.();
      }

      // Ctrl/Cmd + K: Quick Keys
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        onQuickKeys?.();
      }

      // Ctrl/Cmd + /: Show shortcuts help
      if ((e.ctrlKey || e.metaKey) && e.key === "/") {
        e.preventDefault();
        setShowHelp(true);
      }

      // F1-F12: Quick payment methods
      if (e.key.startsWith("F") && !e.ctrlKey && !e.metaKey && !e.altKey) {
        e.preventDefault();
        const fKey = parseInt(e.key.substring(1));
        if (fKey >= 1 && fKey <= 12) {
          // Trigger quick payment for F-keys
          console.log(`Quick payment F${fKey} triggered`);
        }
      }

      // Escape: Close modals
      if (e.key === "Escape") {
        setShowHelp(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onNewTransaction, onSearch, onPayment, onDiscount, onPark, onQuickKeys]);

  const shortcuts = [
    { key: "Ctrl/Cmd + N", action: "New Transaction" },
    { key: "Ctrl/Cmd + F", action: "Search Transactions" },
    { key: "Ctrl/Cmd + P", action: "Process Payment" },
    { key: "Ctrl/Cmd + D", action: "Apply Discount" },
    { key: "Ctrl/Cmd + H", action: "Park Transaction" },
    { key: "Ctrl/Cmd + K", action: "Quick Keys" },
    { key: "Ctrl/Cmd + /", action: "Show Shortcuts" },
    { key: "F1-F12", action: "Quick Payment Methods" },
    { key: "Escape", action: "Close Modal" },
  ];

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setShowHelp(true)}
        className="gap-2"
      >
        <Keyboard className="h-4 w-4" />
        Shortcuts
      </Button>

      <Dialog open={showHelp} onOpenChange={setShowHelp}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Keyboard Shortcuts</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            {shortcuts.map((shortcut, index) => (
              <div
                key={index}
                className="flex items-center justify-between py-2 border-b last:border-0"
              >
                <span className="text-sm text-muted-foreground">
                  {shortcut.action}
                </span>
                <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded-lg">
                  {shortcut.key}
                </kbd>
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
