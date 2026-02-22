import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PackageDetailsModal } from '../package-details-modal';
import { PackagePurchaseDetails } from '@/lib/api/hooks/useClientPackages';

const mockPackageDetails: PackagePurchaseDetails = {
  _id: '1',
  package_definition_id: 'pkg-1',
  client_id: 'client-1',
  purchase_date: '2024-01-15',
  expiration_date: '2024-12-15',
  status: 'active',
  original_price: 200,
  amount_paid: 150,
  is_gift: false,
  package_name: 'Hair & Massage Bundle',
  package_description: 'Complete hair and massage package',
  credits: [
    {
      _id: 'credit-1',
      service_id: 'service-1',
      service_name: 'Haircut',
      service_price: 50,
      initial_quantity: 3,
      remaining_quantity: 2,
      reserved_quantity: 0,
      status: 'available',
    },
    {
      _id: 'credit-2',
      service_id: 'service-2',
      service_name: 'Massage',
      service_price: 50,
      initial_quantity: 2,
      remaining_quantity: 1,
      reserved_quantity: 0,
      status: 'available',
    },
  ],
  redemption_history: [
    {
      _id: 'redemption-1',
      service_name: 'Haircut',
      redemption_date: '2024-02-01',
      service_value: 50,
      redeemed_by_staff_id: 'staff-1',
    },
    {
      _id: 'redemption-2',
      service_name: 'Massage',
      redemption_date: '2024-03-01',
      service_value: 50,
      redeemed_by_staff_id: 'staff-2',
    },
  ],
  days_remaining: 100,
  is_expiring_soon: false,
  total_credits_used: 2,
  total_credits_available: 3,
};

describe('PackageDetailsModal', () => {
  it('does not render when isOpen is false', () => {
    const { container } = render(
      <PackageDetailsModal
        package={mockPackageDetails}
        isOpen={false}
        onClose={jest.fn()}
      />
    );

    expect(container.querySelector('[role="dialog"]')).not.toBeInTheDocument();
  });

  it('renders modal when isOpen is true', () => {
    render(
      <PackageDetailsModal
        package={mockPackageDetails}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    expect(screen.getByText('Hair & Massage Bundle')).toBeInTheDocument();
  });

  it('displays overview tab content', () => {
    render(
      <PackageDetailsModal
        package={mockPackageDetails}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    expect(screen.getByText('Active')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('$150.00')).toBeInTheDocument();
    expect(screen.getByText('$200.00')).toBeInTheDocument();
    expect(screen.getByText('$50.00')).toBeInTheDocument();
  });

  it('displays credits tab with service details', async () => {
    const user = userEvent.setup();
    render(
      <PackageDetailsModal
        package={mockPackageDetails}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    await user.click(screen.getByText('Credits'));

    expect(screen.getByText('Haircut')).toBeInTheDocument();
    expect(screen.getByText('Massage')).toBeInTheDocument();
    expect(screen.getByText('$50.00')).toBeInTheDocument();
  });

  it('displays redemption history tab', async () => {
    const user = userEvent.setup();
    render(
      <PackageDetailsModal
        package={mockPackageDetails}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    await user.click(screen.getByText('History'));

    expect(screen.getByText('Haircut')).toBeInTheDocument();
    expect(screen.getByText('Massage')).toBeInTheDocument();
  });

  it('displays gift package indicator', () => {
    const giftPackage = { ...mockPackageDetails, is_gift: true, gift_message: 'Happy Birthday!' };

    render(
      <PackageDetailsModal
        package={giftPackage}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    expect(screen.getByText('Gift Package')).toBeInTheDocument();
    expect(screen.getByText('Happy Birthday!')).toBeInTheDocument();
  });

  it('displays credit quantities correctly', async () => {
    const user = userEvent.setup();
    render(
      <PackageDetailsModal
        package={mockPackageDetails}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    await user.click(screen.getByText('Credits'));

    expect(screen.getByText('2 / 3')).toBeInTheDocument();
    expect(screen.getByText('1 / 2')).toBeInTheDocument();
  });

  it('displays empty state for no redemption history', () => {
    const packageWithoutHistory = {
      ...mockPackageDetails,
      redemption_history: [],
    };

    render(
      <PackageDetailsModal
        package={packageWithoutHistory}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    const historyTab = screen.getByText('History');
    historyTab.click();

    expect(screen.getByText('No redemptions yet')).toBeInTheDocument();
  });

  it('calls onClose when modal is closed', async () => {
    const onClose = jest.fn();
    const user = userEvent.setup();

    render(
      <PackageDetailsModal
        package={mockPackageDetails}
        isOpen={true}
        onClose={onClose}
      />
    );

    const closeButton = screen.getByRole('button', { name: /close/i });
    await user.click(closeButton);

    expect(onClose).toHaveBeenCalled();
  });

  it('displays expired status for expired packages', () => {
    const expiredPackage = {
      ...mockPackageDetails,
      status: 'expired' as const,
      days_remaining: -5,
    };

    render(
      <PackageDetailsModal
        package={expiredPackage}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    expect(screen.getByText('Expired')).toBeInTheDocument();
  });

  it('displays fully redeemed status', () => {
    const fullyRedeemedPackage = {
      ...mockPackageDetails,
      status: 'fully_redeemed' as const,
    };

    render(
      <PackageDetailsModal
        package={fullyRedeemedPackage}
        isOpen={true}
        onClose={jest.fn()}
      />
    );

    expect(screen.getByText('FULLY REDEEMED')).toBeInTheDocument();
  });
});
