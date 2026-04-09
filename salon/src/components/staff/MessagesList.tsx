import { useState } from "react";
import {
  useMessages,
  useMarkMessageRead,
  useMarkMessageUnread,
  useDeleteMessage,
} from "@/hooks/useMessages";
import type { Notification } from "@/types/notification";
import { formatDistanceToNow } from "@/lib/utils/date";
import {
  Trash2Icon,
  MailIcon,
  MailOpenIcon,
  MegaphoneIcon,
  MessageSquareIcon,
} from "@/components/icons";
import { cn } from "@/lib/utils/cn";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

interface MessagesListProps {
  limit?: number;
  onMessageClick?: (message: Notification) => void;
  showSearch?: boolean;
}

export default function MessagesList({
  limit = 50,
  onMessageClick,
  showSearch = true,
}: MessagesListProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "read" | "unread">(
    "all",
  );

  const {
    data: messages = [],
    isLoading,
    error,
  } = useMessages({
    limit,
    status: statusFilter === "all" ? undefined : statusFilter,
    search: searchQuery,
  });

  const markAsRead = useMarkMessageRead();
  const markAsUnread = useMarkMessageUnread();
  const deleteMessage = useDeleteMessage();

  const handleMarkAsRead = (message: Notification) => {
    if (!message.is_read) {
      markAsRead.mutate(message.id);
    }
  };

  const handleMarkAsUnread = (message: Notification) => {
    if (message.is_read) {
      markAsUnread.mutate(message.id);
    }
  };

  const handleDelete = (messageId: string) => {
    if (window.confirm("Are you sure you want to delete this message?")) {
      deleteMessage.mutate(messageId);
    }
  };

  const getMessageIcon = (notificationType: string) => {
    if (notificationType === "team_announcement") {
      return <MegaphoneIcon className="w-5 h-5" />;
    }
    return <MessageSquareIcon className="w-5 h-5" />;
  };

  const getMessageTypeLabel = (notificationType: string) => {
    if (notificationType === "team_announcement") {
      return "Team Announcement";
    }
    if (notificationType === "manager_message") {
      return "Manager Message";
    }
    return "Message";
  };

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-24 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    let errorMessage = "Unable to load messages. Please try again.";

    if (error && typeof error === "object" && "response" in error) {
      const err = error as any;
      if (err?.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (detail.includes("not authorized")) {
          errorMessage = "You are not authorized to view messages";
        } else if (detail.includes("not found")) {
          errorMessage = "Messages not found";
        } else {
          errorMessage = detail;
        }
      }
    }

    return (
      <Alert variant="error">
        <AlertDescription className="flex items-center justify-between">
          <span>{errorMessage}</span>
          <Button
            onClick={() => window.location.reload()}
            variant="outline"
            size="sm"
            className="ml-4"
          >
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Filter */}
      {showSearch && (
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search messages..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground placeholder-muted-foreground focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setStatusFilter("all")}
              className={cn(
                "px-4 py-2 rounded-lg font-medium transition-colors",
                statusFilter === "all"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80",
              )}
            >
              All
            </button>
            <button
              onClick={() => setStatusFilter("unread")}
              className={cn(
                "px-4 py-2 rounded-lg font-medium transition-colors",
                statusFilter === "unread"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80",
              )}
            >
              Unread
            </button>
            <button
              onClick={() => setStatusFilter("read")}
              className={cn(
                "px-4 py-2 rounded-lg font-medium transition-colors",
                statusFilter === "read"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80",
              )}
            >
              Read
            </button>
          </div>
        </div>
      )}

      {/* Messages List */}
      {messages.length === 0 ? (
        <div className="p-8 text-center text-muted-foreground">
          <MessageSquareIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p className="text-lg font-medium">No messages yet</p>
          <p className="text-sm mt-1">
            {statusFilter === "unread"
              ? "You have no unread messages"
              : statusFilter === "read"
                ? "You have no read messages"
                : "Messages from your manager will appear here"}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "p-4 rounded-lg border transition-all cursor-pointer hover:shadow-md",
                message.is_read
                  ? "bg-card border-border"
                  : "bg-primary/5 border-primary/20 shadow-sm",
              )}
              onClick={() => {
                handleMarkAsRead(message);
                onMessageClick?.(message);
              }}
            >
              <div className="flex items-start gap-3">
                {/* Icon */}
                <div
                  className={cn(
                    "shrink-0 p-2 rounded-lg",
                    message.is_read
                      ? "bg-muted text-muted-foreground"
                      : "bg-primary/10 text-primary",
                  )}
                >
                  {getMessageIcon(message.notification_type)}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <div className="flex-1">
                      {message.subject && (
                        <h3
                          className={cn(
                            "font-semibold text-foreground truncate",
                            !message.is_read && "font-bold",
                          )}
                        >
                          {message.subject}
                        </h3>
                      )}
                      <span className="inline-block px-2 py-0.5 text-xs font-medium rounded-full bg-muted text-muted-foreground mt-1">
                        {getMessageTypeLabel(message.notification_type)}
                      </span>
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      {!message.is_read ? (
                        <span
                          className="w-2 h-2 bg-primary rounded-full"
                          title="Unread"
                        />
                      ) : null}
                    </div>
                  </div>

                  <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                    {message.content}
                  </p>

                  <div className="flex items-center justify-between">
                    <p className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(message.created_at), {
                        addSuffix: true,
                      })}
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1 shrink-0">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      message.is_read
                        ? handleMarkAsUnread(message)
                        : handleMarkAsRead(message);
                    }}
                    className="p-1.5 text-muted-foreground hover:bg-muted rounded transition-colors"
                    title={message.is_read ? "Mark as unread" : "Mark as read"}
                  >
                    {message.is_read ? (
                      <MailIcon className="w-4 h-4" />
                    ) : (
                      <MailOpenIcon className="w-4 h-4" />
                    )}
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(message.id);
                    }}
                    className="p-1.5 text-destructive hover:bg-destructive/10 rounded transition-colors"
                    title="Delete"
                  >
                    <Trash2Icon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
