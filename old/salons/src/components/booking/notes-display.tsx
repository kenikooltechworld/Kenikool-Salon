import React from "react";
import { AlertCircle } from "lucide-react";

interface NotesDisplayProps {
  notes: string;
  showTitle?: boolean;
  prominent?: boolean;
}

export const NotesDisplay: React.FC<NotesDisplayProps> = ({
  notes,
  showTitle = true,
  prominent = false,
}) => {
  if (!notes || notes.trim().length === 0) {
    return null;
  }

  return (
    <div
      className={`rounded-lg border-2 p-4 ${
        prominent ? "border-blue-300 bg-blue-50" : "border-gray-200 bg-gray-50"
      }`}
    >
      {showTitle && (
        <div className="flex items-center gap-2 mb-2">
          <AlertCircle
            className={`h-5 w-5 ${
              prominent ? "text-blue-600" : "text-gray-600"
            }`}
          />
          <h3
            className={`font-medium ${
              prominent ? "text-blue-900" : "text-gray-900"
            }`}
          >
            Special Requests & Notes
          </h3>
        </div>
      )}
      <p
        className={`text-sm whitespace-pre-wrap ${
          prominent ? "text-blue-800" : "text-gray-700"
        }`}
      >
        {notes}
      </p>
    </div>
  );
};
