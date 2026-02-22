import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { StarIcon, XIcon, SearchIcon } from "@/components/icons";
import { toast } from "sonner";
import { formatCurrency } from "@/lib/utils/currency";

interface QuickKey {
  id: string;
  name: string;
  price: number;
  type: "service" | "product";
}

interface QuickKeysModalProps {
  open: boolean;
  onClose: () => void;
  services: any[];
  products: any[];
  quickKeys: QuickKey[];
  onUpdateQuickKeys: (keys: QuickKey[]) => void;
}

export function QuickKeysModal({
  open,
  onClose,
  services,
  products,
  quickKeys,
  onUpdateQuickKeys,
}: QuickKeysModalProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedKeys, setSelectedKeys] = useState<QuickKey[]>(quickKeys);

  useEffect(() => {
    setSelectedKeys(quickKeys);
  }, [quickKeys]);

  const allItems = [
    ...services.map((s: any) => ({
      id: s.id,
      name: s.name,
      price: s.price,
      type: "service" as const,
    })),
    ...products.map((p: any) => ({
      id: p.id,
      name: p.name,
      price: p.price,
      type: "product" as const,
    })),
  ];

  const filteredItems = allItems.filter(
    (item) =>
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !selectedKeys.some((key) => key.id === item.id)
  );

  const addQuickKey = (item: QuickKey) => {
    if (selectedKeys.length >= 12) {
      toast.error("Maximum 12 quick keys allowed");
      return;
    }
    setSelectedKeys([...selectedKeys, item]);
  };

  const removeQuickKey = (id: string) => {
    setSelectedKeys(selectedKeys.filter((key) => key.id !== id));
  };

  const handleSave = () => {
    onUpdateQuickKeys(selectedKeys);
    localStorage.setItem("pos_quick_keys", JSON.stringify(selectedKeys));
    toast.success("Quick keys saved");
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <StarIcon className="h-5 w-5" />
            Manage Quick Keys
          </DialogTitle>
          <p className="text-sm text-muted-foreground">
            Pin frequently used items for quick access (max 12)
          </p>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto space-y-4">
          {/* Selected Quick Keys */}
          <div>
            <Label>Quick Keys ({selectedKeys.length}/12)</Label>
            <div className="grid grid-cols-3 gap-2 mt-2">
              {selectedKeys.map((key) => (
                <div
                  key={key.id}
                  className="relative p-3 border rounded-lg bg-primary/5"
                >
                  <Button
                    variant="ghost"
                    size="icon"
                    className="absolute top-1 right-1 h-6 w-6"
                    onClick={() => removeQuickKey(key.id)}
                  >
                    <XIcon className="h-3 w-3" />
                  </Button>
                  <p className="font-medium text-sm pr-6">{key.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatCurrency(key.price)}
                  </p>
                  <Badge variant="outline" className="mt-1 text-xs">
                    {key.type}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          {/* Search and Add */}
          <div>
            <Label>Add Items</Label>
            <div className="relative mt-2">
              <SearchIcon className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search services or products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            <div className="mt-2 space-y-1 max-h-[300px] overflow-y-auto">
              {filteredItems.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  {searchQuery
                    ? "No items found"
                    : "All items are already added"}
                </p>
              ) : (
                filteredItems.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-2 border rounded hover:bg-accent cursor-pointer"
                    onClick={() => addQuickKey(item)}
                  >
                    <div>
                      <p className="font-medium text-sm">{item.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatCurrency(item.price)} • {item.type}
                      </p>
                    </div>
                    <Button variant="ghost" size="sm">
                      Add
                    </Button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="flex gap-2 pt-4 border-t">
          <Button variant="outline" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          <Button onClick={handleSave} className="flex-1">
            Save Quick Keys
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
