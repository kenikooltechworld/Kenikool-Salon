import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import {
  useInitializePayment,
  useVerifyPayment,
  useRetryPayment,
} from "../usePayments";

// Mock the API client
vi.mock("@/lib/utils/api", () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

const queryClient = new QueryClient();

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

describe("useInitializePayment", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should initialize payment successfully", async () => {
    const { result } = renderHook(() => useInitializePayment(), { wrapper });

    const mockResponse = {
      paymentId: "pay_123",
      authorizationUrl: "https://checkout.paystack.com/test",
      accessCode: "access_123",
      reference: "ref_123",
    };

    // Mock the API response
    const { apiClient } = await import("@/lib/utils/api");
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockResponse });

    // Mock window.location.href
    delete (window as any).location;
    window.location = { href: "" } as any;

    const mutateAsync = result.current.mutateAsync;

    await mutateAsync({
      amount: 50000,
      customerId: "cust_123",
      invoiceId: "inv_123",
      email: "test@example.com",
    });

    await waitFor(() => {
      expect(window.location.href).toBe(mockResponse.authorizationUrl);
    });
  });

  it("should handle payment initialization error", async () => {
    const { result } = renderHook(() => useInitializePayment(), { wrapper });

    const { apiClient } = await import("@/lib/utils/api");
    vi.mocked(apiClient.post).mockRejectedValueOnce(
      new Error("Payment failed"),
    );

    const mutateAsync = result.current.mutateAsync;

    await expect(
      mutateAsync({
        amount: 50000,
        customerId: "cust_123",
        invoiceId: "inv_123",
        email: "test@example.com",
      }),
    ).rejects.toThrow();
  });

  it("should include idempotency key in request", async () => {
    const { result } = renderHook(() => useInitializePayment(), { wrapper });

    const mockResponse = {
      paymentId: "pay_123",
      authorizationUrl: "https://checkout.paystack.com/test",
      accessCode: "access_123",
      reference: "ref_123",
    };

    const { apiClient } = await import("@/lib/utils/api");
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockResponse });

    delete (window as any).location;
    window.location = { href: "" } as any;

    const mutateAsync = result.current.mutateAsync;

    await mutateAsync({
      amount: 50000,
      customerId: "cust_123",
      invoiceId: "inv_123",
      email: "test@example.com",
      idempotencyKey: "idempotency_123",
    });

    expect(apiClient.post).toHaveBeenCalledWith(
      "/payments/initialize",
      expect.objectContaining({
        idempotency_key: "idempotency_123",
      }),
    );
  });
});

describe("useVerifyPayment", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should verify payment successfully", async () => {
    const { result } = renderHook(() => useVerifyPayment(), { wrapper });

    const mockResponse = {
      data: {
        id: "pay_123",
        invoiceId: "inv_123",
        customerId: "cust_123",
        amount: 50000,
        method: "paystack" as const,
        status: "completed" as const,
        transactionId: "ref_123",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    };

    const { apiClient } = await import("@/lib/utils/api");
    vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse);

    const mutateAsync = result.current.mutateAsync;

    const payment = await mutateAsync("ref_123");

    expect(payment).toEqual(mockResponse.data);
  });

  it("should handle verification error", async () => {
    const { result } = renderHook(() => useVerifyPayment(), { wrapper });

    const { apiClient } = await import("@/lib/utils/api");
    vi.mocked(apiClient.get).mockRejectedValueOnce(
      new Error("Verification failed"),
    );

    const mutateAsync = result.current.mutateAsync;

    await expect(mutateAsync("ref_123")).rejects.toThrow();
  });
});

describe("useRetryPayment", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should retry payment successfully", async () => {
    const { result } = renderHook(() => useRetryPayment(), { wrapper });

    const mockResponse = {
      data: {
        id: "pay_123",
        invoiceId: "inv_123",
        customerId: "cust_123",
        amount: 50000,
        method: "paystack" as const,
        status: "pending" as const,
        transactionId: "ref_123",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    };

    const { apiClient } = await import("@/lib/utils/api");
    vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

    const mutateAsync = result.current.mutateAsync;

    const payment = await mutateAsync("pay_123");

    expect(payment).toEqual(mockResponse.data);
  });

  it("should handle retry error", async () => {
    const { result } = renderHook(() => useRetryPayment(), { wrapper });

    const { apiClient } = await import("@/lib/utils/api");
    vi.mocked(apiClient.post).mockRejectedValueOnce(new Error("Retry failed"));

    const mutateAsync = result.current.mutateAsync;

    await expect(mutateAsync("pay_123")).rejects.toThrow();
  });
});
