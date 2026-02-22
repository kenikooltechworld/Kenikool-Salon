import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import ServiceDetailsPage from "./page";
import * as apiClient from "@/lib/api/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Mock the API client
vi.mock("@/lib/api/client", () => ({
  apiClient: {
    get: vi.fn(),
    patch: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}));

// Mock heavy components
vi.mock("@/components/services/service-variant-manager", () => ({
  ServiceVariantManager: () => <div>Variant Manager</div>,
}));

vi.mock("@/components/services/tiered-pricing-editor", () => ({
  TieredPricingEditor: () => <div>Pricing Editor</div>,
}));

vi.mock("@/components/services/booking-rules-editor", () => ({
  BookingRulesEditor: () => <div>Rules Editor</div>,
}));

vi.mock("@/components/services/availability-scheduler", () => ({
  AvailabilityScheduler: () => <div>Availability Scheduler</div>,
}));

vi.mock("@/components/services/capacity-manager", () => ({
  CapacityManager: () => <div>Capacity Manager</div>,
}));

vi.mock("@/components/services/commission-editor", () => ({
  CommissionEditor: () => <div>Commission Editor</div>,
}));

vi.mock("@/components/services/resource-manager", () => ({
  ResourceManager: () => <div>Resource Manager</div>,
}));

vi.mock("@/components/services/marketing-settings", () => ({
  MarketingSettings: () => <div>Marketing Settings</div>,
}));

vi.mock("@/components/services/service-reviews-section", () => ({
  ServiceReviewsSection: ({ serviceId }: { serviceId: string }) => (
    <div data-testid="service-reviews-section">
      Reviews for service {serviceId}
    </div>
  ),
}));

vi.mock("@/components/services/service-recommendations", () => ({
  ServiceRecommendations: () => <div>Recommendations</div>,
}));

vi.mock("@/components/services/recent-bookings-list", () => ({
  RecentBookingsList: () => <div>Recent Bookings</div>,
}));

vi.mock("@/components/services/stylist-performance-widget", () => ({
  StylistPerformanceWidget: () => <div>Stylist Performance</div>,
}));

vi.mock("@/components/services/audit-log-viewer", () => ({
  AuditLogViewer: () => <div>Audit Log</div>,
}));

vi.mock("@/components/services/dependency-manager", () => ({
  DependencyManager: () => <div>Dependencies</div>,
}));

vi.mock("@/components/services/performance-report", () => ({
  PerformanceReport: () => <div>Performance Report</div>,
}));

// Mock react-router-dom
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useParams: () => ({ id: "service-123" }),
    useNavigate: () => vi.fn(),
  };
});

// Mock useStylists hook
vi.mock("@/lib/api/hooks/useStylists", () => ({
  useStylists: () => ({
    data: [
      {
        id: "stylist-1",
        name: "John Doe",
        is_active: true,
      },
    ],
  }),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{component}</BrowserRouter>
    </QueryClientProvider>
  );
};

describe("Service Details Page - Reviews Integration", () => {
  const mockServiceData = {
    service: {
      id: "service-123",
      name: "Haircut",
      description: "Professional haircut service",
      price: 5000,
      duration_minutes: 30,
      category: "Hair",
      is_active: true,
      photo_url: "https://example.com/photo.jpg",
      assigned_stylists: ["stylist-1"],
      tiered_pricing: [],
      booking_rules: {},
      availability: {},
      max_concurrent_bookings: 1,
      commission_structure: {},
      required_resources: [],
      marketing_settings: {},
      prerequisite_services: [],
      mandatory_addons: [],
    },
    statistics: {
      totalBookings: 100,
      completedBookings: 95,
      cancelledBookings: 5,
      totalRevenue: 500000,
      averageBookingValue: 5000,
      revenueTrend: 5.2,
      averageRating: 4.5,
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  it("should render service details page with reviews section", async () => {
    (apiClient.apiClient.get as any).mockResolvedValue({
      data: mockServiceData,
    });

    renderWithProviders(<ServiceDetailsPage />);

    await waitFor(() => {
      expect(screen.getByText("Haircut")).toBeInTheDocument();
    });

    // Check that reviews section is rendered
    expect(screen.getByTestId("service-reviews-section")).toBeInTheDocument();
    expect(screen.getByText("Reviews for service service-123")).toBeInTheDocument();
  });

  it("should display service information and reviews together", async () => {
    (apiClient.apiClient.get as any).mockResolvedValue({
      data: mockServiceData,
    });

    renderWithProviders(<ServiceDetailsPage />);

    await waitFor(() => {
      expect(screen.getByText("Haircut")).toBeInTheDocument();
    });

    // Check service details
    expect(screen.getByText("Professional haircut service")).toBeInTheDocument();
    expect(screen.getByText("Hair")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();

    // Check statistics
    expect(screen.getByText("Total Revenue")).toBeInTheDocument();
    expect(screen.getByText("500,000")).toBeInTheDocument();

    // Check reviews section
    expect(screen.getByTestId("service-reviews-section")).toBeInTheDocument();
  });

  it("should render reviews section in overview tab", async () => {
    (apiClient.apiClient.get as any).mockResolvedValue({
      data: mockServiceData,
    });

    renderWithProviders(<ServiceDetailsPage />);

    await waitFor(() => {
      expect(screen.getByText("Haircut")).toBeInTheDocument();
    });

    // Overview tab should be active by default
    expect(screen.getByText("Overview")).toBeInTheDocument();

    // Reviews section should be visible
    expect(screen.getByTestId("service-reviews-section")).toBeInTheDocument();
  });

  it("should handle service with no reviews", async () => {
    const noReviewsData = {
      ...mockServiceData,
      statistics: {
        ...mockServiceData.statistics,
        averageRating: undefined,
      },
    };

    (apiClient.apiClient.get as any).mockResolvedValue({
      data: noReviewsData,
    });

    renderWithProviders(<ServiceDetailsPage />);

    await waitFor(() => {
      expect(screen.getByText("Haircut")).toBeInTheDocument();
    });

    // Reviews section should still be rendered
    expect(screen.getByTestId("service-reviews-section")).toBeInTheDocument();
  });

  it("should display all service tabs including overview with reviews", async () => {
    (apiClient.apiClient.get as any).mockResolvedValue({
      data: mockServiceData,
    });

    renderWithProviders(<ServiceDetailsPage />);

    await waitFor(() => {
      expect(screen.getByText("Haircut")).toBeInTheDocument();
    });

    // Check that all tabs are present
    expect(screen.getByText("Overview")).toBeInTheDocument();
    expect(screen.getByText("Variants")).toBeInTheDocument();
    expect(screen.getByText("Tiered Pricing")).toBeInTheDocument();

    // Reviews section should be in overview
    expect(screen.getByTestId("service-reviews-section")).toBeInTheDocument();
  });
});
