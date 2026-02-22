import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PackageReceipt } from '../package-receipt';

// Mock jsPDF
vi.mock('jspdf', () => ({
  default: vi.fn().mockImplementation(() => ({
    internal: {
      pageSize: {
        getWidth: () => 210,
        getHeight: () => 297,
      },
    },
    setFontSize: vi.fn(),
    setTextColor: vi.fn(),
    setFont: vi.fn(),
    setDrawColor: vi.fn(),
    text: vi.fn(),
    line: vi.fn(),
    splitTextToSize: vi.fn().mockReturnValue(['line1', 'line2']),
    save: vi.fn(),
  })),
}));

const mockPurchase = {
  _id: 'purchase-123',
  package_name: 'Premium Hair Package',
  package_description: 'Includes 3 haircuts and 2 color treatments',
  client_name: 'John Doe',
  client_email: 'john@example.com',
  purchase_date: '2024-01-15T10:00:00Z',
  expiration_date: '2024-04-15T10:00:00Z',
  amount_paid: 350,
  original_price: 450,
  discount_percentage: 22,
  services: [
    {
      service_name: 'Haircut',
      quantity: 3,
      price: 50,
    },
    {
      service_name: 'Color Treatment',
      quantity: 2,
      price: 100,
    },
  ],
  is_gift: false,
  payment_method: 'card',
};

describe('PackageReceipt', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders receipt header correctly', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    expect(screen.getByText('RECEIPT')).toBeInTheDocument();
    expect(screen.getByText('Package Purchase Confirmation')).toBeInTheDocument();
  });

  it('displays purchase dates', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    expect(screen.getByText('Purchase Date')).toBeInTheDocument();
    expect(screen.getByText('Expiration Date')).toBeInTheDocument();
  });

  it('displays client information', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('displays package details', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    expect(screen.getByText('Premium Hair Package')).toBeInTheDocument();
    expect(screen.getByText('Includes 3 haircuts and 2 color treatments')).toBeInTheDocument();
  });

  it('displays all services with quantities and prices', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    expect(screen.getByText('Haircut')).toBeInTheDocument();
    expect(screen.getByText('Color Treatment')).toBeInTheDocument();
  });

  it('displays pricing summary', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    expect(screen.getByText('Original Value:')).toBeInTheDocument();
    expect(screen.getByText(/Discount/)).toBeInTheDocument();
    expect(screen.getByText('Package Price:')).toBeInTheDocument();
    expect(screen.getByText('Client Savings:')).toBeInTheDocument();
  });

  it('displays payment method', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    expect(screen.getByText('Payment Method')).toBeInTheDocument();
    expect(screen.getByText('Card')).toBeInTheDocument();
  });

  it('displays gift information when is_gift is true', () => {
    const giftPurchase = {
      ...mockPurchase,
      is_gift: true,
      gift_message: 'Happy Birthday!',
      gift_from_name: 'Jane Smith',
    };

    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={giftPurchase}
      />
    );

    expect(screen.getByText(/Gift Package/)).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('Happy Birthday!')).toBeInTheDocument();
  });

  it('does not display gift information when is_gift is false', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    expect(screen.queryByText(/Gift Package/)).not.toBeInTheDocument();
  });

  it('provides download PDF button', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    const downloadButton = screen.getByRole('button', { name: /download pdf/i });
    expect(downloadButton).toBeInTheDocument();
  });

  it('provides email receipt button', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    const emailButton = screen.getByRole('button', { name: /email receipt/i });
    expect(emailButton).toBeInTheDocument();
  });

  it('provides close button', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    const closeButton = screen.getByRole('button', { name: /close/i });
    expect(closeButton).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();

    render(
      <PackageReceipt
        isOpen={true}
        onClose={onClose}
        purchase={mockPurchase}
      />
    );

    const closeButton = screen.getByRole('button', { name: /close/i });
    await user.click(closeButton);

    expect(onClose).toHaveBeenCalled();
  });

  it('calls onEmailReceipt when email button is clicked', async () => {
    const user = userEvent.setup();
    const onEmailReceipt = vi.fn();

    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
        onEmailReceipt={onEmailReceipt}
      />
    );

    const emailButton = screen.getByRole('button', { name: /email receipt/i });
    await user.click(emailButton);

    expect(onEmailReceipt).toHaveBeenCalledWith(mockPurchase.client_email);
  });

  it('displays receipt number', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    const receiptNumber = `Receipt #${mockPurchase._id.slice(-8).toUpperCase()}`;
    expect(screen.getByText(receiptNumber)).toBeInTheDocument();
  });

  it('displays thank you message', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    expect(screen.getByText('Thank you for your purchase!')).toBeInTheDocument();
  });

  it('displays validity information', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    expect(screen.getByText(/This package is valid until/)).toBeInTheDocument();
  });

  it('displays service table headers', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    expect(screen.getByText('Service')).toBeInTheDocument();
    expect(screen.getByText('Qty')).toBeInTheDocument();
    expect(screen.getByText('Price')).toBeInTheDocument();
    expect(screen.getByText('Total')).toBeInTheDocument();
  });

  it('calculates and displays correct savings amount', () => {
    render(
      <PackageReceipt
        isOpen={true}
        onClose={vi.fn()}
        purchase={mockPurchase}
      />
    );

    // Savings should be original_price - amount_paid = 450 - 350 = 100
    expect(screen.getByText('Client Savings:')).toBeInTheDocument();
  });
});
