import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import '@testing-library/jest-dom';
import { ReviewWidget } from './review-widget';

// Mock fetch
global.fetch = vi.fn();

describe('ReviewWidget', () => {
  const mockReviews = [
    {
      _id: '1',
      client_name: 'Alice Johnson',
      rating: 5,
      comment: 'Excellent service and very professional!',
      created_at: '2024-01-15T10:00:00Z',
      service_name: 'Hair Styling'
    },
    {
      _id: '2',
      client_name: 'Bob Smith',
      rating: 4,
      comment: 'Great experience, will come back',
      created_at: '2024-01-14T10:00:00Z',
      service_name: 'Haircut'
    },
    {
      _id: '3',
      client_name: 'Carol White',
      rating: 5,
      comment: 'Amazing results!',
      created_at: '2024-01-13T10:00:00Z',
      service_name: 'Color Treatment'
    }
  ];

  const mockStats = {
    average_rating: 4.7,
    total_reviews: 15
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        reviews: mockReviews,
        stats: mockStats
      })
    });
  });

  describe('Rendering', () => {
    it('renders loading state initially', () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );
      expect(screen.getByText('Loading reviews...')).toBeInTheDocument();
    });

    it('renders widget header with title', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );
      await waitFor(() => {
        expect(screen.getByText('Customer Reviews')).toBeInTheDocument();
      });
    });

    it('renders average rating in header', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );
      await waitFor(() => {
        expect(screen.getByText('4.7')).toBeInTheDocument();
      });
    });

    it('renders total review count', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );
      await waitFor(() => {
        expect(screen.getByText(/Based on 15 reviews/)).toBeInTheDocument();
      });
    });

    it('renders all reviews', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );
      await waitFor(() => {
        expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
        expect(screen.getByText('Bob Smith')).toBeInTheDocument();
        expect(screen.getByText('Carol White')).toBeInTheDocument();
      });
    });

    it('renders review comments', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );
      await waitFor(() => {
        expect(screen.getByText('Excellent service and very professional!')).toBeInTheDocument();
        expect(screen.getByText('Great experience, will come back')).toBeInTheDocument();
      });
    });

    it('renders service names', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );
      await waitFor(() => {
        expect(screen.getByText('Hair Styling')).toBeInTheDocument();
        expect(screen.getByText('Haircut')).toBeInTheDocument();
      });
    });

    it('renders "View all reviews" link', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );
      await waitFor(() => {
        const link = screen.getByText('View all reviews');
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute('href', '/salons/tenant123/reviews');
      });
    });

    it('truncates long comments', async () => {
      const longCommentReviews = [
        {
          _id: '1',
          client_name: 'Test User',
          rating: 5,
          comment: 'A'.repeat(150),
          created_at: '2024-01-15T10:00:00Z',
          service_name: 'Service'
        }
      ];

      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({
          reviews: longCommentReviews,
          stats: mockStats
        })
      });

      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        const comment = screen.getByText(/A+\.\.\./);
        expect(comment).toBeInTheDocument();
      });
    });
  });

  describe('Data Fetching', () => {
    it('fetches reviews from correct endpoint', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
          apiBaseUrl="http://localhost:8000"
        />
      );

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          'http://localhost:8000/api/reviews/widget/tenant123?limit=5'
        );
      });
    });

    it('uses default API base URL', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
        const callUrl = (global.fetch as any).mock.calls[0][0];
        expect(callUrl).toContain('/api/reviews/widget/tenant123');
      });
    });

    it('respects maxReviews config', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 10 }}
          apiBaseUrl="http://localhost:8000"
        />
      );

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          'http://localhost:8000/api/reviews/widget/tenant123?limit=10'
        );
      });
    });

    it('refetches when tenantId changes', async () => {
      const { rerender } = render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
          apiBaseUrl="http://localhost:8000"
        />
      );

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(1);
      });

      rerender(
        <ReviewWidget
          tenantId="tenant456"
          config={{ maxReviews: 5 }}
          apiBaseUrl="http://localhost:8000"
        />
      );

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(2);
        expect(global.fetch).toHaveBeenLastCalledWith(
          'http://localhost:8000/api/reviews/widget/tenant456?limit=5'
        );
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message on fetch failure', async () => {
      (global.fetch as any).mockResolvedValue({
        ok: false,
        status: 500
      });

      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/Error:/)).toBeInTheDocument();
      });
    });

    it('displays error message on network error', async () => {
      (global.fetch as any).mockRejectedValue(
        new Error('Network error')
      );

      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/Error:/)).toBeInTheDocument();
      });
    });

    it('displays "No reviews yet" when reviews array is empty', async () => {
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({
          reviews: [],
          stats: { average_rating: 0, total_reviews: 0 }
        })
      });

      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('No reviews yet')).toBeInTheDocument();
      });
    });
  });

  describe('Styling and Configuration', () => {
    it('applies custom primary color', async () => {
      const { container } = render(
        <ReviewWidget
          tenantId="tenant123"
          config={{
            maxReviews: 5,
            colors: {
              primary: '#ff0000',
              background: '#ffffff',
              text: '#000000'
            }
          }}
        />
      );

      await waitFor(() => {
        const widget = container.querySelector('[style*="background-color"]');
        expect(widget).toBeInTheDocument();
      });
    });

    it('applies custom background color', async () => {
      const { container } = render(
        <ReviewWidget
          tenantId="tenant123"
          config={{
            maxReviews: 5,
            colors: {
              primary: '#3b82f6',
              background: '#f3f4f6',
              text: '#1f2937'
            }
          }}
        />
      );

      await waitFor(() => {
        expect(container.firstChild).toBeInTheDocument();
      });
    });

    it('applies custom text color', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{
            maxReviews: 5,
            colors: {
              primary: '#3b82f6',
              background: '#ffffff',
              text: '#ff0000'
            }
          }}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Customer Reviews')).toBeInTheDocument();
      });
    });

    it('uses default colors when not provided', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Customer Reviews')).toBeInTheDocument();
      });
    });

    it('applies grid layout when configured', async () => {
      const { container } = render(
        <ReviewWidget
          tenantId="tenant123"
          config={{
            maxReviews: 5,
            layout: 'grid'
          }}
        />
      );

      await waitFor(() => {
        const reviewsContainer = container.querySelector('[class*="grid"]');
        expect(reviewsContainer).toBeInTheDocument();
      });
    });

    it('applies list layout when configured', async () => {
      const { container } = render(
        <ReviewWidget
          tenantId="tenant123"
          config={{
            maxReviews: 5,
            layout: 'list'
          }}
        />
      );

      await waitFor(() => {
        expect(container.firstChild).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Layout', () => {
    it('renders responsive grid layout', async () => {
      const { container } = render(
        <ReviewWidget
          tenantId="tenant123"
          config={{
            maxReviews: 5,
            layout: 'grid'
          }}
        />
      );

      await waitFor(() => {
        const widget = container.firstChild;
        expect(widget).toHaveClass('w-full');
      });
    });

    it('renders with proper spacing', async () => {
      const { container } = render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        const widget = container.firstChild;
        expect(widget).toHaveClass('rounded-lg');
      });
    });
  });

  describe('Edge Cases', () => {
    it('handles reviews with missing optional fields', async () => {
      const reviewsWithMissingFields = [
        {
          _id: '1',
          client_name: 'Test User',
          rating: 5,
          created_at: '2024-01-15T10:00:00Z'
          // comment and service_name are missing
        }
      ];

      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({
          reviews: reviewsWithMissingFields,
          stats: mockStats
        })
      });

      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument();
      });
    });

    it('handles single review', async () => {
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({
          reviews: [mockReviews[0]],
          stats: { average_rating: 5, total_reviews: 1 }
        })
      });

      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/Based on 1 review/)).toBeInTheDocument();
      });
    });

    it('handles zero rating', async () => {
      const zeroRatingReview = [
        {
          _id: '1',
          client_name: 'Test User',
          rating: 0,
          comment: 'No rating',
          created_at: '2024-01-15T10:00:00Z',
          service_name: 'Service'
        }
      ];

      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({
          reviews: zeroRatingReview,
          stats: mockStats
        })
      });

      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument();
      });
    });

    it('handles very long client names', async () => {
      const longNameReview = [
        {
          _id: '1',
          client_name: 'A'.repeat(100),
          rating: 5,
          comment: 'Good service',
          created_at: '2024-01-15T10:00:00Z',
          service_name: 'Service'
        }
      ];

      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => ({
          reviews: longNameReview,
          stats: mockStats
        })
      });

      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/A+/)).toBeInTheDocument();
      });
    });
  });

  describe('Link Behavior', () => {
    it('opens review page in new tab', async () => {
      render(
        <ReviewWidget
          tenantId="tenant123"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        const link = screen.getByText('View all reviews');
        expect(link).toHaveAttribute('target', '_blank');
        expect(link).toHaveAttribute('rel', 'noopener noreferrer');
      });
    });

    it('uses correct tenant ID in link', async () => {
      render(
        <ReviewWidget
          tenantId="custom-tenant-id"
          config={{ maxReviews: 5 }}
        />
      );

      await waitFor(() => {
        const link = screen.getByText('View all reviews');
        expect(link).toHaveAttribute('href', '/salons/custom-tenant-id/reviews');
      });
    });
  });
});
