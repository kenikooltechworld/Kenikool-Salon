import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { CustomerPaymentPortal } from "../CustomerPaymentPortal";
import * as useCustomerPaymentPortalModule from "@/lib/api/hooks/useCustomerPaymentPortal";
import * as useGenerateReceiptModule from "@/lib/api/hooks/useGenerateReceipt";
import { vi } from "vitest";
import type { CustomerPayment } from "@/lib/api/hooks/useCustomerPaymentPortal";

const mockCustomerPayments: CustomerPayment[] = [
  {
    id: "1",
    tenant_id: "tenant-1",
    booking_id: "booking-1",
    amount: 100,
    gateway: "paystack",
    reference: "REF001",
    status: "completed",
    payment_type: "full",
    created_at: "2024-01-01",
    updated_at: "2024-01-01",
    service_name: "Hair Cut",
    booking_date: "2024-01-01",
    receipt_url: "https://example.com/receipt.pdf",
  },
  {
    id: "2",
    tenant_id: "tenant-1",
    booking_id: "booking-2",
    amount: 150,
    gateway: "flutterwave",
    reference: "REF002",
    status: "pending",
    payment_type: "full",
    created_at: "2024-01-02",
    updated_at: "2024-01-02",
    service_name: "Hair Coloring",
    booking_date: "2024-01-02",
  },
];

