import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import {
  useCreateGiftCard,
  useGetGiftCardBalance,
  useRedeemGiftCard,
} from "@/lib/api/hooks/usePOS";
import { GiftIcon, CreditCardIcon } from "@/components/icons";
import { formatCurrency } from "@/lib/utils/currency";

interface GiftCardModalProps {
  open: boolean;
  onClose: () => void;
  onRedeemSuccess?: (amount: number, cardNumber: string) => void;
}

export function GiftCardModal({
  open,
  onClose,
  onRedeemSuccess,
}: GiftCardModalProps) {
  // Sell tab state
  const [amount, setAmount] = useState("");
  const [cardType, setCardType] = useState<"physical" | "digital">("physical");
  const [recipientName, setRecipientName] = useState("");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [message, setMessage] = useState("");
  const [expirationMonths, setExpirationMonths] = useState("12");

  // Redeem tab state
  const [cardNumber, setCardNumber] = useState("");
  const [redeemAmount, setRedeemAmount] = useState("");
  const [cardBalance, setCardBalance] = useState<number | null>(null);

  const createGiftCard = useCreateGiftCard();
  const getBalance = useGetGiftCardBalance();
  const redeemCard = useRedeemGiftCard();

  const handleCreateGiftCard = async () => {
    const amountNum = parseFloat(amount);
    if (isNaN(amountNum) || amountNum <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }

    if (cardType === "digital" && !recipientEmail) {
      toast.error("Email is required for digital gift cards");
      return;
    }

    try {
      const result = await createGiftCard.mutateAsync({
        amount: amountNum,
        card_type: cardType,
        recipient_name: recipientName || undefined,
        recipient_email: recipientEmail || undefined,
        message: message || undefined,
        expiration_months: parseInt(expirationMonths),
      });

      toast.success(`Gift card created! Card Number: ${result.card_number}`, {
        duration: 5000,
      });

      // Reset form
      setAmount("");
      setRecipientName("");
      setRecipientEmail("");
      setMessage("");
      setExpirationMonths("12");
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to create gift card");
    }
  };

  const handleCheckBalance = async () => {
    if (!cardNumber.trim()) {
      toast.error("Please enter a card number");
      return;
    }

    try {
      const result = await getBalance.mutateAsync(cardNumber.toUpperCase());
      setCardBalance(result.balance);
      toast.success(`Balance: ${formatCurrency(result.balance)}`);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to check balance");
      setCardBalance(null);
    }
  };

  const handleRedeemGiftCard = async () => {
    if (!cardNumber.trim()) {
      toast.error("Please enter a card number");
      return;
    }

    const redeemAmountNum = parseFloat(redeemAmount);
    if (isNaN(redeemAmountNum) || redeemAmountNum <= 0) {
      toast.error("Please enter a valid amount to redeem");
      return;
    }

    if (cardBalance !== null && redeemAmountNum > cardBalance) {
      toast.error("Redeem amount exceeds card balance");
      return;
    }

    try {
      const result = await redeemCard.mutateAsync({
        card_number: cardNumber.toUpperCase(),
        amount: redeemAmountNum,
        transaction_id: "pending", // Will be updated when transaction is created
      });

      toast.success(
        `Redeemed ${formatCurrency(result.redeemed_amount)}. Remaining: ${formatCurrency(result.remaining_balance)}`
      );

      if (onRedeemSuccess) {
        onRedeemSuccess(result.redeemed_amount, cardNumber.toUpperCase());
      }

      // Reset form
      setCardNumber("");
      setRedeemAmount("");
      setCardBalance(null);
      onClose();
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || "Failed to redeem gift card");
    }
  };

  const handleClose = () => {
    setAmount("");
    setCardType("physical");
    setRecipientName("");
    setRecipientEmail("");
    setMessage("");
    setExpirationMonths("12");
    setCardNumber("");
    setRedeemAmount("");
    setCardBalance(null);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-lg max-h-[85vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <GiftIcon className="h-5 w-5" />
            Gift Cards
          </DialogTitle>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto pr-2">
          <Tabs defaultValue="sell" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="sell">Sell Gift Card</TabsTrigger>
              <TabsTrigger value="redeem">Redeem Gift Card</TabsTrigger>
            </TabsList>

            <TabsContent value="sell" className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="amount">Amount *</Label>
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">₦</span>
                  <Input
                    id="amount"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="0.00"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Card Type</Label>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={cardType === "physical" ? "primary" : "outline"}
                    size="sm"
                    onClick={() => setCardType("physical")}
                    className="flex-1"
                  >
                    <CreditCardIcon className="h-4 w-4 mr-2" />
                    Physical
                  </Button>
                  <Button
                    type="button"
                    variant={cardType === "digital" ? "primary" : "outline"}
                    size="sm"
                    onClick={() => setCardType("digital")}
                    className="flex-1"
                  >
                    Digital
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="recipient-name">Recipient Name</Label>
                <Input
                  id="recipient-name"
                  placeholder="Optional"
                  value={recipientName}
                  onChange={(e) => setRecipientName(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="recipient-email">
                  Recipient Email {cardType === "digital" && "*"}
                </Label>
                <Input
                  id="recipient-email"
                  type="email"
                  placeholder={cardType === "digital" ? "Required" : "Optional"}
                  value={recipientEmail}
                  onChange={(e) => setRecipientEmail(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="message">Gift Message</Label>
                <Textarea
                  id="message"
                  placeholder="Optional message for the recipient"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  maxLength={200}
                  className="min-h-[60px] resize-none"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="expiration">Expiration (Months)</Label>
                <Input
                  id="expiration"
                  type="number"
                  min="1"
                  max="60"
                  value={expirationMonths}
                  onChange={(e) => setExpirationMonths(e.target.value)}
                />
              </div>

              <Button
                onClick={handleCreateGiftCard}
                disabled={createGiftCard.isPending}
                className="w-full"
              >
                {createGiftCard.isPending ? "Creating..." : "Create Gift Card"}
              </Button>
            </TabsContent>

            <TabsContent value="redeem" className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="card-number">Card Number *</Label>
                <Input
                  id="card-number"
                  placeholder="GC-XXXXXXXXXXXX"
                  value={cardNumber}
                  onChange={(e) => setCardNumber(e.target.value.toUpperCase())}
                  className="uppercase"
                />
              </div>

              <Button
                onClick={handleCheckBalance}
                disabled={getBalance.isPending}
                variant="outline"
                className="w-full"
              >
                {getBalance.isPending ? "Checking..." : "Check Balance"}
              </Button>

              {cardBalance !== null && (
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">
                    Available Balance
                  </p>
                  <p className="text-2xl font-bold">
                    {formatCurrency(cardBalance)}
                  </p>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="redeem-amount">Amount to Redeem *</Label>
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">₦</span>
                  <Input
                    id="redeem-amount"
                    type="number"
                    min="0"
                    max={cardBalance || undefined}
                    step="0.01"
                    placeholder="0.00"
                    value={redeemAmount}
                    onChange={(e) => setRedeemAmount(e.target.value)}
                  />
                </div>
                {cardBalance !== null && (
                  <p className="text-xs text-muted-foreground">
                    Max: {formatCurrency(cardBalance)}
                  </p>
                )}
              </div>

              <Button
                onClick={handleRedeemGiftCard}
                disabled={redeemCard.isPending}
                className="w-full"
              >
                {redeemCard.isPending ? "Redeeming..." : "Redeem Gift Card"}
              </Button>
            </TabsContent>
          </Tabs>
        </div>

        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={handleClose}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
