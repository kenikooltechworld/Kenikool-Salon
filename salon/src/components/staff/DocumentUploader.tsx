import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  AlertCircleIcon,
  CheckCircleIcon,
  UploadIcon,
  FileIcon,
} from "@/components/icons";

interface DocumentUploaderProps {
  onUpload: (file: File, name: string) => void;
  isUploading?: boolean;
  error?: string;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
const ALLOWED_TYPES = [
  "application/pdf",
  "image/jpeg",
  "image/jpg",
  "image/png",
];

export function DocumentUploader({
  onUpload,
  isUploading = false,
  error,
}: DocumentUploaderProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentName, setDocumentName] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    setValidationError(null);
    setSuccessMessage(null);

    if (!file) {
      setSelectedFile(null);
      return;
    }

    // Validate file type
    if (!ALLOWED_TYPES.includes(file.type)) {
      setValidationError(
        "Invalid file type. Please upload PDF or image files (JPG, PNG)",
      );
      setSelectedFile(null);
      return;
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      setValidationError(
        `File size exceeds 10MB limit. Selected file is ${(file.size / (1024 * 1024)).toFixed(2)}MB`,
      );
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
    // Auto-populate document name from filename
    if (!documentName) {
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, "");
      setDocumentName(nameWithoutExt);
    }
  };

  const handleUpload = () => {
    setValidationError(null);
    setSuccessMessage(null);

    if (!selectedFile) {
      setValidationError("Please select a file to upload");
      return;
    }

    if (!documentName.trim()) {
      setValidationError("Please enter a document name");
      return;
    }

    onUpload(selectedFile, documentName.trim());

    // Reset form on successful upload
    setSelectedFile(null);
    setDocumentName("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    setSuccessMessage("Document uploaded successfully");
  };

  const handleClear = () => {
    setSelectedFile(null);
    setDocumentName("");
    setValidationError(null);
    setSuccessMessage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-4 rounded-lg border border-border bg-card p-4">
      <div className="flex items-center gap-2">
        <UploadIcon size={20} className="text-primary" />
        <h3 className="text-lg font-semibold">Upload Document</h3>
      </div>

      {successMessage && (
        <Alert className="bg-success/10 border-success/50">
          <CheckCircleIcon size={16} className="text-success" />
          <AlertDescription className="text-success">
            {successMessage}
          </AlertDescription>
        </Alert>
      )}

      {(validationError || error) && (
        <Alert className="bg-destructive/10 border-destructive/50">
          <AlertCircleIcon size={16} className="text-destructive" />
          <AlertDescription className="text-destructive">
            {validationError || error}
          </AlertDescription>
        </Alert>
      )}

      <div>
        <Label htmlFor="document-name">Document Name *</Label>
        <Input
          id="document-name"
          type="text"
          placeholder="e.g., Cosmetology License, CPR Certification"
          value={documentName}
          onChange={(e) => setDocumentName(e.target.value)}
          disabled={isUploading}
        />
        <p className="text-xs text-muted-foreground mt-1">
          Enter a descriptive name for this certification or document
        </p>
      </div>

      <div>
        <Label htmlFor="file-upload">Select File *</Label>
        <Input
          ref={fileInputRef}
          id="file-upload"
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={handleFileSelect}
          disabled={isUploading}
        />
        <p className="text-xs text-muted-foreground mt-1">
          Accepted formats: PDF, JPG, PNG (Max 10MB)
        </p>
      </div>

      {selectedFile && (
        <div className="flex items-center gap-2 rounded-md bg-muted p-3">
          <FileIcon size={20} className="text-muted-foreground" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{selectedFile.name}</p>
            <p className="text-xs text-muted-foreground">
              {(selectedFile.size / 1024).toFixed(2)} KB
            </p>
          </div>
        </div>
      )}

      <div className="flex gap-2">
        <Button
          onClick={handleUpload}
          disabled={!selectedFile || !documentName.trim() || isUploading}
          className="flex-1"
        >
          {isUploading ? "Uploading..." : "Upload Document"}
        </Button>
        {selectedFile && (
          <Button
            variant="outline"
            onClick={handleClear}
            disabled={isUploading}
          >
            Clear
          </Button>
        )}
      </div>
    </div>
  );
}
