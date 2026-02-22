import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReviewPhotoGallery } from './review-photo-gallery';

describe('ReviewPhotoGallery', () => {
  const mockPhotos = [
    {
      id: 'photo-1',
      url: 'https://example.com/photo1.jpg',
      uploaded_at: '2024-01-01T00:00:00Z'
    },
    {
      id: 'photo-2',
      url: 'https://example.com/photo2.jpg',
      uploaded_at: '2024-01-01T00:00:00Z'
    },
    {
      id: 'photo-3',
      url: 'https://example.com/photo3.jpg',
      uploaded_at: '2024-01-01T00:00:00Z'
    }
  ];

  describe('Rendering', () => {
    it('should not render when photos array is empty', () => {
      const { container } = render(
        <ReviewPhotoGallery photos={[]} />
      );
      expect(container.firstChild).toBeNull();
    });

    it('should not render when photos is null', () => {
      const { container } = render(
        <ReviewPhotoGallery photos={null as any} />
      );
      expect(container.firstChild).toBeNull();
    });

    it('should display photo count badge', () => {
      render(<ReviewPhotoGallery photos={mockPhotos} />);
      expect(screen.getByText('Photos (3)')).toBeInTheDocument();
    });

    it('should render grid of photo thumbnails', () => {
      render(<ReviewPhotoGallery photos={mockPhotos} />);
      const images = screen.getAllByRole('img', { hidden: true });
      // Should have 3 photos in grid
      expect(images.length).toBeGreaterThanOrEqual(3);
    });

    it('should display correct number of photos', () => {
      render(<ReviewPhotoGallery photos={mockPhotos} />);
      expect(screen.getByText('Photos (3)')).toBeInTheDocument();
    });
  });

  describe('Lightbox Functionality', () => {
    it('should open lightbox when clicking on a photo', async () => {
      render(<ReviewPhotoGallery photos={mockPhotos} />);
      
      const images = screen.getAllByRole('img', { hidden: true });
      fireEvent.click(images[0]);

      await waitFor(() => {
        expect(screen.getByText('1 of 3')).toBeInTheDocument();
      });
    });

    it('should close lightbox when clicking close button', async () => {
      render(<ReviewPhotoGallery photos={mockPhotos} />);
      
      const images = screen.getAllByRole('img', { hidden: true });
      fireEvent.click(images[0]);

      await waitFor(() => {
        expect(screen.getByText('1 of 3')).toBeInTheDocument();
      });

      const closeButton = screen.getByTitle('Close');
      fireEvent.click(closeButton);

      await waitFor(() => {
        expect(screen.queryByText('1 of 3')).not.toBeInTheDocument();
      });
    });

    it('should navigate to next photo', async () => {
      render(<ReviewPhotoGallery photos={mockPhotos} />);
      
      const images = screen.getAllByRole('img', { hidden: true });
      fireEvent.click(images[0]);

      await waitFor(() => {
        expect(screen.getByText('1 of 3')).toBeInTheDocument();
      });

      const nextButton = screen.getByTitle('Next photo');
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('2 of 3')).toBeInTheDocument();
      });
    });

    it('should navigate to previous photo', async () => {
      render(<ReviewPhotoGallery photos={mockPhotos} />);
      
      const images = screen.getAllByRole('img', { hidden: true });
      fireEvent.click(images[1]);

      await waitFor(() => {
        expect(screen.getByText('2 of 3')).toBeInTheDocument();
      });

      const prevButton = screen.getByTitle('Previous photo');
      fireEvent.click(prevButton);

      await waitFor(() => {
        expect(screen.getByText('1 of 3')).toBeInTheDocument();
      });
    });

    it('should wrap around when navigating past last photo', async () => {
      render(<ReviewPhotoGallery photos={mockPhotos} />);
      
      const images = screen.getAllByRole('img', { hidden: true });
      fireEvent.click(images[2]);

      await waitFor(() => {
        expect(screen.getByText('3 of 3')).toBeInTheDocument();
      });

      const nextButton = screen.getByTitle('Next photo');
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('1 of 3')).toBeInTheDocument();
      });
    });

    it('should wrap around when navigating before first photo', async () => {
      render(<ReviewPhotoGallery photos={mockPhotos} />);
      
      const images = screen.getAllByRole('img', { hidden: true });
      fireEvent.click(images[0]);

      await waitFor(() => {
        expect(screen.getByText('1 of 3')).toBeInTheDocument();
      });

      const prevButton = screen.getByTitle('Previous photo');
      fireEvent.click(prevButton);

      await waitFor(() => {
        expect(screen.getByText('3 of 3')).toBeInTheDocument();
      });
    });

    it('should select photo from thumbnail strip', async () => {
      render(<ReviewPhotoGallery photos={mockPhotos} />);
      
      const images = screen.getAllByRole('img', { hidden: true });
      fireEvent.click(images[0]);

      await waitFor(() => {
        expect(screen.getByText('1 of 3')).toBeInTheDocument();
      });

      // Click on second thumbnail
      const thumbnails = screen.getAllByRole('button', { hidden: true });
      const secondThumbnail = thumbnails.find(btn => btn.querySelector('img[alt="Thumbnail 2"]'));
      
      if (secondThumbnail) {
        fireEvent.click(secondThumbnail);
        
        await waitFor(() => {
          expect(screen.getByText('2 of 3')).toBeInTheDocument();
        });
      }
    });
  });

  describe('Delete Functionality', () => {
    it('should not show delete button when canDelete is false', () => {
      render(
        <ReviewPhotoGallery 
          photos={mockPhotos}
          canDelete={false}
        />
      );
      
      const deleteButtons = screen.queryAllByRole('button', { name: /delete/i });
      expect(deleteButtons.length).toBe(0);
    });

    it('should show delete button when canDelete is true', () => {
      render(
        <ReviewPhotoGallery 
          photos={mockPhotos}
          canDelete={true}
          onDeletePhoto={jest.fn()}
        />
      );
      
      const deleteButtons = screen.getAllByTitle('Delete photo');
      expect(deleteButtons.length).toBe(3);
    });

    it('should call onDeletePhoto when delete button is clicked', async () => {
      const mockDelete = jest.fn();
      render(
        <ReviewPhotoGallery 
          photos={mockPhotos}
          canDelete={true}
          onDeletePhoto={mockDelete}
        />
      );
      
      const deleteButtons = screen.getAllByTitle('Delete photo');
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(mockDelete).toHaveBeenCalledWith('photo-1');
      });
    });

    it('should disable delete button while loading', () => {
      const mockDelete = jest.fn();
      render(
        <ReviewPhotoGallery 
          photos={mockPhotos}
          canDelete={true}
          onDeletePhoto={mockDelete}
          isLoading={true}
        />
      );
      
      const deleteButtons = screen.getAllByTitle('Delete photo');
      expect(deleteButtons[0]).toBeDisabled();
    });
  });

  describe('Single Photo', () => {
    it('should not show navigation buttons for single photo', async () => {
      const singlePhoto = [mockPhotos[0]];
      render(<ReviewPhotoGallery photos={singlePhoto} />);
      
      const images = screen.getAllByRole('img', { hidden: true });
      fireEvent.click(images[0]);

      await waitFor(() => {
        expect(screen.queryByTitle('Previous photo')).not.toBeInTheDocument();
        expect(screen.queryByTitle('Next photo')).not.toBeInTheDocument();
      });
    });

    it('should not show photo counter for single photo', async () => {
      const singlePhoto = [mockPhotos[0]];
      render(<ReviewPhotoGallery photos={singlePhoto} />);
      
      const images = screen.getAllByRole('img', { hidden: true });
      fireEvent.click(images[0]);

      await waitFor(() => {
        expect(screen.queryByText(/of/)).not.toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper alt text for images', () => {
      render(<ReviewPhotoGallery photos={mockPhotos} />);
      
      const images = screen.getAllByRole('img', { hidden: true });
      images.forEach((img, index) => {
        expect(img).toHaveAttribute('alt');
      });
    });

    it('should have proper titles for buttons', () => {
      render(
        <ReviewPhotoGallery 
          photos={mockPhotos}
          canDelete={true}
          onDeletePhoto={jest.fn()}
        />
      );
      
      expect(screen.getAllByTitle('Delete photo')).toBeDefined();
    });
  });
});
