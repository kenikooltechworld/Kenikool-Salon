import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import {
  FileIcon,
  DownloadIcon,
  TrashIcon,
  CheckCircleIcon,
  ClockIcon,
  AlertCircleIcon,
} from "@/components/icons";
import type { Document } from "@/hooks/useDocuments";
import { formatDate } from "@/lib/utils/format";

interface DocumentListProps {
  documents: Document[];
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
  onDelete?: (documentId: string) => void;
  isDeleting?: boolean;
}

export function DocumentList({
  documents,
  isLoading = false,
  error,
  onRetry,
  onDelete,
  isDeleting = false,
}: DocumentListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-4">
        <p className="text-sm text-destructive font-medium">
          Failed to load documents
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          {error || "Network error. Please try again."}
        </p>
        {onRetry && (
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            className="mt-3"
          >
            Retry
          </Button>
        )}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-muted/50 p-8 text-center">
        <FileIcon size={48} className="mx-auto text-muted-foreground mb-3" />
        <p className="text-muted-foreground font-medium">
          No documents uploaded
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          Upload your professional certifications and documents above
        </p>
      </div>
    );
  }

  const getStatusBadge = (status: Document["verificationStatus"]) => {
    switch (status) {
      case "verified":
        return (
          <Badge variant="default" className="bg-success text-white">
            <CheckCircleIcon size={12} className="mr-1" />
            Verified
          </Badge>
        );
      case "pending":
        return (
          <Badge variant="secondary">
            <ClockIcon size={12} className="mr-1" />
            Pending
          </Badge>
        );
      case "expired":
        return (
          <Badge variant="destructive">
            <AlertCircleIcon size={12} className="mr-1" />
            Expired
          </Badge>
        );
    }
  };

  const handleDownload = (url: string) => {
    // Open in new tab for download
    window.open(url, "_blank");
  };

  return (
    <div className="space-y-3">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="rounded-lg border border-border bg-card p-4 hover:shadow-sm transition-shadow"
        >
          <div className="flex items-start gap-3">
            <div className="rounded-md bg-primary/10 p-2">
              <FileIcon size={24} className="text-primary" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-sm truncate">{doc.name}</h4>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {doc.type} • Uploaded {formatDate(doc.uploadedAt)}
                  </p>
                </div>
                {getStatusBadge(doc.verificationStatus)}
              </div>

              {doc.expirationDate && (
                <p className="text-xs text-muted-foreground mt-2">
                  Expires: {formatDate(doc.expirationDate)}
                </p>
              )}

              <div className="flex gap-2 mt-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDownload(doc.url)}
                  className="flex items-center gap-1"
                >
                  <DownloadIcon size={14} />
                  Download
                </Button>
                {onDelete && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onDelete(doc.id)}
                    disabled={isDeleting}
                    className="flex items-center gap-1 text-destructive hover:text-destructive"
                  >
                    <TrashIcon size={14} />
                    Delete
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
