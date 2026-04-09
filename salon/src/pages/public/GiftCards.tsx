import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  GiftIcon as Gift,
  CreditCardIcon as CreditCard,
  ShoppingBag,
} from "@/components/icons";
import GiftCardBalanceChecker from "@/components/public/GiftCardBalanceChecker";

export default function GiftCards() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <Gift className="mx-auto h-16 w-16 text-blue-600" />
          <h1 className="mt-4 text-4xl font-bold text-gray-900">Gift Cards</h1>
          <p className="mt-2 text-xl text-gray-600">
            The perfect gift for any occasion
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-12">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <ShoppingBag className="h-8 w-8 text-blue-600 mb-2" />
              <CardTitle>Purchase a Gift Card</CardTitle>
              <CardDescription>
                Give the gift of beauty and wellness. Choose any amount and
                personalize with a message.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 mb-6 text-sm text-gray-600">
                <li>✓ Choose any amount from ₦1,000</li>
                <li>✓ Add a personal message</li>
                <li>✓ Email or SMS delivery</li>
                <li>✓ Valid for 12 months</li>
                <li>✓ Can be used for any service</li>
              </ul>
              <Button
                className="w-full"
                size="lg"
                onClick={() => navigate("/public/gift-cards/purchase")}
              >
                Purchase Gift Card
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CreditCard className="h-8 w-8 text-green-600 mb-2" />
              <CardTitle>Check Balance</CardTitle>
              <CardDescription>
                Enter your gift card code to check your remaining balance.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <GiftCardBalanceChecker />
            </CardContent>
          </Card>
        </div>

        <Card className="bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle>How It Works</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold mb-3">
                  1
                </div>
                <h3 className="font-semibold mb-2">Choose Amount</h3>
                <p className="text-sm text-gray-600">
                  Select a preset amount or enter a custom value
                </p>
              </div>
              <div>
                <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold mb-3">
                  2
                </div>
                <h3 className="font-semibold mb-2">Personalize</h3>
                <p className="text-sm text-gray-600">
                  Add recipient details and a personal message
                </p>
              </div>
              <div>
                <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold mb-3">
                  3
                </div>
                <h3 className="font-semibold mb-2">Send & Redeem</h3>
                <p className="text-sm text-gray-600">
                  Gift card is delivered instantly and ready to use
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
