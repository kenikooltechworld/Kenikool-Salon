import { useState } from "react";
import { useCheckGiftCardBalance } from "@/hooks/useGiftCards";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  CreditCardIcon as CreditCard,
  SearchIcon as Search,
} from "@/components/icons";
import { format } from "date-fns";

export default function GiftCardBalanceChecker() {
  const [code, setCode] = useState("");
  const checkBalance = useCheckGiftCardBalance();

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim()) return;

    try {
      await checkBalance.mutateAsync(code.trim().toUpperCase());
    } catch (error: any) {
      // Error is handled by the mutation
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800";
      case "redeemed":
        return "bg-gray-100 text-gray-800";
      case "expired":
        return "bg-red-100 text-red-800";
      case "cancelled":
        return "bg-orange-100 text-orange-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="max-w-md mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Check Gift Card Balance
          </CardTitle>
          <CardDescription>
            Enter your gift card code to check the balance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCheck} className="space-y-4">
            <div>
              <Label htmlFor="giftCardCode">Gift Card Code</Label>
              <Input
                id="giftCardCode"
                placeholder="GC-XXXX-XXXX-XXXX"
                value={code}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                maxLength={50}
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={checkBalance.isPending || !code.trim()}
            >
              <Search className="mr-2 h-4 w-4" />
              {checkBalance.isPending ? "Checking..." : "Check Balance"}
            </Button>
          </form>

          {checkBalance.isError && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">
                {(checkBalance.error as any)?.response?.data?.detail ||
                  "Gift card not found or invalid code"}
              </p>
            </div>
          )}

          {checkBalance.isSuccess && checkBalance.data && (
            <div className="mt-6 space-y-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm text-gray-600">Code:</span>
                  <span className="font-mono font-semibold">
                    {checkBalance.data.code}
                  </span>
                </div>
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm text-gray-600">Status:</span>
                  <Badge className={getStatusColor(checkBalance.data.status)}>
                    {checkBalance.data.status.toUpperCase()}
                  </Badge>
                </div>
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm text-gray-600">Balance:</span>
                  <span className="text-2xl font-bold text-blue-600">
                    {checkBalance.data.currency}{" "}
                    {checkBalance.data.current_balance.toLocaleString()}
                  </span>
                </div>
                {checkBalance.data.expiry_date && (
                  <div className="flex justify-between items-start">
                    <span className="text-sm text-gray-600">Expires:</span>
                    <span className="text-sm">
                      {format(new Date(checkBalance.data.expiry_date), "PPP")}
                    </span>
                  </div>
                )}
              </div>

              {checkBalance.data.is_active &&
                checkBalance.data.current_balance > 0 && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                    <p className="text-sm text-green-800">
                      This gift card is active and ready to use!
                    </p>
                  </div>
                )}

              {!checkBalance.data.is_active && (
                <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
                  <p className="text-sm text-gray-800">
                    This gift card is no longer active.
                  </p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
