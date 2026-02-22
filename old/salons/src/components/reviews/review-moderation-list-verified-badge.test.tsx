import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ReviewModerationList } from './review-moderation-list';

describe('ReviewModerationList - Verified Badge', () => {
  const mockReviewWithBooking = {
    _id: '1',
    client_name: 'John Doe',
    rating: 5,
    comment: 'Great service!',
    status: 'approved' as const,
    created_at: '2024-01-15T10:00:00Z',
    booking_id: 'booking123'
  };

  const mockReviewWithoutBooking = {
    _id: '2',
    client_name: 'Jane Doe',
    rating: 4,
    comment: 'Good experience',
    status: 'approved' as const,
    created_at: '2024-01-14T10:00:00Z'
  };

  it('displays verified badge for review with booking_id', () => {
    render(
      <ReviewModerationList
        reviews={[mockReviewWithBooking]}
        onApprove={jest.fn()}
        onReject={jest.fn()}
      />
    );
    expect(screen.getByText(/Verified/)).toBeInTheDocument();
  });

  it('does not display verified badge for review without booking_id', () => {
    render(
      <ReviewModerationList
        reviews={[mockReviewWithoutBooking]}
        onApprove={jest.fn()}
        onReject={jest.fn()}
      />
    );
    expect(screen.queryByText(/Verified/)).not.toBeInTheDocument();
  });

  it('displays verified badge with tooltip', () => {
    render(
      <ReviewModerationList
        reviews={[mockReviewWithBooking]}
        onApprove={jest.fn()}
        onReject={jest.fn()}
      />
    );
    const badge = screen.getByText(/Verified/);
    expect(badge).toHaveAttribute('title', 'This review is from a verified purchase');
  });

  it('displays verified badge for some reviews but not others', () => {
    render(
      <ReviewModerationList
        reviews={[mockReviewWithBooking, mockReviewWithoutBooking]}
        onApprove={jest.fn()}
        onReject={jest.fn()}
      />
    );
    
    // Should have one verified badge
    const verifiedBadges = screen.getAllByText(/Verified/);
    expect(verifiedBadges.length).toBe(1);
  });

  it('displays verified badge next to status badge', () => {
    render(
      <ReviewModerationList
        reviews={[mockReviewWithBooking]}
        onApprove={jest.fn()}
        onReject={jest.fn()}
      />
    );
    
    // Both status and verified badges should be present
    expect(screen.getByText('approved')).toBeInTheDocument();
    expect(screen.getByText(/Verified/)).toBeInTheDocument();
  });
});
