import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  AlertCircle,
  Download,
  Trash2,
  Clock,
  FileText,
  Plus,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Document {
  _id: string;
  document_type: string;
  document_name: string;
  file_url: string;
  file_type: string;
  expiration_date?: string;
  is_expired: boolean;
  uploaded_at: string;
  version: number;
  notes?: string;
}

interface DocumentListProps {
  staffId: string;
  userRole: string;
  onAddDocument?: () => void;
  onDownload?: (documentId: string) => Promise<void>;
  onDelete?: (documentId: string) => Promise<void>;
  onViewVersions?: (documentId: string) => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  staffId,
  userRole,
  onAddDocument,
  onDownload,
  onDelete,
  onViewVersions,
}) => {
  const { showToast } = useToast();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    fetchDocuments();
  }, [staffId, filter]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const url =
        filter === "all"
          ? `/api/staff/documents/${staffId}`
          : `/api/staff/documents/${staffId}?document_type=${filter}`;
      const response = await fetch(url);
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error("Failed to fetch documents:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!window.confirm("Are you sure you want to delete this document?")) {
      return;
    }

    try {
      if (onDelete) {
        await onDelete(documentId);
      }
      await fetchDocuments();
    } catch (error) {
      console.error("Failed to delete document:", error);
      showToast({
        title: "Error",
        description: "Failed to delete document",
        variant: "destructive",
      });
    }
  };

  const handleDownload = async (documentId: string) => {
    try {
      if (onDownload) {
        await onDownload(documentId);
      }
    } catch (error) {
      console.error("Failed to download document:", error);
      showToast({
        title: "Error",
        description: "Failed to download document",
        variant: "destructive",
      });
    }
  };

  const getDocumentTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      contract: "Contract",
      id: "ID",
      license: "License",
      tax_form: "Tax Form",
      other: "Other",
    };
    return labels[type] || type;
  };

  const isExpiringSoon = (expirationDate?: string) => {
    if (!expirationDate) return false;
    const expDate = new Date(expirationDate);
    const now = new Date();
    const daysUntilExpiration = Math.floor(
      (expDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24),
    );
    return daysUntilExpiration <= 30 && daysUntilExpiration > 0;
  };

  const canManageDocuments = ["owner", "manager"].includes(userRole);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Documents
        </CardTitle>
        {canManageDocuments && (
          <Button onClick={onAddDocument} size="sm">
            <Plus className="w-4 h-4 mr-2" />
            Add Document
          </Button>
        )}
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="flex gap-2 flex-wrap">
          <Button
            variant={filter === "all" ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter("all")}
          >
            All
          </Button>
          {["contract", "id", "license", "tax_form", "other"].map((type) => (
            <Button
              key={type}
              variant={filter === type ? "default" : "outline"}
              size="sm"
              onClick={() => setFilter(type)}
            >
              {getDocumentTypeLabel(type)}
            </Button>
          ))}
        </div>

        <ScrollArea className="h-96">
          <div className="space-y-2 pr-4">
            {loading ? (
              <p className="text-center text-slate-500 py-8">Loading...</p>
            ) : documents.length === 0 ? (
              <p className="text-center text-slate-500 py-8">
                No documents found
              </p>
            ) : (
              documents.map((doc) => (
                <div
                  key={doc._id}
                  className="border rounded-lg p-3 hover:bg-slate-50 transition"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-sm">
                          {doc.document_name}
                        </h3>
                        <Badge variant="secondary" className="text-xs">
                          {getDocumentTypeLabel(doc.document_type)}
                        </Badge>
                        {doc.is_expired && (
                          <Badge variant="destructive" className="text-xs">
                            Expired
                          </Badge>
                        )}
                        {isExpiringSoon(doc.expiration_date) && (
                          <Badge variant="outline" className="text-xs">
                            <AlertCircle className="w-3 h-3 mr-1" />
                            Expiring Soon
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        Uploaded{" "}
                        {new Date(doc.uploaded_at).toLocaleDateString()}
                      </p>
                      {doc.expiration_date && (
                        <p className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                          <Clock className="w-3 h-3" />
                          Expires{" "}
                          {new Date(doc.expiration_date).toLocaleDateString()}
                        </p>
                      )}
                      {doc.notes && (
                        <p className="text-xs text-slate-600 mt-2 italic">
                          {doc.notes}
                        </p>
                      )}
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDownload(doc._id)}
                        title="Download"
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                      {onViewVersions && doc.version > 1 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onViewVersions(doc._id)}
                          title="View versions"
                        >
                          v{doc.version}
                        </Button>
                      )}
                      {canManageDocuments && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(doc._id)}
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};
