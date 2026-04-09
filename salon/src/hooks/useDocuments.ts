import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useAuthStore } from "@/stores/auth";

export interface Document {
  id: string;
  name: string;
  type: string;
  url: string;
  uploadedAt: string;
  expirationDate?: string;
  verificationStatus: "pending" | "verified" | "expired";
  fileSize?: number;
}

interface DocumentsResponse {
  certification_files: string[];
  certifications: string[];
}

interface UpdateStaffRequest {
  certification_files: string[];
  certifications: string[];
}

/**
 * Hook for managing staff documents and certifications
 */
export function useDocuments() {
  const user = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();

  // Fetch staff documents
  const {
    data: documentsData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["staff-documents", user?.id],
    queryFn: async () => {
      if (!user?.id) throw new Error("User not authenticated");

      // Get staff record to retrieve certification files
      const response = await apiClient.get<DocumentsResponse>(
        `/staff/user/${user.id}`,
      );

      return response.data;
    },
    enabled: !!user?.id,
  });

  // Parse certification files into Document objects
  const documents: Document[] = (documentsData?.certification_files || []).map(
    (url, index) => {
      const fileName = url.split("/").pop() || `document-${index + 1}`;
      const certName =
        documentsData?.certifications?.[index] || "Certification";

      return {
        id: `doc-${index}`,
        name: certName,
        type: fileName.split(".").pop()?.toUpperCase() || "FILE",
        url,
        uploadedAt: new Date().toISOString(), // We don't have this data, using current date
        verificationStatus: "verified" as const,
      };
    },
  );

  // Upload document mutation
  const uploadMutation = useMutation({
    mutationFn: async ({ file, name }: { file: File; name: string }) => {
      if (!user?.id) throw new Error("User not authenticated");

      // Convert file to base64
      const reader = new FileReader();
      const base64Promise = new Promise<string>((resolve, reject) => {
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = reject;
      });
      reader.readAsDataURL(file);
      const base64Data = await base64Promise;

      // Upload to media service
      const uploadResponse = await apiClient.post<{ url: string }>(
        "/media/upload",
        {
          base64_data: base64Data,
          media_type: "document",
          folder: "staff-certifications",
        },
      );

      const documentUrl = uploadResponse.data.url;

      // Get current staff data
      const staffResponse = await apiClient.get<DocumentsResponse>(
        `/staff/user/${user.id}`,
      );
      const currentFiles = staffResponse.data.certification_files || [];
      const currentCerts = staffResponse.data.certifications || [];

      // Update staff record with new document
      const updateData: UpdateStaffRequest = {
        certification_files: [...currentFiles, documentUrl],
        certifications: [...currentCerts, name],
      };

      await apiClient.put(`/staff/user/${user.id}`, updateData);

      return { url: documentUrl, name };
    },
    onSuccess: () => {
      // Invalidate and refetch documents
      queryClient.invalidateQueries({
        queryKey: ["staff-documents", user?.id],
      });
    },
  });

  // Delete document mutation
  const deleteMutation = useMutation({
    mutationFn: async (documentId: string) => {
      if (!user?.id) throw new Error("User not authenticated");

      // Parse document index from ID
      const index = parseInt(documentId.split("-")[1]);

      // Get current staff data
      const staffResponse = await apiClient.get<DocumentsResponse>(
        `/staff/user/${user.id}`,
      );
      const currentFiles = staffResponse.data.certification_files || [];
      const currentCerts = staffResponse.data.certifications || [];

      // Remove document at index
      const updatedFiles = currentFiles.filter((_, i) => i !== index);
      const updatedCerts = currentCerts.filter((_, i) => i !== index);

      // Update staff record
      const updateData: UpdateStaffRequest = {
        certification_files: updatedFiles,
        certifications: updatedCerts,
      };

      await apiClient.put(`/staff/user/${user.id}`, updateData);
    },
    onSuccess: () => {
      // Invalidate and refetch documents
      queryClient.invalidateQueries({
        queryKey: ["staff-documents", user?.id],
      });
    },
  });

  return {
    documents,
    isLoading,
    error: error?.message,
    refetch,
    uploadDocument: uploadMutation.mutate,
    isUploading: uploadMutation.isPending,
    uploadError: uploadMutation.error?.message,
    deleteDocument: deleteMutation.mutate,
    isDeleting: deleteMutation.isPending,
    deleteError: deleteMutation.error?.message,
  };
}
