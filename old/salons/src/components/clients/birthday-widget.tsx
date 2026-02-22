import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Cake, Send, Calendar } from "@/components/icons";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { toast } from "sonner";
import { useState } from "react";

interface Birthday {
  client_id: string;
  name: string;
  phone: string;
  email?: string;
  birthday: string;
  next_birthday: string;
  days_until: number;
  age: number;
}

export function BirthdayWidget() {
  const queryClient = useQueryClient();
  const [sendingTo, setSendingTo] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["birthdays", "upcoming"],
    queryFn: async () => {
      const response = await apiClient.get(
        "/api/clients/birthdays/upcoming?days_ahead=7"
      );
      return response.data;
    },
    refetchInterval: 60000, // Refetch every minute
  });

  const sendGreeting = useMutation({
    mutationFn: async ({
      clientId,
      channel,
    }: {
      clientId: string;
      channel: string;
    }) => {
      const response = await apiClient.post(
        `/api/clients/${clientId}/send-birthday-greeting?channel=${channel}`
      );
      return response.data;
    },
    onSuccess: (_, variables) => {
      toast.success("Birthday greeting sent!");
      queryClient.invalidateQueries({ queryKey: ["birthdays"] });
      setSendingTo(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to send greeting");
      setSendingTo(null);
    },
  });

  const handleSendGreeting = (clientId: string) => {
    setSendingTo(clientId);
    sendGreeting.mutate({ clientId, channel: "sms" });
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cake className="h-5 w-5" />
            Birthdays This Week
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground">Loading...</div>
        </CardContent>
      </Card>
    );
  }

  const birthdays: Birthday[] = data?.birthdays || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Cake className="h-5 w-5" />
          Birthdays This Week
        </CardTitle>
      </CardHeader>
      <CardContent>
        {birthdays.length === 0 ? (
          <div className="text-sm text-muted-foreground">
            No birthdays this week
          </div>
        ) : (
          <div className="space-y-3">
            {birthdays.map((birthday) => (
              <div
                key={birthday.client_id}
                className="flex items-center justify-between p-3 rounded-lg border bg-card"
              >
                <div className="flex-1">
                  <div className="font-medium">{birthday.name}</div>
                  <div className="text-sm text-muted-foreground flex items-center gap-2">
                    <Calendar className="h-3 w-3" />
                    {birthday.days_until === 0 ? (
                      <span className="text-primary font-medium">Today!</span>
                    ) : (
                      <span>
                        In {birthday.days_until} day
                        {birthday.days_until !== 1 ? "s" : ""}
                      </span>
                    )}
                    <Badge variant="outline" className="ml-2">
                      {birthday.age} years
                    </Badge>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleSendGreeting(birthday.client_id)}
                  disabled={sendingTo === birthday.client_id}
                >
                  <Send className="h-4 w-4 mr-1" />
                  {sendingTo === birthday.client_id
                    ? "Sending..."
                    : "Send Greeting"}
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
