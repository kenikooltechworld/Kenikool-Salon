import { DocumentUploader } from "@/components/staff/DocumentUploader";
import { DocumentList } from "@/components/staff/DocumentList";
import { useDocuments } from "@/hooks/useDocuments";
import { FileIcon } from "@/components/icons";

export default function Documents() {
  const {
    documents,
    isLoading,
    error,
    refetch,
    uploadDocument,
    isUploading,
    uploadError,
    deleteDocument,
    isDeleting,
  } = useDocuments();

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <FileIcon size={28} className="text-primary" />
          <h1 className="text-3xl font-bold">Documents & Certifications</h1>
        </div>
        <p className="text-muted-foreground">
          Upload and manage your professional certifications and documents. Keep
          your credentials current and easily accessible.
        </p>
      </div>

      <div className="space-y-6">
        {/* Upload Section */}
        <DocumentUploader
          onUpload={(file, name) => uploadDocument({ file, name })}
          isUploading={isUploading}
          error={uploadError}
        />

        {/* Documents List Section */}
        <div>
          <h2 className="text-xl font-semibold mb-4">My Documents</h2>
          <DocumentList
            documents={documents}
            isLoading={isLoading}
            error={error}
            onRetry={refetch}
            onDelete={deleteDocument}
            isDeleting={isDeleting}
          />
        </div>
      </div>
    </div>
  );
}
