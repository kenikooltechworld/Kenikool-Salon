import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";

interface DisplayItem {
  name: string;
  quantity: number;
  price: number;
}

interface DisplayData {
  items: DisplayItem[];
  subtotal: number;
  discount: number;
  tax: number;
  tip: number;
  total: number;
  payment?: {
    amount: number;
    change: number;
  };
  status: "idle" | "checkout" | "payment" | "complete";
}

export default function CustomerDisplayPage() {
  const [displayData, setDisplayData] = useState<DisplayData>({
    items: [],
    subtotal: 0,
    discount: 0,
    tax: 0,
    tip: 0,
    total: 0,
    status: "idle",
  });

  useEffect(() => {
    // Listen for updates from main POS window via localStorage
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "pos_customer_display") {
        try {
          const data = JSON.parse(e.newValue || "{}");
          setDisplayData(data);
        } catch (error) {
          console.error("Failed to parse customer display data:", error);
        }
      }
    };

    // Initial load
    const savedData = localStorage.getItem("pos_customer_display");
    if (savedData) {
      try {
        setDisplayData(JSON.parse(savedData));
      } catch (error) {
        console.error("Failed to parse initial data:", error);
      }
    }

    window.addEventListener("storage", handleStorageChange);

    // Also poll for updates (for same-window testing)
    const interval = setInterval(() => {
      const data = localStorage.getItem("pos_customer_display");
      if (data) {
        try {
          setDisplayData(JSON.parse(data));
        } catch (error) {
          console.error("Failed to parse data:", error);
        }
      }
    }, 500);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      clearInterval(interval);
    };
  }, []);

  if (displayData.status === "idle") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-8xl mb-8">🛍️</div>
          <h1 className="text-6xl font-bold text-gray-800 mb-4">Welcome!</h1>
          <p className="text-3xl text-gray-600">Your items will appear here</p>
        </div>
      </div>
    );
  }

  if (displayData.status === "complete" && displayData.payment) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-9xl mb-8">✓</div>
          <h1 className="text-7xl font-bold text-green-800 mb-8">Thank You!</h1>
          <div className="space-y-6">
            <div>
              <p className="text-3xl text-gray-600 mb-2">Payment Received</p>
              <p className="text-6xl font-bold text-gray-800">
                ${displayData.payment.amount.toFixed(2)}
              </p>
            </div>
            {displayData.payment.change > 0 && (
              <div>
                <p className="text-3xl text-gray-600 mb-2">Your Change</p>
                <p className="text-6xl font-bold text-green-600">
                  ${displayData.payment.change.toFixed(2)}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <Card className="p-8 shadow-2xl">
          <div className="mb-8">
            <h1 className="text-5xl font-bold text-gray-800 mb-2">
              Your Purchase
            </h1>
            <Badge
              variant={
                displayData.status === "payment" ? "default" : "secondary"
              }
              className="text-xl px-4 py-2"
            >
              {displayData.status === "payment"
                ? "Processing Payment"
                : "Adding Items"}
            </Badge>
          </div>

          <div className="space-y-4 mb-8">
            {displayData.items.length === 0 ? (
              <p className="text-3xl text-gray-500 text-center py-12">
                No items yet
              </p>
            ) : (
              displayData.items.map((item, index) => (
                <div
                  key={index}
                  className="flex justify-between items-center py-4 border-b border-gray-200"
                >
                  <div className="flex-1">
                    <p className="text-3xl font-medium text-gray-800">
                      {item.name}
                    </p>
                    {item.quantity > 1 && (
                      <p className="text-2xl text-gray-500 mt-1">
                        Qty: {item.quantity}
                      </p>
                    )}
                  </div>
                  <p className="text-4xl font-bold text-gray-800">
                    ${(item.price * item.quantity).toFixed(2)}
                  </p>
                </div>
              ))
            )}
          </div>

          <Separator className="my-8" />

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-3xl text-gray-600">Subtotal</span>
              <span className="text-4xl font-medium text-gray-800">
                ${displayData.subtotal.toFixed(2)}
              </span>
            </div>

            {displayData.discount > 0 && (
              <div className="flex justify-between items-center">
                <span className="text-3xl text-green-600">Discount</span>
                <span className="text-4xl font-medium text-green-600">
                  -${displayData.discount.toFixed(2)}
                </span>
              </div>
            )}

            {displayData.tax > 0 && (
              <div className="flex justify-between items-center">
                <span className="text-3xl text-gray-600">Tax</span>
                <span className="text-4xl font-medium text-gray-800">
                  ${displayData.tax.toFixed(2)}
                </span>
              </div>
            )}

            {displayData.tip > 0 && (
              <div className="flex justify-between items-center">
                <span className="text-3xl text-gray-600">Tip</span>
                <span className="text-4xl font-medium text-gray-800">
                  ${displayData.tip.toFixed(2)}
                </span>
              </div>
            )}

            <Separator className="my-6" />

            <div className="flex justify-between items-center bg-blue-50 p-6 rounded-lg">
              <span className="text-5xl font-bold text-gray-800">Total</span>
              <span className="text-7xl font-bold text-blue-600">
                ${displayData.total.toFixed(2)}
              </span>
            </div>
          </div>

          {displayData.status === "payment" && displayData.payment && (
            <div className="mt-8 p-6 bg-green-50 rounded-lg">
              <div className="flex justify-between items-center">
                <span className="text-4xl font-medium text-gray-800">
                  Payment
                </span>
                <span className="text-5xl font-bold text-green-600">
                  ${displayData.payment.amount.toFixed(2)}
                </span>
              </div>
              {displayData.payment.change > 0 && (
                <div className="flex justify-between items-center mt-4">
                  <span className="text-4xl font-medium text-gray-800">
                    Change
                  </span>
                  <span className="text-5xl font-bold text-green-600">
                    ${displayData.payment.change.toFixed(2)}
                  </span>
                </div>
              )}
            </div>
          )}
        </Card>

        <div className="text-center mt-8">
          <p className="text-2xl text-gray-600">Thank you for your business!</p>
        </div>
      </div>
    </div>
  );
}
