import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ReviewModerationList } from "./review-moderation-list";
import { describe, it, expect, vi } from "vitest";

const mockReviews = [
  {
    _id: "1",
    client_name: "John Doe",
    rating: 5,
    comment: "Great service!",
    status: "pending" as const,
    created_at: new Date().toISOString(),
  },
  {
    _id: "2",
    client_name: "Jane Smith",
    rating: 4,
    comment: "Good experience",
    status: "pending" as const,
    created_at: new Date().toISOString(),
  },
];

describe("ReviewModerationList with Selection", () => {
  it("should render select all checkbox", () => {
    render(
      <ReviewModerationList
        reviews={mockReviews}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onSelectionChange={vi.fn()}
      />
    );

    expect(screen.getByLabelText("Select all reviews")).toBeInTheDocument();
  });

  it("should render individual checkboxes for each review", () => {
    render(
      <ReviewModerationList
        reviews={mockReviews}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onSelectionChange={vi.fn()}
      />
    );

    expect(screen.getByLabelText(/Select review from John Doe/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Select review from Jane Smith/)).toBeInTheDocument();
  });

  it("should select all reviews when select all checkbox is clicked", async () => {
    const onSelectionChange = vi.fn();

    render(
      <ReviewModerationList
        reviews={mockReviews}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onSelectionChange={onSelectionChange}
      />
    );

    const selectAllCheckbox = screen.getByLabelText("Select all reviews");
    fireEvent.click(selectAllCheckbox);

    await waitFor(() => {
      expect(onSelectionChange).toHaveBeenCalledWith(expect.any(Set));
      const selectedSet = onSelectionChange.mock.calls[0][0];
      expect(selectedSet.size).toBe(2);
      expect(selectedSet.has("1")).toBe(true);
      expect(selectedSet.has("2")).toBe(true);
    });
  });

  it("should deselect all reviews when select all checkbox is unchecked", async () => {
    const onSelectionChange = vi.fn();

    render(
      <ReviewModerationList
        reviews={mockReviews}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onSelectionChange={onSelectionChange}
      />
    );

    const selectAllCheckbox = screen.getByLabelText("Select all reviews");
    
    // First click to select all
    fireEvent.click(selectAllCheckbox);
    
    // Second click to deselect all
    fireEvent.click(selectAllCheckbox);

    await waitFor(() => {
      const lastCall = onSelectionChange.mock.calls[onSelectionChange.mock.calls.length - 1];
      const selectedSet = lastCall[0];
      expect(selectedSet.size).toBe(0);
    });
  });

  it("should select individual review when checkbox is clicked", async () => {
    const onSelectionChange = vi.fn();

    render(
      <ReviewModerationList
        reviews={mockReviews}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onSelectionChange={onSelectionChange}
      />
    );

    const firstReviewCheckbox = screen.getByLabelText(/Select review from John Doe/);
    fireEvent.click(firstReviewCheckbox);

    await waitFor(() => {
      expect(onSelectionChange).toHaveBeenCalledWith(expect.any(Set));
      const selectedSet = onSelectionChange.mock.calls[0][0];
      expect(selectedSet.size).toBe(1);
      expect(selectedSet.has("1")).toBe(true);
    });
  });

  it("should deselect individual review when checkbox is unchecked", async () => {
    const onSelectionChange = vi.fn();

    render(
      <ReviewModerationList
        reviews={mockReviews}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onSelectionChange={onSelectionChange}
      />
    );

    const firstReviewCheckbox = screen.getByLabelText(/Select review from John Doe/);
    
    // First click to select
    fireEvent.click(firstReviewCheckbox);
    
    // Second click to deselect
    fireEvent.click(firstReviewCheckbox);

    await waitFor(() => {
      const lastCall = onSelectionChange.mock.calls[onSelectionChange.mock.calls.length - 1];
      const selectedSet = lastCall[0];
      expect(selectedSet.size).toBe(0);
    });
  });

  it("should show selection count in header", async () => {
    render(
      <ReviewModerationList
        reviews={mockReviews}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onSelectionChange={vi.fn()}
      />
    );

    const selectAllCheckbox = screen.getByLabelText("Select all reviews");
    fireEvent.click(selectAllCheckbox);

    await waitFor(() => {
      expect(screen.getByText("2 selected")).toBeInTheDocument();
    });
  });

  it("should highlight selected reviews", async () => {
    render(
      <ReviewModerationList
        reviews={mockReviews}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onSelectionChange={vi.fn()}
      />
    );

    const firstReviewCheckbox = screen.getByLabelText(/Select review from John Doe/);
    fireEvent.click(firstReviewCheckbox);

    await waitFor(() => {
      const reviewCards = screen.getAllByText(/John Doe|Jane Smith/);
      // The first review card should have the ring-2 ring-blue-500 class
      expect(reviewCards[0].closest(".ring-2")).toBeInTheDocument();
    });
  });

  it("should maintain selection across multiple interactions", async () => {
    const onSelectionChange = vi.fn();

    render(
      <ReviewModerationList
        reviews={mockReviews}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onSelectionChange={onSelectionChange}
      />
    );

    const firstCheckbox = screen.getByLabelText(/Select review from John Doe/);
    const secondCheckbox = screen.getByLabelText(/Select review from Jane Smith/);

    // Select first
    fireEvent.click(firstCheckbox);
    
    // Select second
    fireEvent.click(secondCheckbox);

    await waitFor(() => {
      const lastCall = onSelectionChange.mock.calls[onSelectionChange.mock.calls.length - 1];
      const selectedSet = lastCall[0];
      expect(selectedSet.size).toBe(2);
      expect(selectedSet.has("1")).toBe(true);
      expect(selectedSet.has("2")).toBe(true);
    });
  });

  it("should still show approve and reject buttons for pending reviews", () => {
    render(
      <ReviewModerationList
        reviews={mockReviews}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onSelectionChange={vi.fn()}
      />
    );

    expect(screen.getAllByText("Approve")).toHaveLength(2);
    expect(screen.getAllByText("Reject")).toHaveLength(2);
  });

  it("should call onApprove when approve button is clicked", () => {
    const onApprove = vi.fn();

    render(
      <ReviewModerationList
        reviews={mockReviews}
        onApprove={onApprove}
        onReject={vi.fn()}
        onSelectionChange={vi.fn()}
      />
    );

    const approveButtons = screen.getAllByText("Approve");
    fireEvent.click(approveButtons[0]);

    expect(onApprove).toHaveBeenCalledWith("1");
  });

  it("should call onReject when reject button is clicked", () => {
    const onReject = vi.fn();

    render(
      <ReviewModerationList
        reviews={mockReviews}
        onApprove={vi.fn()}
        onReject={onReject}
        onSelectionChange={vi.fn()}
      />
    );

    const rejectButtons = screen.getAllByText("Reject");
    fireEvent.click(rejectButtons[0]);

    expect(onReject).toHaveBeenCalledWith("1");
  });
});
