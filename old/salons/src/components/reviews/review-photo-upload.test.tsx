import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReviewPhotoUpload } from './review-photo-upload';
import * as useToastModule from '@/hooks/use-toast';

// Mock the useToast hook
jest.mock('@/hooks/use-toast', () => ({
  useToast: jest.fn()
}));

describe('ReviewPhotoUpload', () => {
  const mockToast = jest.fn();
  const mockOnPhotosSelected = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useToastModule.useToast as jest.Mock).mockReturnValue({
      toast: mockToast
    });
  });

  describe('Rendering', () => {
    it('should render upload section with label', () => {
      render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );
      
      expect(screen.getByText('Add Photos (Optional)')).toBeInTheDocument();
      expect(screen.getByText(/Upload up to 5 photos/i)).toBeInTheDocument();
    });

    it('should display drag and drop area', () => {
      render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );
      
      expect(screen.getByText(/Drag photos here or click to browse/i)).toBeInTheDocument();
    });

    it('should display photo counter', () => {
      render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );
      
      expect(screen.getByText('0/5 photos selected')).toBeInTheDocument();
    });

    it('should have hidden file input', () => {
      render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );
      
      const fileInput = screen.getByRole('button', { hidden: true }).parentElement?.querySelector('input[type="file"]');
      expect(fileInput).toBeInTheDocument();
      expect(fileInput).toHaveAttribute('accept', 'image/jpeg,image/png,image/webp');
    });
  });

  describe('File Selection', () => {
    it('should handle file selection via input', async () => {
      render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );

      const fileInput = screen.getByRole('button', { hidden: true }).parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
      
      const file = new File(['photo'], 'photo.jpg', { type: 'image/jpeg' });
      
      fireEvent.change(fileInput, { target: { files: [file] } });

      await waitFor(() => {
        expect(mockOnPhotosSelected).toHaveBeenCalled();
      });
    });

    it('should validate file type', async () => {
      render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );

      const fileInput = screen.getByRole('button', { hidden: true }).parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
      
      const invalidFile = new File(['text'], 'file.txt', { type: 'text/plain' });
      
      fireEvent.change(fileInput, { target: { files: [invalidFile] } });

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith(
          'Invalid file type. Please use JPEG, PNG, or WebP',
          'error'
        );
      });
    });

    it('should validate file size', async () => {
      render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );

      const fileInput = screen.getByRole('button', { hidden: true }).parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
      
      // Create a file larger than 5MB
      const largeFile = new File(['x'.repeat(6 * 1024 * 1024)], 'large.jpg', { type: 'image/jpeg' });
      
      fireEvent.change(fileInput, { target: { files: [largeFile] } });

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith(
          'File size exceeds 5MB limit',
          'error'
        );
      });
    });

    it('should respect max photos limit', async () => {
      render(
        <ReviewPhotoUpload 
          onPhotosSelected={mockOnPhotosSelected}
          maxPhotos={2}
        />
      );

      const fileInput = screen.getByRole('button', { hidden: true }).parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
      
      const files = [
        new File(['photo1'], 'photo1.jpg', { type: 'image/jpeg' }),
        new File(['photo2'], 'photo2.jpg', { type: 'image/jpeg' }),
        new File(['photo3'], 'photo3.jpg', { type: 'image/jpeg' })
      ];
      
      fireEvent.change(fileInput, { target: { files } });

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith(
          'Only 2 more photo(s) can be added (max 2 total)',
          'warning'
        );
      });
    });
  });

  describe('Drag and Drop', () => {
    it('should handle drag over', () => {
      const { container } = render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );

      const dragArea = container.querySelector('[class*="border-dashed"]');
      
      fireEvent.dragOver(dragArea!);
      
      expect(dragArea).toHaveClass('border-blue-500');
    });

    it('should handle drag leave', () => {
      const { container } = render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );

      const dragArea = container.querySelector('[class*="border-dashed"]');
      
      fireEvent.dragOver(dragArea!);
      fireEvent.dragLeave(dragArea!);
      
      expect(dragArea).not.toHaveClass('border-blue-500');
    });

    it('should handle drop', async () => {
      render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );

      const dragArea = screen.getByText(/Drag photos here or click to browse/i).closest('div');
      
      const file = new File(['photo'], 'photo.jpg', { type: 'image/jpeg' });
      
      fireEvent.drop(dragArea!, {
        dataTransfer: { files: [file] }
      });

      await waitFor(() => {
        expect(mockOnPhotosSelected).toHaveBeenCalled();
      });
    });
  });

  describe('Photo Preview', () => {
    it('should display photo previews after selection', async () => {
      render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );

      const fileInput = screen.getByRole('button', { hidden: true }).parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
      
      const file = new File(['photo'], 'photo.jpg', { type: 'image/jpeg' });
      
      fireEvent.change(fileInput, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('1/5 photos selected')).toBeInTheDocument();
      });
    });

    it('should allow removing photos', async () => {
      render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );

      const fileInput = screen.getByRole('button', { hidden: true }).parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
      
      const file = new File(['photo'], 'photo.jpg', { type: 'image/jpeg' });
      
      fireEvent.change(fileInput, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('1/5 photos selected')).toBeInTheDocument();
      });

      // Find and click the remove button
      const removeButtons = screen.getAllByRole('button', { hidden: true });
      const removeButton = removeButtons.find(btn => btn.querySelector('svg'));
      
      if (removeButton) {
        fireEvent.click(removeButton);
        
        await waitFor(() => {
          expect(mockOnPhotosSelected).toHaveBeenCalledWith([]);
        });
      }
    });
  });

  describe('Custom Configuration', () => {
    it('should respect custom max photos', () => {
      render(
        <ReviewPhotoUpload 
          onPhotosSelected={mockOnPhotosSelected}
          maxPhotos={3}
        />
      );
      
      expect(screen.getByText(/Upload up to 3 photos/i)).toBeInTheDocument();
      expect(screen.getByText('0/3 photos selected')).toBeInTheDocument();
    });

    it('should respect custom file size limit', async () => {
      const customMaxSize = 2 * 1024 * 1024; // 2MB
      
      render(
        <ReviewPhotoUpload 
          onPhotosSelected={mockOnPhotosSelected}
          maxFileSize={customMaxSize}
        />
      );

      const fileInput = screen.getByRole('button', { hidden: true }).parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
      
      // Create a file larger than 2MB but smaller than 5MB
      const largeFile = new File(['x'.repeat(3 * 1024 * 1024)], 'large.jpg', { type: 'image/jpeg' });
      
      fireEvent.change(fileInput, { target: { files: [largeFile] } });

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith(
          'File size exceeds 5MB limit',
          'error'
        );
      });
    });

    it('should respect custom accepted formats', async () => {
      render(
        <ReviewPhotoUpload 
          onPhotosSelected={mockOnPhotosSelected}
          acceptedFormats={['image/jpeg']}
        />
      );

      const fileInput = screen.getByRole('button', { hidden: true }).parentElement?.querySelector('input[type="file"]') as HTMLInputElement;
      
      const pngFile = new File(['photo'], 'photo.png', { type: 'image/png' });
      
      fireEvent.change(fileInput, { target: { files: [pngFile] } });

      await waitFor(() => {
        expect(mockToast).toHaveBeenCalledWith(
          'Invalid file type. Please use JPEG, PNG, or WebP',
          'error'
        );
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper labels', () => {
      render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );
      
      expect(screen.getByText('Add Photos (Optional)')).toBeInTheDocument();
    });

    it('should have descriptive text', () => {
      render(
        <ReviewPhotoUpload onPhotosSelected={mockOnPhotosSelected} />
      );
      
      expect(screen.getByText(/Upload up to 5 photos/i)).toBeInTheDocument();
      expect(screen.getByText(/JPEG, PNG, or WebP/i)).toBeInTheDocument();
    });
  });
});
