import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReviewResponseModal } from './review-response-modal';

describe('ReviewResponseModal', () => {
  const mockReview = {
    _id: 'review-1',
    client_name: 'Jane Smith',
    rating: 5,
    comment: 'Great service!',
    status: 'approved' as const,
    created_at: '2024-01-15T10:00:00Z',
  };

  const mockTemplates = [
    {
      _id: 'template-1',
      name: 'Thank You',
      category: 'positive' as const,
      text: 'Thank you for your wonderful review!',
    },
    {
      _id: 'template-2',
      name: "We're Sorry",
      category: 'negative' as const,
      text: "We're sorry to hear that...",
    },
  ];

  const mockOnSubmit = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders modal when open', () => {
    render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Add Response')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    const { container } = render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={false}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    expect(container.querySelector('[role="dialog"]')).not.toBeInTheDocument();
  });

  it('shows "Edit Response" title when response exists', () => {
    const reviewWithResponse = {
      ...mockReview,
      response: {
        text: 'Thank you for your review!',
        responder_name: 'John Doe',
        responded_at: '2024-01-15T11:00:00Z',
      },
    };

    render(
      <ReviewResponseModal
        review={reviewWithResponse}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Edit Response')).toBeInTheDocument();
  });

  it('allows typing response text', async () => {
    const user = userEvent.setup();

    render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    const textarea = screen.getByPlaceholderText('Write your response here...');
    await user.type(textarea, 'Thank you for your review!');

    expect(textarea).toHaveValue('Thank you for your review!');
  });

  it('displays character count', async () => {
    const user = userEvent.setup();

    render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    const textarea = screen.getByPlaceholderText('Write your response here...');
    await user.type(textarea, 'Test response');

    expect(screen.getByText(/13 \/ 500 characters/)).toBeInTheDocument();
  });

  it('shows warning when approaching character limit', async () => {
    const user = userEvent.setup();

    render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    const textarea = screen.getByPlaceholderText('Write your response here...');
    // Type 420 characters (84% of limit)
    await user.type(textarea, 'A'.repeat(420));

    expect(screen.getByText(/Approaching limit/)).toBeInTheDocument();
  });

  it('allows selecting template', async () => {
    const user = userEvent.setup();

    render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    const templateSelect = screen.getByRole('combobox');
    await user.click(templateSelect);

    const option = screen.getByText('Thank You');
    await user.click(option);

    const textarea = screen.getByPlaceholderText('Write your response here...');
    expect(textarea).toHaveValue('Thank you for your wonderful review!');
  });

  it('shows preview tab', async () => {
    const user = userEvent.setup();

    render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    const textarea = screen.getByPlaceholderText('Write your response here...');
    await user.type(textarea, 'Thank you for your review!');

    const previewTab = screen.getByRole('tab', { name: /Preview/ });
    await user.click(previewTab);

    expect(screen.getByText('Thank you for your review!')).toBeInTheDocument();
  });

  it('submits response', async () => {
    const user = userEvent.setup();
    mockOnSubmit.mockResolvedValue(undefined);

    render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    const textarea = screen.getByPlaceholderText('Write your response here...');
    await user.type(textarea, 'Thank you for your review!');

    const submitButton = screen.getByRole('button', { name: /Submit Response/ });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('Thank you for your review!');
    });
  });

  it('shows error when response is empty', async () => {
    const user = userEvent.setup();

    render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    const submitButton = screen.getByRole('button', { name: /Submit Response/ });
    await user.click(submitButton);

    expect(screen.getByText('Response cannot be empty')).toBeInTheDocument();
  });

  it('disables submit button when response is empty', () => {
    render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    const submitButton = screen.getByRole('button', { name: /Submit Response/ });
    expect(submitButton).toBeDisabled();
  });

  it('closes modal on cancel', async () => {
    const user = userEvent.setup();

    render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /Cancel/ });
    await user.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('shows existing response info', () => {
    const reviewWithResponse = {
      ...mockReview,
      response: {
        text: 'Thank you for your review!',
        responder_name: 'John Doe',
        responded_at: '2024-01-15T11:00:00Z',
      },
    };

    render(
      <ReviewResponseModal
        review={reviewWithResponse}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText(/Last response by John Doe/)).toBeInTheDocument();
  });

  it('handles submission error', async () => {
    const user = userEvent.setup();
    mockOnSubmit.mockRejectedValue(new Error('Network error'));

    render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    const textarea = screen.getByPlaceholderText('Write your response here...');
    await user.type(textarea, 'Thank you!');

    const submitButton = screen.getByRole('button', { name: /Submit Response/ });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('disables buttons while loading', () => {
    render(
      <ReviewResponseModal
        review={mockReview}
        templates={mockTemplates}
        isOpen={true}
        isLoading={true}
        onSubmit={mockOnSubmit}
        onClose={mockOnClose}
      />
    );

    const submitButton = screen.getByRole('button', { name: /Submit Response/ });
    const cancelButton = screen.getByRole('button', { name: /Cancel/ });

    expect(submitButton).toBeDisabled();
    expect(cancelButton).toBeDisabled();
  });
});
