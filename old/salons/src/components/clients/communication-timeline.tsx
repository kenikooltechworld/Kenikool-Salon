import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useGetClientCommunications,
  useGetClientCommunicationsStats,
  useSendClientCommunication,
} from "@/lib/api/hooks/useClients";
import {
  MailIcon,
  MessageSquareIcon,
  PhoneIcon,
  SendIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  EyeIcon,
  FilterIcon,
  PlusIcon,
} from "@/components/icons";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

interface CommunicationTimelineProps {
  clientId: string;
}

export function CommunicationTimeline({
  clientId,
}: CommunicationTimelineProps) {
  const [channelFilter, setChannelFilter] = useState<string | undefined>();
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [newMessage, setNewMessage] = useState({
    channel: "sms" as "sms" | "email" | "whatsapp",
    subject: "",
    content: "",
  });

  const { data: communications, isLoading } = useGetClientCommunications(
    clientId,
    50,
    0,
  );

  const { data: stats } = useGetClientCommunicationsStats(clientId);
  const sendCommunication = useSendClientCommunication(clientId);

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case "email":
        return <MailIcon className="h-4 w-4" />;
      case "whatsapp":
        return <MessageSquareIcon className="h-4 w-4" />;
      case "sms":
      default:
        return <PhoneIcon className="h-4 w-4" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "sent":
        return <SendIcon className="h-4 w-4 text-blue-500" />;
      case "delivered":
        return <CheckCircleIcon className="h-4 w-4 text-green-500" />;
      case "read":
        return <EyeIcon className="h-4 w-4 text-purple-500" />;
      case "failed":
        return <XCircleIcon className="h-4 w-4 text-red-500" />;
      case "pending":
      default:
        return <ClockIcon className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "sent":
        return "bg-blue-100 text-blue-800";
      case "delivered":
        return "bg-green-100 text-green-800";
      case "read":
        return "bg-purple-100 text-purple-800";
      case "failed":
        return "bg-red-100 text-red-800";
      case "pending":
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.content.trim()) {
      toast.error("Message content is required");
      return;
    }

    if (newMessage.channel === "email" && !newMessage.subject.trim()) {
      toast.error("Email subject is required");
      return;
    }

    try {
      await sendCommunication.mutateAsync(newMessage);
      toast.success("Message sent successfully");
      setIsComposeOpen(false);
      setNewMessage({ channel: "sms", subject: "", content: "" });
    } catch (error: any) {
      toast.error(error.response?.data?.error || "Failed to send message");
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Communication History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">
                Total Communications
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.total_communications}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">SMS</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.by_channel.sms || 0}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Email</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.by_channel.email || 0}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">
                Response Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.response_rate}%</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Timeline */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Communication History</CardTitle>
            <div className="flex items-center gap-2">
              {/* Filters */}
              <div className="w-32">
                <Select value={channelFilter} onValueChange={setChannelFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Channel" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Channels</SelectItem>
                    <SelectItem value="sms">SMS</SelectItem>
                    <SelectItem value="email">Email</SelectItem>
                    <SelectItem value="whatsapp">WhatsApp</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="w-32">
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="sent">Sent</SelectItem>
                    <SelectItem value="delivered">Delivered</SelectItem>
                    <SelectItem value="read">Read</SelectItem>
                    <SelectItem value="failed">Failed</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Compose Button */}
              <Dialog open={isComposeOpen} onOpenChange={setIsComposeOpen}>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <PlusIcon className="h-4 w-4 mr-2" />
                    Send Message
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Send Message</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">Channel</label>
                      <Select
                        value={newMessage.channel}
                        onValueChange={(value: any) =>
                          setNewMessage({ ...newMessage, channel: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="sms">SMS</SelectItem>
                          <SelectItem value="email">Email</SelectItem>
                          <SelectItem value="whatsapp">WhatsApp</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {newMessage.channel === "email" && (
                      <div>
                        <label className="text-sm font-medium">Subject</label>
                        <Input
                          value={newMessage.subject}
                          onChange={(e) =>
                            setNewMessage({
                              ...newMessage,
                              subject: e.target.value,
                            })
                          }
                          placeholder="Email subject"
                        />
                      </div>
                    )}

                    <div>
                      <label className="text-sm font-medium">Message</label>
                      <Textarea
                        value={newMessage.content}
                        onChange={(e) =>
                          setNewMessage({
                            ...newMessage,
                            content: e.target.value,
                          })
                        }
                        placeholder="Type your message..."
                        rows={5}
                      />
                    </div>

                    <div className="flex justify-end gap-2">
                      <Button
                        variant="outline"
                        onClick={() => setIsComposeOpen(false)}
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={handleSendMessage}
                        disabled={sendCommunication.isPending}
                      >
                        {sendCommunication.isPending ? "Sending..." : "Send"}
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {!communications ||
          !communications.items ||
          communications.items.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No communications yet
            </p>
          ) : (
            <div className="space-y-4">
              {communications.items.map((comm) => (
                <div
                  key={comm.id}
                  className="flex gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                      {getChannelIcon(comm.channel)}
                    </div>
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline" className="capitalize">
                        {comm.channel}
                      </Badge>
                      <Badge className={getStatusColor(comm.status)}>
                        <span className="flex items-center gap-1">
                          {getStatusIcon(comm.status)}
                          {comm.status}
                        </span>
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(comm.created_at).toLocaleString()}
                      </span>
                    </div>

                    {comm.subject && (
                      <p className="font-medium text-sm mb-1">{comm.subject}</p>
                    )}

                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {comm.content}
                    </p>

                    {comm.error_message && (
                      <p className="text-xs text-red-600 mt-1">
                        Error: {comm.error_message}
                      </p>
                    )}

                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span>To: {comm.recipient}</span>
                      {comm.sent_at && (
                        <span>
                          Sent: {new Date(comm.sent_at).toLocaleString()}
                        </span>
                      )}
                      {comm.delivered_at && (
                        <span>
                          Delivered:{" "}
                          {new Date(comm.delivered_at).toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {communications.has_more && (
                <div className="text-center">
                  <Button variant="outline" size="sm">
                    Load More
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
