import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import PackageSalesPage from '../page';

// Mock the hooks
vi.mock('@/lib/api/hooks/usePackageSales', () => ({
  useActivePackages: () => ({
    packages: [
      {
        _id: 'pkg-1',
        name: 'Basic Package',
        description: 'Basic hair services',
        services: [
          {
            service_id: 'svc-1',
            service_name: 'Haircut',
            quantity: 2,
            price: 50,
          },
        ],
        original_price: 100,
        package_price: 80,
        discount_percentage: 20,
        validity_days: 60,
        is_active: true,
        is_transferable: true,
        is_giftable: true,
      },
      {
        _id: 'pkg-2',
        name: 'Premium Package',
        description: 'Premium hair and beauty services',
        services: [
          {
            service_id: 'svc-2',
            service_name: 'Haircut',
            quantity: 3,
            price: 50,
          },
          {
            service_id: 'svc-3',
            service_name: 'Color',
            quantity: 2,
            price: 100,
          },
        ],
        original_price: 350,
        package_price: 280,
        discount_percentage: 20,
        validity_days: 90,
        is_active: true,
        is_transferable: true,
        is_giftable: true,
      },
    ],
    isLoading: false,
    error: null,
  }),
}));

vi.mock('@/lib/api/client', () => ({
  apiClient: {
    get: vi.fn().mockImplementation((url) => {
      if (url.includes('/clients')) {
        return Promise.resolve({
          data: {
            clients: [
              { _id: 'client-1', name: 'John Doe', email: 'john@example.com' },
              { _id: 'client-2', name: 'Jane Smith', email: 'jane@example.com' },
            ],
          },
        });
      }
      if (url.includes('/packages/analytics/sales')) {
        return Promise.resolve({
          data: {
            total_sales: 5000,
            total_packages_sold: 15,
            average_package_price: 333.33,
            total_savings: 1200,
          },
        });
      }
      return Promise.resolve({ data: {} });
    }),
    post: vi.fn().mockResolvedValue({ data: {} }),
  },
}));

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

vi.mock('@/components/packages/package-sale-modal', () => ({
  PackageSaleModal: ({ isOpen, onClose }: any) => (
    isOpen ? <div data-testid="package-sale-modal">Package Sale Modal</div> : null
  ),
}));

vi.mock('@/components/packages/package-receipt', () => ({
  PackageReceipt: ({ isOpen, onClose }: any) => (
    isOpen ? <div data-testid="package-receipt">Package Receipt</div> : null
  ),
}));

const queryClient = new QueryClient();

describe('PackageSalesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders page header', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Package Sales')).toBeInTheDocument();
    });
  });

  it('displays page description', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(
        screen.getByText('Sell service packages to clients and generate receipts')
      ).toBeInTheDocument();
    });
  });

  it('displays sales metrics', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Sales This Month')).toBeInTheDocument();
      expect(screen.getByText('Average Package Value')).toBeInTheDocument();
      expect(screen.getByText('Total Savings Given')).toBeInTheDocument();
    });
  });

  it('displays search input', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(
        screen.getByPlaceholderText('Search packages by name or description...')
      ).toBeInTheDocument();
    });
  });

  it('displays package tabs', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /all packages/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /popular/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /new/i })).toBeInTheDocument();
    });
  });

  it('displays all packages', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Package')).toBeInTheDocument();
      expect(screen.getByText('Premium Package')).toBeInTheDocument();
    });
  });

  it('displays package descriptions', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic hair services')).toBeInTheDocument();
      expect(screen.getByText('Premium hair and beauty services')).toBeInTheDocument();
    });
  });

  it('displays package pricing', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Services:')).toBeInTheDocument();
    });
  });

  it('displays sell package buttons', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      const sellButtons = screen.getAllByRole('button', { name: /sell package/i });
      expect(sellButtons.length).toBeGreaterThan(0);
    });
  });

  it('filters packages by search query', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Package')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(
      'Search packages by name or description...'
    );
    await user.type(searchInput, 'Premium');

    await waitFor(() => {
      expect(screen.getByText('Premium Package')).toBeInTheDocument();
      expect(screen.queryByText('Basic Package')).not.toBeInTheDocument();
    });
  });

  it('opens sale modal when package is selected', async () => {
    const user = userEvent.setup();
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Package')).toBeInTheDocument();
    });

    const sellButton = screen.getAllByRole('button', { name: /sell package/i })[0];
    await user.click(sellButton);

    await waitFor(() => {
      expect(screen.getByTestId('package-sale-modal')).toBeInTheDocument();
    });
  });

  it('displays package services with quantities', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Haircut (x2)')).toBeInTheDocument();
      expect(screen.getByText('Haircut (x3)')).toBeInTheDocument();
    });
  });

  it('displays package validity information', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Valid for 60 days')).toBeInTheDocument();
      expect(screen.getByText('Valid for 90 days')).toBeInTheDocument();
    });
  });

  it('displays giftable badge for giftable packages', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      const giftableBadges = screen.getAllByText('Giftable');
      expect(giftableBadges.length).toBeGreaterThan(0);
    });
  });

  it('displays package savings', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Savings:')).toBeInTheDocument();
    });
  });

  it('displays original and package prices', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PackageSalesPage />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Original:')).toBeInTheDocument();
      expect(screen.getByText('Package Price:')).toBeInTheDocument();
    });
  });
});
