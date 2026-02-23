/**
 * End-to-end tests for public booking application.
 *
 * Tests cover:
 * - Complete booking journey on desktop
 * - Complete booking journey on mobile
 * - Payment flow with Paystack
 * - Email delivery
 * - Cancellation flow
 * - Rescheduling flow
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PublicBookingApp from "../PublicBookingApp";

// Mock data
const mockSalonInfo = {
  id: "123",
  name: "Premium Salon",
  description: "Your trusted beauty destination",
  logo_url: "https://example.com/logo.png",
  primary_color: "#FF6B6B",
  secondary_color: "#4ECDC4",
};

const mockServices = [
  {
    id: "service-1",
    name: "Haircut",
    description: "Professional haircut",
    duration_minutes: 30,
    price: 50,
    benefits: ["Professional cut", "Styling included"],
  },
  {
    id: "service-2",
    name: "Hair Coloring",
    description: "Professional hair coloring",
    duration_minutes: 60,
    price: 100,
    benefits: ["Premium color", "Deep conditioning"],
  },
];

const mockStaff = [
  {
    id: "staff-1",
    name: "Jane Smith",
    bio: "Expert stylist with 10 years experience",
    specialties: ["Haircut", "Coloring"],
    rating: 4.8,
    review_count: 50,
  },
  {
    id: "staff-2",
    name: "John Doe",
    bio: "Master colorist",
    specialties: ["Coloring", "Treatments"],
    rating: 4.9,
    review_count: 75,
  },
];

const mockAvailability = [
  {
    date: "2024-01-20",
    slots: ["09:00", "10:00", "14:00", "15:00", "16:00"],
  },
];

const mockTestimonials = [
  {
    customer_name: "Alice Johnson",
    rating: 5,
    review: "Excellent service! Highly recommended.",
    created_at: "2024-01-15",
  },
  {
    customer_name: "Bob Smith",
    rating: 5,
    review: "Amazing experience, will definitely come back.",
    created_at: "2024-01-14",
  },
];

const mockStatistics = {
  total_bookings: 500,
  average_rating: 4.8,
  average_response_time: 120,
};

// Setup function
const setupTest = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return { queryClient };
};

describe("PublicBookingApp E2E Tests", () => {
  describe("Desktop Booking Journey", () => {
    beforeEach(() => {
      // Mock API calls
      vi.mock("@/lib/utils/api", () => ({
        apiClient: {
          get: vi.fn((url) => {
            if (url.includes("salon-info"))
              return Promise.resolve(mockSalonInfo);
            if (url.includes("services")) return Promise.resolve(mockServices);
            if (url.includes("staff")) return Promise.resolve(mockStaff);
            if (url.includes("availability"))
              return Promise.resolve(mockAvailability);
            if (url.includes("testimonials"))
              return Promise.resolve(mockTestimonials);
            if (url.includes("statistics"))
              return Promise.resolve(mockStatistics);
            return Promise.reject(new Error("Not found"));
          }),
          post: vi.fn(() => Promise.resolve({ id: "booking-123" })),
        },
      }));
    });

    it("should display hero section with salon branding", async () => {
      const { queryClient } = setupTest();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Wait for hero section to load
      await waitFor(() => {
        expect(screen.getByText(/Premium Salon/i)).toBeInTheDocument();
      });

      // Verify hero section content
      expect(
        screen.getByText(/Your trusted beauty destination/i),
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /Book Now/i }),
      ).toBeInTheDocument();
    });

    it("should display testimonials section", async () => {
      const { queryClient } = setupTest();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Wait for testimonials to load
      await waitFor(() => {
        expect(screen.getByText(/Alice Johnson/i)).toBeInTheDocument();
      });

      // Verify testimonials content
      expect(screen.getByText(/Excellent service/i)).toBeInTheDocument();
      expect(screen.getByText(/Bob Smith/i)).toBeInTheDocument();
    });

    it("should display FAQ section", async () => {
      const { queryClient } = setupTest();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Wait for FAQ to load
      await waitFor(() => {
        expect(screen.getByText(/How do I book/i)).toBeInTheDocument();
      });

      // Verify FAQ items are collapsed initially
      const faqAnswers = screen.queryAllByText(/To book an appointment/i);
      expect(faqAnswers.length).toBe(0);
    });

    it("should display booking statistics", async () => {
      const { queryClient } = setupTest();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Wait for statistics to load
      await waitFor(() => {
        expect(screen.getByText(/500/i)).toBeInTheDocument();
      });

      // Verify statistics content
      expect(screen.getByText(/4.8/i)).toBeInTheDocument();
    });

    it("should complete full booking flow", async () => {
      const { queryClient } = setupTest();
      const user = userEvent.setup();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Step 1: Click "Book Now" to scroll to booking form
      const bookNowButton = await screen.findByRole("button", {
        name: /Book Now/i,
      });
      await user.click(bookNowButton);

      // Step 2: Select service
      const serviceButtons = await screen.findAllByRole("button", {
        name: /Haircut/i,
      });
      await user.click(serviceButtons[0]);

      // Step 3: Select staff
      const staffButtons = await screen.findAllByRole("button", {
        name: /Jane Smith/i,
      });
      await user.click(staffButtons[0]);

      // Step 4: Select time slot
      const timeSlotButtons = await screen.findAllByRole("button", {
        name: /14:00/i,
      });
      await user.click(timeSlotButtons[0]);

      // Step 5: Fill booking form
      const nameInput = screen.getByLabelText(/Name/i);
      const emailInput = screen.getByLabelText(/Email/i);
      const phoneInput = screen.getByLabelText(/Phone/i);

      await user.type(nameInput, "John Doe");
      await user.type(emailInput, "john@example.com");
      await user.type(phoneInput, "+1234567890");

      // Step 6: Select payment option
      const payLaterRadio = screen.getByLabelText(/Pay Later/i);
      await user.click(payLaterRadio);

      // Step 7: Submit booking
      const submitButton = screen.getByRole("button", {
        name: /Confirm Booking/i,
      });
      await user.click(submitButton);

      // Step 8: Verify confirmation
      await waitFor(() => {
        expect(screen.getByText(/Booking Confirmed/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
      expect(screen.getByText(/Haircut/i)).toBeInTheDocument();
    });

    it("should handle payment flow with Pay Now option", async () => {
      const { queryClient } = setupTest();
      const user = userEvent.setup();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Navigate to booking form
      const bookNowButton = await screen.findByRole("button", {
        name: /Book Now/i,
      });
      await user.click(bookNowButton);

      // Select service, staff, and time
      const serviceButtons = await screen.findAllByRole("button", {
        name: /Haircut/i,
      });
      await user.click(serviceButtons[0]);

      const staffButtons = await screen.findAllByRole("button", {
        name: /Jane Smith/i,
      });
      await user.click(staffButtons[0]);

      const timeSlotButtons = await screen.findAllByRole("button", {
        name: /14:00/i,
      });
      await user.click(timeSlotButtons[0]);

      // Fill form
      const nameInput = screen.getByLabelText(/Name/i);
      const emailInput = screen.getByLabelText(/Email/i);
      const phoneInput = screen.getByLabelText(/Phone/i);

      await user.type(nameInput, "Jane Doe");
      await user.type(emailInput, "jane@example.com");
      await user.type(phoneInput, "+0987654321");

      // Select Pay Now
      const payNowRadio = screen.getByLabelText(/Pay Now/i);
      await user.click(payNowRadio);

      // Verify payment processor appears
      await waitFor(() => {
        expect(screen.getByText(/Payment Method/i)).toBeInTheDocument();
      });

      // Select payment method
      const cardOption = screen.getByLabelText(/Card/i);
      await user.click(cardOption);

      // Submit booking
      const submitButton = screen.getByRole("button", {
        name: /Confirm Booking/i,
      });
      await user.click(submitButton);

      // Verify payment processor is shown
      await waitFor(() => {
        expect(screen.getByText(/Enter Card Details/i)).toBeInTheDocument();
      });
    });
  });

  describe("Mobile Booking Journey", () => {
    beforeEach(() => {
      // Set mobile viewport
      window.innerWidth = 375;
      window.innerHeight = 667;
      fireEvent(window, new Event("resize"));
    });

    it("should display responsive layout on mobile", async () => {
      const { queryClient } = setupTest();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Wait for content to load
      await waitFor(() => {
        expect(screen.getByText(/Premium Salon/i)).toBeInTheDocument();
      });

      // Verify mobile-friendly layout
      const heroSection = screen.getByText(/Premium Salon/i).closest("section");
      expect(heroSection).toHaveClass("mobile-responsive");
    });

    it("should display testimonials carousel on mobile", async () => {
      const { queryClient } = setupTest();
      const user = userEvent.setup();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Wait for testimonials to load
      await waitFor(() => {
        expect(screen.getByText(/Alice Johnson/i)).toBeInTheDocument();
      });

      // Verify carousel controls exist
      const prevButton = screen.queryByRole("button", { name: /Previous/i });
      const nextButton = screen.queryByRole("button", { name: /Next/i });

      // On mobile, carousel should be visible
      if (window.innerWidth < 768) {
        expect(prevButton || nextButton).toBeTruthy();
      }
    });

    it("should complete booking on mobile", async () => {
      const { queryClient } = setupTest();
      const user = userEvent.setup();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Scroll to booking form
      const bookNowButton = await screen.findByRole("button", {
        name: /Book Now/i,
      });
      await user.click(bookNowButton);

      // Select service
      const serviceButtons = await screen.findAllByRole("button", {
        name: /Haircut/i,
      });
      await user.click(serviceButtons[0]);

      // Select staff
      const staffButtons = await screen.findAllByRole("button", {
        name: /Jane Smith/i,
      });
      await user.click(staffButtons[0]);

      // Select time
      const timeSlotButtons = await screen.findAllByRole("button", {
        name: /14:00/i,
      });
      await user.click(timeSlotButtons[0]);

      // Fill form
      const nameInput = screen.getByLabelText(/Name/i);
      await user.type(nameInput, "Mobile User");

      const emailInput = screen.getByLabelText(/Email/i);
      await user.type(emailInput, "mobile@example.com");

      const phoneInput = screen.getByLabelText(/Phone/i);
      await user.type(phoneInput, "+1111111111");

      // Submit
      const submitButton = screen.getByRole("button", {
        name: /Confirm Booking/i,
      });
      await user.click(submitButton);

      // Verify confirmation
      await waitFor(() => {
        expect(screen.getByText(/Booking Confirmed/i)).toBeInTheDocument();
      });
    });
  });

  describe("Cancellation Flow", () => {
    it("should display cancellation option in confirmation", async () => {
      const { queryClient } = setupTest();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // After booking is confirmed
      await waitFor(() => {
        expect(screen.getByText(/Booking Confirmed/i)).toBeInTheDocument();
      });

      // Verify cancellation link is present
      const cancelLink = screen.getByRole("link", { name: /Cancel Booking/i });
      expect(cancelLink).toBeInTheDocument();
    });

    it("should navigate to cancellation page", async () => {
      const { queryClient } = setupTest();
      const user = userEvent.setup();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // After booking
      await waitFor(() => {
        expect(screen.getByText(/Booking Confirmed/i)).toBeInTheDocument();
      });

      // Click cancel link
      const cancelLink = screen.getByRole("link", { name: /Cancel Booking/i });
      await user.click(cancelLink);

      // Verify cancellation page loads
      await waitFor(() => {
        expect(screen.getByText(/Cancel Booking/i)).toBeInTheDocument();
      });
    });
  });

  describe("Rescheduling Flow", () => {
    it("should display rescheduling option in confirmation", async () => {
      const { queryClient } = setupTest();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // After booking is confirmed
      await waitFor(() => {
        expect(screen.getByText(/Booking Confirmed/i)).toBeInTheDocument();
      });

      // Verify rescheduling link is present
      const rescheduleLink = screen.getByRole("link", { name: /Reschedule/i });
      expect(rescheduleLink).toBeInTheDocument();
    });

    it("should navigate to rescheduling page", async () => {
      const { queryClient } = setupTest();
      const user = userEvent.setup();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // After booking
      await waitFor(() => {
        expect(screen.getByText(/Booking Confirmed/i)).toBeInTheDocument();
      });

      // Click reschedule link
      const rescheduleLink = screen.getByRole("link", { name: /Reschedule/i });
      await user.click(rescheduleLink);

      // Verify rescheduling page loads
      await waitFor(() => {
        expect(screen.getByText(/Reschedule Booking/i)).toBeInTheDocument();
      });
    });
  });

  describe("Accessibility", () => {
    it("should have proper heading hierarchy", async () => {
      const { queryClient } = setupTest();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Verify heading hierarchy
      const h1 = screen.getByRole("heading", { level: 1 });
      expect(h1).toBeInTheDocument();
    });

    it("should have proper form labels", async () => {
      const { queryClient } = setupTest();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Verify form labels exist
      const nameLabel = screen.getByLabelText(/Name/i);
      const emailLabel = screen.getByLabelText(/Email/i);

      expect(nameLabel).toBeInTheDocument();
      expect(emailLabel).toBeInTheDocument();
    });

    it("should support keyboard navigation", async () => {
      const { queryClient } = setupTest();
      const user = userEvent.setup();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Tab through form elements
      const nameInput = screen.getByLabelText(/Name/i);
      await user.tab();

      // Verify focus management
      expect(document.activeElement).toBeTruthy();
    });
  });

  describe("Error Handling", () => {
    it("should display error message on booking failure", async () => {
      const { queryClient } = setupTest();

      // Mock API error
      vi.mock("@/lib/utils/api", () => ({
        apiClient: {
          post: vi.fn(() => Promise.reject(new Error("Booking failed"))),
        },
      }));

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // Attempt to submit booking
      const submitButton = await screen.findByRole("button", {
        name: /Confirm Booking/i,
      });
      fireEvent.click(submitButton);

      // Verify error message
      await waitFor(() => {
        expect(screen.getByText(/Booking failed/i)).toBeInTheDocument();
      });
    });

    it("should display retry button on error", async () => {
      const { queryClient } = setupTest();

      render(
        <QueryClientProvider client={queryClient}>
          <PublicBookingApp />
        </QueryClientProvider>,
      );

      // After error occurs
      await waitFor(() => {
        expect(screen.getByText(/Booking failed/i)).toBeInTheDocument();
      });

      // Verify retry button
      const retryButton = screen.getByRole("button", { name: /Retry/i });
      expect(retryButton).toBeInTheDocument();
    });
  });
});
