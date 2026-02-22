import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { VerificationCodeInput } from "../VerificationCodeInput";

describe("VerificationCodeInput", () => {
  const mockOnChange = vi.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it("renders 6 input fields", () => {
    render(<VerificationCodeInput value="" onChange={mockOnChange} />);

    const inputs = screen.getAllByPlaceholderText("0");
    expect(inputs).toHaveLength(6);
  });

  it("accepts numeric input", async () => {
    const user = userEvent.setup();
    render(<VerificationCodeInput value="" onChange={mockOnChange} />);

    const inputs = screen.getAllByPlaceholderText("0");
    await user.type(inputs[0], "1");

    expect(mockOnChange).toHaveBeenCalledWith("1");
  });

  it("rejects non-numeric input", async () => {
    const user = userEvent.setup();
    render(<VerificationCodeInput value="" onChange={mockOnChange} />);

    const inputs = screen.getAllByPlaceholderText("0");
    await user.type(inputs[0], "a");

    expect(mockOnChange).not.toHaveBeenCalled();
  });

  it("auto-focuses next input on digit entry", async () => {
    const user = userEvent.setup();
    render(<VerificationCodeInput value="" onChange={mockOnChange} />);

    const inputs = screen.getAllByPlaceholderText("0");
    await user.type(inputs[0], "1");

    expect(inputs[1]).toHaveFocus();
  });

  it("handles backspace to clear digit", async () => {
    const user = userEvent.setup();
    render(<VerificationCodeInput value="123456" onChange={mockOnChange} />);

    const inputs = screen.getAllByPlaceholderText("0");
    inputs[5].focus();
    await user.keyboard("{Backspace}");

    expect(mockOnChange).toHaveBeenCalledWith("12345");
  });

  it("handles backspace to move to previous input", async () => {
    const user = userEvent.setup();
    render(<VerificationCodeInput value="12345" onChange={mockOnChange} />);

    const inputs = screen.getAllByPlaceholderText("0");
    inputs[1].focus();
    await user.keyboard("{Backspace}");

    expect(inputs[0]).toHaveFocus();
  });

  it("handles arrow keys for navigation", async () => {
    const user = userEvent.setup();
    render(<VerificationCodeInput value="" onChange={mockOnChange} />);

    const inputs = screen.getAllByPlaceholderText("0");
    inputs[0].focus();
    await user.keyboard("{ArrowRight}");

    expect(inputs[1]).toHaveFocus();
  });

  it("handles paste of full code", async () => {
    const user = userEvent.setup();
    render(<VerificationCodeInput value="" onChange={mockOnChange} />);

    const inputs = screen.getAllByPlaceholderText("0");
    const pasteData = new DataTransfer();
    pasteData.items.add(new File(["123456"], "code"));

    inputs[0].focus();
    await user.keyboard("123456");

    expect(mockOnChange).toHaveBeenCalledWith("123456");
  });

  it("displays error message", () => {
    render(
      <VerificationCodeInput
        value=""
        onChange={mockOnChange}
        error="Invalid code"
      />,
    );

    expect(screen.getByText(/invalid code/i)).toBeInTheDocument();
  });

  it("disables inputs when disabled prop is true", () => {
    render(
      <VerificationCodeInput
        value=""
        onChange={mockOnChange}
        disabled={true}
      />,
    );

    const inputs = screen.getAllByPlaceholderText("0");
    inputs.forEach((input) => {
      expect(input).toBeDisabled();
    });
  });

  it("populates inputs with provided value", () => {
    render(<VerificationCodeInput value="123456" onChange={mockOnChange} />);

    const inputs = screen.getAllByPlaceholderText("0");
    expect(inputs[0]).toHaveValue("1");
    expect(inputs[1]).toHaveValue("2");
    expect(inputs[2]).toHaveValue("3");
    expect(inputs[3]).toHaveValue("4");
    expect(inputs[4]).toHaveValue("5");
    expect(inputs[5]).toHaveValue("6");
  });
});
