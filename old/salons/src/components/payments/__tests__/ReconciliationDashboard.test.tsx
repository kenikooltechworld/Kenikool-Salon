import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReconciliationDashboard } from "../ReconciliationDashboard";
import * as useReconciliationModule from "@/lib/api/hooks/useReconciliation";
import { vi } from "vitest";
import type { UnmatchedPayment } from "@/lib/api/hooks/useReconciliation";

const mockUnmatchedPayment: UnmatchedPayment = {
  id: "1",
  tenant_id: "tenant-1",
  booking_id: "",
  amount: 100,
  gateway: "paystack",
  reference: "REF001",
  status: "completed",
  payment_type: "full",
  created_at: "2024-01-01",
  updated_at: "2024-01-01",
  discrepancy_type: "unmatched",
};

const mockMismatchedPayment: UnmatchedPayment = {
  id: "2",
  tenant_id: "tenant-1",
  booking_id: "booking-1",
  amount: 100,
  gateway: "paystack",
  reference: "REF002",
  status: "completed",
  payment_type: "full",
  created_at: "2024-01-02",
  updated_at: "2024-01-02",
  discrepancy_type: "amount_mismatch",
  gateway_amount: 150,
};

const mockReconciliationData = {
  unmatched_payments: [mockUnmatchedPayment],
  mismatched_amounts: [mockMismatchedPayment],
  duplicate_payments: [],
  gateway_sync_status: {
    paystack: "synced",
    flutterwave: "pending",
  },
  total_unmatched: 1,
  total_mismatched: 1,
  total_duplicates: 0,
};

describe("ReconciliationDashboard", () => {
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
        <ReconciliationDashboard />
      </QueryClientProvider>
    );
  };

  it("renders loading state initially", () => {
    vi.spyOn(useReconciliationModule, "useReconciliationData").mockReturnValue({
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
    expect(screen.getByText("Payment Reconciliation")).toBeInTheDocument();
  });

  it("renders reconciliation data when loaded", async () => {
    vi.spyOn(useReconciliationModule, "useReconciliationData").mockReturnValue({
      data: mockReconciliationData,
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
      expect(screen.getByText("1")).toBeInTheDocument();
    });
  });

  it("displays summary cards", async () => {
    vi.spyOn(useReconciliationModule, "useReconciliationData").mockReturnValue({
      data: mockReconciliationData,
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
      expect(screen.getByText("Unmatched Payments")).toBeInTheDocument();
      expect(screen.getByText("Amount Mismatches")).toBeInTheDocument();
      expect(screen.getByText("Duplicate Payments")).toBeInTheDocument();
    });
  });

  it("displays unmatched payments section", async () => {
    vi.spyOn(useReconciliationModule, "useReconciliationData").mockReturnValue({
      data: mockReconciliationData,
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
      expect(screen.getByText("REF001")).toBeInTheDocument();
      expect(screen.getByText("$100.00 • paystack")).toBeInTheDocument();
    });
  });

  it("displays mismatched amounts section", async () => {
    vi.spyOn(useReconciliationModule, "useReconciliationData").mockReturnValue({
      data: mockReconciliationData,
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
      expect(screen.getByText("Amount Mismatches")).toBeInTheDocument();
      expect(screen.getByText("REF002")).toBeInTheDocument();
    });
  });

  it("handles manual match action", async () => {
    const mockMatch = vi.fn().mockResolvedValue({
      id: "1",
      booking_id: "booking-1",
    });

    vi.spyOn(useReconciliationModule, "useManualMatchPayment").mockReturnValue({
      mutate: mockMatch,
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

    vi.spyOn(useReconciliationModule, "useReconciliationData").mockReturnValue({
      data: mockReconciliationData,
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
      const matchButtons = screen.getAllByText("Match");
      fireEvent.click(matchButtons[0]);
    });
  });

  it("handles sync with gateway action", async () => {
    const mockSync = vi.fn().mockResolvedValue({
      id: "2",
      gateway_sync_status: "synced",
    });

    vi.spyOn(useReconciliationModule, "useSyncWithGateway").mockReturnValue({
      mutate: mockSync,
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

    vi.spyOn(useReconciliationModule, "useReconciliationData").mockReturnValue({
      data: mockReconciliationData,
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
      const syncButtons = screen.getAllByText("Sync");
      fireEvent.click(syncButtons[0]);
    });
  });

  it("renders error state", () => {
    const mockError = new Error("Failed to load reconciliation data");
    vi.spyOn(useReconciliationModule, "useReconciliationData").mockReturnValue({
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
      screen.getByText(/Failed to load reconciliation data/i)
    ).toBeInTheDocument();
  });

  it("displays success message on successful match", () => {
    vi.spyOn(useReconciliationModule, "useManualMatchPayment").mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      isError: false,
      isSuccess: true,
      data: { id: "1", booking_id: "booking-1" } as any,
      error: null,
      status: "success",
      reset: vi.fn(),
      mutateAsync: vi.fn(),
      failureCount: 0,
      failureReason: null,
      variables: undefined,
      context: undefined,
      submittedAt: 0,
    } as any);

    vi.spyOn(useReconciliationModule, "useReconciliationData").mockReturnValue({
      data: mockReconciliationData,
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

    expect(
      screen.getByText(/Payment successfully matched to booking/i)
    ).toBeInTheDocument();
  });
});
