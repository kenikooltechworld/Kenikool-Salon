import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PackageCard } from '../package-card';
import { PackagePurchase } from '@/lib/api/hooks/useClientPackages';

const mockPackage: PackagePurchase = {
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
  package_description: '3 haircuts + 2 massages',
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
};

describe('PackageCard', () => {
  it('renders package name and description', () => {
    render(
      <PackageCard
        package={mockPackage}
        daysRemaining={100}
        isExpiringsoon={false}
        onViewDetails={jest.fn()}
      />
    );

    expect(screen.getByText('Hair & Massage Bundle')).toBeInTheDocument();
    expect(screen.getByText('3 haircuts + 2 massages')).toBeInTheDocument();
  });

  it('displays active status badge', () => {
    render(
      <PackageCard
        package={mockPackage}
        daysRemaining={100}
        isExpiringsoon={false}
        onViewDetails={jest.fn()}
      />
    );

    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('displays days remaining', () => {
    render(
      <PackageCard
        package={mockPackage}
        daysRemaining={100}
        isExpiringsoon={false}
        onViewDetails={jest.fn()}
      />
    );

    expect(screen.getByText(/100 days remaining/)).toBeInTheDocument();
  });

  it('displays expiring soon badge when applicable', () => {
    render(
      <PackageCard
        package={mockPackage}
        daysRemaining={5}
        isExpiringsoon={true}
        onViewDetails={jest.fn()}
      />
    );

    expect(screen.getByText('Expiring Soon')).toBeInTheDocument();
  });

  it('displays credit progress', () => {
    render(
      <PackageCard
        package={mockPackage}
        daysRemaining={100}
        isExpiringsoon={false}
        onViewDetails={jest.fn()}
      />
    );

    expect(screen.getByText('Credits Used')).toBeInTheDocument();
    expect(screen.getByText('2 / 5')).toBeInTheDocument();
  });

  it('displays all services with remaining quantities', () => {
    render(
      <PackageCard
        package={mockPackage}
        daysRemaining={100}
        isExpiringsoon={false}
        onViewDetails={jest.fn()}
      />
    );

    expect(screen.getByText('Haircut')).toBeInTheDocument();
    expect(screen.getByText('Massage')).toBeInTheDocument();
    expect(screen.getByText('2 / 3')).toBeInTheDocument();
    expect(screen.getByText('1 / 2')).toBeInTheDocument();
  });

  it('displays purchase price', () => {
    render(
      <PackageCard
        package={mockPackage}
        daysRemaining={100}
        isExpiringsoon={false}
        onViewDetails={jest.fn()}
      />
    );

    expect(screen.getByText('$150.00')).toBeInTheDocument();
  });

  it('calls onViewDetails when button clicked', async () => {
    const onViewDetails = jest.fn();
    const user = userEvent.setup();

    render(
      <PackageCard
        package={mockPackage}
        daysRemaining={100}
        isExpiringsoon={false}
        onViewDetails={onViewDetails}
      />
    );

    await user.click(screen.getByText('View Details'));
    expect(onViewDetails).toHaveBeenCalledWith('1');
  });

  it('displays gift indicator for gift packages', () => {
    const giftPackage = { ...mockPackage, is_gift: true };

    render(
      <PackageCard
        package={giftPackage}
        daysRemaining={100}
        isExpiringsoon={false}
        onViewDetails={jest.fn()}
      />
    );

    expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument();
  });

  it('displays expired status for expired packages', () => {
    const expiredPackage = { ...mockPackage, status: 'expired' as const };

    render(
      <PackageCard
        package={expiredPackage}
        daysRemaining={-5}
        isExpiringsoon={false}
        onViewDetails={jest.fn()}
      />
    );

    expect(screen.getByText('Expired')).toBeInTheDocument();
  });

  it('displays fully redeemed status', () => {
    const fullyRedeemedPackage = {
      ...mockPackage,
      status: 'fully_redeemed' as const,
      credits: mockPackage.credits.map((c) => ({
        ...c,
        remaining_quantity: 0,
      })),
    };

    render(
      <PackageCard
        package={fullyRedeemedPackage}
        daysRemaining={100}
        isExpiringsoon={false}
        onViewDetails={jest.fn()}
      />
    );

    expect(screen.getByText('Fully Redeemed')).toBeInTheDocument();
  });
});
