import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

interface EmailTemplate {
  template: string;
  is_custom: boolean;
  available_variables: Record<string, string>;
}

interface PreviewResponse {
  success: boolean;
  html: string;
  sample_data: Record<string, any>;
}

interface ValidationResponse {
  valid: boolean;
  error?: string;
}

const EMAIL_TEMPLATES_KEY = "emailTemplates";

export function useGetCustomerWelcomeTemplate() {
  return useQuery({
    queryKey: [EMAIL_TEMPLATES_KEY, "customer-welcome"],
    queryFn: async () => {
      const { data } = await apiClient.get("/email-templates/customer-welcome");
      return data as EmailTemplate;
    },
  });
}

export function useUpdateCustomerWelcomeTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (template: string) => {
      const { data } = await apiClient.put(
        "/email-templates/customer-welcome",
        {
          template,
        },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [EMAIL_TEMPLATES_KEY, "customer-welcome"],
      });
    },
  });
}

export function useResetCustomerWelcomeTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post(
        "/email-templates/customer-welcome/reset",
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [EMAIL_TEMPLATES_KEY, "customer-welcome"],
      });
    },
  });
}

export function usePreviewCustomerWelcomeTemplate() {
  return useMutation({
    mutationFn: async (template: string) => {
      const { data } = await apiClient.post(
        "/email-templates/customer-welcome/preview",
        { template },
      );
      return data as PreviewResponse;
    },
  });
}

export function useValidateCustomerWelcomeTemplate() {
  return useMutation({
    mutationFn: async (template: string) => {
      const { data } = await apiClient.post(
        "/email-templates/customer-welcome/validate",
        { template },
      );
      return data as ValidationResponse;
    },
  });
}
