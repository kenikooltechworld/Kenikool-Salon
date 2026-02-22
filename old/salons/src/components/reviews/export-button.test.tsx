import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ExportButton } from "./export-button";
import * as useClientReviewsModule from "@/lib/api/hooks/useClientReviews";

// Mock the hooks
jest.mock("@/lib/api/hooks/useClientReviews");
jest.mock("@/lib/utils/toast");

describe("ExportButton", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient();
    jest.clearAllMocks();
  });

  const renderWithProviders = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    );
  };

  it("renders export button", () => {
    const mockMutation = {
      mutateAsync: jest.fn(),
      isPending: false,
    };
    jest
      .spyOn(useClientReviewsModule, "useExportReviews")
      .mockReturnValue(mockMutation as any);

    renderWithProviders(<ExportButton />);

    expect(screen.getByText("Export")).toBeInTheDocument();
  });

  it("opens dropdown menu when clicked", async () => {
    const mockMutation = {
      mutateAsync: jest.fn(),
      isPending: false,
    };
    jest
      .spyOn(useClientReviewsModule, "useExportReviews")
      .mockReturnValue(mockMutation as any);

    renderWithProviders(<ExportButton />);

    const button = screen.getByText("Export");
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText("Export as CSV")).toBeInTheDocument();
      expect(screen.getByText("Export as PDF")).toBeInTheDocument();
    });
  });

  it("calls export with CSV format when CSV option clicked", async () => {
    const mockMutateAsync = jest.fn().mockResolvedValue({ success: true });
    const mockMutation = {
      mutateAsync: mockMutateAsync,
      isPending: false,
    };
    jest
      .spyOn(useClientReviewsModule, "useExportReviews")
      .mockReturnValue(mockMutation as any);

    renderWithProviders(<ExportButton />);

    const button = screen.getByText("Export");
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText("Export as CSV")).toBeInTheDocument();
    });

    const csvOption = screen.getByText("Export as CSV");
    fireEvent.click(csvOption);

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith({
        format: "csv",
        filters: undefined,
      });
    });
  });

  it("calls export with PDF format when PDF option clicked", async () => {
    const mockMutateAsync = jest.fn().mockResolvedValue({ success: true });
    const mockMutation = {
      mutateAsync: mockMutateAsync,
      isPending: false,
    };
    jest
      .spyOn(useClientReviewsModule, "useExportReviews")
      .mockReturnValue(mockMutation as any);

    renderWithProviders(<ExportButton />);

    const button = screen.getByText("Export");
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText("Export as PDF")).toBeInTheDocument();
    });

    const pdfOption = screen.getByText("Export as PDF");
    fireEvent.click(pdfOption);

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith({
        format: "pdf",
        filters: undefined,
      });
    });
  });

  it("passes filters to export mutation", async () => {
    const mockMutateAsync = jest.fn().mockResolvedValue({ success: true });
    const mockMutation = {
      mutateAsync: mockMutateAsync,
      isPending: false,
    };
    jest
      .spyOn(useClientReviewsModule, "useExportReviews")
      .mockReturnValue(mockMutation as any);

    const filters = {
      status: "approved" as const,
      rating: [4, 5],
      skip: 0,
      limit: 20,
    };

    renderWithProviders(<ExportButton filters={filters} />);

    const button = screen.getByText("Export");
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText("Export as CSV")).toBeInTheDocument();
    });

    const csvOption = screen.getByText("Export as CSV");
    fireEvent.click(csvOption);

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith({
        format: "csv",
        filters,
      });
    });
  });

  it("disables button when disabled prop is true", () => {
    const mockMutation = {
      mutateAsync: jest.fn(),
      isPending: false,
    };
    jest
      .spyOn(useClientReviewsModule, "useExportReviews")
      .mockReturnValue(mockMutation as any);

    renderWithProviders(<ExportButton disabled={true} />);

    const button = screen.getByText("Export");
    expect(button).toBeDisabled();
  });

  it("shows loading state during export", () => {
    const mockMutation = {
      mutateAsync: jest.fn(),
      isPending: true,
    };
    jest
      .spyOn(useClientReviewsModule, "useExportReviews")
      .mockReturnValue(mockMutation as any);

    renderWithProviders(<ExportButton />);

    expect(screen.getByText("Exporting...")).toBeInTheDocument();
  });

  it("closes dropdown after successful export", async () => {
    const mockMutateAsync = jest.fn().mockResolvedValue({ success: true });
    const mockMutation = {
      mutateAsync: mockMutateAsync,
      isPending: false,
    };
    jest
      .spyOn(useClientReviewsModule, "useExportReviews")
      .mockReturnValue(mockMutation as any);

    renderWithProviders(<ExportButton />);

    const button = screen.getByText("Export");
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText("Export as CSV")).toBeInTheDocument();
    });

    const csvOption = screen.getByText("Export as CSV");
    fireEvent.click(csvOption);

    await waitFor(() => {
      expect(screen.queryByText("Export as CSV")).not.toBeInTheDocument();
    });
  });
});
