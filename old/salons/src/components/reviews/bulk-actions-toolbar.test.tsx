import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BulkActionsToolbar } from "./bulk-actions-toolbar";
import { describe, it, expect, vi } from "vitest";

describe("BulkActionsToolbar", () => {
  it("should not render when no reviews are selected", () => {
    const { container } = render(
      <BulkActionsToolbar
        selectedIds={new Set()}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={vi.fn()}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  it("should render when reviews are selected", () => {
    const selectedIds = new Set(["1", "2", "3"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={vi.fn()}
      />
    );

    expect(screen.getByText("3 reviews selected")).toBeInTheDocument();
  });

  it("should display correct selection count", () => {
    const selectedIds = new Set(["1"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={vi.fn()}
      />
    );

    expect(screen.getByText("1 review selected")).toBeInTheDocument();
  });

  it("should show approve button", () => {
    const selectedIds = new Set(["1"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={vi.fn()}
      />
    );

    expect(screen.getByText("Approve All")).toBeInTheDocument();
  });

  it("should show reject button", () => {
    const selectedIds = new Set(["1"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={vi.fn()}
      />
    );

    expect(screen.getByText("Reject All")).toBeInTheDocument();
  });

  it("should show delete button", () => {
    const selectedIds = new Set(["1"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={vi.fn()}
      />
    );

    expect(screen.getByText("Delete All")).toBeInTheDocument();
  });

  it("should show clear button", () => {
    const selectedIds = new Set(["1"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={vi.fn()}
      />
    );

    expect(screen.getByText("Clear")).toBeInTheDocument();
  });

  it("should call onClear when clear button is clicked", async () => {
    const onClear = vi.fn();
    const selectedIds = new Set(["1"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={onClear}
      />
    );

    const clearButton = screen.getByText("Clear");
    fireEvent.click(clearButton);

    expect(onClear).toHaveBeenCalled();
  });

  it("should show approve confirmation dialog when approve button is clicked", async () => {
    const selectedIds = new Set(["1", "2"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={vi.fn()}
      />
    );

    const approveButton = screen.getByText("Approve All");
    fireEvent.click(approveButton);

    await waitFor(() => {
      expect(screen.getByText("Approve Reviews")).toBeInTheDocument();
      expect(screen.getByText(/Are you sure you want to approve 2 reviews/)).toBeInTheDocument();
    });
  });

  it("should show reject confirmation dialog when reject button is clicked", async () => {
    const selectedIds = new Set(["1", "2"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={vi.fn()}
      />
    );

    const rejectButton = screen.getByText("Reject All");
    fireEvent.click(rejectButton);

    await waitFor(() => {
      expect(screen.getByText("Reject Reviews")).toBeInTheDocument();
      expect(screen.getByText(/Are you sure you want to reject 2 reviews/)).toBeInTheDocument();
    });
  });

  it("should show delete confirmation dialog when delete button is clicked", async () => {
    const selectedIds = new Set(["1", "2"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={vi.fn()}
      />
    );

    const deleteButton = screen.getByText("Delete All");
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(screen.getByText("Delete Reviews")).toBeInTheDocument();
      expect(screen.getByText(/Are you sure you want to delete 2 reviews/)).toBeInTheDocument();
    });
  });

  it("should call onApprove with selected IDs when confirmed", async () => {
    const onApprove = vi.fn().mockResolvedValue(undefined);
    const selectedIds = new Set(["1", "2"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={onApprove}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={vi.fn()}
      />
    );

    const approveButton = screen.getByText("Approve All");
    fireEvent.click(approveButton);

    await waitFor(() => {
      expect(screen.getByText("Approve Reviews")).toBeInTheDocument();
    });

    const confirmButton = screen.getByRole("button", { name: /Approve/ });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(onApprove).toHaveBeenCalledWith(["1", "2"]);
    });
  });

  it("should call onReject with selected IDs when confirmed", async () => {
    const onReject = vi.fn().mockResolvedValue(undefined);
    const selectedIds = new Set(["1", "2"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={onReject}
        onDelete={vi.fn()}
        onClear={vi.fn()}
      />
    );

    const rejectButton = screen.getByText("Reject All");
    fireEvent.click(rejectButton);

    await waitFor(() => {
      expect(screen.getByText("Reject Reviews")).toBeInTheDocument();
    });

    const confirmButton = screen.getByRole("button", { name: /Reject/ });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(onReject).toHaveBeenCalledWith(["1", "2"]);
    });
  });

  it("should call onDelete with selected IDs when confirmed", async () => {
    const onDelete = vi.fn().mockResolvedValue(undefined);
    const selectedIds = new Set(["1", "2"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={onDelete}
        onClear={vi.fn()}
      />
    );

    const deleteButton = screen.getByText("Delete All");
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(screen.getByText("Delete Reviews")).toBeInTheDocument();
    });

    const confirmButton = screen.getByRole("button", { name: /Delete/ });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(onDelete).toHaveBeenCalledWith(["1", "2"]);
    });
  });

  it("should disable buttons when loading", () => {
    const selectedIds = new Set(["1"]);

    render(
      <BulkActionsToolbar
        selectedIds={selectedIds}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onDelete={vi.fn()}
        onClear={vi.fn()}
        isLoading={true}
      />
    );

    expect(screen.getByText("Approve All")).toBeDisabled();
    expect(screen.getByText("Reject All")).toBeDisabled();
    expect(screen.getByText("Delete All")).toBeDisabled();
    expect(screen.getByText("Clear")).toBeDisabled();
  });
});
