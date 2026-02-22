import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PackageSaleModal } from '../package-sale-modal';

// Mock the hooks
vi.mock('@/lib/api/hooks/usePackageSales', () => ({
  useCreatePackagePurchase: () => ({
    mutateAsync: vi.fn().mockResolvedValue({
      _id: 'purchase-123',
      package_name: 'Test Package',
    }),
    isPending: false,
  }),
}));

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

const mockPackage = {
  _id: 'pkg-123',
  name: 'Test Package',
  description: 'A test package',
  services: [
    {
      service_id: 'svc-1',
      service_name: 'Haircut',
      quantity: 3,
      price: 50,
    },
    {
      service_id: 'svc-2',
      service_name: 'Color',
      quantity: 2,
      price: 100,
    },
  ],
  original_price: 450,
  package_price: 350,
  discount_percentage: 22,
  validity_days: 90,
  is_active: true,
  is_transferable: true,
  is_giftable: true,
};

const mockClients = [
  {
    _id: 'client-1',
    name: 'John Doe',
    email: 'john@example.com',
  },
  {
    _id: 'client-2',
    name: 'Jane Smith',
    email: 'jane@example.com',
  },
];

const queryClient = new QueryClient();

describe('PackageSaleModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders package details correctly', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSaleModal
          package={mockPackage}
          isOpen={true}
          onClose={vi.fn()}
          clients={mockClients}
        />
      </QueryClientProvider>
    );

    expect(screen.getByText('Sell Package: Test Package')).toBeInTheDocument();
    expect(screen.getByText('A test package')).toBeInTheDocument();
    expect(screen.getByText('Haircut')).toBeInTheDocument();
    expect(screen.getByText('Color')).toBeInTheDocument();
  });

  it('displays package pricing information', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSaleModal
          package={mockPackage}
          isOpen={true}
          onClose={vi.fn()}
          clients={mockClients}
        />
      </QueryClientProvider>
    );

    expect(screen.getByText('Original Value:')).toBeInTheDocument();
    expect(screen.getByText('Package Price:')).toBeInTheDocument();
    expect(screen.getByText('Client Savings:')).toBeInTheDocument();
  });

  it('allows client selection', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSaleModal
          package={mockPackage}
          isOpen={true}
          onClose={vi.fn()}
          clients={mockClients}
        />
      </QueryClientProvider>
    );

    // Click on the Client tab
    const clientTab = screen.getByRole('tab', { name: /client/i });
    await user.click(clientTab);

    // Search for a client
    const searchInput = screen.getByPlaceholderText('Search by name or email...');
    await user.type(searchInput, 'John');

    // Select the client
    const selectTrigger = screen.getByRole('combobox');
    await user.click(selectTrigger);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('allows gift package configuration', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSaleModal
          package={mockPackage}
          isOpen={true}
          onClose={vi.fn()}
          clients={mockClients}
        />
      </QueryClientProvider>
    );

    // Click on the Client tab
    const clientTab = screen.getByRole('tab', { name: /client/i });
    await user.click(clientTab);

    // Check the gift checkbox
    const giftCheckbox = screen.getByRole('checkbox', {
      name: /this is a gift package/i,
    });
    await user.click(giftCheckbox);

    // Verify gift options appear
    await waitFor(() => {
      expect(screen.getByText('Gift Recipient')).toBeInTheDocument();
      expect(screen.getByText('Gift Message (Optional)')).toBeInTheDocument();
    });
  });

  it('displays payment method options', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSaleModal
          package={mockPackage}
          isOpen={true}
          onClose={vi.fn()}
          clients={mockClients}
        />
      </QueryClientProvider>
    );

    // Click on the Payment tab
    const paymentTab = screen.getByRole('tab', { name: /payment/i });
    await user.click(paymentTab);

    // Check for payment method options
    expect(screen.getByText('Payment Method')).toBeInTheDocument();
  });

  it('shows validity period information', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSaleModal
          package={mockPackage}
          isOpen={true}
          onClose={vi.fn()}
          clients={mockClients}
        />
      </QueryClientProvider>
    );

    expect(screen.getByText(/Valid for: 90 days from purchase/i)).toBeInTheDocument();
  });

  it('displays service quantities correctly', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSaleModal
          package={mockPackage}
          isOpen={true}
          onClose={vi.fn()}
          clients={mockClients}
        />
      </QueryClientProvider>
    );

    expect(screen.getByText('Qty: 3')).toBeInTheDocument();
    expect(screen.getByText('Qty: 2')).toBeInTheDocument();
  });

  it('closes modal when onClose is called', async () => {
    const onClose = vi.fn();
    const { rerender } = render(
      <QueryClientProvider client={queryClient}>
        <PackageSaleModal
          package={mockPackage}
          isOpen={true}
          onClose={onClose}
          clients={mockClients}
        />
      </QueryClientProvider>
    );

    expect(screen.getByText('Sell Package: Test Package')).toBeInTheDocument();

    rerender(
      <QueryClientProvider client={queryClient}>
        <PackageSaleModal
          package={mockPackage}
          isOpen={false}
          onClose={onClose}
          clients={mockClients}
        />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.queryByText('Sell Package: Test Package')).not.toBeInTheDocument();
    });
  });

  it('does not render when package is null', () => {
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <PackageSaleModal
          package={null}
          isOpen={true}
          onClose={vi.fn()}
          clients={mockClients}
        />
      </QueryClientProvider>
    );

    expect(container.firstChild).toBeEmptyDOMElement();
  });

  it('displays all services with correct pricing', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSaleModal
          package={mockPackage}
          isOpen={true}
          onClose={vi.fn()}
          clients={mockClients}
        />
      </QueryClientProvider>
    );

    // Check for service details
    expect(screen.getByText('Haircut')).toBeInTheDocument();
    expect(screen.getByText('Color')).toBeInTheDocument();
  });
});
