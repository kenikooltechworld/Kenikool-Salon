/**
 * NotesAndRequestsInput Component
 * Allows users to add special notes and requests for their booking
 */
import React from "react";
import { Textarea } from "@/components/ui/textarea";

interface NotesAndRequestsInputProps {
  onNotesChange: (notes: string) => void;
  initialValue?: string;
  placeholder?: string;
  maxLength?: number;
}

export const NotesAndRequestsInput: React.FC<NotesAndRequestsInputProps> = ({
  onNotesChange,
  initialValue = "",
  placeholder = "Add any special requests or notes for your appointment...",
  maxLength = 500,
}) => {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-foreground">
        Special Requests & Notes
      </label>
      <Textarea
        placeholder={placeholder}
        value={initialValue}
        onChange={(e) => onNotesChange(e.target.value)}
        maxLength={maxLength}
        rows={4}
        className="resize-none"
      />
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>Optional - Let us know about any special requirements</span>
        <span>
          {initialValue.length}/{maxLength}
        </span>
      </div>
    </div>
  );
};

export default NotesAndRequestsInput;
