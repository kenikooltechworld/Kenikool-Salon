import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BulkActionsToolbar } from "../BulkActionsToolbar";
import * as useBulkPaymentOperationsModule from "@/lib/api/hooks/useBulkPaymentOperations";
import { vi } from "vitest";
import type { Payment } from "@/lib/api/types";

const mockPayments: Payment[] = [
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
  },
];

describe("BulkActionsToolbar", () => {
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

  const renderComponent = (
    selectedPayments: Payment[] = [],
    onClearSelection = vi.fn()
  ) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BulkActionsToolbar
          selectedPayments={selectedPayments}
          onClearSelection={onClearSelection}
        />
      </QueryClientProvider>
    );
  };

  it("does not render when no payments are selected", () => {
    renderComponent([]);
    expect(screen.queryByText(/selected/i)).not.toBeInTheDocument();
  });

  it("renders toolbar when payments are selected", () => {
    renderComponent(mockPayments);
    expect(screen.getByText("2 payments selected")).toBeInTheDocument();
  });

  it("displays correct count for single payment", () => {
    renderComponent([mockPayments[0]]);
    expect(screen.getByText("1 payment selected")).toBeInTheDocument();
  });

  it("displays export button", () => {
    renderComponent(mockPayments);
    expect(screen.getByText("Export")).toBeInTheDocument();
  });

  it("displays status update dropdown", () => {
    renderComponent(mockPayments);
    expect(screen.getByPlaceholderText("Update status...")).toBeInTheDocument();
  });

  it("displays clear button", () => {
    renderComponent(mockPayments);
    expect(screen.getByText("Clear")).toBeInTheDocument();
  });

  it("calls onClearSelection when clear button is clicked", () => {
    const onClearSelection = vi.fn();
    renderComponent(mockPayments, onClearSelection);

    const clearButton = screen.getByText("Clear");
    fireEvent.click(clearButton);

    expect(onClearSelection).toHaveBeenCalled();
  });

  it("handles export action", async () => {
    const mockExport = vi.fn().mockResolvedValue(new Blob());
    vi.spyOn(useBulkPaymentOperationsModule, "useBulkExportPayments").mockReturnValue({
      mutate: mockExport,
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

    renderComponent(mockPayments);

    const exportButton = screen.getByText("Export");
    fireEvent.click(exportButton);

    await waitFor(() => {
      expect(mockExport).toHaveBeenCalled();
    });
  });

  it("handles status update action", async () => {
    const mockStatusUpdate = vi.fn().mockResolvedValue({
      success: true,
      message: "Updated",
      processed_count: 2,
      failed_count: 0,
    });

    vi.spyOn(useBulkPaymentOperationsModule, "useBulkStatusUpdate").mockReturnValue({
      mutate: mockStatusUpdate,
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

    renderComponent(mockPayments);

    // Select a status
    const statusSelect = screen.getByPlaceholderText("Update status...");
    fireEvent.click(statusSelect);

    const completedOption = screen.getByText("Completed");
    fireEvent.click(completedOption);

    // Click update button
    const updateButton = screen.getByText("Update Status");
    fireEvent.click(updateButton);

    await waitFor(() => {
      expect(mockStatusUpdate).toHaveBeenCalled();
    });
  });

  it("disables export button when export is pending", () => {
    vi.spyOn(useBulkPaymentOperationsModule, "useBulkExportPayments").mockReturnValue({
      mutate: vi.fn(),
      isPending: true,
      isError: false,
      isSuccess: false,
      data: undefined,
      error: null,
      status: "pending",
      reset: vi.fn(),
      mutateAsync: vi.fn(),
      failureCount: 0,
      failureReason: null,
      variables: undefined,
      context: undefined,
      submittedAt: 0,
    } as any);

    renderComponent(mockPayments);

    const exportButton = screen.getByText("Export");
    expect(exportButton).toBeDisabled();
  });

  it("displays error message on export failure", () => {
    const mockError = new Error("Export failed");
    vi.spyOn(useBulkPaymentOperationsModule, "useBulkExportPayments").mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      isError: true,
      isSuccess: false,
      data: undefined,
      error: mockError as any,
      status: "error",
      reset: vi.fn(),
      mutateAsync: vi.fn(),
      failureCount: 1,
      failureReason: mockError,
      variables: undefined,
      context: undefined,
      submittedAt: 0,
    } as any);

    renderComponent(mockPayments);

    expect(
      screen.getByText(/Failed to export payments/i)
    ).toBeInTheDocument();
  });

  it("displays success message on status update", () => {
    vi.spyOn(useBulkPaymentOperationsModule, "useBulkStatusUpdate").mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      isError: false,
      isSuccess: true,
      data: {
        success: true,
        message: "Updated",
        processed_count: 2,
        failed_count: 0,
      },
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

    renderComponent(mockPayments);

    expect(
      screen.getByText(/Successfully updated 2 payment/i)
    ).toBeInTheDocument();
  });
});
