import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ReviewSort, SortBy, SortOrder } from "./review-sort";

describe("ReviewSort Component", () => {
  it("renders sort controls", () => {
    const mockOnSortChange = jest.fn();
    render(<ReviewSort onSortChange={mockOnSortChange} />);

    expect(screen.getByText("Sort by:")).toBeInTheDocument();
    expect(screen.getByText(/Date/)).toBeInTheDocument();
  });

  it("displays default sort option", () => {
    const mockOnSortChange = jest.fn();
    render(<ReviewSort onSortChange={mockOnSortChange} />);

    expect(screen.getByText(/Date \(Descending\)/)).toBeInTheDocument();
  });

  it("calls onSortChange when sort field is changed", async () => {
    const mockOnSortChange = jest.fn();
    render(<ReviewSort onSortChange={mockOnSortChange} />);

    const sortByTrigger = screen.getAllByRole("combobox")[0];
    await userEvent.click(sortByTrigger);

    const ratingOption = screen.getByText("Rating");
    await userEvent.click(ratingOption);

    expect(mockOnSortChange).toHaveBeenCalledWith("rating", "desc");
  });

  it("calls onSortChange when sort order is changed", async () => {
    const mockOnSortChange = jest.fn();
    render(<ReviewSort onSortChange={mockOnSortChange} />);

    const sortOrderTrigger = screen.getAllByRole("combobox")[1];
    await userEvent.click(sortOrderTrigger);

    const ascendingOption = screen.getByText("Ascending");
    await userEvent.click(ascendingOption);

    expect(mockOnSortChange).toHaveBeenCalledWith("created_at", "asc");
  });

  it("displays all sort options", async () => {
    const mockOnSortChange = jest.fn();
    render(<ReviewSort onSortChange={mockOnSortChange} />);

    const sortByTrigger = screen.getAllByRole("combobox")[0];
    await userEvent.click(sortByTrigger);

    expect(screen.getByText("Date")).toBeInTheDocument();
    expect(screen.getByText("Rating")).toBeInTheDocument();
    expect(screen.getByText("Status")).toBeInTheDocument();
    expect(screen.getByText("Helpfulness")).toBeInTheDocument();
  });

  it("displays all sort order options", async () => {
    const mockOnSortChange = jest.fn();
    render(<ReviewSort onSortChange={mockOnSortChange} />);

    const sortOrderTrigger = screen.getAllByRole("combobox")[1];
    await userEvent.click(sortOrderTrigger);

    expect(screen.getByText("Descending")).toBeInTheDocument();
    expect(screen.getByText("Ascending")).toBeInTheDocument();
  });

  it("respects currentSortBy prop", () => {
    const mockOnSortChange = jest.fn();
    render(
      <ReviewSort
        onSortChange={mockOnSortChange}
        currentSortBy="rating"
        currentSortOrder="desc"
      />
    );

    expect(screen.getByText(/Rating \(Descending\)/)).toBeInTheDocument();
  });

  it("respects currentSortOrder prop", () => {
    const mockOnSortChange = jest.fn();
    render(
      <ReviewSort
        onSortChange={mockOnSortChange}
        currentSortBy="created_at"
        currentSortOrder="asc"
      />
    );

    expect(screen.getByText(/Date \(Ascending\)/)).toBeInTheDocument();
  });

  it("maintains sort order when changing sort field", async () => {
    const mockOnSortChange = jest.fn();
    render(
      <ReviewSort
        onSortChange={mockOnSortChange}
        currentSortBy="created_at"
        currentSortOrder="asc"
      />
    );

    const sortByTrigger = screen.getAllByRole("combobox")[0];
    await userEvent.click(sortByTrigger);

    const ratingOption = screen.getByText("Rating");
    await userEvent.click(ratingOption);

    expect(mockOnSortChange).toHaveBeenCalledWith("rating", "asc");
  });

  it("maintains sort field when changing sort order", async () => {
    const mockOnSortChange = jest.fn();
    render(
      <ReviewSort
        onSortChange={mockOnSortChange}
        currentSortBy="rating"
        currentSortOrder="desc"
      />
    );

    const sortOrderTrigger = screen.getAllByRole("combobox")[1];
    await userEvent.click(sortOrderTrigger);

    const ascendingOption = screen.getByText("Ascending");
    await userEvent.click(ascendingOption);

    expect(mockOnSortChange).toHaveBeenCalledWith("rating", "asc");
  });

  it("displays sort descriptions in dropdown", async () => {
    const mockOnSortChange = jest.fn();
    render(<ReviewSort onSortChange={mockOnSortChange} />);

    const sortByTrigger = screen.getAllByRole("combobox")[0];
    await userEvent.click(sortByTrigger);

    expect(screen.getByText("Sort by review date")).toBeInTheDocument();
    expect(screen.getByText("Sort by star rating")).toBeInTheDocument();
    expect(screen.getByText("Sort by approval status")).toBeInTheDocument();
    expect(screen.getByText("Sort by helpful votes")).toBeInTheDocument();
  });

  it("displays order descriptions in dropdown", async () => {
    const mockOnSortChange = jest.fn();
    render(<ReviewSort onSortChange={mockOnSortChange} />);

    const sortOrderTrigger = screen.getAllByRole("combobox")[1];
    await userEvent.click(sortOrderTrigger);

    expect(screen.getByText("Highest to lowest")).toBeInTheDocument();
    expect(screen.getByText("Lowest to highest")).toBeInTheDocument();
  });
});
