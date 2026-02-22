import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import GiftCardDashboard from '../gift-card-dashboard';

// Mock the hooks
jest.mock('@/lib/api/hooks/useGiftCardDashboard', () => ({
  useGiftCardDashboard: () => ({
    listCards: jest.fn().mockResolvedValue({
      cards: [
        {
          id: '1',
          card_number: 'GC-123456789',
          balance: 50000,
          status: 'active',
          card_type: 'digital',
          created_at: '2024-01-01T00:00:00Z',
          expires_at: '2025-01-01T00:00:00Z',
          recipient_name: 'John Doe',
          recipient_email: 'john@example.com',
        },
      ],
      total: 1,
      page: 1,
      limit: 20,
    }),
    loading: false,
    error: null,
    cards: [
      {
        id: '1',
        card_number: 'GC-123456789',
        balance: 50000,
        status: 'active',
        card_type: 'digital',
        created_at: '2024-01-01T00:00:00Z',
        expires_at: '2025-01-01T00:00:00Z',
        recipient_name: 'John Doe',
        recipient_email: 'john@example.com',
      },
    ],
    total: 1,
  }),
}));

// Mock fetch for analytics
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () =>
      Promise.resolve({
        total_sold: 100000,
        total_redeemed: 50000,
        outstanding_liability: 50000,
        expiration_rate: 5,
      }),
  })
) as jest.Mock;

describe('GiftCardDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders dashboard with title', () => {
    render(<GiftCardDashboard tenantId="test-tenant" />);
    expect(screen.getByText('Gift Cards')).toBeInTheDocument();
  });

  it('displays key metrics', async () => {
    render(<GiftCardDashboard tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('Total Sold')).toBeInTheDocument();
      expect(screen.getByText('Total Redeemed')).toBeInTheDocument();
      expect(screen.getByText('Outstanding Liability')).toBeInTheDocument();
      expect(screen.getByText('Expiration Rate')).toBeInTheDocument();
    });
  });

  it('displays create button', () => {
    render(<GiftCardDashboard tenantId="test-tenant" />);
    expect(screen.getByText('Create Gift Card')).toBeInTheDocument();
  });

  it('displays export buttons', () => {
    render(<GiftCardDashboard tenantId="test-tenant" />);
    expect(screen.getByText('Export CSV')).toBeInTheDocument();
    expect(screen.getByText('Export PDF')).toBeInTheDocument();
  });

  it('displays filter options', () => {
    render(<GiftCardDashboard tenantId="test-tenant" />);
    expect(screen.getByText('Filters & Search')).toBeInTheDocument();
  });

  it('displays gift card list', async () => {
    render(<GiftCardDashboard tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('GC-123456789')).toBeInTheDocument();
    });
  });

  it('filters by status', async () => {
    render(<GiftCardDashboard tenantId="test-tenant" />);
    
    const statusSelect = screen.getByDisplayValue('All Statuses');
    fireEvent.change(statusSelect, { target: { value: 'active' } });
    
    await waitFor(() => {
      expect(statusSelect).toHaveValue('active');
    });
  });

  it('filters by type', async () => {
    render(<GiftCardDashboard tenantId="test-tenant" />);
    
    const typeSelect = screen.getByDisplayValue('All Types');
    fireEvent.change(typeSelect, { target: { value: 'digital' } });
    
    await waitFor(() => {
      expect(typeSelect).toHaveValue('digital');
    });
  });

  it('searches by query', async () => {
    render(<GiftCardDashboard tenantId="test-tenant" />);
    
    const searchInput = screen.getByPlaceholderText('Card number, name, email...');
    fireEvent.change(searchInput, { target: { value: 'GC-123' } });
    
    await waitFor(() => {
      expect(searchInput).toHaveValue('GC-123');
    });
  });
});
