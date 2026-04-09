import { useEffect } from "react";
import { useMessage, useMarkMessageRead } from "@/hooks/useMessages";
import type { Notification } from "@/types/notification";
import {
  XIcon,
  MegaphoneIcon,
  MessageSquareIcon,
  UserIcon,
  CalendarIcon,
} from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface MessageDetailProps {
  messageId: string;
  onClose: () => void;
  className?: string;
}

export default function MessageDetail({
  messageId,
  onClose,
  className,
}: MessageDetailProps) {
  const { data: message, isLoading, error } = useMessage(messageId);
  const markAsRead = useMarkMessageRead();

  // Mark as read when opened
  useEffect(() => {
    if (message && !message.is_read) {
      markAsRead.mutate(messageId);
    }
  }, [message, messageId, markAsRead]);

  const getMessageIcon = (notificationType: string) => {
    if (notificationType === "team_announcement") {
      return <MegaphoneIcon className="w-6 h-6" />;
    }
    return <MessageSquareIcon className="w-6 h-6" />;
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

  const getSenderName = (message: Notification) => {
    // Extract sender from template variables if available
    const templateVars = (message as any).template_variables;
    if (templateVars?.sender_name) {
      return templateVars.sender_name;
    }
    if (templateVars?.manager_name) {
      return templateVars.manager_name;
    }
    return "Manager";
  };

  if (isLoading) {
    return (
      <div
        className={cn(
          "bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6",
          className,
        )}
      >
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !message) {
    return (
      <div
        className={cn(
          "bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6",
          className,
        )}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Message
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            <XIcon className="w-5 h-5" />
          </button>
        </div>
        <div className="text-center py-8">
          <p className="text-red-600 dark:text-red-400">
            Failed to load message
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "bg-white dark:bg-gray-900 rounded-lg shadow-lg",
        className,
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              "p-3 rounded-lg",
              message.notification_type === "team_announcement"
                ? "bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400"
                : "bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400",
            )}
          >
            {getMessageIcon(message.notification_type)}
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              {message.subject || "Message"}
            </h2>
            <span className="inline-block px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 mt-1">
              {getMessageTypeLabel(message.notification_type)}
            </span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
        >
          <XIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Message Info */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <UserIcon className="w-4 h-4" />
            <span className="font-medium">From:</span>
            <span>{getSenderName(message)}</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <CalendarIcon className="w-4 h-4" />
            <span className="font-medium">Sent:</span>
            <span>
              {new Date(message.created_at).toLocaleString("en-US", {
                year: "numeric",
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          </div>
        </div>
      </div>

      {/* Message Content */}
      <div className="p-6">
        <div className="prose dark:prose-invert max-w-none">
          <div className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
            {message.content}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
        <button
          onClick={onClose}
          className="w-full sm:w-auto px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 active:bg-blue-800 transition-colors font-medium"
        >
          Close
        </button>
      </div>
    </div>
  );
}
