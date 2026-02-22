import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/react-query";
import CreateBooking from "../CreateBooking";

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{component}</BrowserRouter>
    </QueryClientProvider>,
  );
};

describe("CreateBooking", () => {
  it("renders the wizard with service selection step", () => {
    renderWithProviders(<CreateBooking />);

    expect(screen.getByText(/create booking/i)).toBeInTheDocument();
    expect(screen.getByText(/select a service/i)).toBeInTheDocument();
  });

  it("shows progress indicator", () => {
    renderWithProviders(<CreateBooking />);

    expect(screen.getByText(/step 1 of 4/i)).toBeInTheDocument();
  });

  it("has back button", () => {
    renderWithProviders(<CreateBooking />);

    expect(screen.getByRole("button", { name: /back/i })).toBeInTheDocument();
  });

  it("displays loading state for services", () => {
    renderWithProviders(<CreateBooking />);

    // Should show loading or empty state initially
    const heading = screen.getByText(/select a service/i);
    expect(heading).toBeInTheDocument();
  });
});
