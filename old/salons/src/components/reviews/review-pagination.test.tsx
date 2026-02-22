import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ReviewPagination } from "./review-pagination";

describe("ReviewPagination Component", () => {
  const mockOnPageChange = jest.fn();
  const mockOnPageSizeChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders pagination controls", () => {
    render(
      <ReviewPagination
        currentPage={1}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    expect(screen.getByText(/Showing 1-20 of 100 reviews/)).toBeInTheDocument();
  });

  it("displays correct item range", () => {
    render(
      <ReviewPagination
        currentPage={2}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    expect(screen.getByText(/Showing 21-40 of 100 reviews/)).toBeInTheDocument();
  });

  it("displays correct item range on last page", () => {
    render(
      <ReviewPagination
        currentPage={5}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    expect(screen.getByText(/Showing 81-100 of 100 reviews/)).toBeInTheDocument();
  });

  it("calls onPageChange when next button is clicked", () => {
    render(
      <ReviewPagination
        currentPage={1}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const nextButton = screen.getByTitle("Next page");
    fireEvent.click(nextButton);

    expect(mockOnPageChange).toHaveBeenCalledWith(2);
  });

  it("calls onPageChange when previous button is clicked", () => {
    render(
      <ReviewPagination
        currentPage={2}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const prevButton = screen.getByTitle("Previous page");
    fireEvent.click(prevButton);

    expect(mockOnPageChange).toHaveBeenCalledWith(1);
  });

  it("disables previous button on first page", () => {
    render(
      <ReviewPagination
        currentPage={1}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const prevButton = screen.getByTitle("Previous page");
    expect(prevButton).toBeDisabled();
  });

  it("disables next button on last page", () => {
    render(
      <ReviewPagination
        currentPage={5}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const nextButton = screen.getByTitle("Next page");
    expect(nextButton).toBeDisabled();
  });

  it("calls onPageChange when page number is clicked", () => {
    render(
      <ReviewPagination
        currentPage={1}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const page3Button = screen.getByRole("button", { name: "3" });
    fireEvent.click(page3Button);

    expect(mockOnPageChange).toHaveBeenCalledWith(3);
  });

  it("highlights current page", () => {
    render(
      <ReviewPagination
        currentPage={2}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const page2Button = screen.getByRole("button", { name: "2" });
    expect(page2Button).toHaveClass("bg-primary");
  });

  it("calls onPageChange when first page button is clicked", () => {
    render(
      <ReviewPagination
        currentPage={3}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const firstButton = screen.getByTitle("First page");
    fireEvent.click(firstButton);

    expect(mockOnPageChange).toHaveBeenCalledWith(1);
  });

  it("calls onPageChange when last page button is clicked", () => {
    render(
      <ReviewPagination
        currentPage={1}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const lastButton = screen.getByTitle("Last page");
    fireEvent.click(lastButton);

    expect(mockOnPageChange).toHaveBeenCalledWith(5);
  });

  it("changes page size and resets to first page", async () => {
    render(
      <ReviewPagination
        currentPage={2}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const pageSizeSelect = screen.getByDisplayValue("20");
    await userEvent.click(pageSizeSelect);

    const option50 = screen.getByRole("option", { name: "50" });
    await userEvent.click(option50);

    expect(mockOnPageSizeChange).toHaveBeenCalledWith(50);
    expect(mockOnPageChange).toHaveBeenCalledWith(1);
  });

  it("allows jumping to a specific page", async () => {
    render(
      <ReviewPagination
        currentPage={1}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const jumpInput = screen.getByPlaceholderText("1-5");
    await userEvent.type(jumpInput, "3");

    const goButton = screen.getByRole("button", { name: "Go" });
    fireEvent.click(goButton);

    expect(mockOnPageChange).toHaveBeenCalledWith(3);
  });

  it("jumps to page on Enter key", async () => {
    render(
      <ReviewPagination
        currentPage={1}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const jumpInput = screen.getByPlaceholderText("1-5");
    await userEvent.type(jumpInput, "3");
    fireEvent.keyPress(jumpInput, { key: "Enter", code: "Enter" });

    expect(mockOnPageChange).toHaveBeenCalledWith(3);
  });

  it("disables go button when jump input is empty", () => {
    render(
      <ReviewPagination
        currentPage={1}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const goButton = screen.getByRole("button", { name: "Go" });
    expect(goButton).toBeDisabled();
  });

  it("displays page info", () => {
    render(
      <ReviewPagination
        currentPage={2}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    expect(screen.getByText(/Page 2 of 5/)).toBeInTheDocument();
  });

  it("returns null when totalCount is 0", () => {
    const { container } = render(
      <ReviewPagination
        currentPage={1}
        pageSize={20}
        totalCount={0}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  it("disables controls when isLoading is true", () => {
    render(
      <ReviewPagination
        currentPage={1}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
        isLoading={true}
      />
    );

    const nextButton = screen.getByTitle("Next page");
    const pageSizeSelect = screen.getByDisplayValue("20");
    const jumpInput = screen.getByPlaceholderText("1-5");

    expect(nextButton).toBeDisabled();
    expect(pageSizeSelect).toBeDisabled();
    expect(jumpInput).toBeDisabled();
  });

  it("displays all page size options", async () => {
    render(
      <ReviewPagination
        currentPage={1}
        pageSize={20}
        totalCount={100}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const pageSizeSelect = screen.getByDisplayValue("20");
    await userEvent.click(pageSizeSelect);

    expect(screen.getByRole("option", { name: "10" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "20" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "50" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "100" })).toBeInTheDocument();
  });

  it("handles large page numbers correctly", () => {
    render(
      <ReviewPagination
        currentPage={50}
        pageSize={20}
        totalCount={1000}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    expect(screen.getByText(/Showing 981-1000 of 1000 reviews/)).toBeInTheDocument();
    expect(screen.getByText(/Page 50 of 50/)).toBeInTheDocument();
  });

  it("shows ellipsis for large page ranges", () => {
    render(
      <ReviewPagination
        currentPage={1}
        pageSize={20}
        totalCount={1000}
        onPageChange={mockOnPageChange}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    // Should show ellipsis between page numbers
    const ellipsis = screen.getAllByText("...");
    expect(ellipsis.length).toBeGreaterThan(0);
  });
});
