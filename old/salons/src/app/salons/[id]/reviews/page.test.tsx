import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PublicReviewsPage from './page';

// Mock fetch
global.fetch = jest.fn();

const mockReviews = [
  {
    _id: '1',
    client_name: 'John Doe',
    rating: 5,
    comment: 'Great service!',
    created_at: '2024-01-15T10:00:00Z',
    booking_id: 'booking1',
    service_name: 'Haircut',
    stylist_name: 'Jane Smith'
  },
  {
    _id: '2',
    client_name: 'Jane Doe',
    rating: 4,
    comment: 'Good experience',
    created_at: '2024-01-14T10:00:00Z',
    booking_id: 'booking2',
    service_name: 'Color',
    stylist_name: 'Jane Smith'
  }
];

const mockAggregation = {
  average_rating: 4.5,
  total_reviews: 2,
  rating_distribution: {
    '1': 0,
    '2': 0,
    '3': 0,
    '4': 1,
    '5': 1
  }
};

describe('PublicReviewsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the page title', async () => {
    (global.fetch as jest.Mock).mockImplementation((url) => {
      if (url.includes('/aggregation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAggregation)
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ reviews: mockReviews, total: 2 })
      });
    });

    render(<PublicReviewsPage params={{ id: 'salon123' }} />);

    await waitFor(() => {
      expect(screen.getByText('Customer Reviews')).toBeInTheDocument();
    });
  });

  it('displays loading state initially', () => {
    (global.fetch as jest.Mock).mockImplementation(() => new Promise(() => {}));

    render(<PublicReviewsPage params={{ id: 'salon123' }} />);

    expect(screen.getByText('Loading reviews...')).toBeInTheDocument();
  });

  it('displays reviews after loading', async () => {
    (global.fetch as jest.Mock).mockImplementation((url) => {
      if (url.includes('/aggregation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAggregation)
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ reviews: mockReviews, total: 2 })
      });
    });

    render(<PublicReviewsPage params={{ id: 'salon123' }} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    });
  });

  it('displays average rating', async () => {
    (global.fetch as jest.Mock).mockImplementation((url) => {
      if (url.includes('/aggregation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAggregation)
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ reviews: mockReviews, total: 2 })
      });
    });

    render(<PublicReviewsPage params={{ id: 'salon123' }} />);

    await waitFor(() => {
      expect(screen.getByText('4.5')).toBeInTheDocument();
    });
  });

  it('displays verified purchase badge for reviews with booking_id', async () => {
    (global.fetch as jest.Mock).mockImplementation((url) => {
      if (url.includes('/aggregation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAggregation)
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ reviews: mockReviews, total: 2 })
      });
    });

    render(<PublicReviewsPage params={{ id: 'salon123' }} />);

    await waitFor(() => {
      const badges = screen.getAllByText(/Verified Purchase/);
      expect(badges.length).toBeGreaterThan(0);
    });
  });

  it('displays error message on fetch failure', async () => {
    (global.fetch as jest.Mock).mockImplementation(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ error: 'Failed to fetch' })
      })
    );

    render(<PublicReviewsPage params={{ id: 'salon123' }} />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to/)).toBeInTheDocument();
    });
  });

  it('displays empty state when no reviews', async () => {
    (global.fetch as jest.Mock).mockImplementation((url) => {
      if (url.includes('/aggregation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            average_rating: 0,
            total_reviews: 0,
            rating_distribution: { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0 }
          })
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ reviews: [], total: 0 })
      });
    });

    render(<PublicReviewsPage params={{ id: 'salon123' }} />);

    await waitFor(() => {
      expect(screen.getByText(/No reviews yet/)).toBeInTheDocument();
    });
  });

  it('handles pagination', async () => {
    const manyReviews = Array.from({ length: 25 }, (_, i) => ({
      ...mockReviews[0],
      _id: `${i}`,
      client_name: `Client ${i}`
    }));

    (global.fetch as jest.Mock).mockImplementation((url) => {
      if (url.includes('/aggregation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAggregation)
        });
      }
      // Return first page
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          reviews: manyReviews.slice(0, 10),
          total: 25
        })
      });
    });

    render(<PublicReviewsPage params={{ id: 'salon123' }} />);

    await waitFor(() => {
      expect(screen.getByText('Page 1 of 3')).toBeInTheDocument();
    });
  });

  it('sorts reviews by date', async () => {
    (global.fetch as jest.Mock).mockImplementation((url) => {
      if (url.includes('/aggregation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAggregation)
        });
      }
      if (url.includes('sort_by=created_at')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ reviews: mockReviews, total: 2 })
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ reviews: mockReviews, total: 2 })
      });
    });

    render(<PublicReviewsPage params={{ id: 'salon123' }} />);

    await waitFor(() => {
      const newestButton = screen.getByText(/Newest/);
      fireEvent.click(newestButton);
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('sort_by=created_at')
      );
    });
  });

  it('sorts reviews by rating', async () => {
    (global.fetch as jest.Mock).mockImplementation((url) => {
      if (url.includes('/aggregation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAggregation)
        });
      }
      if (url.includes('sort_by=rating')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ reviews: mockReviews, total: 2 })
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ reviews: mockReviews, total: 2 })
      });
    });

    render(<PublicReviewsPage params={{ id: 'salon123' }} />);

    await waitFor(() => {
      const ratedButton = screen.getByText(/Highest Rated/);
      fireEvent.click(ratedButton);
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('sort_by=rating')
      );
    });
  });

  it('displays review comments', async () => {
    (global.fetch as jest.Mock).mockImplementation((url) => {
      if (url.includes('/aggregation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAggregation)
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ reviews: mockReviews, total: 2 })
      });
    });

    render(<PublicReviewsPage params={{ id: 'salon123' }} />);

    await waitFor(() => {
      expect(screen.getByText('Great service!')).toBeInTheDocument();
      expect(screen.getByText('Good experience')).toBeInTheDocument();
    });
  });

  it('displays service and stylist names', async () => {
    (global.fetch as jest.Mock).mockImplementation((url) => {
      if (url.includes('/aggregation')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockAggregation)
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ reviews: mockReviews, total: 2 })
      });
    });

    render(<PublicReviewsPage params={{ id: 'salon123' }} />);

    await waitFor(() => {
      expect(screen.getByText(/Haircut.*Jane Smith/)).toBeInTheDocument();
    });
  });
});
