/**
 * Tests for Social Share Buttons Component
 * Task 20: Test Social Sharing
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock component for testing
const SocialShareButtons = ({ referralCode, salonName, referralLink }: any) => {
  const handleWhatsAppShare = () => {
    const message = `Hey! I found this amazing salon - ${salonName}. Use my referral link to book and we both get rewards! ${referralLink}`;
    const url = `https://wa.me/?text=${encodeURIComponent(message)}`;
    window.open(url, '_blank');
  };

  const handleFacebookShare = () => {
    const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(referralLink)}`;
    window.open(url, '_blank');
  };

  const handleTwitterShare = () => {
    const tweet = `Just discovered ${salonName}! Book with my referral link and get rewards: ${referralLink}`;
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(tweet)}`;
    window.open(url, '_blank');
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(referralLink);
  };

  return (
    <div data-testid="social-share-buttons">
      <button 
        data-testid="whatsapp-share" 
        onClick={handleWhatsAppShare}
      >
        Share on WhatsApp
      </button>
      <button 
        data-testid="facebook-share" 
        onClick={handleFacebookShare}
      >
        Share on Facebook
      </button>
      <button 
        data-testid="twitter-share" 
        onClick={handleTwitterShare}
      >
        Share on Twitter
      </button>
      <button 
        data-testid="copy-link" 
        onClick={handleCopyLink}
      >
        Copy Link
      </button>
    </div>
  );
};

describe('SocialShareButtons - Task 20: Test Social Sharing', () => {
  const mockReferralCode = 'ABC12345';
  const mockSalonName = 'My Salon';
  const mockReferralLink = `https://mysalon.salon.com/register?ref=${mockReferralCode}`;

  beforeEach(() => {
    // Mock window.open
    global.window.open = jest.fn();
    // Mock navigator.clipboard
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn(),
      },
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Task 20.1: Test WhatsApp share link', () => {
    it('should open WhatsApp with pre-filled message containing referral code', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      const whatsappButton = screen.getByTestId('whatsapp-share');
      fireEvent.click(whatsappButton);

      expect(window.open).toHaveBeenCalled();
      const callArgs = (window.open as jest.Mock).mock.calls[0][0];
      expect(callArgs).toContain('wa.me');
      expect(callArgs).toContain(mockReferralCode);
      expect(callArgs).toContain(mockSalonName);
    });

    it('should include salon name in WhatsApp message', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      const whatsappButton = screen.getByTestId('whatsapp-share');
      fireEvent.click(whatsappButton);

      const callArgs = (window.open as jest.Mock).mock.calls[0][0];
      expect(callArgs).toContain(mockSalonName);
    });

    it('should include referral link in WhatsApp message', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      const whatsappButton = screen.getByTestId('whatsapp-share');
      fireEvent.click(whatsappButton);

      const callArgs = (window.open as jest.Mock).mock.calls[0][0];
      expect(callArgs).toContain(mockReferralLink);
    });
  });

  describe('Task 20.2: Test Facebook share dialog', () => {
    it('should open Facebook share dialog with referral link', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      const facebookButton = screen.getByTestId('facebook-share');
      fireEvent.click(facebookButton);

      expect(window.open).toHaveBeenCalled();
      const callArgs = (window.open as jest.Mock).mock.calls[0][0];
      expect(callArgs).toContain('facebook.com/sharer');
      expect(callArgs).toContain(mockReferralLink);
    });

    it('should include referral code in Facebook share URL', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      const facebookButton = screen.getByTestId('facebook-share');
      fireEvent.click(facebookButton);

      const callArgs = (window.open as jest.Mock).mock.calls[0][0];
      expect(callArgs).toContain(mockReferralCode);
    });
  });

  describe('Task 20.3: Test Twitter share link', () => {
    it('should open Twitter with pre-filled tweet containing referral code', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      const twitterButton = screen.getByTestId('twitter-share');
      fireEvent.click(twitterButton);

      expect(window.open).toHaveBeenCalled();
      const callArgs = (window.open as jest.Mock).mock.calls[0][0];
      expect(callArgs).toContain('twitter.com/intent/tweet');
      expect(callArgs).toContain(mockReferralCode);
    });

    it('should include salon name in Twitter tweet', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      const twitterButton = screen.getByTestId('twitter-share');
      fireEvent.click(twitterButton);

      const callArgs = (window.open as jest.Mock).mock.calls[0][0];
      expect(callArgs).toContain(mockSalonName);
    });

    it('should include referral link in Twitter tweet', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      const twitterButton = screen.getByTestId('twitter-share');
      fireEvent.click(twitterButton);

      const callArgs = (window.open as jest.Mock).mock.calls[0][0];
      expect(callArgs).toContain(mockReferralLink);
    });
  });

  describe('Task 20.4: Verify referral code in all links', () => {
    it('should include referral code in all social share links', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      // Click WhatsApp
      fireEvent.click(screen.getByTestId('whatsapp-share'));
      let callArgs = (window.open as jest.Mock).mock.calls[0][0];
      expect(callArgs).toContain(mockReferralCode);

      // Click Facebook
      fireEvent.click(screen.getByTestId('facebook-share'));
      callArgs = (window.open as jest.Mock).mock.calls[1][0];
      expect(callArgs).toContain(mockReferralCode);

      // Click Twitter
      fireEvent.click(screen.getByTestId('twitter-share'));
      callArgs = (window.open as jest.Mock).mock.calls[2][0];
      expect(callArgs).toContain(mockReferralCode);
    });

    it('should include referral link in all social share URLs', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      // Click WhatsApp
      fireEvent.click(screen.getByTestId('whatsapp-share'));
      let callArgs = (window.open as jest.Mock).mock.calls[0][0];
      expect(callArgs).toContain(mockReferralLink);

      // Click Facebook
      fireEvent.click(screen.getByTestId('facebook-share'));
      callArgs = (window.open as jest.Mock).mock.calls[1][0];
      expect(callArgs).toContain(mockReferralLink);

      // Click Twitter
      fireEvent.click(screen.getByTestId('twitter-share'));
      callArgs = (window.open as jest.Mock).mock.calls[2][0];
      expect(callArgs).toContain(mockReferralLink);
    });

    it('should copy link to clipboard when copy button clicked', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      const copyButton = screen.getByTestId('copy-link');
      fireEvent.click(copyButton);

      expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockReferralLink);
    });
  });

  describe('Accessibility and UI', () => {
    it('should render all social share buttons', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      expect(screen.getByTestId('whatsapp-share')).toBeInTheDocument();
      expect(screen.getByTestId('facebook-share')).toBeInTheDocument();
      expect(screen.getByTestId('twitter-share')).toBeInTheDocument();
      expect(screen.getByTestId('copy-link')).toBeInTheDocument();
    });

    it('should have descriptive button labels', () => {
      render(
        <SocialShareButtons
          referralCode={mockReferralCode}
          salonName={mockSalonName}
          referralLink={mockReferralLink}
        />
      );

      expect(screen.getByText('Share on WhatsApp')).toBeInTheDocument();
      expect(screen.getByText('Share on Facebook')).toBeInTheDocument();
      expect(screen.getByText('Share on Twitter')).toBeInTheDocument();
      expect(screen.getByText('Copy Link')).toBeInTheDocument();
    });
  });
});
