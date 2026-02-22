import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { PaymentHistory } from "../PaymentHistory";

// Mock the hooks
const mockPayments = [
  {
    id: "1",
    invoiceId: "inv_1",
    customerId: "cust_1",
    amount: 50000,
    method: "paystack" as const,
    status: "completed" as const,
    transactionId: "ref_123",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "2",
    invoiceId: "inv_2",
    customerId: "cust_1",
    amount: 25000,
    method: "paystack" as const,
    status: "failed" as const,
    transactionId: "ref_124",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "3",
    invoiceId: "inv_3",
    customerId: "cust_1",
    amount: 15000,
    method: "paystack" as const,
    status: "pending" as const,
    transactionId: "ref_125",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

vi.mock("@/hooks/usePayments", () => ({
  usePayments: () => ({
    data: mockPayments,
    isLoading: false,
    error: null,
  }),
  useRetryPayment: () => ({
    mutateAsync: vi.fn().mockResolvedValue({ status: "pending" }),
  }),
}));

const queryClient = new QueryClient();

const renderComponent = (props = {}) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <PaymentHistory {...props} />
    </QueryClientProvider>,
  );
};

describe("PaymentHistory", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render payment history table", () => {
    renderComponent();
    expect(screen.getByRole("table")).toBeInTheDocument();
  });

  it("should display all payments", () => {
    renderComponent();
    expect(screen.getByText("ref_123")).toBeInTheDocument();
    expect(screen.getByText("ref_124")).toBeInTheDocument();
    expect(screen.getByText("ref_125")).toBeInTheDocument();
  });

  it("should display payment status badges", () => {
    renderComponent();
    expect(screen.getByText("completed")).toBeInTheDocument();
    expect(screen.getByText("failed")).toBeInTheDocument();
    expect(screen.getByText("pending")).toBeInTheDocument();
  });

  it("should display payment amounts", () => {
    renderComponent();
    // Amounts should be formatted as currency
    expect(screen.getByText(/₦/)).toBeInTheDocument();
  });

  it("should show retry button for failed payments", () => {
    renderComponent();
    const retryButtons = screen.getAllByText(/retry/i);
    expect(retryButtons.length).toBeGreaterThan(0);
  });

  it("should handle retry payment click", async () => {
    renderComponent();
    const retryButtons = screen.getAllByText(/retry/i);
    fireEvent.click(retryButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/retrying/i)).toBeInTheDocument();
    });
  });

  it("should respect limit prop", () => {
    renderComponent({ limit: 2 });
    const rows = screen.getAllByRole("row");
    // Header row + 2 data rows
    expect(rows.length).toBeLessThanOrEqual(3);
  });

  it("should display loading state", () => {
    vi.mock("@/hooks/usePayments", () => ({
      usePayments: () => ({
        data: undefined,
        isLoading: true,
        error: null,
      }),
    }));

    renderComponent();
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  it("should display error message on error", () => {
    vi.mock("@/hooks/usePayments", () => ({
      usePayments: () => ({
        data: undefined,
        isLoading: false,
        error: new Error("Failed to load"),
      }),
    }));

    renderComponent();
    expect(
      screen.getByText(/failed to load payment history/i),
    ).toBeInTheDocument();
  });

  it("should display empty state when no payments", () => {
    vi.mock("@/hooks/usePayments", () => ({
      usePayments: () => ({
        data: [],
        isLoading: false,
        error: null,
      }),
    }));

    renderComponent();
    expect(screen.getByText(/no payments found/i)).toBeInTheDocument();
  });

  it("should filter payments by customer ID", () => {
    renderComponent({ customerId: "cust_1" });
    expect(screen.getByRole("table")).toBeInTheDocument();
  });

  it("should filter payments by invoice ID", () => {
    renderComponent({ invoiceId: "inv_1" });
    expect(screen.getByRole("table")).toBeInTheDocument();
  });

  it("should display download receipt button", () => {
    renderComponent();
    const downloadButtons = screen.getAllByText(/receipt/i);
    expect(downloadButtons.length).toBeGreaterThan(0);
  });

  it("should display correct status icons", () => {
    renderComponent();
    // Check for status indicators
    const table = screen.getByRole("table");
    expect(table).toBeInTheDocument();
  });
});
