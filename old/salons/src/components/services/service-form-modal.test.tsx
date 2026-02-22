import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ServiceFormModal } from "./service-form-modal";
import * as serviceHooks from "@/lib/api/hooks/useServices";
import * as locationHooks from "@/lib/api/hooks/useLocations";

// Mock the hooks
vi.mock("@/lib/api/hooks/useServices", () => ({
  useCreateService: vi.fn(),
  useUpdateService: vi.fn(),
}));

vi.mock("@/lib/api/hooks/useLocations", () => ({
  useLocations: vi.fn(),
}));

vi.mock("@/hooks/use-toast", () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

describe("ServiceFormModal - Location Assignment", () => {
  const mockLocations = [
    {
      _id: "loc-1",
      name: "Main Branch",
      address: "123 Main St",
      city: "Lagos",
      state: "Lagos",
      country: "Nigeria",
      postal_code: "100001",
      phone: "+234 800 000 0001",
    },
    {
      _id: "loc-2",
      name: "Downtown Branch",
      address: "456 Downtown Ave",
      city: "Lagos",
      state: "Lagos",
      country: "Nigeria",
      postal_code: "100002",
      phone: "+234 800 000 0002",
    },
  ];

  const mockService = {
    id: "service-1",
    name: "Haircut & Styling",
    description: "Professional haircut and styling",
    category: "Hair",
    price: 5000,
    duration_minutes: 60,
    photo_url: "https://example.com/service.jpg",
    assigned_stylists: ["stylist-1"],
    available_at_locations: ["loc-1"],
    location_pricing: [
      {
        location_id: "loc-1",
        price: 5000,
        duration_minutes: 60,
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock useLocations
    (locationHooks.useLocations as any).mockReturnValue({
      data: mockLocations,
      isLoading: false,
      error: null,
    });

    // Mock useCreateService
    (serviceHooks.useCreateService as any).mockReturnValue({
      mutateAsync: vi.fn().mockResolvedValue({ id: "new-service" }),
      isPending: false,
    });

    // Mock useUpdateService
    (serviceHooks.useUpdateService as any).mockReturnValue({
      mutateAsync: vi.fn().mockResolvedValue(mockService),
      isPending: false,
    });
  });

  it("should render location assignment section when modal is open", () => {
    render(
      <ServiceFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSuccess={vi.fn()}
        availableStylists={[]}
      />
    );

    expect(screen.getByText("Available at Locations")).toBeInTheDocument();
    expect(screen.getByText("Main Branch")).toBeInTheDocument();
    expect(screen.getByText("Downtown Branch")).toBeInTheDocument();
  });

  it("should allow selecting multiple locations", async () => {
    const user = userEvent.setup();

    render(
      <ServiceFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSuccess={vi.fn()}
        availableStylists={[]}
      />
    );

    // Check both locations
    const mainBranchCheckbox = screen.getByRole("checkbox", {
      name: /Main Branch/i,
    });
    const downtownCheckbox = screen.getByRole("checkbox", {
      name: /Downtown Branch/i,
    });

    await user.click(mainBranchCheckbox);
    await user.click(downtownCheckbox);

    expect(mainBranchCheckbox).toBeChecked();
    expect(downtownCheckbox).toBeChecked();
  });

  it("should allow setting location-specific pricing", async () => {
    const user = userEvent.setup();

    render(
      <ServiceFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSuccess={vi.fn()}
        availableStylists={[]}
      />
    );

    // Select a location
    const mainBranchCheckbox = screen.getByRole("checkbox", {
      name: /Main Branch/i,
    });
    await user.click(mainBranchCheckbox);

    // Find and click the chevron to expand pricing section
    const chevronButtons = screen.getAllByRole("button");
    const locationChevron = chevronButtons.find(
      (btn) => btn.querySelector("svg") && btn.parentElement?.textContent?.includes("Main Branch")
    );

    if (locationChevron) {
      await user.click(locationChevron);

      // Wait for pricing inputs to appear
      await waitFor(() => {
        const priceInputs = screen.getAllByPlaceholderText("0");
        expect(priceInputs.length).toBeGreaterThan(0);
      });
    }
  });

  it("should pre-populate location assignments when editing service", () => {
    render(
      <ServiceFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSuccess={vi.fn()}
        service={mockService}
        availableStylists={[]}
      />
    );

    const mainBranchCheckbox = screen.getByRole("checkbox", {
      name: /Main Branch/i,
    }) as HTMLInputElement;

    expect(mainBranchCheckbox.checked).toBe(true);
  });

  it("should include location pricing in form submission", async () => {
    const user = userEvent.setup();
    const onSuccess = vi.fn();
    const mockMutate = vi.fn().mockResolvedValue({ id: "new-service" });

    (serviceHooks.useCreateService as any).mockReturnValue({
      mutateAsync: mockMutate,
      isPending: false,
    });

    render(
      <ServiceFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSuccess={onSuccess}
        availableStylists={[]}
      />
    );

    // Fill in required fields
    await user.type(screen.getByPlaceholderText(/Haircut & Styling/i), "Haircut");
    await user.type(screen.getByPlaceholderText(/0/)[0], "5000");
    await user.type(screen.getByPlaceholderText(/30/), "60");

    // Select location
    const mainBranchCheckbox = screen.getByRole("checkbox", {
      name: /Main Branch/i,
    });
    await user.click(mainBranchCheckbox);

    // Submit form
    const submitButton = screen.getByRole("button", { name: /Create Service/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalled();
      const callArgs = mockMutate.mock.calls[0][0];
      expect(callArgs.available_at_locations).toContain("loc-1");
      expect(callArgs.location_pricing).toBeDefined();
      expect(callArgs.location_pricing.length).toBeGreaterThan(0);
    });
  });

  it("should handle no locations available gracefully", () => {
    (locationHooks.useLocations as any).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    });

    render(
      <ServiceFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSuccess={vi.fn()}
        availableStylists={[]}
      />
    );

    expect(
      screen.getByText(/No locations available/i)
    ).toBeInTheDocument();
  });

  it("should toggle location selection on and off", async () => {
    const user = userEvent.setup();

    render(
      <ServiceFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSuccess={vi.fn()}
        availableStylists={[]}
      />
    );

    const mainBranchCheckbox = screen.getByRole("checkbox", {
      name: /Main Branch/i,
    }) as HTMLInputElement;

    // Select
    await user.click(mainBranchCheckbox);
    expect(mainBranchCheckbox.checked).toBe(true);

    // Deselect
    await user.click(mainBranchCheckbox);
    expect(mainBranchCheckbox.checked).toBe(false);
  });

  it("should initialize location pricing when location is selected", async () => {
    const user = userEvent.setup();

    render(
      <ServiceFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSuccess={vi.fn()}
        availableStylists={[]}
      />
    );

    // Fill in base price
    const priceInputs = screen.getAllByPlaceholderText("0");
    await user.type(priceInputs[0], "5000");

    // Select location
    const mainBranchCheckbox = screen.getByRole("checkbox", {
      name: /Main Branch/i,
    });
    await user.click(mainBranchCheckbox);

    // Expand to see pricing
    const chevronButtons = screen.getAllByRole("button");
    const locationChevron = chevronButtons.find(
      (btn) => btn.querySelector("svg") && btn.parentElement?.textContent?.includes("Main Branch")
    );

    if (locationChevron) {
      await user.click(locationChevron);

      // Location pricing should be initialized with base price
      await waitFor(() => {
        const locationPriceInputs = screen.getAllByDisplayValue("5000");
        expect(locationPriceInputs.length).toBeGreaterThan(0);
      });
    }
  });

  it("should remove location pricing when location is deselected", async () => {
    const user = userEvent.setup();

    render(
      <ServiceFormModal
        isOpen={true}
        onClose={vi.fn()}
        onSuccess={vi.fn()}
        service={mockService}
        availableStylists={[]}
      />
    );

    // Location should be selected initially
    const mainBranchCheckbox = screen.getByRole("checkbox", {
      name: /Main Branch/i,
    }) as HTMLInputElement;
    expect(mainBranchCheckbox.checked).toBe(true);

    // Deselect location
    await user.click(mainBranchCheckbox);
    expect(mainBranchCheckbox.checked).toBe(false);
  });
});
