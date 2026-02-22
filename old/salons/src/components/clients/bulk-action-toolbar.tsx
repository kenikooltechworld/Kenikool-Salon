import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  MessageSquareIcon,
  TagIcon,
  DownloadIcon,
  XIcon,
  ChevronDownIcon,
} from "@/components/icons";
import {
  Dropdown,
  DropdownContent,
  DropdownItem,
  DropdownTrigger,
} from "@/components/ui/dropdown";

export interface BulkActionToolbarProps {
  selectedCount: number;
  onSendMessage: () => void;
  onAddTag: () => void;
  onExport: () => void;
  onClearSelection: () => void;
  isLoading?: boolean;
}

/**
 * Toolbar displayed when clients are selected for bulk operations
 * Provides quick access to bulk actions
 * 
 * Requirements: REQ-CM-011 (Task 27.2)
 */
export function BulkActionToolbar({
  selectedCount,
  onSendMessage,
  onAddTag,
  onExport,
  onClearSelection,
  isLoading = false,
}: BulkActionToolbarProps) {
  const [isOpen, setIsOpen] = useState(true);

  if (!isOpen || selectedCount === 0) {
    return null;
  }

  return (
    <Card className="sticky bottom-0 left-0 right-0 p-4 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800 shadow-lg">
      <div className="flex items-center justify-between gap-4">
        {/* Selection info */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-foreground">
            {selectedCount} client{selectedCount !== 1 ? "s" : ""} selected
          </span>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {/* Send Message */}
          <Dropdown>
            <DropdownTrigger>
              <Button
                variant="outline"
                size="sm"
                disabled={isLoading}
                className="gap-2"
              >
                <MessageSquareIcon size={16} />
                Send Message
                <ChevronDownIcon size={14} />
              </Button>
            </DropdownTrigger>
            <DropdownContent align="end">
              <DropdownItem onClick={() => onSendMessage()}>
                SMS
              </DropdownItem>
              <DropdownItem onClick={() => onSendMessage()}>
                Email
              </DropdownItem>
              <DropdownItem onClick={() => onSendMessage()}>
                WhatsApp
              </DropdownItem>
            </DropdownContent>
          </Dropdown>

          {/* Add Tag */}
          <Button
            variant="outline"
            size="sm"
            onClick={onAddTag}
            disabled={isLoading}
            className="gap-2"
          >
            <TagIcon size={16} />
            Add Tag
          </Button>

          {/* Export */}
          <Button
            variant="outline"
            size="sm"
            onClick={onExport}
            disabled={isLoading}
            className="gap-2"
          >
            <DownloadIcon size={16} />
            Export
          </Button>

          {/* Clear Selection */}
          <Button
            variant="ghost"
            size="sm"
            onClick={onClearSelection}
            disabled={isLoading}
            className="gap-2"
          >
            <XIcon size={16} />
            Clear
          </Button>
        </div>
      </div>
    </Card>
  );
}

/**
 * Compact version of bulk action toolbar for mobile
 */
export function BulkActionToolbarMobile({
  selectedCount,
  onSendMessage,
  onAddTag,
  onExport,
  onClearSelection,
  isLoading = false,
}: BulkActionToolbarProps) {
  if (selectedCount === 0) {
    return null;
  }

  return (
    <Card className="sticky bottom-0 left-0 right-0 p-3 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800 shadow-lg md:hidden">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium text-foreground">
          {selectedCount} selected
        </span>

        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={onSendMessage}
            disabled={isLoading}
            className="h-8 w-8 p-0"
            title="Send message"
          >
            <MessageSquareIcon size={16} />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={onAddTag}
            disabled={isLoading}
            className="h-8 w-8 p-0"
            title="Add tag"
          >
            <TagIcon size={16} />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={onExport}
            disabled={isLoading}
            className="h-8 w-8 p-0"
            title="Export"
          >
            <DownloadIcon size={16} />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={onClearSelection}
            disabled={isLoading}
            className="h-8 w-8 p-0"
            title="Clear selection"
          >
            <XIcon size={16} />
          </Button>
        </div>
      </div>
    </Card>
  );
}
