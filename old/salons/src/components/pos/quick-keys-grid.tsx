import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { formatCurrency } from "@/lib/utils/currency";

interface QuickKey {
  id: string;
  type: "service" | "product";
  name: string;
  price: number;
}

interface QuickKeysGridProps {
  quickKeys: QuickKey[];
  onEditQuickKeys: () => void;
  onQuickKeyClick: (key: QuickKey) => void;
}

export function QuickKeysGrid({
  quickKeys,
  onEditQuickKeys,
  onQuickKeyClick,
}: QuickKeysGridProps) {
  if (quickKeys.length === 0) return null;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm">Quick Keys</CardTitle>
          <Button variant="ghost" size="sm" onClick={onEditQuickKeys}>
            Edit
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
          {quickKeys.map((key) => (
            <Card
              key={key.id}
              className="cursor-pointer hover:bg-accent transition-colors"
              onClick={() => onQuickKeyClick(key)}
            >
              <CardContent className="p-3">
                <p className="font-medium text-sm truncate">{key.name}</p>
                <p className="text-xs text-muted-foreground">
                  {formatCurrency(key.price)}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
