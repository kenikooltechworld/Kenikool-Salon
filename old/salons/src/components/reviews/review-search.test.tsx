import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ReviewSearch } from "./review-search";

describe("ReviewSearch Component", () => {
  it("renders search input with placeholder", () => {
    const mockOnSearch = jest.fn();
    render(<ReviewSearch onSearch={mockOnSearch} />);

    const input = screen.getByPlaceholderText(
      /search reviews by client name/i
    );
    expect(input).toBeInTheDocument();
  });

  it("calls onSearch with debounced query", async () => {
    const mockOnSearch = jest.fn();
    render(<ReviewSearch onSearch={mockOnSearch} />);

    const input = screen.getByPlaceholderText(
      /search reviews by client name/i
    ) as HTMLInputElement;

    await userEvent.type(input, "excellent");

    // Wait for debounce (300ms)
    await waitFor(
      () => {
        expect(mockOnSearch).toHaveBeenCalledWith("excellent");
      },
      { timeout: 500 }
    );
  });

  it("shows clear button when search query is present", async () => {
    const mockOnSearch = jest.fn();
    render(<ReviewSearch onSearch={mockOnSearch} />);

    const input = screen.getByPlaceholderText(
      /search reviews by client name/i
    ) as HTMLInputElement;

    await userEvent.type(input, "test");

    await waitFor(() => {
      const clearButton = screen.getByLabelText("Clear search");
      expect(clearButton).toBeInTheDocument();
    });
  });

  it("clears search when clear button is clicked", async () => {
    const mockOnSearch = jest.fn();
    render(<ReviewSearch onSearch={mockOnSearch} />);

    const input = screen.getByPlaceholderText(
      /search reviews by client name/i
    ) as HTMLInputElement;

    await userEvent.type(input, "test");

    await waitFor(() => {
      const clearButton = screen.getByLabelText("Clear search");
      fireEvent.click(clearButton);
    });

    expect(input.value).toBe("");
    expect(mockOnSearch).toHaveBeenCalledWith("");
  });

  it("displays result count when provided", async () => {
    const mockOnSearch = jest.fn();
    render(
      <ReviewSearch onSearch={mockOnSearch} resultCount={5} />
    );

    const input = screen.getByPlaceholderText(
      /search reviews by client name/i
    ) as HTMLInputElement;

    await userEvent.type(input, "test");

    await waitFor(() => {
      expect(screen.getByText(/Found/)).toBeInTheDocument();
      expect(screen.getByText("5")).toBeInTheDocument();
    });
  });

  it("shows loading indicator when isLoading is true", () => {
    const mockOnSearch = jest.fn();
    render(<ReviewSearch onSearch={mockOnSearch} isLoading={true} />);

    expect(screen.getByText("Searching...")).toBeInTheDocument();
  });

  it("disables input when isLoading is true", () => {
    const mockOnSearch = jest.fn();
    render(<ReviewSearch onSearch={mockOnSearch} isLoading={true} />);

    const input = screen.getByPlaceholderText(
      /search reviews by client name/i
    ) as HTMLInputElement;
    expect(input).toBeDisabled();
  });

  it("uses custom placeholder when provided", () => {
    const mockOnSearch = jest.fn();
    const customPlaceholder = "Search by name...";
    render(
      <ReviewSearch
        onSearch={mockOnSearch}
        placeholder={customPlaceholder}
      />
    );

    expect(screen.getByPlaceholderText(customPlaceholder)).toBeInTheDocument();
  });

  it("debounces multiple rapid inputs", async () => {
    const mockOnSearch = jest.fn();
    render(<ReviewSearch onSearch={mockOnSearch} />);

    const input = screen.getByPlaceholderText(
      /search reviews by client name/i
    ) as HTMLInputElement;

    // Type multiple characters rapidly
    await userEvent.type(input, "test", { delay: 50 });

    // Should only call once after debounce
    await waitFor(
      () => {
        expect(mockOnSearch).toHaveBeenCalledTimes(1);
        expect(mockOnSearch).toHaveBeenCalledWith("test");
      },
      { timeout: 500 }
    );
  });

  it("handles empty search query", async () => {
    const mockOnSearch = jest.fn();
    render(<ReviewSearch onSearch={mockOnSearch} />);

    const input = screen.getByPlaceholderText(
      /search reviews by client name/i
    ) as HTMLInputElement;

    await userEvent.type(input, "test");
    await userEvent.clear(input);

    await waitFor(
      () => {
        expect(mockOnSearch).toHaveBeenCalledWith("");
      },
      { timeout: 500 }
    );
  });
});
