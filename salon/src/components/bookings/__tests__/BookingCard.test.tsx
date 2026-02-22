import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BookingCard } from "../BookingCard";
import type { Booking } from "@/types";

const mockBooking: Booking = {
  id: "1",
  customerId: "cust-1",
  serviceId: "svc-1",
  staffId: "staff-1",
  startTime: "2026-02-15T10:00:00Z",
  endTime: "2026-02-15T10:30:00Z",
  status: "confirmed",
  createdAt: "2026-02-14T10:00:00Z",
  updatedAt: "2026-02-14T10:00:00Z",
};

describe("BookingCard", () => {
  it("renders booking information", () => {
    render(
      <BookingCard
        booking={mockBooking}
        onView={() => {}}
        onConfirm={() => {}}
        onCancel={() => {}}
      />,
    );

    expect(screen.getByText(/booking/i)).toBeInTheDocument();
    expect(screen.getByText(/confirmed/i)).toBeInTheDocument();
  });

  it("calls onView when view button is clicked", async () => {
    const onView = vi.fn();
    const user = userEvent.setup();

    render(
      <BookingCard
        booking={mockBooking}
        onView={onView}
        onConfirm={() => {}}
        onCancel={() => {}}
      />,
    );

    const viewButton = screen.getByRole("button", { name: /view/i });
    await user.click(viewButton);

    expect(onView).toHaveBeenCalledWith(mockBooking.id);
  });

  it("disables buttons when loading", () => {
    render(
      <BookingCard
        booking={mockBooking}
        onView={() => {}}
        onConfirm={() => {}}
        onCancel={() => {}}
        isLoading={true}
      />,
    );

    const buttons = screen.getAllByRole("button");
    buttons.forEach((button) => {
      expect(button).toBeDisabled();
    });
  });
});
