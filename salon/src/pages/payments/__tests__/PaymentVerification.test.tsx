import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import PaymentVerification from "../PaymentVerification";

// Mock the hooks
vi.mock("@/hooks/usePayments", () => ({
  useVerifyPayment: () => ({
    mutateAsync: vi.fn().mockResolvedValue({ status: "success" }),
  }),
}));

// Mock useSearchParams and useNavigate
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useSearchParams: () => [
      new URLSearchParams("reference=test_ref&invoice_id=inv_123"),
    ],
  };
});

const queryClient = new QueryClient();

const renderComponent = () => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <PaymentVerification />
      </BrowserRouter>
    </QueryClientProvider>,
  );
};

describe("PaymentVerification", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should display loading state initially", () => {
    renderComponent();
    expect(screen.getByText(/verifying your payment/i)).toBeInTheDocument();
  });

  it("should display success message after verification", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText(/payment successful/i)).toBeInTheDocument();
    });
  });

  it("should show success icon on successful verification", async () => {
    renderComponent();

    await waitFor(() => {
      const successIcon = screen.getByText(/payment successful/i);
      expect(successIcon).toBeInTheDocument();
    });
  });

  it("should redirect to invoice after successful verification", async () => {
    renderComponent();

    await waitFor(
      () => {
        expect(mockNavigate).toHaveBeenCalledWith("/invoices/inv_123");
      },
      { timeout: 4000 },
    );
  });

  it("should display error message if reference is missing", async () => {
    vi.mock("react-router-dom", async () => {
      const actual = await vi.importActual("react-router-dom");
      return {
        ...actual,
        useSearchParams: () => [new URLSearchParams("")],
      };
    });

    renderComponent();

    await waitFor(() => {
      expect(
        screen.getByText(/payment reference not found/i),
      ).toBeInTheDocument();
    });
  });

  it("should display retry button on failed verification", async () => {
    vi.mock("@/hooks/usePayments", () => ({
      useVerifyPayment: () => ({
        mutateAsync: vi
          .fn()
          .mockRejectedValue(new Error("Verification failed")),
      }),
    }));

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText(/retry payment/i)).toBeInTheDocument();
    });
  });

  it("should display back to invoices button", async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText(/back to invoices/i)).toBeInTheDocument();
    });
  });
});