describe("CustomerPaymentPortal", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  const renderComponent = (customerId: string = "customer-1") => {
    return render(
      <QueryClientProvider client={queryClient}>
        <CustomerPaymentPortal customerId={customerId} />
      </QueryClientProvider>
    );
  };

  it("renders loading state initially", () => {
    vi.spyOn(useCustomerPaymentPortalModule, "useCustomerPayments").mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
      isError: false,
      isSuccess: false,
      status: "pending",
      dataUpdatedAt: 0,
      errorUpdatedAt: 0,
      failureCount: 0,
      failureReason: null,
      isFetched: false,
      isFetchedAfterMount: false,
      isFetching: false,
      isPaused: false,
      isPending: true,
      refetch: vi.fn(),
      remove: vi.fn(),
    } as any);

    renderComponent();
    expect(screen.getByText("Payment History")).toBeInTheDocument();
  });

  it("renders customer payments when loaded", async () => {
    vi.spyOn(useCustomerPaymentPortalModule, "useCustomerPayments").mockReturnValue({
      data: mockCustomerPayments,
      isLoading: false,
      error: null,
      isError: false,
      isSuccess: true,
      status: "success",
      dataUpdatedAt: Date.now(),
      errorUpdatedAt: 0,
      failureCount: 0,
      failureReason: null,
      isFetched: true,
      isFetchedAfterMount: true,
      isFetching: false,
      isPaused: false,
      isPending: false,
      refetch: vi.fn(),
      remove: vi.fn(),
    } as any);

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("Hair Cut")).toBeInTheDocument();
      expect(screen.getByText("Hair Coloring")).toBeInTheDocument();
    });
  });

  it("displays payment amounts correctly", async () => {
    vi.spyOn(useCustomerPaymentPortalModule, "useCustomerPayments").mockReturnValue({
      data: mockCustomerPayments,
      isLoading: false,
      error: null,
      isError: false,
      isSuccess: true,
      status: "success",
      dataUpdatedAt: Date.now(),
      errorUpdatedAt: 0,
      failureCount: 0,
      failureReason: null,
      isFetched: true,
      isFetchedAfterMount: true,
      isFetching: false,
      isPaused: false,
      isPending: false,
      refetch: vi.fn(),
      remove: vi.fn(),
    } as any);

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("$100.00")).toBeInTheDocument();
      expect(screen.getByText("$150.00")).toBeInTheDocument();
    });
  });

  it("displays payment status badges", async () => {
    vi.spyOn(useCustomerPaymentPortalModule, "useCustomerPayments").mockReturnValue({
      data: mockCustomerPayments,
      isLoading: false,
      error: null,
      isError: false,
      isSuccess: true,
      status: "success",
      dataUpdatedAt: Date.now(),
      errorUpdatedAt: 0,
      failureCount: 0,
      failureReason: null,
      isFetched: true,
      isFetchedAfterMount: true,
      isFetching: false,
      isPaused: false,
      isPending: false,
      refetch: vi.fn(),
      remove: vi.fn(),
    } as any);

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText("completed")).toBeInTheDocument();
      expect(screen.getByText("pending")).toBeInTheDocument();
    });
  });

  it("displays receipt download button for completed payments", async () => {
    vi.spyOn(useCustomerPaymentPortalModule, "useCustomerPayments").mockReturnValue({
      data: mockCustomerPayments,
      isLoading: false,
      error: null,
      isError: false,
      isSuccess: true,
      status: "success",
      dataUpdatedAt: Date.now(),
      errorUpdatedAt: 0,
      failureCount: 0,
      failureReason: null,
      isFetched: true,
      isFetchedAfterMount: true,
      isFetching: false,
      isPaused: false,
      isPending: false,
      refetch: vi.fn(),
      remove: vi.fn(),
    } as any);

    vi.spyOn(useGenerateReceiptModule, "useGenerateReceipt").mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      isError: false,
      isSuccess: false,
      data: undefined,
      error: null,
      status: "idle",
      reset: vi.fn(),
      mutateAsync: vi.fn(),
      failureCount: 0,
      failureReason: null,
      variables: undefined,
      context: undefined,
      submittedAt: 0,
    } as any);

    renderComponent();

    await waitFor(() => {
      const receiptButtons = screen.getAllByText("Receipt");
      expect(receiptButtons.length).toBeGreaterThan(0);
    });
  });

  it("displays pay now button for pending payments", async () => {
    vi.spyOn(useCustomerPaymentPortalModule, "useCustomerPayments").mockReturnValue({
      data: mockCustomerPayments,
      isLoading: false,
      error: null,
      isError: false,
      isSuccess: true,
      status: "success",
      dataUpdatedAt: Date.now(),
      errorUpdatedAt: 0,
      failureCount: 0,
      failureReason: null,
      isFetched: true,
      isFetchedAfterMount: true,
      isFetching: false,
      isPaused: false,
      isPending: false,
      refetch: vi.fn(),
      remove: vi.fn(),
    } as any);

    renderComponent();

    await waitFor(() => {
      const payNowButtons = screen.getAllByText("Pay Now");
      expect(payNowButtons.length).toBeGreaterThan(0);
    });
  });

  it("handles generate payment link action", async () => {
    const mockGenerateLink = vi.fn().mockResolvedValue({
      token: "token-123",
      payment_url: "https://example.com/pay",
      expires_at: "2024-01-31",
    });

    vi.spyOn(useCustomerPaymentPortalModule, "useGeneratePaymentLink").mockReturnValue({
      mutate: mockGenerateLink,
      isPending: false,
      isError: false,
      isSuccess: false,
      data: undefined,
      error: null,
      status: "idle",
      reset: vi.fn(),
      mutateAsync: vi.fn(),
      failureCount: 0,
      failureReason: null,
      variables: undefined,
      context: undefined,
      submittedAt: 0,
    } as any);

    vi.spyOn(useCustomerPaymentPortalModule, "useCustomerPayments").mockReturnValue({
      data: mockCustomerPayments,
      isLoading: false,
      error: null,
      isError: false,
      isSuccess: true,
      status: "success",
      dataUpdatedAt: Date.now(),
      errorUpdatedAt: 0,
      failureCount: 0,
      failureReason: null,
      isFetched: true,
      isFetchedAfterMount: true,
      isFetching: false,
      isPaused: false,
      isPending: false,
      refetch: vi.fn(),
      remove: vi.fn(),
    } as any);

    renderComponent();

    await waitFor(() => {
      const payNowButtons = screen.getAllByText("Pay Now");
      fireEvent.click(payNowButtons[0]);
    });
  });

  it("renders empty state when no payments", async () => {
    vi.spyOn(useCustomerPaymentPortalModule, "useCustomerPayments").mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
      isError: false,
      isSuccess: true,
      status: "success",
      dataUpdatedAt: Date.now(),
      errorUpdatedAt: 0,
      failureCount: 0,
      failureReason: null,
      isFetched: true,
      isFetchedAfterMount: true,
      isFetching: false,
      isPaused: false,
      isPending: false,
      refetch: vi.fn(),
      remove: vi.fn(),
    } as any);

    renderComponent();

    await waitFor(() => {
      expect(
        screen.getByText(/No payments found/i)
      ).toBeInTheDocument();
    });
  });

  it("renders error state", () => {
    const mockError = new Error("Failed to load payments");
    vi.spyOn(useCustomerPaymentPortalModule, "useCustomerPayments").mockReturnValue({
      data: undefined,
      isLoading: false,
      error: mockError as any,
      isError: true,
      isSuccess: false,
      status: "error",
      dataUpdatedAt: 0,
      errorUpdatedAt: Date.now(),
      failureCount: 1,
      failureReason: mockError,
      isFetched: true,
      isFetchedAfterMount: true,
      isFetching: false,
      isPaused: false,
      isPending: false,
      refetch: vi.fn(),
      remove: vi.fn(),
    } as any);

    renderComponent();

    expect(
      screen.getByText(/Failed to load your payment history/i)
    ).toBeInTheDocument();
  });

  it("displays refund information when payment is refunded", async () => {
    const refundedPayment: CustomerPayment = {
      ...mockCustomerPayments[0],
      status: "refunded",
      refund_amount: 100,
    };

    vi.spyOn(useCustomerPaymentPortalModule, "useCustomerPayments").mockReturnValue({
      data: [refundedPayment],
      isLoading: false,
      error: null,
      isError: false,
      isSuccess: true,
      status: "success",
      dataUpdatedAt: Date.now(),
      errorUpdatedAt: 0,
      failureCount: 0,
      failureReason: null,
      isFetched: true,
      isFetchedAfterMount: true,
      isFetching: false,
      isPaused: false,
      isPending: false,
      refetch: vi.fn(),
      remove: vi.fn(),
    } as any);

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText(/Refunded: \$100.00/i)).toBeInTheDocument();
    });
  });
});
