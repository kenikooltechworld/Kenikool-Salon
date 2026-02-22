import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { DollarIcon, CalculatorIcon } from "@/components/icons";
import { useToast } from "@/hooks/use-toast";

export function PriceCalculator() {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [serviceId, setServiceId] = useState("");
  const [bookingDate, setBookingDate] = useState("");
  const [bookingTime, setBookingTime] = useState("");
  const [result, setResult] = useState<any>(null);

  const handleCalculate = async () => {
    if (!serviceId || !bookingDate || !bookingTime) {
      showToast({
        title: "Validation Error",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/pricing/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          service_id: serviceId,
          booking_date: bookingDate,
          booking_time: bookingTime,
        }),
      });

      if (!response.ok) throw new Error("Failed to calculate price");

      const data = await response.json();
      setResult(data);
    } catch (error: any) {
      showToast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-3">
          <CalculatorIcon size={24} className="text-primary" />
          <CardTitle>Price Calculator</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="service-id">Service ID</Label>
          <Input
            id="service-id"
            value={serviceId}
            onChange={(e) => setServiceId(e.target.value)}
            placeholder="Enter service ID"
          />
        </div>

        <div>
          <Label htmlFor="booking-date">Booking Date</Label>
          <Input
            id="booking-date"
            type="date"
            value={bookingDate}
            onChange={(e) => setBookingDate(e.target.value)}
          />
        </div>

        <div>
          <Label htmlFor="booking-time">Booking Time</Label>
          <Input
            id="booking-time"
            type="time"
            value={bookingTime}
            onChange={(e) => setBookingTime(e.target.value)}
          />
        </div>

        <Button onClick={handleCalculate} disabled={loading} className="w-full">
          {loading ? <Spinner /> : "Calculate Price"}
        </Button>

        {result && (
          <div className="space-y-3 pt-4 border-t">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Base Price:</span>
              <span className="font-semibold">
                ₦{result.base_price.toLocaleString()}
              </span>
            </div>

            {result.applied_rules.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium">Applied Rules:</p>
                {result.applied_rules.map((rule: any, index: number) => (
                  <div
                    key={index}
                    className="flex items-center justify-between text-sm p-2 bg-muted/50 rounded"
                  >
                    <span>{rule.name}</span>
                    <Badge variant="secondary">
                      {((rule.multiplier - 1) * 100).toFixed(0)}%
                    </Badge>
                  </div>
                ))}
              </div>
            )}

            <div className="flex items-center justify-between pt-2 border-t">
              <span className="text-sm text-muted-foreground">
                Total Multiplier:
              </span>
              <span className="font-semibold">{result.total_multiplier}x</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-primary/10 rounded-lg">
              <div className="flex items-center gap-2">
                <DollarIcon size={20} className="text-primary" />
                <span className="font-semibold">Final Price:</span>
              </div>
              <span className="text-xl font-bold text-primary">
                ₦{result.final_price.toLocaleString()}
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
