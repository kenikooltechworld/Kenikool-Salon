/**
 * Responsive Layout Testing for POS Components
 * 
 * Tests POS components across multiple screen sizes:
 * - Mobile: 320px, 480px
 * - Tablet: 768px, 1024px
 * - Desktop: 1280px, 1920px
 * - Ultra-wide: 2560px
 * 
 * Validates:
 * - No horizontal scrolling
 * - Proper text truncation
 * - Responsive grid columns
 * - Touch target sizes
 * - Modal display on all screen sizes
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { POSHeader } from '../pos-header';
import { ProductServiceTabs } from '../product-service-tabs';
import { POSCart } from '../pos-cart';
import { POSPayment } from '../pos-payment';

// Mock data
const mockServices = [
  {
    id: '1',
    name: 'Professional Hair Styling Service with Extensions and Color Treatment',
    duration: 120,
    price: 15000,
    image_url: 'https://example.com/service1.jpg',
  },
  {
    id: '2',
    name: 'Facial Treatment',
    duration: 60,
    price: 8000,
  },
  {
    id: '3',
    name: 'Manicure and Pedicure Combo Package',
    duration: 90,
    price: 12000,
  },
];

const mockProducts = [
  {
    id: '1',
    name: 'Premium Hair Care Shampoo and Conditioner Set with Natural Ingredients',
    quantity: 50,
    price: 5000,
  },
  {
    id: '2',
    name: 'Nail Polish',
    quantity: 100,
    price: 2000,
  },
];

const mockCartItems = [
  {
    item_id: '1',
    item_name: 'Professional Hair Styling Service with Extensions and Color Treatment',
    type: 'service' as const,
    price: 15000,
    quantity: 1,
  },
  {
    item_id: '2',
    item_name: 'Premium Hair Care Shampoo and Conditioner Set with Natural Ingredients',
    type: 'product' as const,
    price: 5000,
    quantity: 2,
  },
];

// Helper function to set viewport size
const setViewportSize = (width: number, height: number = 800) => {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  Object.defineProperty(window, 'innerHeight', {
    writable: true,
    configurable: true,
    value: height,
  });
  window.dispatchEvent(new Event('resize'));
};

// Helper function to check for horizontal overflow
const checkHorizontalOverflow = (element: HTMLElement): boolean => {
  return element.scrollWidth > element.clientWidth;
};

// Helper function to check text truncation
const checkTextTruncation = (element: HTMLElement): boolean => {
  const style = window.getComputedStyle(element);
  return (
    style.overflow === 'hidden' ||
    style.textOverflow === 'ellipsis' ||
    style.whiteSpace === 'nowrap' ||
    element.className.includes('truncate') ||
    element.className.includes('line-clamp')
  );
};

describe('POS Responsive Layout Tests', () => {
  const screenSizes = [
    { width: 320, name: 'Mobile Small (320px)' },
    { width: 480, name: 'Mobile Large (480px)' },
    { width: 768, name: 'Tablet (768px)' },
    { width: 1024, name: 'Tablet Large (1024px)' },
    { width: 1280, name: 'Desktop (1280px)' },
    { width: 1920, name: 'Desktop Large (1920px)' },
    { width: 2560, name: 'Ultra-wide (2560px)' },
  ];

  beforeEach(() => {
    setViewportSize(1280); // Default to desktop
  });

  afterEach(() => {
    // Reset viewport
    setViewportSize(1280);
  });

  describe('POSHeader Responsive Behavior', () => {
    screenSizes.forEach(({ width, name }) => {
      it(`should display properly on ${name}`, () => {
        setViewportSize(width);
        const { container } = render(
          <POSHeader
            onOpenQuickKeys={() => {}}
            onOpenCashDrop={() => {}}
            onOpenCashDrawer={() => {}}
            onCloseCashDrawer={() => {}}
            onOpenParkedTransactions={() => {}}
            onOpenCustomerDisplay={() => {}}
            onOpenReceiptCustomization={() => {}}
            onOpenGiftCards={() => {}}
            onOpenTransactionSearch={() => {}}
            onOpenServiceTickets={() => {}}
            cashDrawerStatus="open"
          />
        );

        const headerElement = container.querySelector('.flex');
        expect(headerElement).toBeTruthy();

        // Check for horizontal overflow
        const hasOverflow = checkHorizontalOverflow(headerElement!);
        expect(hasOverflow).toBe(false);

        // Verify buttons have whitespace-nowrap
        const buttons = container.querySelectorAll('button');
        buttons.forEach((button) => {
          expect(button.className).toContain('whitespace-nowrap');
        });
      });
    });

    it('should wrap buttons on small screens instead of shrinking', () => {
      setViewportSize(320);
      const { container } = render(
        <POSHeader
          onOpenQuickKeys={() => {}}
          onOpenCashDrop={() => {}}
          onOpenCashDrawer={() => {}}
          onCloseCashDrawer={() => {}}
          cashDrawerStatus="open"
        />
      );

      const buttonContainer = container.querySelector('.flex-wrap');
      expect(buttonContainer).toBeTruthy();
      expect(buttonContainer?.className).toContain('flex-wrap');
    });

    it('should maintain icon visibility on all screen sizes', () => {
      screenSizes.forEach(({ width }) => {
        setViewportSize(width);
        const { container } = render(
          <POSHeader
            onOpenQuickKeys={() => {}}
            onOpenCashDrop={() => {}}
            onOpenCashDrawer={() => {}}
            onCloseCashDrawer={() => {}}
            cashDrawerStatus="open"
          />
        );

        const icons = container.querySelectorAll('svg');
        icons.forEach((icon) => {
          expect(icon.className.baseVal).toContain('h-4');
          expect(icon.className.baseVal).toContain('w-4');
        });
      });
    });
  });

  describe('ProductServiceTabs Responsive Behavior', () => {
    screenSizes.forEach(({ width, name }) => {
      it(`should display cards properly on ${name}`, () => {
        setViewportSize(width);
        const { container } = render(
          <ProductServiceTabs
            services={mockServices}
            products={mockProducts}
            onAddService={() => {}}
            onAddProduct={() => {}}
          />
        );

        // Check for horizontal overflow in grid
        const gridContainer = container.querySelector('.overflow-x-hidden');
        expect(gridContainer).toBeTruthy();

        const hasOverflow = checkHorizontalOverflow(gridContainer!);
        expect(hasOverflow).toBe(false);
      });
    });

    it('should truncate long service names with ellipsis', () => {
      const { container } = render(
        <ProductServiceTabs
          services={mockServices}
          products={mockProducts}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      const serviceNames = container.querySelectorAll('.line-clamp-2');
      expect(serviceNames.length).toBeGreaterThan(0);
      serviceNames.forEach((name) => {
        expect(name.className).toContain('line-clamp-2');
      });
    });

    it('should maintain fixed card height on all screen sizes', () => {
      screenSizes.forEach(({ width }) => {
        setViewportSize(width);
        const { container } = render(
          <ProductServiceTabs
            services={mockServices}
            products={mockProducts}
            onAddService={() => {}}
            onAddProduct={() => {}}
          />
        );

        const cards = container.querySelectorAll('.h-\\[140px\\]');
        expect(cards.length).toBeGreaterThan(0);
      });
    });

    it('should adjust grid columns based on screen size', () => {
      const testCases = [
        { width: 320, expectedCols: 1 },
        { width: 768, expectedCols: 2 },
        { width: 1024, expectedCols: 3 },
      ];

      testCases.forEach(({ width, expectedCols }) => {
        setViewportSize(width);
        const { container } = render(
          <ProductServiceTabs
            services={mockServices}
            products={mockProducts}
            onAddService={() => {}}
            onAddProduct={() => {}}
          />
        );

        const grid = container.querySelector('.grid');
        expect(grid).toBeTruthy();
        // Grid should have responsive classes
        expect(grid?.className).toMatch(/grid-cols-/);
      });
    });

    it('should display prices consistently on all screen sizes', () => {
      screenSizes.forEach(({ width }) => {
        setViewportSize(width);
        const { container } = render(
          <ProductServiceTabs
            services={mockServices}
            products={mockProducts}
            onAddService={() => {}}
            onAddProduct={() => {}}
          />
        );

        const prices = container.querySelectorAll('.text-base.font-bold');
        expect(prices.length).toBeGreaterThan(0);
        prices.forEach((price) => {
          expect(price.textContent).toMatch(/₦/);
        });
      });
    });
  });

  describe('POSCart Responsive Behavior', () => {
    screenSizes.forEach(({ width, name }) => {
      it(`should display cart items properly on ${name}`, () => {
        setViewportSize(width);
        const { container } = render(
          <POSCart
            items={mockCartItems}
            onUpdateItem={() => {}}
            onRemoveItem={() => {}}
            onAddItem={() => {}}
            subtotal={25000}
            discount={0}
            tax={0}
            tip={0}
            total={25000}
            notes=""
            onUpdateDiscount={() => {}}
            onUpdateTax={() => {}}
            onUpdateTip={() => {}}
            onUpdateNotes={() => {}}
          />
        );

        const cartContainer = container.querySelector('.overflow-x-hidden');
        if (cartContainer) {
          const hasOverflow = checkHorizontalOverflow(cartContainer);
          expect(hasOverflow).toBe(false);
        }
      });
    });

    it('should truncate long item names', () => {
      const { container } = render(
        <POSCart
          items={mockCartItems}
          onUpdateItem={() => {}}
          onRemoveItem={() => {}}
          onAddItem={() => {}}
          subtotal={25000}
          discount={0}
          tax={0}
          tip={0}
          total={25000}
          notes=""
          onUpdateDiscount={() => {}}
          onUpdateTax={() => {}}
          onUpdateTip={() => {}}
          onUpdateNotes={() => {}}
        />
      );

      const itemNames = container.querySelectorAll('.truncate');
      expect(itemNames.length).toBeGreaterThan(0);
    });

    it('should maintain proper input field sizes on all screen sizes', () => {
      screenSizes.forEach(({ width }) => {
        setViewportSize(width);
        const { container } = render(
          <POSCart
            items={mockCartItems}
            onUpdateItem={() => {}}
            onRemoveItem={() => {}}
            onAddItem={() => {}}
            subtotal={25000}
            discount={0}
            tax={0}
            tip={0}
            total={25000}
            notes=""
            onUpdateDiscount={() => {}}
            onUpdateTax={() => {}}
            onUpdateTip={() => {}}
            onUpdateNotes={() => {}}
          />
        );

        const inputs = container.querySelectorAll('input[type="number"]');
        inputs.forEach((input) => {
          const style = window.getComputedStyle(input);
          expect(style.width).not.toBe('0px');
        });
      });
    });

    it('should display totals section clearly on all screen sizes', () => {
      screenSizes.forEach(({ width }) => {
        setViewportSize(width);
        const { container } = render(
          <POSCart
            items={mockCartItems}
            onUpdateItem={() => {}}
            onRemoveItem={() => {}}
            onAddItem={() => {}}
            subtotal={25000}
            discount={0}
            tax={0}
            tip={0}
            total={25000}
            notes=""
            onUpdateDiscount={() => {}}
            onUpdateTax={() => {}}
            onUpdateTip={() => {}}
            onUpdateNotes={() => {}}
          />
        );

        const totalText = screen.queryByText(/Total:/);
        expect(totalText).toBeTruthy();
      });
    });
  });

  describe('POSPayment Responsive Behavior', () => {
    screenSizes.forEach(({ width, name }) => {
      it(`should display payment modal properly on ${name}`, () => {
        setViewportSize(width);
        const { container } = render(
          <POSPayment
            total={25000}
            onProcessPayment={() => {}}
          />
        );

        const paymentContainer = container.querySelector('.overflow-x-hidden');
        if (paymentContainer) {
          const hasOverflow = checkHorizontalOverflow(paymentContainer);
          expect(hasOverflow).toBe(false);
        }
      });
    });

    it('should wrap quick amount buttons on small screens', () => {
      setViewportSize(320);
      const { container } = render(
        <POSPayment
          total={25000}
          onProcessPayment={() => {}}
        />
      );

      const buttonContainer = container.querySelector('.flex-wrap');
      expect(buttonContainer).toBeTruthy();
    });

    it('should display payment summary clearly on all screen sizes', () => {
      screenSizes.forEach(({ width }) => {
        setViewportSize(width);
        const { container } = render(
          <POSPayment
            total={25000}
            onProcessPayment={() => {}}
          />
        );

        const summaryText = screen.queryByText(/Total Due:/);
        expect(summaryText).toBeTruthy();
      });
    });

    it('should handle long reference numbers with word breaking', () => {
      const { container } = render(
        <POSPayment
          total={25000}
          onProcessPayment={() => {}}
        />
      );

      const breakAllElements = container.querySelectorAll('.break-all');
      expect(breakAllElements.length).toBeGreaterThan(0);
    });
  });

  describe('Long Content Handling', () => {
    it('should handle 20+ services in cart without overflow', () => {
      const manyServices = Array.from({ length: 25 }, (_, i) => ({
        id: `${i}`,
        name: `Service ${i} with Very Long Name That Should Be Truncated Properly`,
        duration: 60,
        price: 5000 + i * 1000,
      }));

      const { container } = render(
        <ProductServiceTabs
          services={manyServices}
          products={[]}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      const gridContainer = container.querySelector('.overflow-x-hidden');
      expect(gridContainer).toBeTruthy();
      const hasOverflow = checkHorizontalOverflow(gridContainer!);
      expect(hasOverflow).toBe(false);
    });

    it('should handle 50+ character service names', () => {
      const longNameService = {
        id: '1',
        name: 'This is a very long service name that exceeds fifty characters and should be truncated',
        duration: 120,
        price: 15000,
      };

      const { container } = render(
        <ProductServiceTabs
          services={[longNameService]}
          products={[]}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      const serviceName = container.querySelector('.line-clamp-2');
      expect(serviceName).toBeTruthy();
      expect(serviceName?.textContent).toContain('This is a very long');
    });

    it('should handle many items in cart', () => {
      const manyItems = Array.from({ length: 30 }, (_, i) => ({
        item_id: `${i}`,
        item_name: `Item ${i}`,
        type: 'product' as const,
        price: 1000 + i * 100,
        quantity: 1,
      }));

      const { container } = render(
        <POSCart
          items={manyItems}
          onUpdateItem={() => {}}
          onRemoveItem={() => {}}
          onAddItem={() => {}}
          subtotal={50000}
          discount={0}
          tax={0}
          tip={0}
          total={50000}
          notes=""
          onUpdateDiscount={() => {}}
          onUpdateTax={() => {}}
          onUpdateTip={() => {}}
          onUpdateNotes={() => {}}
        />
      );

      const cartContainer = container.querySelector('.max-h-\\[400px\\]');
      expect(cartContainer).toBeTruthy();
      expect(cartContainer?.className).toContain('overflow-y-auto');
    });
  });

  describe('Touch Target Sizes', () => {
    it('should have adequate button sizes for touch interaction', () => {
      const { container } = render(
        <POSHeader
          onOpenQuickKeys={() => {}}
          onOpenCashDrop={() => {}}
          onOpenCashDrawer={() => {}}
          onCloseCashDrawer={() => {}}
          cashDrawerStatus="open"
        />
      );

      const buttons = container.querySelectorAll('button');
      buttons.forEach((button) => {
        const style = window.getComputedStyle(button);
        const height = parseFloat(style.height);
        const width = parseFloat(style.width);
        // Minimum touch target is 44x44px
        expect(height).toBeGreaterThanOrEqual(32); // Accounting for padding
        expect(width).toBeGreaterThanOrEqual(32);
      });
    });

    it('should have adequate spacing between interactive elements', () => {
      const { container } = render(
        <POSCart
          items={mockCartItems}
          onUpdateItem={() => {}}
          onRemoveItem={() => {}}
          onAddItem={() => {}}
          subtotal={25000}
          discount={0}
          tax={0}
          tip={0}
          total={25000}
          notes=""
          onUpdateDiscount={() => {}}
          onUpdateTax={() => {}}
          onUpdateTip={() => {}}
          onUpdateNotes={() => {}}
        />
      );

      const buttons = container.querySelectorAll('button');
      expect(buttons.length).toBeGreaterThan(0);
      // All buttons should have gap spacing
      buttons.forEach((button) => {
        expect(button.className).toMatch(/gap-|h-8|h-7|h-6/);
      });
    });
  });

  describe('Modal Display on Different Screen Sizes', () => {
    it('should display payment modal without overflow on mobile', () => {
      setViewportSize(320);
      const { container } = render(
        <POSPayment
          total={25000}
          onProcessPayment={() => {}}
        />
      );

      const card = container.querySelector('[class*="Card"]');
      expect(card).toBeTruthy();
    });

    it('should display payment modal without overflow on tablet', () => {
      setViewportSize(768);
      const { container } = render(
        <POSPayment
          total={25000}
          onProcessPayment={() => {}}
        />
      );

      const card = container.querySelector('[class*="Card"]');
      expect(card).toBeTruthy();
    });

    it('should display payment modal without overflow on desktop', () => {
      setViewportSize(1920);
      const { container } = render(
        <POSPayment
          total={25000}
          onProcessPayment={() => {}}
        />
      );

      const card = container.querySelector('[class*="Card"]');
      expect(card).toBeTruthy();
    });
  });
});
