import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ReviewFilters, type ReviewFilters as ReviewFiltersType } from "./review-filters";

describe("ReviewFilters Integration with Reviews Page", () => {
  const mockFilterStats = {
    totalReviews: 100,
    byStatus: {
      pending: 20,
      approved: 70,
      rejected: 10,
    },
    byRating: {
      1: 5,
      2: 10,
      3: 15,
      4: 30,
      5: 40,
    },
    byService: {
      service_1: 50,
      service_2: 30,
      service_3: 20,
    },
    byStylist: {
      stylist_1: 60,
      stylist_2: 40,
    },
    withResponse: 25,
    withPhotos: 15,
    flagged: 3,
  };

  const mockServices = [
    { id: "service_1", name: "Haircut" },
    { id: "service_2", name: "Color" },
    { id: "service_3", name: "Styling" },
  ];

  const mockStylists = [
    { id: "stylist_1", name: "Alice" },
    { id: "stylist_2", name: "Bob" },
  ];

  it("should render filter component with all filter options", () => {
    const handleFilterChange = jest.fn();

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    expect(screen.getByText("Filters")).toBeInTheDocument();
    expect(screen.getByText("Show")).toBeInTheDocument();
  });

  it("should expand and collapse filter panel", async () => {
    const handleFilterChange = jest.fn();

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    const expandButton = screen.getByText("Show");
    fireEvent.click(expandButton);

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

  it("should filter by status", async () => {
    const handleFilterChange = jest.fn();

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    const expandButton = screen.getByText("Show");
    fireEvent.click(expandButton);

    await waitFor(() => {
      const approvedButton = screen.getByText(/Approved/);
      fireEvent.click(approvedButton);
    });

    expect(handleFilterChange).toHaveBeenCalledWith(
      expect.objectContaining({
        status: "approved",
      })
    );
  });

  it("should filter by multiple ratings", async () => {
    const handleFilterChange = jest.fn();

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    const expandButton = screen.getByText("Show");
    fireEvent.click(expandButton);

    await waitFor(() => {
      const fiveStarButtons = screen.getAllByText(/5/);
      fireEvent.click(fiveStarButtons[0]);
    });

    expect(handleFilterChange).toHaveBeenCalledWith(
      expect.objectContaining({
        rating: expect.arrayContaining([5]),
      })
    );

    await waitFor(() => {
      const fourStarButtons = screen.getAllByText(/4/);
      fireEvent.click(fourStarButtons[0]);
    });

    expect(handleFilterChange).toHaveBeenCalledWith(
      expect.objectContaining({
        rating: expect.arrayContaining([5, 4]),
      })
    );
  });

  it("should filter by service", async () => {
    const handleFilterChange = jest.fn();

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    const expandButton = screen.getByText("Show");
    fireEvent.click(expandButton);

    await waitFor(() => {
      const serviceSelect = screen.getByDisplayValue("");
      fireEvent.click(serviceSelect);
    });

    const haircutOption = screen.getByText("Haircut");
    fireEvent.click(haircutOption);

    expect(handleFilterChange).toHaveBeenCalledWith(
      expect.objectContaining({
        serviceId: "service_1",
      })
    );
  });

  it("should filter by stylist", async () => {
    const handleFilterChange = jest.fn();

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    const expandButton = screen.getByText("Show");
    fireEvent.click(expandButton);

    await waitFor(() => {
      const stylistSelects = screen.getAllByDisplayValue("");
      fireEvent.click(stylistSelects[1]);
    });

    const aliceOption = screen.getByText("Alice");
    fireEvent.click(aliceOption);

    expect(handleFilterChange).toHaveBeenCalledWith(
      expect.objectContaining({
        stylistId: "stylist_1",
      })
    );
  });

  it("should filter by date range", async () => {
    const handleFilterChange = jest.fn();

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    const expandButton = screen.getByText("Show");
    fireEvent.click(expandButton);

    await waitFor(() => {
      const dateInputs = screen.getAllByDisplayValue("");
      const fromInput = dateInputs[0];
      fireEvent.change(fromInput, { target: { value: "2024-01-01" } });
    });

    expect(handleFilterChange).toHaveBeenCalledWith(
      expect.objectContaining({
        dateRange: expect.objectContaining({
          start: "2024-01-01",
        }),
      })
    );
  });

  it("should filter by has response", async () => {
    const handleFilterChange = jest.fn();

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    const expandButton = screen.getByText("Show");
    fireEvent.click(expandButton);

    await waitFor(() => {
      const hasResponseCheckbox = screen.getByRole("checkbox", {
        name: /Has Response/,
      });
      fireEvent.click(hasResponseCheckbox);
    });

    expect(handleFilterChange).toHaveBeenCalledWith(
      expect.objectContaining({
        hasResponse: true,
      })
    );
  });

  it("should show active filter count", async () => {
    const handleFilterChange = jest.fn();
    const currentFilters: ReviewFiltersType = {
      status: "approved",
      rating: [5, 4],
    };

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
        currentFilters={currentFilters}
      />
    );

    expect(screen.getByText("2 active")).toBeInTheDocument();
  });

  it("should display active filters when collapsed", async () => {
    const handleFilterChange = jest.fn();
    const currentFilters: ReviewFiltersType = {
      status: "approved",
      rating: [5],
    };

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
        currentFilters={currentFilters}
      />
    );

    expect(screen.getByText(/Status: approved/)).toBeInTheDocument();
    expect(screen.getByText(/Rating: 5/)).toBeInTheDocument();
  });

  it("should clear all filters", async () => {
    const handleFilterChange = jest.fn();
    const currentFilters: ReviewFiltersType = {
      status: "approved",
      rating: [5],
      hasResponse: true,
    };

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
        currentFilters={currentFilters}
      />
    );

    const expandButton = screen.getByText("Show");
    fireEvent.click(expandButton);

    await waitFor(() => {
      const clearButton = screen.getByText("Clear All Filters");
      fireEvent.click(clearButton);
    });

    expect(handleFilterChange).toHaveBeenCalledWith({});
  });

  it("should show filter counts for each option", async () => {
    const handleFilterChange = jest.fn();

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    const expandButton = screen.getByText("Show");
    fireEvent.click(expandButton);

    await waitFor(() => {
      expect(screen.getByText(/Pending.*20/)).toBeInTheDocument();
      expect(screen.getByText(/Approved.*70/)).toBeInTheDocument();
      expect(screen.getByText(/Rejected.*10/)).toBeInTheDocument();
    });
  });

  it("should remove individual filter badges", async () => {
    const handleFilterChange = jest.fn();
    const currentFilters: ReviewFiltersType = {
      status: "approved",
      rating: [5],
    };

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
        currentFilters={currentFilters}
      />
    );

    const removeButtons = screen.getAllByRole("button", { name: "" });
    const statusRemoveButton = removeButtons[0];
    fireEvent.click(statusRemoveButton);

    expect(handleFilterChange).toHaveBeenCalledWith(
      expect.objectContaining({
        status: undefined,
        rating: [5],
      })
    );
  });

  it("should combine multiple filters", async () => {
    const handleFilterChange = jest.fn();

    render(
      <ReviewFilters
        onFilterChange={handleFilterChange}
        stats={mockFilterStats}
        services={mockServices}
        stylists={mockStylists}
      />
    );

    const expandButton = screen.getByText("Show");
    fireEvent.click(expandButton);

    // Apply status filter
    await waitFor(() => {
      const approvedButton = screen.getByText(/Approved/);
      fireEvent.click(approvedButton);
    });

    // Apply rating filter
    await waitFor(() => {
      const fiveStarButtons = screen.getAllByText(/5/);
      fireEvent.click(fiveStarButtons[0]);
    });

    // Verify combined filters
    expect(handleFilterChange).toHaveBeenLastCalledWith(
      expect.objectContaining({
        status: "approved",
        rating: expect.arrayContaining([5]),
      })
    );
  });
});
