import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReviewFlagModal } from './review-flag-modal';

describe('ReviewFlagModal', () => {
  const mockOnClose = jest.fn();
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should not render when isOpen is false', () => {
      const { container } = render(
        <ReviewFlagModal
          isOpen={false}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      expect(screen.queryByText('Flag Review')).not.toBeInTheDocument();
    });

    it('should render when isOpen is true', () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      expect(screen.getByText('Flag Review')).toBeInTheDocument();
    });

    it('should display all flag reasons', () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      expect(screen.getByLabelText(/Spam/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Offensive/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Fake Review/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Other/)).toBeInTheDocument();
    });

    it('should display reason descriptions', () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      expect(screen.getByText('Promotional or irrelevant content')).toBeInTheDocument();
      expect(screen.getByText('Abusive, hateful, or inappropriate language')).toBeInTheDocument();
      expect(screen.getByText('Appears to be fraudulent or unverified')).toBeInTheDocument();
      expect(screen.getByText('Something else')).toBeInTheDocument();
    });

    it('should display info box', () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      expect(screen.getByText(/Flagged reviews are reviewed by our moderation team/)).toBeInTheDocument();
    });
  });

  describe('Reason Selection', () => {
    it('should allow selecting spam reason', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const spamRadio = screen.getByRole('radio', { name: /Spam/ });
      fireEvent.click(spamRadio);
      
      expect(spamRadio).toBeChecked();
    });

    it('should allow selecting offensive reason', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const offensiveRadio = screen.getByRole('radio', { name: /Offensive/ });
      fireEvent.click(offensiveRadio);
      
      expect(offensiveRadio).toBeChecked();
    });

    it('should allow selecting fake reason', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const fakeRadio = screen.getByRole('radio', { name: /Fake Review/ });
      fireEvent.click(fakeRadio);
      
      expect(fakeRadio).toBeChecked();
    });

    it('should allow selecting other reason', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const otherRadio = screen.getByRole('radio', { name: /Other/ });
      fireEvent.click(otherRadio);
      
      expect(otherRadio).toBeChecked();
    });

    it('should only allow one reason to be selected', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const spamRadio = screen.getByRole('radio', { name: /Spam/ });
      const offensiveRadio = screen.getByRole('radio', { name: /Offensive/ });
      
      fireEvent.click(spamRadio);
      expect(spamRadio).toBeChecked();
      expect(offensiveRadio).not.toBeChecked();
      
      fireEvent.click(offensiveRadio);
      expect(spamRadio).not.toBeChecked();
      expect(offensiveRadio).toBeChecked();
    });
  });

  describe('Additional Details', () => {
    it('should show details textarea when reason is selected', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      expect(screen.queryByPlaceholderText('Provide any additional context...')).not.toBeInTheDocument();
      
      const spamRadio = screen.getByRole('radio', { name: /Spam/ });
      fireEvent.click(spamRadio);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Provide any additional context...')).toBeInTheDocument();
      });
    });

    it('should hide details textarea when no reason is selected', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const spamRadio = screen.getByRole('radio', { name: /Spam/ });
      fireEvent.click(spamRadio);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Provide any additional context...')).toBeInTheDocument();
      });
      
      // Deselect by clicking another reason then back to none
      const offensiveRadio = screen.getByRole('radio', { name: /Offensive/ });
      fireEvent.click(offensiveRadio);
      
      // The textarea should still be visible since a reason is selected
      expect(screen.getByPlaceholderText('Provide any additional context...')).toBeInTheDocument();
    });

    it('should allow entering additional details', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const spamRadio = screen.getByRole('radio', { name: /Spam/ });
      fireEvent.click(spamRadio);
      
      const textarea = await screen.findByPlaceholderText('Provide any additional context...');
      fireEvent.change(textarea, { target: { value: 'This is spam content' } });
      
      expect(textarea).toHaveValue('This is spam content');
    });

    it('should display character count', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const spamRadio = screen.getByRole('radio', { name: /Spam/ });
      fireEvent.click(spamRadio);
      
      const textarea = await screen.findByPlaceholderText('Provide any additional context...');
      fireEvent.change(textarea, { target: { value: 'Test' } });
      
      expect(screen.getByText('4/500 characters')).toBeInTheDocument();
    });
  });

  describe('Form Submission', () => {
    it('should require reason before submission', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const submitButton = screen.getByRole('button', { name: /Flag Review/ });
      expect(submitButton).toBeDisabled();
    });

    it('should enable submit button when reason is selected', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const spamRadio = screen.getByRole('radio', { name: /Spam/ });
      fireEvent.click(spamRadio);
      
      const submitButton = screen.getByRole('button', { name: /Flag Review/ });
      expect(submitButton).not.toBeDisabled();
    });

    it('should call onSubmit with reason when submitted', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const spamRadio = screen.getByRole('radio', { name: /Spam/ });
      fireEvent.click(spamRadio);
      
      const submitButton = screen.getByRole('button', { name: /Flag Review/ });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith('spam', '');
      });
    });

    it('should call onSubmit with reason and details', async () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const spamRadio = screen.getByRole('radio', { name: /Spam/ });
      fireEvent.click(spamRadio);
      
      const textarea = await screen.findByPlaceholderText('Provide any additional context...');
      fireEvent.change(textarea, { target: { value: 'This is spam' } });
      
      const submitButton = screen.getByRole('button', { name: /Flag Review/ });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith('spam', 'This is spam');
      });
    });

    it('should close modal after successful submission', async () => {
      mockOnSubmit.mockResolvedValueOnce(undefined);
      
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const spamRadio = screen.getByRole('radio', { name: /Spam/ });
      fireEvent.click(spamRadio);
      
      const submitButton = screen.getByRole('button', { name: /Flag Review/ });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(mockOnClose).toHaveBeenCalled();
      });
    });

    it('should display error message on submission failure', async () => {
      mockOnSubmit.mockRejectedValueOnce(new Error('Failed to flag review'));
      
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const spamRadio = screen.getByRole('radio', { name: /Spam/ });
      fireEvent.click(spamRadio);
      
      const submitButton = screen.getByRole('button', { name: /Flag Review/ });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to flag review')).toBeInTheDocument();
      });
    });

    it('should disable submit button while loading', async () => {
      mockOnSubmit.mockImplementationOnce(() => new Promise(resolve => setTimeout(resolve, 1000)));
      
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
          isLoading={true}
        />
      );
      
      const submitButton = screen.getByRole('button', { name: /Flag Review/ });
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Cancel Button', () => {
    it('should call onClose when cancel button is clicked', () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const cancelButton = screen.getByRole('button', { name: /Cancel/ });
      fireEvent.click(cancelButton);
      
      expect(mockOnClose).toHaveBeenCalled();
    });

    it('should reset form when closed', async () => {
      const { rerender } = render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      const spamRadio = screen.getByRole('radio', { name: /Spam/ });
      fireEvent.click(spamRadio);
      
      expect(spamRadio).toBeChecked();
      
      const cancelButton = screen.getByRole('button', { name: /Cancel/ });
      fireEvent.click(cancelButton);
      
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper labels for radio buttons', () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      expect(screen.getByRole('radio', { name: /Spam/ })).toBeInTheDocument();
      expect(screen.getByRole('radio', { name: /Offensive/ })).toBeInTheDocument();
      expect(screen.getByRole('radio', { name: /Fake Review/ })).toBeInTheDocument();
      expect(screen.getByRole('radio', { name: /Other/ })).toBeInTheDocument();
    });

    it('should have proper button labels', () => {
      render(
        <ReviewFlagModal
          isOpen={true}
          onClose={mockOnClose}
          onSubmit={mockOnSubmit}
        />
      );
      
      expect(screen.getByRole('button', { name: /Cancel/ })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Flag Review/ })).toBeInTheDocument();
    });
  });
});
