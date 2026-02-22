import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { StylistReviewsSection } from "./stylist-reviews-section";
import * as apiClient from "@/lib/api/client";

// Mock the API client
vi.mock("@/lib/api/client", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe("StylistReviewsSection", () => {
  const mockStylistId = "stylist-123";

  const mockReviews = [
    {
      _id: "review-1",
      client_name: "John Doe",
      rating: 5,
      comment: "Amazing stylist!",
      created_at: "2024-01-15T10:00:00Z",
      status: "approved",
    },
    {
      _id: "review-2",
      client_name: "Jane Smith",
      rating: 5,
      comment: "Highly skilled",
      created_at: "2024-01-14T10:00:00Z",
      status: "approved",
    },
    {
      _id: "review-3",
      client_name: "Bob Johnson",
      rating: 4,
      comment: "Very professional",
      created_at: "2024-01-13T10:00:00Z",
      status: "approved",
    },
  ];

  const mockAggregation = {
    average_rating: 4.67,
    total_reviews: 3,
    rating_distribution: {
      "5": 2,
      "4": 1,
      "3": 0,
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

    render(<StylistReviewsSection stylistId={mockStylistId} />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("should display reviews and aggregation data", async () => {
    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({ data: mockAggregation });
      }
      return Promise.resolve({ data: { reviews: mockReviews } });
    });

    render(<StylistReviewsSection stylistId={mockStylistId} />);

    await waitFor(() => {
      expect(screen.getByText("Customer Reviews")).toBeInTheDocument();
    });

    // Check average rating
    expect(screen.getByText("4.67")).toBeInTheDocument();

    // Check review count
    expect(screen.getByText(/Based on 3 reviews/)).toBeInTheDocument();

    // Check reviews are displayed
    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(screen.getByText("Jane Smith")).toBeInTheDocument();
    expect(screen.getByText("Bob Johnson")).toBeInTheDocument();

    // Check review comments
    expect(screen.getByText("Amazing stylist!")).toBeInTheDocument();
    expect(screen.getByText("Highly skilled")).toBeInTheDocument();
    expect(screen.getByText("Very professional")).toBeInTheDocument();
  });

  it("should display rating distribution", async () => {
    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({ data: mockAggregation });
      }
      return Promise.resolve({ data: { reviews: mockReviews } });
    });

    render(<StylistReviewsSection stylistId={mockStylistId} />);

    await waitFor(() => {
      expect(screen.getByText("4.67")).toBeInTheDocument();
    });

    // Check rating distribution is displayed
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
  });

  it("should filter reviews by rating when clicked", async () => {
    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({ data: mockAggregation });
      }
      return Promise.resolve({ data: { reviews: mockReviews } });
    });

    render(<StylistReviewsSection stylistId={mockStylistId} />);

    await waitFor(() => {
      expect(screen.getByText("4.67")).toBeInTheDocument();
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

    render(<StylistReviewsSection stylistId={mockStylistId} />);

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

    render(<StylistReviewsSection stylistId={mockStylistId} />);

    await waitFor(() => {
      expect(screen.getByText("No Reviews Yet")).toBeInTheDocument();
      expect(
        screen.getByText("Be the first to review this stylist!")
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

    render(<StylistReviewsSection stylistId={mockStylistId} />);

    await waitFor(() => {
      expect(screen.getByText("John Doe")).toBeInTheDocument();
    });

    // Check that star icons are rendered
    const starIcons = screen.getAllByRole("img", { hidden: true });
    expect(starIcons.length).toBeGreaterThan(0);
  });

  it("should fetch reviews with correct stylist_id parameter", async () => {
    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({ data: mockAggregation });
      }
      return Promise.resolve({ data: { reviews: mockReviews } });
    });

    render(<StylistReviewsSection stylistId={mockStylistId} />);

    await waitFor(() => {
      expect(apiClient.apiClient.get).toHaveBeenCalledWith(
        "/api/reviews",
        expect.objectContaining({
          params: expect.objectContaining({
            stylist_id: mockStylistId,
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

    render(<StylistReviewsSection stylistId={mockStylistId} />);

    await waitFor(() => {
      expect(screen.getByText("About Reviews")).toBeInTheDocument();
      expect(
        screen.getByText(
          /All reviews are from verified customers who have completed services with this stylist/
        )
      ).toBeInTheDocument();
    });
  });

  it("should handle high average rating", async () => {
    const highRatedReviews = [
      {
        _id: "review-1",
        client_name: "Client 1",
        rating: 5,
        comment: "Perfect!",
        created_at: "2024-01-15T10:00:00Z",
        status: "approved",
      },
      {
        _id: "review-2",
        client_name: "Client 2",
        rating: 5,
        comment: "Excellent!",
        created_at: "2024-01-14T10:00:00Z",
        status: "approved",
      },
    ];

    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({
          data: {
            average_rating: 5.0,
            total_reviews: 2,
            rating_distribution: {
              "5": 2,
              "4": 0,
              "3": 0,
              "2": 0,
              "1": 0,
            },
          },
        });
      }
      return Promise.resolve({ data: { reviews: highRatedReviews } });
    });

    render(<StylistReviewsSection stylistId={mockStylistId} />);

    await waitFor(() => {
      expect(screen.getByText("5.0")).toBeInTheDocument();
    });

    // Check that all reviews are 5-star
    expect(screen.getByText("Perfect!")).toBeInTheDocument();
    expect(screen.getByText("Excellent!")).toBeInTheDocument();
  });

  it("should clear filter when clicking clear button", async () => {
    (apiClient.apiClient.get as any).mockImplementation((url: string) => {
      if (url.includes("aggregation")) {
        return Promise.resolve({ data: mockAggregation });
      }
      return Promise.resolve({ data: { reviews: mockReviews } });
    });

    render(<StylistReviewsSection stylistId={mockStylistId} />);

    await waitFor(() => {
      expect(screen.getByText("4.67")).toBeInTheDocument();
    });

    // Click on 5-star filter
    const fiveStarButtons = screen.getAllByText("5");
    fireEvent.click(fiveStarButtons[0]);

    // Should show filter badge
    await waitFor(() => {
      expect(screen.getByText(/Showing 5-star reviews/)).toBeInTheDocument();
    });

    // Click on the badge to clear filter
    const filterBadge = screen.getByText(/Showing 5-star reviews/);
    fireEvent.click(filterBadge);

    // Filter should be cleared
    await waitFor(() => {
      expect(screen.queryByText(/Showing 5-star reviews/)).not.toBeInTheDocument();
    });
  });
});
