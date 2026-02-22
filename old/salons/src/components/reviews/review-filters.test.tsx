import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ReviewFilters, FilterStats } from "./review-filters";

describe("ReviewFilters Component", () => {
  const mockStats: FilterStats = {
    totalReviews: 100,
    byStatus: {
      pending: 30,
      approved: 50,
      rejected: 20,
    },
    byRating: {
      5: 40,
      4: 30,
      3: 15,
      2: 10,
      1: 5,
    },
    byService: {
      service1: 50,
      service2: 50,
    },
    byStylist: {
      stylist1: 60,
      stylist2: 40,
    },
    withResponse: 45,
    withPhotos: 30,
    flagged: 5,
  };

  const mockServices = [
    { id: "service1", name: "Haircut" },
    { id: "service2", name: "Color" },
  ];

  const mockStylists = [
    { id: "stylist1", name: "Alice" },
    { id: "stylist2", name: "Bob" },
  ];

  it("renders filter component with initial state", () => {
    const mockOnFilterChange = jest.fn();
    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    expect(screen.getByText("Filters")).toBeInTheDocument();
    expect(screen.getByText("Show")).toBeInTheDocument();
  });

  it("expands and collapses filter panel", async () => {
    const mockOnFilterChange = jest.fn();
    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    const showButton = screen.getByText("Show");
    fireEvent.click(showButton);

    await waitFor(() => {
      expect(screen.getByText("Status")).toBeInTheDocument();
      expect(screen.getByText("Rating")).toBeInTheDocument();
    });

    const hideButton = screen.getByText("Hide");
    fireEvent.click(hideButton);

    await waitFor(() => {
      expect(screen.queryByText("Status")).not.toBeInTheDocument();
    });
  });

  it("filters by status", async () => {
    const mockOnFilterChange = jest.fn();
    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    fireEvent.click(screen.getByText("Show"));

    await waitFor(() => {
      const pendingButton = screen.getByText(/Pending/);
      fireEvent.click(pendingButton);
    });

    expect(mockOnFilterChange).toHaveBeenCalledWith({
      status: "pending",
    });
  });

  it("filters by rating", async () => {
    const mockOnFilterChange = jest.fn();
    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    fireEvent.click(screen.getByText("Show"));

    await waitFor(() => {
      const ratingButtons = screen.getAllByText(/\(\d+\)/);
      fireEvent.click(ratingButtons[0]); // Click 5-star rating
    });

    expect(mockOnFilterChange).toHaveBeenCalledWith({
      rating: [5],
    });
  });

  it("filters by service", async () => {
    const mockOnFilterChange = jest.fn();
    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    fireEvent.click(screen.getByText("Show"));

    await waitFor(() => {
      const serviceSelect = screen.getByDisplayValue("All Services");
      fireEvent.click(serviceSelect);
    });

    const haircutOption = screen.getByText("Haircut");
    fireEvent.click(haircutOption);

    expect(mockOnFilterChange).toHaveBeenCalledWith({
      serviceId: "service1",
    });
  });

  it("filters by stylist", async () => {
    const mockOnFilterChange = jest.fn();
    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    fireEvent.click(screen.getByText("Show"));

    await waitFor(() => {
      const stylistSelect = screen.getByDisplayValue("All Stylists");
      fireEvent.click(stylistSelect);
    });

    const aliceOption = screen.getByText("Alice");
    fireEvent.click(aliceOption);

    expect(mockOnFilterChange).toHaveBeenCalledWith({
      stylistId: "stylist1",
    });
  });

  it("filters by date range", async () => {
    const mockOnFilterChange = jest.fn();
    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    fireEvent.click(screen.getByText("Show"));

    await waitFor(() => {
      const dateInputs = screen.getAllByDisplayValue("");
      const fromInput = dateInputs[0];
      fireEvent.change(fromInput, { target: { value: "2024-01-01" } });
    });

    expect(mockOnFilterChange).toHaveBeenCalledWith({
      dateRange: { start: "2024-01-01", end: "" },
    });
  });

  it("toggles has response filter", async () => {
    const mockOnFilterChange = jest.fn();
    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    fireEvent.click(screen.getByText("Show"));

    await waitFor(() => {
      const hasResponseCheckbox = screen.getByRole("checkbox", {
        name: /Has Response/,
      });
      fireEvent.click(hasResponseCheckbox);
    });

    expect(mockOnFilterChange).toHaveBeenCalledWith({
      hasResponse: true,
    });
  });

  it("toggles has photos filter", async () => {
    const mockOnFilterChange = jest.fn();
    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    fireEvent.click(screen.getByText("Show"));

    await waitFor(() => {
      const hasPhotosCheckbox = screen.getByRole("checkbox", {
        name: /Has Photos/,
      });
      fireEvent.click(hasPhotosCheckbox);
    });

    expect(mockOnFilterChange).toHaveBeenCalledWith({
      hasPhotos: true,
    });
  });

  it("toggles is flagged filter", async () => {
    const mockOnFilterChange = jest.fn();
    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    fireEvent.click(screen.getByText("Show"));

    await waitFor(() => {
      const isFlaggedCheckbox = screen.getByRole("checkbox", {
        name: /Flagged/,
      });
      fireEvent.click(isFlaggedCheckbox);
    });

    expect(mockOnFilterChange).toHaveBeenCalledWith({
      isFlagged: true,
    });
  });

  it("clears all filters", async () => {
    const mockOnFilterChange = jest.fn();
    const currentFilters = {
      status: "pending" as const,
      rating: [5],
      hasResponse: true,
    };

    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
        currentFilters={currentFilters}
      />
    );

    fireEvent.click(screen.getByText("Show"));

    await waitFor(() => {
      const clearButton = screen.getByText("Clear All Filters");
      fireEvent.click(clearButton);
    });

    expect(mockOnFilterChange).toHaveBeenCalledWith({});
  });

  it("displays active filter count", () => {
    const mockOnFilterChange = jest.fn();
    const currentFilters = {
      status: "pending" as const,
      rating: [5],
      hasResponse: true,
    };

    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
        currentFilters={currentFilters}
      />
    );

    expect(screen.getByText("3 active")).toBeInTheDocument();
  });

  it("displays active filters as badges when collapsed", () => {
    const mockOnFilterChange = jest.fn();
    const currentFilters = {
      status: "pending" as const,
      hasResponse: true,
    };

    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
        currentFilters={currentFilters}
      />
    );

    expect(screen.getByText(/Status: pending/)).toBeInTheDocument();
    expect(screen.getByText("Has Response")).toBeInTheDocument();
  });

  it("shows filter counts for each option", async () => {
    const mockOnFilterChange = jest.fn();
    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    fireEvent.click(screen.getByText("Show"));

    await waitFor(() => {
      expect(screen.getByText("(30)")).toBeInTheDocument(); // pending count
      expect(screen.getByText("(50)")).toBeInTheDocument(); // approved count
    });
  });

  it("allows multiple rating selections", async () => {
    const mockOnFilterChange = jest.fn();
    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    fireEvent.click(screen.getByText("Show"));

    await waitFor(() => {
      const ratingButtons = screen.getAllByRole("button");
      // Click 5-star
      fireEvent.click(ratingButtons[0]);
      // Click 4-star
      fireEvent.click(ratingButtons[1]);
    });

    expect(mockOnFilterChange).toHaveBeenLastCalledWith(
      expect.objectContaining({
        rating: expect.arrayContaining([5, 4]),
      })
    );
  });

  it("removes individual filters from badge display", async () => {
    const mockOnFilterChange = jest.fn();
    const currentFilters = {
      status: "pending" as const,
      hasResponse: true,
    };

    render(
      <ReviewFilters
        onFilterChange={mockOnFilterChange}
        stats={mockStats}
        services={mockServices}
        stylists={mockStylists}
        currentFilters={currentFilters}
      />
    );

    const removeButtons = screen.getAllByRole("button", { name: "" });
    fireEvent.click(removeButtons[0]); // Remove status filter

    expect(mockOnFilterChange).toHaveBeenCalledWith({
      hasResponse: true,
    });
  });
});
