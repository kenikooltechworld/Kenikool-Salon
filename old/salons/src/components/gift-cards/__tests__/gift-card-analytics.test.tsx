import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import GiftCardAnalytics from '../gift-card-analytics';

// Mock fetch
global.fetch = jest.fn();

const mockAnalyticsData = {
  total_sold: 500000,
  total_redeemed: 300000,
  outstanding_liability: 200000,
  redemption_rate: 60,
  expiration_rate: 5,
  average_card_value: 50000,
  total_cards_created: 10,
  total_cards_redeemed: 6,
  total_cards_expired: 1,
  card_type_breakdown: {
    digital: 7,
    physical: 3,
  },
  top_purchasers: [
    { name: 'John Doe', count: 5, amount: 250000 },
    { name: 'Jane Smith', count: 3, amount: 150000 },
  ],
  top_recipients: [
    { name: 'Alice Johnson', count: 4, amount: 200000 },
    { name: 'Bob Wilson', count: 3, amount: 150000 },
  ],
};

describe('GiftCardAnalytics', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockAnalyticsData),
    });
  });

  it('renders analytics dashboard with title', async () => {
    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('Gift Card Analytics')).toBeInTheDocument();
    });
  });

  it('displays key metrics', async () => {
    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('Total Sold')).toBeInTheDocument();
      expect(screen.getByText('Total Redeemed')).toBeInTheDocument();
      expect(screen.getByText('Outstanding Liability')).toBeInTheDocument();
    });
  });

  it('displays redemption rate', async () => {
    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('Redemption Rate')).toBeInTheDocument();
      expect(screen.getByText('60.0%')).toBeInTheDocument();
    });
  });

  it('displays expiration rate', async () => {
    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('Expiration Rate')).toBeInTheDocument();
      expect(screen.getByText('5.0%')).toBeInTheDocument();
    });
  });

  it('displays average card value', async () => {
    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('Average Card Value')).toBeInTheDocument();
    });
  });

  it('displays card type breakdown', async () => {
    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('Card Type Breakdown')).toBeInTheDocument();
      expect(screen.getByText('Digital Cards')).toBeInTheDocument();
      expect(screen.getByText('Physical Cards')).toBeInTheDocument();
    });
  });

  it('displays top purchasers', async () => {
    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('Top Purchasers')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('displays top recipients', async () => {
    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('Top Recipients')).toBeInTheDocument();
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
    });
  });

  it('displays export buttons', async () => {
    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('Export CSV')).toBeInTheDocument();
      expect(screen.getByText('Export PDF')).toBeInTheDocument();
    });
  });

  it('displays date range filter', async () => {
    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('Date Range')).toBeInTheDocument();
    });
  });

  it('allows filtering by date range', async () => {
    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      const fromInput = screen.getByDisplayValue('');
      expect(fromInput).toBeInTheDocument();
    });
  });

  it('handles export CSV', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockAnalyticsData),
    });

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      blob: () => Promise.resolve(new Blob(['csv data'])),
    });

    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      const exportCSVButton = screen.getAllByText('Export CSV')[0];
      fireEvent.click(exportCSVButton);
    });
  });

  it('handles export PDF', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockAnalyticsData),
    });

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      blob: () => Promise.resolve(new Blob(['pdf data'])),
    });

    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      const exportPDFButton = screen.getAllByText('Export PDF')[0];
      fireEvent.click(exportPDFButton);
    });
  });

  it('displays loading state', () => {
    (global.fetch as jest.Mock).mockImplementationOnce(
      () => new Promise(() => {}) // Never resolves
    );

    render(<GiftCardAnalytics tenantId="test-tenant" />);
    expect(screen.getByText('Loading analytics...')).toBeInTheDocument();
  });

  it('displays error state', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ detail: 'Failed to load analytics' }),
    });

    render(<GiftCardAnalytics tenantId="test-tenant" />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load analytics')).toBeInTheDocument();
    });
  });
});
