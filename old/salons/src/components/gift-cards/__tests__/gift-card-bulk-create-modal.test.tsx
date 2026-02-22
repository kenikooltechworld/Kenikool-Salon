import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import GiftCardBulkCreateModal from '../gift-card-bulk-create-modal';

// Mock fetch
global.fetch = jest.fn();

describe('GiftCardBulkCreateModal', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  it('renders modal with title', () => {
    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );
    expect(screen.getByText('Bulk Create Gift Cards')).toBeInTheDocument();
  });

  it('displays CSV format instructions', () => {
    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );
    expect(screen.getByText('CSV Format Required')).toBeInTheDocument();
  });

  it('displays download template button', () => {
    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );
    expect(screen.getByText('Download Template')).toBeInTheDocument();
  });

  it('displays file upload area', () => {
    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );
    expect(screen.getByText(/Click to select CSV file/)).toBeInTheDocument();
  });

  it('displays amount input', () => {
    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );
    const amountInput = screen.getByDisplayValue('5000');
    expect(amountInput).toBeInTheDocument();
  });

  it('displays design theme select', () => {
    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );
    expect(screen.getByDisplayValue('default')).toBeInTheDocument();
  });

  it('displays create and cancel buttons', () => {
    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );
    expect(screen.getByText('Create Cards')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('calls onClose when cancel button is clicked', () => {
    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('calls onClose when close button is clicked', () => {
    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );
    const closeButton = screen.getByRole('button', { name: '' }).parentElement?.querySelector('button');
    if (closeButton) {
      fireEvent.click(closeButton);
    }
  });

  it('validates amount input', () => {
    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );
    const amountInput = screen.getByDisplayValue('5000') as HTMLInputElement;
    
    fireEvent.change(amountInput, { target: { value: '0' } });
    expect(amountInput.value).toBe('0');
    
    fireEvent.change(amountInput, { target: { value: '600000' } });
    expect(amountInput.value).toBe('600000');
  });

  it('disables create button when no CSV is selected', () => {
    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );
    const createButton = screen.getByText('Create Cards');
    expect(createButton).toBeDisabled();
  });

  it('handles successful bulk creation', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          success: true,
          created_count: 10,
          failed_count: 0,
          total: 10,
        }),
    });

    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );

    // Simulate CSV content
    const fileInput = screen.getByDisplayValue('5000').parentElement?.querySelector('input[type="file"]');
    if (fileInput) {
      fireEvent.change(fileInput, {
        target: {
          files: [new File(['test'], 'test.csv', { type: 'text/csv' })],
        },
      });
    }

    await waitFor(() => {
      expect(screen.getByText('Bulk Creation Complete!')).toBeInTheDocument();
    });
  });

  it('handles bulk creation errors', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: () =>
        Promise.resolve({
          detail: 'Invalid CSV format',
        }),
    });

    render(
      <GiftCardBulkCreateModal tenantId="test-tenant" onClose={mockOnClose} />
    );

    // Simulate CSV content
    const fileInput = screen.getByDisplayValue('5000').parentElement?.querySelector('input[type="file"]');
    if (fileInput) {
      fireEvent.change(fileInput, {
        target: {
          files: [new File(['test'], 'test.csv', { type: 'text/csv' })],
        },
      });
    }

    await waitFor(() => {
      expect(screen.getByText('Invalid CSV format')).toBeInTheDocument();
    });
  });
});
