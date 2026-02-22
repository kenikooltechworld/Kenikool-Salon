export interface Notification {
  id: string;
  recipient_id: string;
  recipient_type: "customer" | "staff" | "owner";
  notification_type: string;
  channel: "email" | "sms" | "push" | "in_app";
  status: "pending" | "sent" | "delivered" | "failed" | "bounced";
  subject?: string;
  content: string;
  is_read: boolean;
  read_at?: string;
  created_at: string;
  sent_at?: string;
  delivered_at?: string;
}

export interface NotificationPreference {
  id: string;
  customer_id: string;
  notification_type: string;
  channel: "email" | "sms" | "push" | "in_app";
  enabled: boolean;
}
