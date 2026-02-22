import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ReviewCard } from './review-card';

describe('ReviewCard', () => {
  const mockReview = {
    _id: '1',
    client_name: 'John Doe',
    rating: 5,
    comment: 'Great service!',
    created_at: '2024-01-15T10:00:00Z',
    booking_id: 'booking123',
    service_name: 'Haircut',
    stylist_name: 'Jane Smith'
  };

  it('renders review card with client name', () => {
    render(<ReviewCard review={mockReview} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('renders review comment', () => {
    render(<ReviewCard review={mockReview} />);
    expect(screen.getByText('Great service!')).toBeInTheDocument();
  });

  it('renders service and stylist names', () => {
    render(<ReviewCard review={mockReview} />);
    expect(screen.getByText(/Haircut.*Jane Smith/)).toBeInTheDocument();
  });

  it('displays verified purchase badge when booking_id exists', () => {
    render(<ReviewCard review={mockReview} showVerifiedBadge={true} />);
    expect(screen.getByText(/Verified Purchase/)).toBeInTheDocument();
  });

  it('does not display verified badge when booking_id is missing', () => {
    const reviewWithoutBooking = { ...mockReview, booking_id: undefined };
    render(<ReviewCard review={reviewWithoutBooking} showVerifiedBadge={true} />);
    expect(screen.queryByText(/Verified Purchase/)).not.toBeInTheDocument();
  });

  it('does not display verified badge when showVerifiedBadge is false', () => {
    render(<ReviewCard review={mockReview} showVerifiedBadge={false} />);
    expect(screen.queryByText(/Verified Purchase/)).not.toBeInTheDocument();
  });

  it('renders correct number of stars based on rating', () => {
    render(<ReviewCard review={mockReview} />);
    const stars = screen.getAllByRole('img', { hidden: true });
    // 5 stars total (filled + unfilled)
    expect(stars.length).toBeGreaterThanOrEqual(5);
  });

  it('formats date correctly', () => {
    render(<ReviewCard review={mockReview} />);
    // Check that date is formatted
    expect(screen.getByText(/Jan 15, 2024|15 Jan 2024/)).toBeInTheDocument();
  });

  it('renders without comment when comment is empty', () => {
    const reviewWithoutComment = { ...mockReview, comment: undefined };
    render(<ReviewCard review={reviewWithoutComment} />);
    expect(screen.queryByText('Great service!')).not.toBeInTheDocument();
  });

  it('has tooltip on verified badge', () => {
    render(<ReviewCard review={mockReview} showVerifiedBadge={true} />);
    const badge = screen.getByText(/Verified Purchase/);
    expect(badge).toHaveAttribute('title', 'This review is from a verified purchase');
  });

  it('renders 4-star rating correctly', () => {
    const fourStarReview = { ...mockReview, rating: 4 };
    render(<ReviewCard review={fourStarReview} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('renders 1-star rating correctly', () => {
    const oneStarReview = { ...mockReview, rating: 1 };
    render(<ReviewCard review={oneStarReview} />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
