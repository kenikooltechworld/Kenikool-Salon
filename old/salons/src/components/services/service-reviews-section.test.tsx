import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { ServiceReviewsSection } from "./service-reviews-section";
import * as apiClient from "@/lib/api/client";

// Mock the API client
vi.mock("@/lib/api/client", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe("ServiceReviewsSection", () => {
  const mockServiceId = "service-123";

  const mockReviews = [
    {
      _id: "review-1",
      client_name: "John Doe",
      rating: 5,
      comment: "Excellent service!",
      created_at: "2024-01-15T10:00:00Z",
      status: "approved",
    },
    {
      _id: "review-2",
      client_name: "Jane Smith",
      rating: 4,
      comment: "Very good, would recommend",
      created_at: "2024-01-14T10:00:00Z",
      status: "approved",
    },
    {
      _id: "review-3",
      client_name: "Bob Johnson",
      rating: 3,
      comment: "Average experience",
      created_at: "2024-01-13T10:00:00Z",
      status: "approved",
    },
  ];

  const mockAggregation = {
    average_rating: 4.0,
    total_reviews: 3,
    rating_distribution: {
      "5": 1,
      "4": 1,
      "3": 1,
      "2": 0,
      "1": 0,
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render loading state initially", () => {
    (apiClient.apiClient.get as any).mockImplementation(
      () =>
        new Promise(() => {
          /* Never resolves */
        })
    );

    render(<ServiceReviewsSection serviceId={mockServiceId} />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("should display reviews and aggregation data", async () => {
    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({ data: mockAggregation });
      }
      return Promise.resolve({ data: { reviews: mockReviews } });
    });

    render(<ServiceReviewsSection serviceId={mockServiceId} />);

    await waitFor(() => {
      expect(screen.getByText("Customer Reviews")).toBeInTheDocument();
    });

    // Check average rating
    expect(screen.getByText("4.0")).toBeInTheDocument();

    // Check review count
    expect(screen.getByText(/Based on 3 reviews/)).toBeInTheDocument();

    // Check reviews are displayed
    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(screen.getByText("Jane Smith")).toBeInTheDocument();
    expect(screen.getByText("Bob Johnson")).toBeInTheDocument();

    // Check review comments
    expect(screen.getByText("Excellent service!")).toBeInTheDocument();
    expect(screen.getByText("Very good, would recommend")).toBeInTheDocument();
    expect(screen.getByText("Average experience")).toBeInTheDocument();
  });

  it("should display rating distribution", async () => {
    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({ data: mockAggregation });
      }
      return Promise.resolve({ data: { reviews: mockReviews } });
    });

    render(<ServiceReviewsSection serviceId={mockServiceId} />);

    await waitFor(() => {
      expect(screen.getByText("4.0")).toBeInTheDocument();
    });

    // Check rating distribution is displayed
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("should filter reviews by rating when clicked", async () => {
    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({ data: mockAggregation });
      }
      return Promise.resolve({ data: { reviews: mockReviews } });
    });

    render(<ServiceReviewsSection serviceId={mockServiceId} />);

    await waitFor(() => {
      expect(screen.getByText("4.0")).toBeInTheDocument();
    });

    // Click on 5-star filter
    const fiveStarButtons = screen.getAllByText("5");
    fireEvent.click(fiveStarButtons[0]);

    // Should show filter badge
    await waitFor(() => {
      expect(screen.getByText(/Showing 5-star reviews/)).toBeInTheDocument();
    });
  });

  it("should display error message on API failure", async () => {
    (apiClient.apiClient.get as any).mockRejectedValue(
      new Error("API Error")
    );

    render(<ServiceReviewsSection serviceId={mockServiceId} />);

    await waitFor(() => {
      expect(screen.getByText("Error")).toBeInTheDocument();
      expect(screen.getByText("Failed to load reviews")).toBeInTheDocument();
    });
  });

  it("should display empty state when no reviews", async () => {
    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({
          data: {
            average_rating: 0,
            total_reviews: 0,
            rating_distribution: { "1": 0, "2": 0, "3": 0, "4": 0, "5": 0 },
          },
        });
      }
      return Promise.resolve({ data: { reviews: [] } });
    });

    render(<ServiceReviewsSection serviceId={mockServiceId} />);

    await waitFor(() => {
      expect(screen.getByText("No Reviews Yet")).toBeInTheDocument();
      expect(
        screen.getByText("Be the first to review this service!")
      ).toBeInTheDocument();
    });
  });

  it("should render star ratings correctly", async () => {
    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({ data: mockAggregation });
      }
      return Promise.resolve({ data: { reviews: mockReviews } });
    });

    render(<ServiceReviewsSection serviceId={mockServiceId} />);

    await waitFor(() => {
      expect(screen.getByText("John Doe")).toBeInTheDocument();
    });

    // Check that star icons are rendered (they should be present for each review)
    const starIcons = screen.getAllByRole("img", { hidden: true });
    expect(starIcons.length).toBeGreaterThan(0);
  });

  it("should fetch reviews with correct service_id parameter", async () => {
    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({ data: mockAggregation });
      }
      return Promise.resolve({ data: { reviews: mockReviews } });
    });

    render(<ServiceReviewsSection serviceId={mockServiceId} />);

    await waitFor(() => {
      expect(apiClient.apiClient.get).toHaveBeenCalledWith(
        "/api/reviews",
        expect.objectContaining({
          params: expect.objectContaining({
            service_id: mockServiceId,
            status: "approved",
          }),
        })
      );
    });
  });

  it("should display info card with review information", async () => {
    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({ data: mockAggregation });
      }
      return Promise.resolve({ data: { reviews: mockReviews } });
    });

    render(<ServiceReviewsSection serviceId={mockServiceId} />);

    await waitFor(() => {
      expect(screen.getByText("About Reviews")).toBeInTheDocument();
      expect(
        screen.getByText(
          /All reviews are from verified customers who have completed this service/
        )
      ).toBeInTheDocument();
    });
  });

  it("should handle multiple reviews with different ratings", async () => {
    const multipleReviews = [
      ...mockReviews,
      {
        _id: "review-4",
        client_name: "Alice Brown",
        rating: 5,
        comment: "Perfect!",
        created_at: "2024-01-12T10:00:00Z",
        status: "approved",
      },
      {
        _id: "review-5",
        client_name: "Charlie Davis",
        rating: 2,
        comment: "Not satisfied",
        created_at: "2024-01-11T10:00:00Z",
        status: "approved",
      },
    ];

    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({
          data: {
            average_rating: 3.8,
            total_reviews: 5,
            rating_distribution: {
              "5": 2,
              "4": 1,
              "3": 1,
              "2": 1,
              "1": 0,
            },
          },
        });
      }
      return Promise.resolve({ data: { reviews: multipleReviews } });
    });

    render(<ServiceReviewsSection serviceId={mockServiceId} />);

    await waitFor(() => {
      expect(screen.getByText("3.8")).toBeInTheDocument();
    });

    // Check all reviews are displayed
    expect(screen.getByText("Alice Brown")).toBeInTheDocument();
    expect(screen.getByText("Charlie Davis")).toBeInTheDocument();
  });
});
