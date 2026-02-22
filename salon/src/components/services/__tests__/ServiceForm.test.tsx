import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/react-query";
import { ServiceForm } from "../ServiceForm";

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>{component}</QueryClientProvider>,
  );
};

describe("ServiceForm", () => {
  it("renders form fields", () => {
    renderWithProviders(
      <ServiceForm onSuccess={() => {}} onCancel={() => {}} />,
    );

    expect(screen.getByPlaceholderText(/service name/i)).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/service description/i),
    ).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/e\.g\., hair/i)).toBeInTheDocument();
  });

  it("shows create button for new service", () => {
    renderWithProviders(
      <ServiceForm onSuccess={() => {}} onCancel={() => {}} />,
    );

    expect(
      screen.getByRole("button", { name: /create service/i }),
    ).toBeInTheDocument();
  });

  it("shows update button for existing service", () => {
    const mockService = {
      id: "1",
      name: "Haircut",
      description: "Professional haircut",
      duration: 30,
      price: 5000,
      category: "Hair",
      isActive: true,
      isPublished: true,
      createdAt: "2026-02-14T10:00:00Z",
      updatedAt: "2026-02-14T10:00:00Z",
    };

    renderWithProviders(
      <ServiceForm
        service={mockService}
        onSuccess={() => {}}
        onCancel={() => {}}
      />,
    );

    expect(
      screen.getByRole("button", { name: /update service/i }),
    ).toBeInTheDocument();
  });

  it("calls onCancel when cancel button is clicked", async () => {
    const onCancel = vi.fn();
    const user = userEvent.setup();

    renderWithProviders(
      <ServiceForm onSuccess={() => {}} onCancel={onCancel} />,
    );

    const cancelButton = screen.getByRole("button", { name: /cancel/i });
    await user.click(cancelButton);

    expect(onCancel).toHaveBeenCalled();
  });

  it("validates required fields", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <ServiceForm onSuccess={() => {}} onCancel={() => {}} />,
    );

    const submitButton = screen.getByRole("button", {
      name: /create service/i,
    });
    await user.click(submitButton);

    // Form should not submit without required fields
    const nameInput = screen.getByPlaceholderText(
      /service name/i,
    ) as HTMLInputElement;
    expect(nameInput.validity.valid).toBe(false);
  });
});
