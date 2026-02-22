/**
 * Tests for redeem rewards modal component (Task 19)
 * Validates: REQ-4
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RedeemRewardsModal } from './redeem-rewards-modal';
import * as useReferralsHook from '@/lib/api/hooks/useReferrals';

// Mock the useRedeemRewards hook
jest.mock('@/lib/api/hooks/useReferrals', () => ({
  useRedeemRewards: jest.fn(),
}));

describe('RedeemRewardsModal', () => {
  const mockClientId = 'client-123';
  const mockAvailableBalance = 5000;

  const mockMutate = jest.fn();
  const mockMutateAsync = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useReferralsHook.useRedeemRewards as jest.Mock).mockReturnValue({
      mutateAsync: mockMutateAsync,
      isPending: false,
    });
  });

  describe('Modal Rendering', () => {
    it('should render modal when isOpen is true', () => {
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      expect(screen.getByText(/redeem rewards/i)).toBeInTheDocument();
    });

    it('should not render modal when isOpen is false', () => {
      const { container } = render(
        <RedeemRewardsModal
          isOpen={false}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      // Dialog should not be visible
      const dialog = container.querySelector('[role="dialog"]');
      expect(dialog).not.toBeVisible();
    });

    it('should display available balance', () => {
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      expect(screen.getByText(/available balance/i)).toBeInTheDocument();
      expect(screen.getByText(`₦${mockAvailableBalance.toFixed(2)}`)).toBeInTheDocument();
    });

    it('should display redemption amount input', () => {
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      expect(screen.getByPlaceholderText(/enter amount/i)).toBeInTheDocument();
    });

    it('should display quick amount buttons', () => {
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      expect(screen.getByRole('button', { name: /25%/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /50%/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /100%/i })).toBeInTheDocument();
    });

    it('should display action buttons', () => {
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /redeem/i })).toBeInTheDocument();
    });
  });

  describe('Amount Input Validation', () => {
    it('should show error for empty amount', async () => {
      const user = userEvent.setup();
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      await waitFor(() => {
        expect(screen.getByText(/please enter a valid amount/i)).toBeInTheDocument();
      });
    });

    it('should show error for non-numeric amount', async () => {
      const user = userEvent.setup();
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, 'abc');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      await waitFor(() => {
        expect(screen.getByText(/please enter a valid amount/i)).toBeInTheDocument();
      });
    });

    it('should show error for zero amount', async () => {
      const user = userEvent.setup();
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '0');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      await waitFor(() => {
        expect(screen.getByText(/amount must be greater than 0/i)).toBeInTheDocument();
      });
    });

    it('should show error for negative amount', async () => {
      const user = userEvent.setup();
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '-1000');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      await waitFor(() => {
        expect(screen.getByText(/amount must be greater than 0/i)).toBeInTheDocument();
      });
    });

    it('should show error for amount exceeding balance', async () => {
      const user = userEvent.setup();
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '10000');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      await waitFor(() => {
        expect(screen.getByText(/insufficient balance/i)).toBeInTheDocument();
      });
    });

    it('should clear error when amount changes', async () => {
      const user = userEvent.setup();
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '10000');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      await waitFor(() => {
        expect(screen.getByText(/insufficient balance/i)).toBeInTheDocument();
      });

      // Clear and enter valid amount
      await user.clear(input);
      await user.type(input, '1000');

      await waitFor(() => {
        expect(screen.queryByText(/insufficient balance/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Quick Amount Buttons', () => {
    it('should set amount to 25% of balance', async () => {
      const user = userEvent.setup();
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const button25 = screen.getByRole('button', { name: /25%/i });
      await user.click(button25);

      const input = screen.getByPlaceholderText(/enter amount/i) as HTMLInputElement;
      expect(input.value).toBe((mockAvailableBalance * 0.25).toString());
    });

    it('should set amount to 50% of balance', async () => {
      const user = userEvent.setup();
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const button50 = screen.getByRole('button', { name: /50%/i });
      await user.click(button50);

      const input = screen.getByPlaceholderText(/enter amount/i) as HTMLInputElement;
      expect(input.value).toBe((mockAvailableBalance * 0.5).toString());
    });

    it('should set amount to 100% of balance', async () => {
      const user = userEvent.setup();
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const button100 = screen.getByRole('button', { name: /100%/i });
      await user.click(button100);

      const input = screen.getByPlaceholderText(/enter amount/i) as HTMLInputElement;
      expect(input.value).toBe(mockAvailableBalance.toString());
    });
  });

  describe('Redemption Process', () => {
    it('should call redeem mutation with correct parameters', async () => {
      const user = userEvent.setup();
      mockMutateAsync.mockResolvedValue({ status: 'success' });

      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '2000');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      await waitFor(() => {
        expect(mockMutateAsync).toHaveBeenCalledWith({
          client_id: mockClientId,
          amount: 2000,
        });
      });
    });

    it('should show success message after redemption', async () => {
      const user = userEvent.setup();
      mockMutateAsync.mockResolvedValue({ status: 'success' });

      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '2000');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      await waitFor(() => {
        expect(screen.getByText(/rewards redeemed successfully/i)).toBeInTheDocument();
      });
    });

    it('should close modal after successful redemption', async () => {
      const user = userEvent.setup();
      const onClose = jest.fn();
      mockMutateAsync.mockResolvedValue({ status: 'success' });

      jest.useFakeTimers();

      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={onClose}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '2000');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      jest.advanceTimersByTime(2000);

      await waitFor(() => {
        expect(onClose).toHaveBeenCalled();
      });

      jest.useRealTimers();
    });

    it('should show error message on redemption failure', async () => {
      const user = userEvent.setup();
      mockMutateAsync.mockRejectedValue(new Error('Redemption failed'));

      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '2000');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      await waitFor(() => {
        expect(screen.getByText(/redemption failed/i)).toBeInTheDocument();
      });
    });

    it('should clear input after successful redemption', async () => {
      const user = userEvent.setup();
      mockMutateAsync.mockResolvedValue({ status: 'success' });

      jest.useFakeTimers();

      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i) as HTMLInputElement;
      await user.type(input, '2000');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      jest.advanceTimersByTime(2000);

      await waitFor(() => {
        expect(input.value).toBe('');
      });

      jest.useRealTimers();
    });
  });

  describe('Button States', () => {
    it('should disable redeem button when amount is empty', () => {
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      expect(redeemButton).toBeDisabled();
    });

    it('should enable redeem button when valid amount is entered', async () => {
      const user = userEvent.setup();
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '1000');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      expect(redeemButton).not.toBeDisabled();
    });

    it('should disable buttons during redemption', async () => {
      const user = userEvent.setup();
      mockMutateAsync.mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      );

      (useReferralsHook.useRedeemRewards as jest.Mock).mockReturnValue({
        mutateAsync: mockMutateAsync,
        isPending: true,
      });

      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '1000');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      const cancelButton = screen.getByRole('button', { name: /cancel/i });

      expect(redeemButton).toBeDisabled();
      expect(cancelButton).toBeDisabled();
    });

    it('should show loading state during redemption', async () => {
      const user = userEvent.setup();
      mockMutateAsync.mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      );

      (useReferralsHook.useRedeemRewards as jest.Mock).mockReturnValue({
        mutateAsync: mockMutateAsync,
        isPending: true,
      });

      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '1000');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      expect(screen.getByText(/processing/i)).toBeInTheDocument();
    });
  });

  describe('Modal Closing', () => {
    it('should close modal when cancel button is clicked', async () => {
      const user = userEvent.setup();
      const onClose = jest.fn();

      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={onClose}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      expect(onClose).toHaveBeenCalled();
    });

    it('should not close modal during redemption', async () => {
      const user = userEvent.setup();
      const onClose = jest.fn();
      mockMutateAsync.mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 1000))
      );

      (useReferralsHook.useRedeemRewards as jest.Mock).mockReturnValue({
        mutateAsync: mockMutateAsync,
        isPending: true,
      });

      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={onClose}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '1000');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      expect(onClose).not.toHaveBeenCalled();
    });

    it('should clear state when modal is closed', async () => {
      const user = userEvent.setup();
      const onClose = jest.fn();

      const { rerender } = render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={onClose}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '1000');

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      // Reopen modal
      rerender(
        <RedeemRewardsModal
          isOpen={true}
          onClose={onClose}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const newInput = screen.getByPlaceholderText(/enter amount/i) as HTMLInputElement;
      expect(newInput.value).toBe('');
    });
  });

  describe('Edge Cases', () => {
    it('should handle zero balance', () => {
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={0}
        />
      );

      expect(screen.getByText('₦0.00')).toBeInTheDocument();
    });

    it('should handle very large balance', () => {
      const largeBalance = 999999999;
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={largeBalance}
        />
      );

      expect(screen.getByText(`₦${largeBalance.toFixed(2)}`)).toBeInTheDocument();
    });

    it('should handle decimal amounts', async () => {
      const user = userEvent.setup();
      mockMutateAsync.mockResolvedValue({ status: 'success' });

      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const input = screen.getByPlaceholderText(/enter amount/i);
      await user.type(input, '1234.56');

      const redeemButton = screen.getByRole('button', { name: /redeem/i });
      await user.click(redeemButton);

      await waitFor(() => {
        expect(mockMutateAsync).toHaveBeenCalledWith({
          client_id: mockClientId,
          amount: 1234.56,
        });
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper dialog role', () => {
      const { container } = render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      const dialog = container.querySelector('[role="dialog"]');
      expect(dialog).toBeInTheDocument();
    });

    it('should have accessible labels for inputs', () => {
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      expect(screen.getByText(/redemption amount/i)).toBeInTheDocument();
    });

    it('should have accessible button labels', () => {
      render(
        <RedeemRewardsModal
          isOpen={true}
          onClose={jest.fn()}
          clientId={mockClientId}
          availableBalance={mockAvailableBalance}
        />
      );

      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /redeem/i })).toBeInTheDocument();
    });
  });
});
