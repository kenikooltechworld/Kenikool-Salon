"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Loader2Icon,
  UploadIcon,
  DownloadIcon,
  TrashIcon,
  ImageIcon,
  FileTextIcon,
  FileIcon,
} from "@/components/icons";
import { useToast } from "@/hooks/use-toast";
import {
  useUploadClientDocument,
  useGetClientDocuments,
  useDeleteClientDocument,
} from "@/lib/api/hooks/useClients";

interface Document {
  id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  size: number;
  document_type: string;
  category?: string;
  description?: string;
  uploaded_at: string;
}

interface DocumentsSectionProps {
  clientId: string;
  tenantId: string;
}

export function DocumentsSection({
  clientId,
  tenantId,
}: DocumentsSectionProps) {
  const { toast } = useToast();
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [showPreviewDialog, setShowPreviewDialog] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(
    null,
  );

  const { data: documents = [], refetch } = useGetClientDocuments(
    clientId,
    tenantId,
  );
  const uploadMutation = useUploadClientDocument(clientId, tenantId);
  const deleteMutation = useDeleteClientDocument(clientId, tenantId);

  const handleUpload = (formData: FormData) => {
    uploadMutation.mutate(formData, {
      onSuccess: () => {
        toast("Document uploaded successfully", "success");
        setShowUploadDialog(false);
        refetch();
      },
      onError: (error: Error) => {
        toast(error.message || "Failed to upload document", "error");
      },
    });
  };

  const handleDelete = (docId: string) => {
    deleteMutation.mutate(docId, {
      onSuccess: () => {
        toast("Document deleted successfully", "success");
        refetch();
      },
      onError: (error: Error) => {
        toast(error.message || "Failed to delete document", "error");
      },
    });
  };

  const getFileIcon = (fileType: string) => {
    if (["jpg", "jpeg", "png", "gif"].includes(fileType.toLowerCase())) {
      return <ImageIcon className="h-4 w-4" />;
    }
    return <FileTextIcon className="h-4 w-4" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Documents</CardTitle>
              <CardDescription>
                Manage client documents and files
              </CardDescription>
            </div>
            <Button onClick={() => setShowUploadDialog(true)}>
              <UploadIcon className="mr-2 h-4 w-4" />
              Upload Document
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <div className="text-center py-12">
              <FileIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600">No documents uploaded yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc: Document) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center gap-4 flex-1">
                    {getFileIcon(doc.file_type)}
                    <div className="flex-1">
                      <p className="font-medium">{doc.original_filename}</p>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <span>{formatFileSize(doc.size)}</span>
                        <span>•</span>
                        <span>
                          {new Date(doc.uploaded_at).toLocaleDateString()}
                        </span>
                        {doc.category && (
                          <>
                            <span>•</span>
                            <Badge variant="secondary" className="text-xs">
                              {doc.category}
                            </Badge>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        setSelectedDocument(doc);
                        setShowPreviewDialog(true);
                      }}
                    >
                      Preview
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={async () => {
                        const response = await fetch(
                          `/api/documents/clients/${clientId}/documents/${doc.id}/download`,
                          { headers: { "X-Tenant-ID": tenantId } },
                        );
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = doc.original_filename;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                      }}
                    >
                      <DownloadIcon className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(doc.id)}
                      disabled={deleteMutation.isPending}
                    >
                      <TrashIcon className="h-4 w-4 text-red-600" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Dialog */}
      <UploadDocumentDialog
        open={showUploadDialog}
        onOpenChange={setShowUploadDialog}
        onUpload={handleUpload}
        isLoading={uploadMutation.isPending}
      />

      {/* Preview Dialog */}
      {selectedDocument && (
        <PreviewDocumentDialog
          open={showPreviewDialog}
          onOpenChange={setShowPreviewDialog}
          document={selectedDocument}
          clientId={clientId}
        />
      )}
    </div>
  );
}

interface UploadDocumentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onUpload: (formData: FormData) => void;
  isLoading: boolean;
}

function UploadDocumentDialog({
  open,
  onOpenChange,
  onUpload,
  isLoading,
}: UploadDocumentDialogProps) {
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");

  const handleUpload = () => {
    if (!file || !documentType) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("document_type", documentType);
    if (category) formData.append("category", category);
    if (description) formData.append("description", description);

    onUpload(formData);
    setFile(null);
    setDocumentType("");
    setCategory("");
    setDescription("");
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload Document</DialogTitle>
          <DialogDescription>
            Upload a document to attach to this client's profile
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">File</label>
            <Input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              disabled={isLoading}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Document Type *
            </label>
            <Select value={documentType} onValueChange={setDocumentType}>
              <SelectTrigger>
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="consent_form">Consent Form</SelectItem>
                <SelectItem value="contract">Contract</SelectItem>
                <SelectItem value="receipt">Receipt</SelectItem>
                <SelectItem value="invoice">Invoice</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Category</label>
            <Input
              placeholder="e.g., Legal, Financial"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              disabled={isLoading}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              Description
            </label>
            <Textarea
              placeholder="Add notes about this document"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isLoading}
            />
          </div>
          <div className="flex gap-4 justify-end">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={!file || !documentType || isLoading}
            >
              {isLoading && (
                <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />
              )}
              Upload
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

interface PreviewDocumentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  document: Document;
  clientId: string;
}

function PreviewDocumentDialog({
  open,
  onOpenChange,
  document,
  clientId,
}: PreviewDocumentDialogProps) {
  const isImage = ["jpg", "jpeg", "png", "gif"].includes(
    document.file_type.toLowerCase(),
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{document.original_filename}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          {isImage ? (
            <img
              src={`/api/documents/clients/${clientId}/documents/${document.id}/thumbnail`}
              alt={document.original_filename}
              className="w-full max-h-96 object-contain"
            />
          ) : (
            <Alert>
              <FileTextIcon className="h-4 w-4" />
              <AlertDescription>
                Preview not available for this file type. Please download to
                view.
              </AlertDescription>
            </Alert>
          )}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Type</p>
              <p className="font-semibold capitalize">
                {document.document_type}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Size</p>
              <p className="font-semibold">
                {Math.round((document.size / 1024) * 100) / 100} KB
              </p>
            </div>
            <div>
              <p className="text-gray-600">Uploaded</p>
              <p className="font-semibold">
                {new Date(document.uploaded_at).toLocaleDateString()}
              </p>
            </div>
            {document.category && (
              <div>
                <p className="text-gray-600">Category</p>
                <p className="font-semibold">{document.category}</p>
              </div>
            )}
          </div>
          {document.description && (
            <div>
              <p className="text-sm text-gray-600">Description</p>
              <p className="text-sm">{document.description}</p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
