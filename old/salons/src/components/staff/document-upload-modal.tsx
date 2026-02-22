import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { X, Upload } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface DocumentUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  staffId: string;
  onUpload?: (data: {
    document_type: string;
    document_name: string;
    file_url: string;
    file_type: string;
    file_size_bytes: number;
    expiration_date?: string;
    notes?: string;
  }) => Promise<void>;
}

export const DocumentUploadModal: React.FC<DocumentUploadModalProps> = ({
  isOpen,
  onClose,
  staffId,
  onUpload,
}) => {
  const { showToast } = useToast();
  const [documentType, setDocumentType] = useState("contract");
  const [documentName, setDocumentName] = useState("");
  const [expirationDate, setExpirationDate] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState("");

  const documentTypes = [
    { value: "contract", label: "Employment Contract" },
    { value: "id", label: "ID Document" },
    { value: "license", label: "License" },
    { value: "tax_form", label: "Tax Form" },
    { value: "other", label: "Other" },
  ];

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
      if (!documentName) {
        setDocumentName(file.name.split(".")[0]);
      }
    }
  };

  const handleUpload = async () => {
    if (!fileName || !documentName || !documentType) {
      showToast({
        title: "Validation Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      // In a real implementation, you would upload the file to a storage service
      // and get back a file_url. For now, we'll use a placeholder.
      const fileExt = fileName.split(".").pop() || "pdf";
      const fileUrl = `/documents/${staffId}/${Date.now()}.${fileExt}`;

      if (onUpload) {
        await onUpload({
          document_type: documentType,
          document_name: documentName,
          file_url: fileUrl,
          file_type: fileExt,
          file_size_bytes: 0, // Would be actual file size
          expiration_date: expirationDate || undefined,
          notes: notes || undefined,
        });
      }

      // Reset form
      setDocumentType("contract");
      setDocumentName("");
      setExpirationDate("");
      setNotes("");
      setFileName("");
      onClose();
    } catch (error) {
      console.error("Failed to upload document:", error);
      showToast({
        title: "Error",
        description: "Failed to upload document",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Upload Document
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>

        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Document Type *
            </label>
            <Select value={documentType} onValueChange={setDocumentType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {documentTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Document Name *
            </label>
            <Input
              placeholder="e.g., Employment Agreement 2024"
              value={documentName}
              onChange={(e) => setDocumentName(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Select File *
            </label>
            <div className="border-2 border-dashed rounded-lg p-4 text-center">
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,.docx"
                onChange={handleFileSelect}
                className="hidden"
                id="file-input"
              />
              <label
                htmlFor="file-input"
                className="cursor-pointer text-sm text-slate-600 hover:text-slate-900"
              >
                {fileName ? (
                  <div>
                    <p className="font-medium">{fileName}</p>
                    <p className="text-xs text-slate-500">Click to change</p>
                  </div>
                ) : (
                  <div>
                    <p>Click to select file</p>
                    <p className="text-xs text-slate-500">
                      PDF, JPG, PNG, DOCX
                    </p>
                  </div>
                )}
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Expiration Date (Optional)
            </label>
            <Input
              type="date"
              value={expirationDate}
              onChange={(e) => setExpirationDate(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Notes (Optional)
            </label>
            <Textarea
              placeholder="Add any notes about this document..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleUpload}
              disabled={loading || !fileName}
              className="flex-1"
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload
            </Button>
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
