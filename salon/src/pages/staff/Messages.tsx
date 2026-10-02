import { useState } from "react";
import MessagesList from "@/components/staff/MessagesList";
import MessageDetail from "@/components/staff/MessageDetail";
import type { Notification } from "@/types/notification";
import { MessageSquareIcon, ChevronLeftIcon } from "@/components/icons";

export default function Messages() {
  const [selectedMessage, setSelectedMessage] = useState<Notification | null>(
    null,
  );
  const [showDetail, setShowDetail] = useState(false);

  const handleMessageClick = (message: Notification) => {
    setSelectedMessage(message);
    setShowDetail(true);
  };

  const handleCloseDetail = () => {
    setShowDetail(false);
    setSelectedMessage(null);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <MessageSquareIcon className="w-7 h-7" />
            Messages
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            View messages and announcements from your manager
          </p>
        </div>
        {showDetail && (
          <button
            onClick={handleCloseDetail}
            className="lg:hidden flex items-center gap-1 text-sm text-primary hover:text-primary/80 font-medium"
          >
            <ChevronLeftIcon className="w-4 h-4" />
            Back to list
          </button>
        )}
      </div>

      {/* Messages Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Messages List */}
        <div
          className={`${
            showDetail ? "hidden lg:block" : ""
          } transition-all`}
        >
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <MessagesList
              onMessageClick={handleMessageClick}
              showSearch={true}
            />
          </div>
        </div>

        {/* Message Detail */}
        {showDetail && selectedMessage && (
          <div className="lg:col-span-2">
            <MessageDetail
              messageId={selectedMessage.id}
              onClose={handleCloseDetail}
              className="sticky top-6"
            />
          </div>
        )}
      </div>
    </div>
  );
}
