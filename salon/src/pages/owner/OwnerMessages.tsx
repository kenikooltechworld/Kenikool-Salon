import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectItem } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";
import { useSendMessage } from "@/hooks/useMessages";
import { useStaff } from "@/hooks/useStaff";
import { useRoles } from "@/hooks/useRoles";
import { Send, Users } from "@/components/icons";

type RecipientType = "all_staff" | "role" | "specific";

export default function OwnerMessages() {
  const { showToast } = useToast();
  const sendMessage = useSendMessage();
  const { data: staff = [], isLoading: staffLoading } = useStaff({ status: "active" });
  const { data: roles = [], isLoading: rolesLoading } = useRoles();

  const [recipientType, setRecipientType] = useState<RecipientType>("all_staff");
  const [selectedRoleId, setSelectedRoleId] = useState("");
  const [selectedStaffIds, setSelectedStaffIds] = useState<string[]>([]);
  const [subject, setSubject] = useState("");
  const [content, setContent] = useState("");
  const [messageType, setMessageType] = useState("team_announcement");
  const [sendEmail, setSendEmail] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!content.trim()) {
      showToast({
        title: "Error",
        description: "Please enter a message",
        variant: "error",
      });
      return;
    }

    try {
      const payload: any = {
        recipient_type: recipientType,
        notification_type: messageType,
        content: content.trim(),
        subject: subject.trim() || undefined,
        channel: "in_app",
        send_email: sendEmail,
      };

      if (recipientType === "role") {
        if (!selectedRoleId) {
          showToast({
            title: "Error",
            description: "Please select a role",
            variant: "error",
          });
          return;
        }
        payload.role_id = selectedRoleId;
      } else if (recipientType === "specific") {
        if (selectedStaffIds.length === 0) {
          showToast({
            title: "Error",
            description: "Please select at least one staff member",
            variant: "error",
          });
          return;
        }
        payload.recipient_ids = selectedStaffIds;
      }

      await sendMessage.mutateAsync(payload);

      showToast({
        title: "Success",
        description: "Message sent successfully",
        variant: "success",
      });

      setSubject("");
      setContent("");
      setSelectedRoleId("");
      setSelectedStaffIds([]);
      setRecipientType("all_staff");
    } catch (error: any) {
      showToast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to send message",
        variant: "error",
      });
    }
  };

  const toggleStaff = (staffId: string) => {
    setSelectedStaffIds((prev) =>
      prev.includes(staffId)
        ? prev.filter((id) => id !== staffId)
        : [...prev, staffId],
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Send Message</h1>
        <p className="text-muted-foreground mt-1">
          Send announcements and messages to your staff
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Recipient Selection */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 text-foreground">
            Recipients
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">
                Send To
              </label>
              <Select
                value={recipientType}
                onChange={(e) => setRecipientType(e.target.value as RecipientType)}
              >
                <SelectItem value="all_staff">All Staff</SelectItem>
                <SelectItem value="role">Staff by Role</SelectItem>
                <SelectItem value="specific">Specific Staff Members</SelectItem>
              </Select>
            </div>

            {recipientType === "role" && (
              <div>
                <label className="block text-sm font-medium mb-2 text-foreground">
                  Select Role
                </label>
                <Select
                  value={selectedRoleId}
                  onChange={(e) => setSelectedRoleId(e.target.value)}
                >
                  <SelectItem value="">Select a role</SelectItem>
                  {roles.map((role) => (
                    <SelectItem key={role.id} value={role.id}>
                      {role.name}
                    </SelectItem>
                  ))}
                </Select>
              </div>
            )}

            {recipientType === "specific" && (
              <div>
                <label className="block text-sm font-medium mb-2 text-foreground">
                  Select Staff Members
                </label>
                <div className="border border-border rounded-lg p-3 max-h-60 overflow-y-auto space-y-2">
                  {staffLoading ? (
                    <div className="space-y-2">
                      <Skeleton className="h-10 w-full rounded-lg" />
                      <Skeleton className="h-10 w-full rounded-lg" />
                      <Skeleton className="h-10 w-full rounded-lg" />
                    </div>
                  ) : staff.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No staff members found</p>
                  ) : (
                    staff.map((member) => (
                      <label
                        key={member.id}
                        className="flex items-center gap-2 p-2 rounded hover:bg-muted cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={selectedStaffIds.includes(member.id)}
                          onChange={() => toggleStaff(member.id)}
                          className="rounded border-border"
                        />
                        <span className="text-sm text-foreground">
                          {member.firstName} {member.lastName}
                        </span>
                        <Badge variant="secondary" className="ml-auto text-xs">
                          {member.email}
                        </Badge>
                      </label>
                    ))
                  )}
                </div>
                {selectedStaffIds.length > 0 && (
                  <p className="text-sm text-muted-foreground mt-2">
                    {selectedStaffIds.length} staff member(s) selected
                  </p>
                )}
              </div>
            )}
          </div>
        </Card>

        {/* Message Details */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 text-foreground">
            Message Details
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">
                Message Type
              </label>
              <Select
                value={messageType}
                onChange={(e) => setMessageType(e.target.value)}
              >
                <SelectItem value="team_announcement">Team Announcement</SelectItem>
                <SelectItem value="manager_message">Manager Message</SelectItem>
                <SelectItem value="custom">Custom Message</SelectItem>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">
                Subject
              </label>
              <Input
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Enter message subject"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">
                Message *
              </label>
              <Textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Enter your message..."
                rows={6}
                required
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="sendEmail"
                checked={sendEmail}
                onChange={(e) => setSendEmail(e.target.checked)}
                className="rounded border-border"
              />
              <label htmlFor="sendEmail" className="text-sm text-foreground">
                Also send via email
              </label>
            </div>
          </div>
        </Card>

        <div className="flex gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => window.history.back()}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={sendMessage.isPending}
            className="flex-1"
          >
            {sendMessage.isPending ? (
              "Sending..."
            ) : (
              <>
                <Send size={16} className="mr-2" />
                Send Message
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
