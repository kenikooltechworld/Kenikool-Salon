"use client";

import { useState, useEffect } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function AttendanceClock() {
  const [currentTime, setCurrentTime] = useState<string>("");

  // Update current time
  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Get current attendance status
  const { data: statusData, refetch } = useQuery({
    queryKey: ["attendance-status"],
    queryFn: async () => {
      const res = await fetch("/api/staff/attendance");
      if (!res.ok) throw new Error("Failed to fetch status");
      return res.json();
    },
  });

  const records = statusData?.data || [];
  const todayRecord = records.find((r: any) => {
    const recordDate = new Date(r.date).toDateString();
    const today = new Date().toDateString();
    return recordDate === today && !r.clock_out;
  });

  // Clock in mutation
  const clockInMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch("/api/staff/attendance/clock-in", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) throw new Error("Failed to clock in");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Clocked in successfully");
      refetch();
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to clock in");
    },
  });

  // Clock out mutation
  const clockOutMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch("/api/staff/attendance/clock-out", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) throw new Error("Failed to clock out");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Clocked out successfully");
      refetch();
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to clock out");
    },
  });

  // Break start mutation
  const breakStartMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch("/api/staff/attendance/break-start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) throw new Error("Failed to start break");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Break started");
      refetch();
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to start break");
    },
  });

  // Break end mutation
  const breakEndMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch("/api/staff/attendance/break-end", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) throw new Error("Failed to end break");
      return res.json();
    },
    onSuccess: () => {
      toast.success("Break ended");
      refetch();
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to end break");
    },
  });

  const isClockedIn = !!todayRecord;
  const isOnBreak = todayRecord?.breaks?.some((b: any) => !b.end);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Time Clock</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Current Time */}
        <div className="text-center">
          <div className="text-5xl font-bold font-mono">{currentTime}</div>
          <p className="text-sm text-muted-foreground mt-2">
            {new Date().toLocaleDateString("en-US", {
              weekday: "long",
              month: "long",
              day: "numeric",
            })}
          </p>
        </div>

        {/* Status */}
        <div className="flex justify-center gap-2">
          {isClockedIn && (
            <Badge className="bg-green-100 text-green-800">Clocked In</Badge>
          )}
          {isOnBreak && (
            <Badge className="bg-blue-100 text-blue-800">On Break</Badge>
          )}
          {!isClockedIn && (
            <Badge className="bg-gray-100 text-gray-800">Clocked Out</Badge>
          )}
        </div>

        {/* Clock In/Out Buttons */}
        <div className="flex gap-3">
          <Button
            onClick={() => clockInMutation.mutate()}
            disabled={isClockedIn || clockInMutation.isPending}
            className="flex-1"
            size="lg"
          >
            {clockInMutation.isPending ? "Clocking In..." : "Clock In"}
          </Button>
          <Button
            onClick={() => clockOutMutation.mutate()}
            disabled={!isClockedIn || clockOutMutation.isPending}
            variant="outline"
            className="flex-1"
            size="lg"
          >
            {clockOutMutation.isPending ? "Clocking Out..." : "Clock Out"}
          </Button>
        </div>

        {/* Break Buttons */}
        {isClockedIn && (
          <div className="flex gap-3">
            <Button
              onClick={() => breakStartMutation.mutate()}
              disabled={isOnBreak || breakStartMutation.isPending}
              variant="secondary"
              className="flex-1"
            >
              {breakStartMutation.isPending ? "Starting..." : "Start Break"}
            </Button>
            <Button
              onClick={() => breakEndMutation.mutate()}
              disabled={!isOnBreak || breakEndMutation.isPending}
              variant="secondary"
              className="flex-1"
            >
              {breakEndMutation.isPending ? "Ending..." : "End Break"}
            </Button>
          </div>
        )}

        {/* Today's Summary */}
        {todayRecord && (
          <div className="bg-muted p-4 rounded space-y-2">
            <h4 className="font-medium">Today's Summary</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Clock In</p>
                <p className="font-semibold">
                  {new Date(todayRecord.clock_in).toLocaleTimeString()}
                </p>
              </div>
              {todayRecord.clock_out && (
                <div>
                  <p className="text-muted-foreground">Clock Out</p>
                  <p className="font-semibold">
                    {new Date(todayRecord.clock_out).toLocaleTimeString()}
                  </p>
                </div>
              )}
              <div>
                <p className="text-muted-foreground">Total Hours</p>
                <p className="font-semibold">
                  {todayRecord.total_hours?.toFixed(2) || "0.00"}h
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Break Time</p>
                <p className="font-semibold">
                  {todayRecord.total_break_minutes || 0}m
                </p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
