import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePurchaseGiftCard } from "@/hooks/useGiftCards";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  CalendarIcon,
  GiftIcon as Gift,
  MailIcon as Mail,
  PhoneIcon as Phone,
} from "@/components/icons";
import { cn } from "@/lib/utils";

const PRESET_AMOUNTS = [5000, 10000, 20000, 50000, 100000];

export default function GiftCardPurchase() {
  const navigate = useNavigate();
  const purchaseGiftCard = usePurchaseGiftCard();

  const [amount, setAmount] = useState<number>(10000);
  const [customAmount, setCustomAmount] = useState<string>("");
  const [purchaserName, setPurchaserName] = useState("");
  const [purchaserEmail, setPurchaserEmail] = useState("");
  const [purchaserPhone, setPurchaserPhone] = useState("");
  const [recipientName, setRecipientName] = useState("");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [recipientPhone, setRecipientPhone] = useState("");
  const [deliveryMethod, setDeliveryMethod] = useState<
    "email" | "sms" | "both"
  >("email");
  const [deliveryDate, setDeliveryDate] = useState<Date>();
  const [personalMessage, setPersonalMessage] = useState("");
  const [expiryMonths, setExpiryMonths] = useState(12);
  const [paymentMethod, setPaymentMethod] = useState<
    "paystack" | "cash" | "bank_transfer"
  >("paystack");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const finalAmount = customAmount ? parseFloat(customAmount) : amount;

    if (finalAmount < 1000) {
      alert("Minimum gift card amount is ₦1,000");
      return;
    }

    try {
      const result = await purchaseGiftCard.mutateAsync({
        amount: finalAmount,
        purchased_by_name: purchaserName,
        purchased_by_email: purchaserEmail,
        purchased_by_phone: purchaserPhone,
        recipient_name: recipientName || undefined,
        recipient_email: recipientEmail || undefined,
        recipient_phone: recipientPhone || undefined,
        delivery_method: deliveryMethod,
        delivery_date: deliveryDate?.toISOString(),
        personal_message: personalMessage || undefined,
        expiry_months: expiryMonths,
        payment_method: paymentMethod,
      });

      if (result.payment_url) {
        // Redirect to payment page
        window.location.href = result.payment_url;
      } else {
        // Show success message
        alert(result.message);
        navigate("/public/gift-cards/success", {
          state: { giftCard: result.gift_card },
        });
      }
    } catch (error: any) {
      alert(error.response?.data?.detail || "Failed to purchase gift card");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <Gift className="mx-auto h-12 w-12 text-blue-600" />
          <h1 className="mt-4 text-3xl font-bold text-gray-900">
            Purchase a Gift Card
          </h1>
          <p className="mt-2 text-gray-600">
            Give the gift of beauty and wellness
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Amount Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Select Amount</CardTitle>
              <CardDescription>
                Choose a preset amount or enter a custom value
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                {PRESET_AMOUNTS.map((presetAmount) => (
                  <Button
                    key={presetAmount}
                    type="button"
                    variant={
                      amount === presetAmount && !customAmount
                        ? "primary"
                        : "outline"
                    }
                    onClick={() => {
                      setAmount(presetAmount);
                      setCustomAmount("");
                    }}
                  >
                    ₦{presetAmount.toLocaleString()}
                  </Button>
                ))}
              </div>
              <div>
                <Label htmlFor="customAmount">Custom Amount</Label>
                <Input
                  id="customAmount"
                  type="number"
                  placeholder="Enter custom amount"
                  value={customAmount}
                  onChange={(e) => setCustomAmount(e.target.value)}
                  min="1000"
                />
              </div>
            </CardContent>
          </Card>

          {/* Purchaser Information */}
          <Card>
            <CardHeader>
              <CardTitle>Your Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="purchaserName">Full Name *</Label>
                <Input
                  id="purchaserName"
                  required
                  value={purchaserName}
                  onChange={(e) => setPurchaserName(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="purchaserEmail">Email *</Label>
                <Input
                  id="purchaserEmail"
                  type="email"
                  required
                  value={purchaserEmail}
                  onChange={(e) => setPurchaserEmail(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="purchaserPhone">Phone *</Label>
                <Input
                  id="purchaserPhone"
                  type="tel"
                  required
                  value={purchaserPhone}
                  onChange={(e) => setPurchaserPhone(e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Recipient Information */}
          <Card>
            <CardHeader>
              <CardTitle>Recipient Information (Optional)</CardTitle>
              <CardDescription>
                Leave blank if purchasing for yourself
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="recipientName">Recipient Name</Label>
                <Input
                  id="recipientName"
                  value={recipientName}
                  onChange={(e) => setRecipientName(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="recipientEmail">Recipient Email</Label>
                <Input
                  id="recipientEmail"
                  type="email"
                  value={recipientEmail}
                  onChange={(e) => setRecipientEmail(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="recipientPhone">Recipient Phone</Label>
                <Input
                  id="recipientPhone"
                  type="tel"
                  value={recipientPhone}
                  onChange={(e) => setRecipientPhone(e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Delivery Options */}
          <Card>
            <CardHeader>
              <CardTitle>Delivery Options</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Delivery Method *</Label>
                <RadioGroup
                  value={deliveryMethod}
                  onValueChange={(v: any) => setDeliveryMethod(v)}
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="email" id="email" />
                    <Label
                      htmlFor="email"
                      className="flex items-center gap-2 cursor-pointer"
                    >
                      <Mail className="h-4 w-4" />
                      Email
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="sms" id="sms" />
                    <Label
                      htmlFor="sms"
                      className="flex items-center gap-2 cursor-pointer"
                    >
                      <Phone className="h-4 w-4" />
                      SMS
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="both" id="both" />
                    <Label
                      htmlFor="both"
                      className="flex items-center gap-2 cursor-pointer"
                    >
                      <Mail className="h-4 w-4" />
                      <Phone className="h-4 w-4" />
                      Both
                    </Label>
                  </div>
                </RadioGroup>
              </div>

              <div>
                <Label>Delivery Date (Optional)</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal",
                        !deliveryDate && "text-muted-foreground",
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {deliveryDate
                        ? deliveryDate.toLocaleDateString()
                        : "Send immediately"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={deliveryDate}
                      onSelect={(date) => {
                        if (date instanceof Date) {
                          setDeliveryDate(date);
                        } else {
                          setDeliveryDate(undefined);
                        }
                      }}
                      disabled={(date) => date < new Date()}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>

              <div>
                <Label htmlFor="personalMessage">
                  Personal Message (Optional)
                </Label>
                <Textarea
                  id="personalMessage"
                  placeholder="Add a personal message..."
                  value={personalMessage}
                  onChange={(e) => setPersonalMessage(e.target.value)}
                  maxLength={500}
                  rows={4}
                />
                <p className="text-sm text-gray-500 mt-1">
                  {personalMessage.length}/500 characters
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Validity & Payment */}
          <Card>
            <CardHeader>
              <CardTitle>Validity & Payment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="expiryMonths">Valid For (Months)</Label>
                <Input
                  id="expiryMonths"
                  type="number"
                  min="1"
                  max="60"
                  value={expiryMonths}
                  onChange={(e) => setExpiryMonths(parseInt(e.target.value))}
                />
              </div>

              <div>
                <Label>Payment Method *</Label>
                <RadioGroup
                  value={paymentMethod}
                  onValueChange={(v: any) => setPaymentMethod(v)}
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="paystack" id="paystack" />
                    <Label htmlFor="paystack" className="cursor-pointer">
                      Online Payment (Paystack)
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="cash" id="cash" />
                    <Label htmlFor="cash" className="cursor-pointer">
                      Cash
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="bank_transfer" id="bank_transfer" />
                    <Label htmlFor="bank_transfer" className="cursor-pointer">
                      Bank Transfer
                    </Label>
                  </div>
                </RadioGroup>
              </div>
            </CardContent>
          </Card>

          {/* Summary */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-6">
              <div className="flex justify-between items-center text-lg font-semibold">
                <span>Total Amount:</span>
                <span className="text-2xl text-blue-600">
                  ₦
                  {(customAmount
                    ? parseFloat(customAmount)
                    : amount
                  ).toLocaleString()}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Submit Button */}
          <Button
            type="submit"
            className="w-full"
            size="lg"
            disabled={purchaseGiftCard.isPending}
          >
            {purchaseGiftCard.isPending
              ? "Processing..."
              : "Purchase Gift Card"}
          </Button>
        </form>
      </div>
    </div>
  );
}
