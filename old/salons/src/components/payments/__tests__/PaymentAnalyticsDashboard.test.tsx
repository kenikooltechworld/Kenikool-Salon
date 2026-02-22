import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { PaymentAnalyticsDashboard } from "../PaymentAnalyticsDashboard";
import * as usePaymentAnalyticsModule from "@/lib/api/hooks/usePaymentAnalytics";
import { vi } from "vitest";

const mockAnalyticsData = {
  date_range: {
    from: "2024-01-01",
    to: "2024-01-31",
  },
  total_revenue: 5000,
  total_transactions: 50,
  average_payment: 100,
  revenue_trends: [
    { date: "2024-01-01", amount: 500, count: 5 },
    { date: "2024-01-02", amount: 600, count: 6 },
  ],
  payment_method_breakdown: [
    { method: "card", amount: 3000, count: 30, percentage: 0.6 },
    { method: "cash", amount: 2000, count: 20, percentage: 0.4 },
  ],
  gateway_breakdown: [
    { gateway: "paystack", amount: 3000, count: 30, success_rate: 0.95 },
    { gateway: "flutterwave", amount: 2000, count: 20, success_rate: 0.9 },
  ],
  payment_type_breakdown: [
    { type: "full", amount: 4000, count: 40 },
    { type: "deposit", amount: 1000, count: 10 },
  ],
  status_breakdown: {
    completed: 48,
    pending: 1,
    failed: 1,
  },
  total_refunded: 500,
  refund_count: 5,
  refund_rate: 0.1,
  failed_payment_count: 1,
  failed_payment_amount: 100,
  common_failure_reasons: [
    { reason: "Insufficient funds", count: 1 },
  ],
};

describe("PaymentAnalyticsDashboard", () => {
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

  const renderComponent = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <PaymentAnalyticsDashboard />
      </QueryClientProvider>
    );
  };

  it("renders loading state initially", () => {
    vi.spyOn(usePaymentAnalyticsModule, "usePaymentAnalytics").mockReturnValue({
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
    expect(screen.getByText("Payment Analytics")).toBeInTheDocument();
  });

  it("renders analytics data when loaded", async () => {
    vi.spyOn(usePaymentAnalyticsModule, "usePaymentAnalytics").mockReturnValue({
      data: mockAnalyticsData,
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
      expect(screen.getByText("$5000.00")).toBeInTheDocument();
      expect(screen.getByText("50")).toBeInTheDocument();
      expect(screen.getByText("$100.00")).toBeInTheDocument();
    });
  });

  it("displays key metrics cards", async () => {
    vi.spyOn(usePaymentAnalyticsModule, "usePaymentAnalytics").mockReturnValue({
      data: mockAnalyticsData,
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
      expect(screen.getByText("Total Revenue")).toBeInTheDocument();
      expect(screen.getByText("Transactions")).toBeInTheDocument();
      expect(screen.getByText("Average Payment")).toBeInTheDocument();
      expect(screen.getByText("Refund Rate")).toBeInTheDocument();
    });
  });

  it("displays gateway performance table", async () => {
    vi.spyOn(usePaymentAnalyticsModule, "usePaymentAnalytics").mockReturnValue({
      data: mockAnalyticsData,
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
      expect(screen.getByText("Gateway Performance")).toBeInTheDocument();
      expect(screen.getByText("paystack")).toBeInTheDocument();
      expect(screen.getByText("flutterwave")).toBeInTheDocument();
    });
  });

  it("displays failed payments analysis", async () => {
    vi.spyOn(usePaymentAnalyticsModule, "usePaymentAnalytics").mockReturnValue({
      data: mockAnalyticsData,
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
      expect(screen.getByText("Failed Payments Analysis")).toBeInTheDocument();
      expect(screen.getByText("Insufficient funds")).toBeInTheDocument();
    });
  });

  it("displays refund statistics", async () => {
    vi.spyOn(usePaymentAnalyticsModule, "usePaymentAnalytics").mockReturnValue({
      data: mockAnalyticsData,
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
      expect(screen.getByText("Refund Statistics")).toBeInTheDocument();
      expect(screen.getByText("$500.00")).toBeInTheDocument();
      expect(screen.getByText("5")).toBeInTheDocument();
    });
  });

  it("handles date range selection", async () => {
    const mockUsePaymentAnalytics = vi.spyOn(
      usePaymentAnalyticsModule,
      "usePaymentAnalytics"
    );
    mockUsePaymentAnalytics.mockReturnValue({
      data: mockAnalyticsData,
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

    const last7DaysButton = screen.getByText("Last 7 Days");
    fireEvent.click(last7DaysButton);

    await waitFor(() => {
      expect(mockUsePaymentAnalytics).toHaveBeenCalledWith(
        expect.objectContaining({
          period: "7days",
        }),
        expect.anything()
      );
    });
  });

  it("renders error state", () => {
    const mockError = new Error("Failed to load analytics");
    vi.spyOn(usePaymentAnalyticsModule, "usePaymentAnalytics").mockReturnValue({
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
      screen.getByText(/Failed to load payment analytics/i)
    ).toBeInTheDocument();
  });
});
