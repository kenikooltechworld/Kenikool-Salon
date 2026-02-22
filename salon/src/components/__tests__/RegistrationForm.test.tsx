import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { RegistrationForm } from "../RegistrationForm";

describe("RegistrationForm", () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it("renders all form fields", () => {
    render(<RegistrationForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/salon name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/owner name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/phone/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/bank account/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/referral code/i)).toBeInTheDocument();
  });

  it("shows error for invalid email", async () => {
    const user = userEvent.setup();
    render(<RegistrationForm onSubmit={mockOnSubmit} />);

    const emailInput = screen.getByLabelText(/email/i);
    await user.type(emailInput, "invalid-email");
    await user.tab();

    expect(screen.getByText(/invalid email format/i)).toBeInTheDocument();
  });

  it("shows error for invalid phone", async () => {
    const user = userEvent.setup();
    render(<RegistrationForm onSubmit={mockOnSubmit} />);

    const phoneInput = screen.getByLabelText(/phone/i);
    await user.type(phoneInput, "123");
    await user.tab();

    expect(screen.getByText(/invalid phone format/i)).toBeInTheDocument();
  });

  it("shows error for short salon name", async () => {
    const user = userEvent.setup();
    render(<RegistrationForm onSubmit={mockOnSubmit} />);

    const salonInput = screen.getByLabelText(/salon name/i);
    await user.type(salonInput, "AB");
    await user.tab();

    expect(screen.getByText(/3-255 characters/i)).toBeInTheDocument();
  });

  it("shows error for weak password", async () => {
    const user = userEvent.setup();
    render(<RegistrationForm onSubmit={mockOnSubmit} />);

    const passwordInput = screen.getByLabelText(/password/i);
    await user.type(passwordInput, "weak");
    await user.tab();

    expect(screen.getByText(/at least 12 characters/i)).toBeInTheDocument();
  });

  it("shows password strength indicator", async () => {
    const user = userEvent.setup();
    render(<RegistrationForm onSubmit={mockOnSubmit} />);

    const passwordInput = screen.getByLabelText(/password/i);
    await user.type(passwordInput, "SecurePass123!");

    expect(screen.getByText(/very strong/i)).toBeInTheDocument();
  });

  it("disables submit button when form has errors", async () => {
    const user = userEvent.setup();
    render(<RegistrationForm onSubmit={mockOnSubmit} />);

    const emailInput = screen.getByLabelText(/email/i);
    await user.type(emailInput, "invalid-email");
    await user.tab();

    const submitButton = screen.getByRole("button", {
      name: /create account/i,
    });
    expect(submitButton).toBeDisabled();
  });

  it("calls onSubmit with valid data", async () => {
    const user = userEvent.setup();
    render(<RegistrationForm onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/salon name/i), "Test Salon");
    await user.type(screen.getByLabelText(/owner name/i), "John Doe");
    await user.type(screen.getByLabelText(/email/i), "john@example.com");
    await user.type(screen.getByLabelText(/phone/i), "+234 123 456 7890");
    await user.type(screen.getByLabelText(/password/i), "SecurePass123!");
    await user.type(screen.getByLabelText(/address/i), "123 Main St, Lagos");

    const submitButton = screen.getByRole("button", {
      name: /create account/i,
    });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          salon_name: "Test Salon",
          owner_name: "John Doe",
          email: "john@example.com",
          phone: "+234 123 456 7890",
          password: "SecurePass123!",
          address: "123 Main St, Lagos",
        }),
      );
    });
  });

  it("shows loading state during submission", async () => {
    const user = userEvent.setup();
    const slowSubmit = vi.fn(
      () => new Promise((resolve) => setTimeout(resolve, 100)),
    );
    render(<RegistrationForm onSubmit={slowSubmit} />);

    await user.type(screen.getByLabelText(/salon name/i), "Test Salon");
    await user.type(screen.getByLabelText(/owner name/i), "John Doe");
    await user.type(screen.getByLabelText(/email/i), "john@example.com");
    await user.type(screen.getByLabelText(/phone/i), "+234 123 456 7890");
    await user.type(screen.getByLabelText(/password/i), "SecurePass123!");
    await user.type(screen.getByLabelText(/address/i), "123 Main St, Lagos");

    const submitButton = screen.getByRole("button", {
      name: /create account/i,
    });
    await user.click(submitButton);

    expect(screen.getByText(/creating account/i)).toBeInTheDocument();
  });

  it("displays error message", () => {
    render(
      <RegistrationForm onSubmit={mockOnSubmit} error="Registration failed" />,
    );

    expect(screen.getByText(/registration failed/i)).toBeInTheDocument();
  });

  it("disables form during loading", () => {
    render(<RegistrationForm onSubmit={mockOnSubmit} isLoading={true} />);

    expect(screen.getByLabelText(/salon name/i)).toBeDisabled();
    expect(screen.getByLabelText(/email/i)).toBeDisabled();
    expect(screen.getByLabelText(/password/i)).toBeDisabled();
  });
});
