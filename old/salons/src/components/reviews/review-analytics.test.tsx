import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReviewAnalytics } from './review-analytics';

// Mock fetch
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(() => 'test-token'),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

const mockAnalyticsData = {
  period: {
    start_date: '2024-01-01T00:00:00',
    end_date: '2024-01-31T23:59:59'
  },
  filters: {
    service_id: null,
    stylist_id: null
  },
  overall_metrics: {
    average_rating: 4.5,
    total_reviews: 100,
    rating_distribution: {
      '1': 2,
      '2': 5,
      '3': 10,
      '4': 30,
      '5': 53
    },
    response_rate: 75.0,
    responded_count: 75
  },
  rating_trend: [
    {
      date: '2024-01-01',
      average_rating: 4.2,
      total_reviews: 5
    },
    {
      date: '2024-01-02',
      average_rating: 4.5,
      total_reviews: 8
    }
  ],
  service_ratings: [
    {
      service_id: 'service_1',
      service_name: 'Haircut',
      average_rating: 4.6,
      total_reviews: 50
    },
    {
      service_id: 'service_2',
      service_name: 'Color',
      average_rating: 4.4,
      total_reviews: 50
    }
  ],
  stylist_ratings: [
    {
      stylist_id: 'stylist_1',
      stylist_name: 'Jane Smith',
      average_rating: 4.7,
      total_reviews: 40
    },
    {
      stylist_id: 'stylist_2',
      stylist_name: 'Bob Johnson',
      average_rating: 4.3,
      total_reviews: 60
    }
  ],
  response_rate: {
    response_rate: 75.0,
    responded_count: 75,
    total_reviews: 100
  },
  review_volume: [
    {
      date: '2024-01-01',
      total_reviews: 5,
      approved: 4,
      pending: 1,
      rejected: 0
    }
  ],
  monthly_aggregation: [
    {
      month: '2024-01',
      average_rating: 4.5,
      total_reviews: 100,
      rating_distribution: {
        '1': 2,
        '2': 5,
        '3': 10,
        '4': 30,
        '5': 53
      }
    }
  ]
};

describe('ReviewAnalytics', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockAnalyticsData
    });
  });

  it('renders loading state initially', () => {
    (global.fetch as jest.Mock).mockImplementationOnce(
      () => new Promise(() => {}) // Never resolves
    );

    render(<ReviewAnalytics tenantId="test-tenant" />);
    expect(screen.getByText('Loading analytics...')).toBeInTheDocument();
  });

  it('renders analytics data after loading', async () => {
    render(<ReviewAnalytics tenantId="test-tenant" />);

    await waitFor(() => {
      expect(screen.getByText('4.50')).toBeInTheDocument(); // Average rating
      expect(screen.getByText('100')).toBeInTheDocument(); // Total reviews
      expect(screen.getByText('75.0%')).toBeInTheDocument(); // Response rate
    });
  });

  it('displays metric cards', async () => {
    render(<ReviewAnalytics tenantId="test-tenant" />);

    await waitFor(() => {
      expect(screen.getByText('Average Rating')).toBeInTheDocument();
      expect(screen.getByText('Total Reviews')).toBeInTheDocument();
      expect(screen.getByText('Response Rate')).toBeInTheDocument();
      expect(screen.getByText('Responded')).toBeInTheDocument();
    });
  });

  it('displays chart titles', async () => {
    render(<ReviewAnalytics tenantId="test-tenant" />);

    await waitFor(() => {
      expect(screen.getByText('Rating Trend Over Time')).toBeInTheDocument();
      expect(screen.getByText('Service Ratings')).toBeInTheDocument();
      expect(screen.getByText('Stylist Ratings')).toBeInTheDocument();
      expect(screen.getByText('Rating Distribution')).toBeInTheDocument();
      expect(screen.getByText('Review Volume by Status')).toBeInTheDocument();
    });
  });

  it('renders date range buttons', async () => {
    render(<ReviewAnalytics tenantId="test-tenant" />);

    await waitFor(() => {
      expect(screen.getByText('Last 7 Days')).toBeInTheDocument();
      expect(screen.getByText('Last 30 Days')).toBeInTheDocument();
      expect(screen.getByText('Last 90 Days')).toBeInTheDocument();
      expect(screen.getByText('Last Year')).toBeInTheDocument();
    });
  });

  it('handles date range changes', async () => {
    const user = userEvent.setup();
    render(<ReviewAnalytics tenantId="test-tenant" />);

    const button = await screen.findByText('Last 7 Days');
    await user.click(button);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2); // Initial + after click
    });
  });

  it('handles fetch errors', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500
    });

    render(<ReviewAnalytics tenantId="test-tenant" />);

    await waitFor(() => {
      expect(screen.getByText(/Error:/)).toBeInTheDocument();
    });
  });

  it('displays retry button on error', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500
    });

    render(<ReviewAnalytics tenantId="test-tenant" />);

    await waitFor(() => {
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });

  it('calls onDateRangeChange callback', async () => {
    const onDateRangeChange = jest.fn();
    const user = userEvent.setup();

    render(
      <ReviewAnalytics
        tenantId="test-tenant"
        onDateRangeChange={onDateRangeChange}
      />
    );

    const button = await screen.findByText('Last 7 Days');
    await user.click(button);

    await waitFor(() => {
      expect(onDateRangeChange).toHaveBeenCalled();
    });
  });

  it('displays service ratings data', async () => {
    render(<ReviewAnalytics tenantId="test-tenant" />);

    await waitFor(() => {
      expect(screen.getByText('Haircut')).toBeInTheDocument();
      expect(screen.getByText('Color')).toBeInTheDocument();
    });
  });

  it('displays stylist ratings data', async () => {
    render(<ReviewAnalytics tenantId="test-tenant" />);

    await waitFor(() => {
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('Bob Johnson')).toBeInTheDocument();
    });
  });

  it('handles empty analytics data', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ...mockAnalyticsData,
        rating_trend: [],
        service_ratings: [],
        stylist_ratings: [],
        review_volume: []
      })
    });

    render(<ReviewAnalytics tenantId="test-tenant" />);

    await waitFor(() => {
      expect(screen.getByText('No data available')).toBeInTheDocument();
    });
  });

  it('includes authorization header in fetch', async () => {
    render(<ReviewAnalytics tenantId="test-tenant" />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/reviews/analytics'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          })
        })
      );
    });
  });

  it('includes date range in fetch query', async () => {
    render(<ReviewAnalytics tenantId="test-tenant" />);

    await waitFor(() => {
      const call = (global.fetch as jest.Mock).mock.calls[0][0];
      expect(call).toContain('start_date=');
      expect(call).toContain('end_date=');
    });
  });
});
