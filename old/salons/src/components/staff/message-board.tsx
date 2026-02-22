import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bell, Send, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Announcement {
  _id: string;
  title: string;
  content: string;
  sender_id: string;
  sender_name?: string;
  target_roles?: string[];
  created_at: string;
}

interface MessageBoardProps {
  isOpen: boolean;
  onClose: () => void;
  userRole: string;
  onSendAnnouncement?: (
    title: string,
    content: string,
    targetRoles?: string[],
  ) => Promise<void>;
}

export const MessageBoard: React.FC<MessageBoardProps> = ({
  isOpen,
  onClose,
  userRole,
  onSendAnnouncement,
}) => {
  const { showToast } = useToast();
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [isComposing, setIsComposing] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [targetRoles, setTargetRoles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchAnnouncements();
    }
  }, [isOpen]);

  const fetchAnnouncements = async () => {
    try {
      const response = await fetch("/api/staff/messages/announcements");
      const data = await response.json();
      setAnnouncements(data.announcements || []);
    } catch (error) {
      console.error("Failed to fetch announcements:", error);
    }
  };

  const handleSendAnnouncement = async () => {
    if (!title.trim() || !content.trim()) {
      showToast({
        title: "Validation Error",
        description: "Please fill in title and content",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      if (onSendAnnouncement) {
        await onSendAnnouncement(
          title,
          content,
          targetRoles.length > 0 ? targetRoles : undefined,
        );
      }
      setTitle("");
      setContent("");
      setTargetRoles([]);
      setIsComposing(false);
      await fetchAnnouncements();
    } catch (error) {
      console.error("Failed to send announcement:", error);
      showToast({
        title: "Error",
        description: "Failed to send announcement",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const canSendAnnouncements = ["owner", "manager"].includes(userRole);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[80vh] flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Message Board
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>

        <CardContent className="flex-1 flex flex-col gap-4 overflow-hidden">
          {canSendAnnouncements && !isComposing && (
            <Button onClick={() => setIsComposing(true)} className="w-full">
              <Send className="w-4 h-4 mr-2" />
              Send Announcement
            </Button>
          )}

          {isComposing && (
            <div className="border rounded-lg p-4 space-y-3 bg-slate-50">
              <Input
                placeholder="Announcement title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
              <Textarea
                placeholder="Announcement content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={4}
              />
              <div className="flex gap-2">
                <Button
                  onClick={handleSendAnnouncement}
                  disabled={loading}
                  className="flex-1"
                >
                  Send
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsComposing(false);
                    setTitle("");
                    setContent("");
                  }}
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}

          <ScrollArea className="flex-1">
            <div className="space-y-3 pr-4">
              {announcements.length === 0 ? (
                <p className="text-center text-slate-500 py-8">
                  No announcements yet
                </p>
              ) : (
                announcements.map((announcement) => (
                  <div
                    key={announcement._id}
                    className="border rounded-lg p-3 hover:bg-slate-50 transition"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <h3 className="font-semibold text-sm">
                          {announcement.title}
                        </h3>
                        <p className="text-xs text-slate-500 mt-1">
                          {announcement.sender_name || "Management"}
                        </p>
                      </div>
                      {announcement.target_roles && (
                        <div className="flex gap-1">
                          {announcement.target_roles.map((role) => (
                            <Badge
                              key={role}
                              variant="secondary"
                              className="text-xs"
                            >
                              {role}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                    <p className="text-sm mt-2 text-slate-700">
                      {announcement.content}
                    </p>
                    <p className="text-xs text-slate-400 mt-2">
                      {new Date(announcement.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};
