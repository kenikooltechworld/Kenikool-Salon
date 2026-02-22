import { useState, useEffect } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/hooks/use-toast";

interface PricingRuleFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  rule?: any;
}

const RULE_TYPES = [
  { value: "time_of_day", label: "Time of Day" },
  { value: "day_of_week", label: "Day of Week" },
  { value: "demand", label: "Demand-Based" },
  { value: "seasonal", label: "Seasonal" },
];

const DAYS_OF_WEEK = [
  { value: 0, label: "Monday" },
  { value: 1, label: "Tuesday" },
  { value: 2, label: "Wednesday" },
  { value: 3, label: "Thursday" },
  { value: 4, label: "Friday" },
  { value: 5, label: "Saturday" },
  { value: 6, label: "Sunday" },
];

export function PricingRuleFormModal({
  isOpen,
  onClose,
  onSuccess,
  rule,
}: PricingRuleFormModalProps) {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState("");
  const [ruleType, setRuleType] = useState("time_of_day");
  const [multiplier, setMultiplier] = useState("1.5");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [daysOfWeek, setDaysOfWeek] = useState<number[]>([]);
  const [minBookings, setMinBookings] = useState("");
  const [maxBookings, setMaxBookings] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [priority, setPriority] = useState("0");

  useEffect(() => {
    if (rule) {
      setName(rule.name);
      setRuleType(rule.rule_type);
      setMultiplier(rule.multiplier.toString());
      setStartTime(rule.start_time || "");
      setEndTime(rule.end_time || "");
      setDaysOfWeek(rule.days_of_week || []);
      setMinBookings(rule.min_bookings?.toString() || "");
      setMaxBookings(rule.max_bookings?.toString() || "");
      setStartDate(rule.start_date || "");
      setEndDate(rule.end_date || "");
      setPriority(rule.priority?.toString() || "0");
    } else {
      // Reset form
      setName("");
      setRuleType("time_of_day");
      setMultiplier("1.5");
      setStartTime("");
      setEndTime("");
      setDaysOfWeek([]);
      setMinBookings("");
      setMaxBookings("");
      setStartDate("");
      setEndDate("");
      setPriority("0");
    }
  }, [rule, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload: any = {
        name,
        rule_type: ruleType,
        multiplier: parseFloat(multiplier),
        service_ids: [],
        days_of_week: daysOfWeek,
        enabled: true,
        priority: parseInt(priority),
      };

      if (ruleType === "time_of_day") {
        payload.start_time = startTime;
        payload.end_time = endTime;
      } else if (ruleType === "day_of_week") {
        payload.days_of_week = daysOfWeek;
      } else if (ruleType === "demand") {
        if (minBookings) payload.min_bookings = parseInt(minBookings);
        if (maxBookings) payload.max_bookings = parseInt(maxBookings);
      } else if (ruleType === "seasonal") {
        payload.start_date = startDate;
        payload.end_date = endDate;
      }

      const url = rule ? `/api/pricing/${rule.id}` : "/api/pricing";
      const method = rule ? "PATCH" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error("Failed to save pricing rule");

      onSuccess();
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

  const toggleDay = (day: number) => {
    setDaysOfWeek((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day],
    );
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        <h2 className="text-xl font-bold text-foreground">
          {rule ? "Edit Pricing Rule" : "Create Pricing Rule"}
        </h2>

        <div className="space-y-4">
          {/* Name */}
          <div>
            <Label htmlFor="name">Rule Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Peak Hours Premium"
              required
            />
          </div>

          {/* Rule Type */}
          <div>
            <Label htmlFor="rule-type">Rule Type</Label>
            <Select value={ruleType} onValueChange={setRuleType}>
              <SelectTrigger id="rule-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {RULE_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Multiplier */}
          <div>
            <Label htmlFor="multiplier">Price Multiplier</Label>
            <Input
              id="multiplier"
              type="number"
              step="0.1"
              min="0.1"
              max="5"
              value={multiplier}
              onChange={(e) => setMultiplier(e.target.value)}
              required
            />
            <p className="text-xs text-muted-foreground mt-1">
              1.5 = 150% (50% increase), 0.8 = 80% (20% discount)
            </p>
          </div>

          {/* Time of Day Fields */}
          {ruleType === "time_of_day" && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="start-time">Start Time</Label>
                <Input
                  id="start-time"
                  type="time"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  required
                />
              </div>
              <div>
                <Label htmlFor="end-time">End Time</Label>
                <Input
                  id="end-time"
                  type="time"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  required
                />
              </div>
            </div>
          )}

          {/* Day of Week Fields */}
          {ruleType === "day_of_week" && (
            <div>
              <Label>Days of Week</Label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {DAYS_OF_WEEK.map((day) => (
                  <div key={day.value} className="flex items-center gap-2">
                    <Checkbox
                      id={`day-${day.value}`}
                      checked={daysOfWeek.includes(day.value)}
                      onCheckedChange={() => toggleDay(day.value)}
                    />
                    <Label
                      htmlFor={`day-${day.value}`}
                      className="cursor-pointer"
                    >
                      {day.label}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Demand Fields */}
          {ruleType === "demand" && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="min-bookings">Min Bookings</Label>
                <Input
                  id="min-bookings"
                  type="number"
                  min="0"
                  value={minBookings}
                  onChange={(e) => setMinBookings(e.target.value)}
                  placeholder="Optional"
                />
              </div>
              <div>
                <Label htmlFor="max-bookings">Max Bookings</Label>
                <Input
                  id="max-bookings"
                  type="number"
                  min="0"
                  value={maxBookings}
                  onChange={(e) => setMaxBookings(e.target.value)}
                  placeholder="Optional"
                />
              </div>
            </div>
          )}

          {/* Seasonal Fields */}
          {ruleType === "seasonal" && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="start-date">Start Date</Label>
                <Input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  required
                />
              </div>
              <div>
                <Label htmlFor="end-date">End Date</Label>
                <Input
                  id="end-date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  required
                />
              </div>
            </div>
          )}

          {/* Priority */}
          <div>
            <Label htmlFor="priority">Priority</Label>
            <Input
              id="priority"
              type="number"
              min="0"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Higher rules are applied first
            </p>
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? "Saving..." : rule ? "Update Rule" : "Create Rule"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
