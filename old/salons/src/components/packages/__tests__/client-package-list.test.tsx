import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ClientPackageList } from '../client-package-list';
import * as useClientPackagesModule from '@/lib/api/hooks/useClientPackages';

const mockPackages = [
  {
    _id: '1',
    package_definition_id: 'pkg-1',
    client_id: 'client-1',
    purchase_date: '2024-01-15',
    expiration_date: '2024-12-15',
    status: 'active' as const,
    original_price: 200,
    amount_paid: 150,
    is_gift: false,
    package_name: 'Active Package',
    package_description: 'Active package description',
    credits: [
      {
        _id: 'credit-1',
        service_id: 'service-1',
        service_name: 'Service 1',
        service_price: 50,
        initial_quantity: 3,
        remaining_quantity: 2,
        reserved_quantity: 0,
        status: 'available' as const,
      },
    ],
  },
  {
    _id: '2',
    package_definition_id: 'pkg-2',
    client_id: 'client-1',
    purchase_date: '2023-01-15',
    expiration_date: '2023-12-15',
    status: 'expired' as const,
    original_price: 100,
    amount_paid: 80,
    is_gift: false,
    package_name: 'Expired Package',
    package_description: 'Expired package description',
    credits: [
      {
        _id: 'credit-2',
        service_id: 'service-2',
        service_name: 'Service 2',
        service_price: 50,
        initial_quantity: 2,
        remaining_quantity: 0,
        reserved_quantity: 0,
        status: 'expired' as const,
      },
    ],
  },
  {
    _id: '3',
    package_definition_id: 'pkg-3',
    client_id: 'client-1',
    purchase_date: '2024-01-01',
    expiration_date: '2024-06-01',
    status: 'fully_redeemed' as const,
    original_price: 150,
    amount_paid: 120,
    is_gift: false,
    package_name: 'Fully Redeemed Package',
    package_description: 'Fully redeemed package description',
    credits: [
      {
        _id: 'credit-3',
        service_id: 'service-3',
        service_name: 'Service 3',
        service_price: 50,
        initial_quantity: 3,
        remaining_quantity: 0,
        reserved_quantity: 0,
        status: 'redeemed' as const,
      },
    ],
  },
];

describe('ClientPackageList', () => {
  beforeEach(() => {
    jest.spyOn(useClientPackagesModule, 'useClientPackages').mockReturnValue({
      packages: mockPackages,
      activePackages: [mockPackages[0]],
      expiredPackages: [mockPackages[1]],
      fullyRedeemedPackages: [mockPackages[2]],
      isLoading: false,
      error: null,
    });

    jest.spyOn(useClientPackagesModule, 'usePackageDetails').mockReturnValue({
      details: null,
      isLoading: false,
      error: null,
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('renders tabs for all package statuses', () => {
    render(<ClientPackageList clientId="client-1" />);

    expect(screen.getByText(/Active \(1\)/)).toBeInTheDocument();
    expect(screen.getByText(/Fully Redeemed \(1\)/)).toBeInTheDocument();
    expect(screen.getByText(/Expired \(1\)/)).toBeInTheDocument();
  });

  it('displays active packages by default', () => {
    render(<ClientPackageList clientId="client-1" />);

    expect(screen.getByText('Active Package')).toBeInTheDocument();
  });

  it('switches to expired packages tab', async () => {
    const user = userEvent.setup();
    render(<ClientPackageList clientId="client-1" />);

    await user.click(screen.getByText(/Expired \(1\)/));

    await waitFor(() => {
      expect(screen.getByText('Expired Package')).toBeInTheDocument();
    });
  });

  it('switches to fully redeemed packages tab', async () => {
    const user = userEvent.setup();
    render(<ClientPackageList clientId="client-1" />);

    await user.click(screen.getByText(/Fully Redeemed \(1\)/));

    await waitFor(() => {
      expect(screen.getByText('Fully Redeemed Package')).toBeInTheDocument();
    });
  });

  it('displays loading skeleton when loading', () => {
    jest.spyOn(useClientPackagesModule, 'useClientPackages').mockReturnValue({
      packages: [],
      activePackages: [],
      expiredPackages: [],
      fullyRedeemedPackages: [],
      isLoading: true,
      error: null,
    });

    render(<ClientPackageList clientId="client-1" />);

    const skeletons = screen.getAllByTestId('skeleton');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('displays empty state when no packages', () => {
    jest.spyOn(useClientPackagesModule, 'useClientPackages').mockReturnValue({
      packages: [],
      activePackages: [],
      expiredPackages: [],
      fullyRedeemedPackages: [],
      isLoading: false,
      error: null,
    });

    render(<ClientPackageList clientId="client-1" />);

    expect(screen.getByText("You haven't purchased any packages yet")).toBeInTheDocument();
    expect(screen.getByText('Browse available packages')).toBeInTheDocument();
  });

  it('displays empty message for tab with no packages', async () => {
    jest.spyOn(useClientPackagesModule, 'useClientPackages').mockReturnValue({
      packages: [mockPackages[0]],
      activePackages: [mockPackages[0]],
      expiredPackages: [],
      fullyRedeemedPackages: [],
      isLoading: false,
      error: null,
    });

    const user = userEvent.setup();
    render(<ClientPackageList clientId="client-1" />);

    await user.click(screen.getByText(/Expired \(0\)/));

    await waitFor(() => {
      expect(screen.getByText('No packages in this category')).toBeInTheDocument();
    });
  });

  it('calls useClientPackages with correct clientId', () => {
    const useClientPackagesSpy = jest.spyOn(useClientPackagesModule, 'useClientPackages');

    render(<ClientPackageList clientId="client-123" />);

    expect(useClientPackagesSpy).toHaveBeenCalledWith('client-123');
  });
});
