import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X, Download, Clock } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface DocumentVersion {
  _id: string;
  document_name: string;
  file_url: string;
  file_type: string;
  version: number;
  uploaded_at: string;
  uploaded_by?: string;
}

interface DocumentVersionHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  documentId: string;
  onDownload?: (documentId: string) => Promise<void>;
}

export const DocumentVersionHistory: React.FC<DocumentVersionHistoryProps> = ({
  isOpen,
  onClose,
  documentId,
  onDownload,
}) => {
  const { showToast } = useToast();
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && documentId) {
      fetchVersions();
    }
  }, [isOpen, documentId]);

  const fetchVersions = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `/api/staff/documents/${documentId}/versions`,
      );
      const data = await response.json();
      setVersions(data.versions || []);
    } catch (error) {
      console.error("Failed to fetch versions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (versionId: string) => {
    try {
      if (onDownload) {
        await onDownload(versionId);
      }
    } catch (error) {
      console.error("Failed to download version:", error);
      showToast({
        title: "Error",
        description: "Failed to download version",
        variant: "destructive",
      });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md max-h-[80vh] flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between border-b">
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Version History
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>

        <CardContent className="flex-1 overflow-hidden p-4">
          <ScrollArea className="h-full">
            <div className="space-y-3 pr-4">
              {loading ? (
                <p className="text-center text-slate-500 py-8">Loading...</p>
              ) : versions.length === 0 ? (
                <p className="text-center text-slate-500 py-8">
                  No version history available
                </p>
              ) : (
                versions.map((version, index) => (
                  <div
                    key={version._id}
                    className="border rounded-lg p-3 hover:bg-slate-50 transition"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-sm">
                            {version.document_name}
                          </h3>
                          <Badge variant="secondary" className="text-xs">
                            v{version.version}
                          </Badge>
                          {index === 0 && (
                            <Badge className="text-xs">Current</Badge>
                          )}
                        </div>
                        <p className="text-xs text-slate-500 mt-1">
                          Uploaded{" "}
                          {new Date(version.uploaded_at).toLocaleDateString()}{" "}
                          at{" "}
                          {new Date(version.uploaded_at).toLocaleTimeString(
                            [],
                            {
                              hour: "2-digit",
                              minute: "2-digit",
                            },
                          )}
                        </p>
                        {version.uploaded_by && (
                          <p className="text-xs text-slate-500 mt-1">
                            By: {version.uploaded_by}
                          </p>
                        )}
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDownload(version._id)}
                        title="Download"
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
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
