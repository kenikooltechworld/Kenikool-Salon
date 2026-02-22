import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { DayView } from "../DayView";
import type { Booking } from "@/types";

const mockBookings: Booking[] = [
  {
    id: "1",
    customerId: "cust-1",
    serviceId: "svc-1",
    staffId: "staff-1",
    startTime: "2026-02-15T10:00:00Z",
    endTime: "2026-02-15T10:30:00Z",
    status: "confirmed",
    createdAt: "2026-02-14T10:00:00Z",
    updatedAt: "2026-02-14T10:00:00Z",
  },
  {
    id: "2",
    customerId: "cust-2",
    serviceId: "svc-2",
    staffId: "staff-1",
    startTime: "2026-02-15T14:00:00Z",
    endTime: "2026-02-15T14:30:00Z",
    status: "scheduled",
    createdAt: "2026-02-14T10:00:00Z",
    updatedAt: "2026-02-14T10:00:00Z",
  },
];

describe("DayView", () => {
  it("renders day view with bookings", () => {
    const date = new Date("2026-02-15");
    render(
      <DayView date={date} bookings={mockBookings} onBookingClick={() => {}} />,
    );

    expect(screen.getByText(/sunday/i)).toBeInTheDocument();
  });

  it("displays hourly timeline", () => {
    const date = new Date("2026-02-15");
    render(<DayView date={date} bookings={[]} onBookingClick={() => {}} />);

    expect(screen.getByText("00:00")).toBeInTheDocument();
    expect(screen.getByText("23:00")).toBeInTheDocument();
  });

  it("calls onBookingClick when booking is clicked", async () => {
    const onBookingClick = vi.fn();
    const user = userEvent.setup();
    const date = new Date("2026-02-15");

    render(
      <DayView
        date={date}
        bookings={mockBookings}
        onBookingClick={onBookingClick}
      />,
    );

    const bookingButtons = screen.getAllByRole("button");
    await user.click(bookingButtons[0]);

    expect(onBookingClick).toHaveBeenCalled();
  });

  it("shows loading state", () => {
    const date = new Date("2026-02-15");
    render(
      <DayView
        date={date}
        bookings={[]}
        onBookingClick={() => {}}
        isLoading={true}
      />,
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
});
