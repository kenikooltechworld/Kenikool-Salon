import React from "react";
import { format } from "date-fns";
import { User, Clock } from "lucide-react";

interface NoteEntry {
  id: string;
  content: string;
  author: string;
  timestamp: string;
  type: "customer" | "stylist" | "system";
}

interface NotesHistoryProps {
  entries: NoteEntry[];
  loading?: boolean;
}

export const NotesHistory: React.FC<NotesHistoryProps> = ({
  entries,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="text-sm text-gray-500">Loading notes history...</div>
    );
  }

  if (!entries || entries.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-center text-sm text-gray-600">
        No notes history
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="font-medium text-gray-900">Notes History</h3>
      <div className="space-y-2">
        {entries.map((entry) => (
          <div
            key={entry.id}
            className="rounded-lg border border-gray-200 bg-white p-3 space-y-2"
          >
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-gray-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {entry.author}
                  </p>
                  <p className="text-xs text-gray-600">
                    {entry.type === "customer"
                      ? "Customer"
                      : entry.type === "stylist"
                        ? "Stylist"
                        : "System"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1 text-xs text-gray-600">
                <Clock className="h-3 w-3" />
                {format(new Date(entry.timestamp), "MMM dd, yyyy h:mm a")}
              </div>
            </div>

            {/* Content */}
            <p className="text-sm text-gray-700 whitespace-pre-wrap">
              {entry.content}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
