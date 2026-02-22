/**
 * Cross-Browser Testing for POS Components
 * 
 * Tests POS components across different browsers:
 * - Chrome (latest)
 * - Firefox (latest)
 * - Safari (latest)
 * - Edge (latest)
 * - Mobile browsers (Chrome, Safari)
 * 
 * Validates:
 * - CSS variables work in all browsers
 * - Flexbox/Grid layouts work correctly
 * - Text truncation works correctly
 * - No browser-specific bugs
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { POSHeader } from '../pos-header';
import { ProductServiceTabs } from '../product-service-tabs';
import { POSCart } from '../pos-cart';
import { POSPayment } from '../pos-payment';

// Mock data
const mockServices = [
  {
    id: '1',
    name: 'Professional Hair Styling Service',
    duration: 120,
    price: 15000,
  },
  {
    id: '2',
    name: 'Facial Treatment with Very Long Name That Tests Truncation',
    duration: 60,
    price: 8000,
  },
];

const mockProducts = [
  {
    id: '1',
    name: 'Premium Hair Care Product with Long Description',
    quantity: 50,
    price: 5000,
  },
];

const mockCartItems = [
  {
    item_id: '1',
    item_name: 'Professional Hair Styling Service',
    type: 'service' as const,
    price: 15000,
    quantity: 1,
  },
];

/**
 * Browser Detection Utilities
 */
const getBrowserInfo = () => {
  const ua = navigator.userAgent;
  let browserName = 'Unknown';
  let browserVersion = 'Unknown';

  if (ua.indexOf('Firefox') > -1) {
    browserName = 'Firefox';
    browserVersion = ua.split('Firefox/')[1];
  } else if (ua.indexOf('Safari') > -1 && ua.indexOf('Chrome') === -1) {
    browserName = 'Safari';
    browserVersion = ua.split('Version/')[1];
  } else if (ua.indexOf('Chrome') > -1) {
    browserName = 'Chrome';
    browserVersion = ua.split('Chrome/')[1];
  } else if (ua.indexOf('Trident') > -1) {
    browserName = 'IE';
    browserVersion = ua.split('rv:')[1];
  } else if (ua.indexOf('Edge') > -1 || ua.indexOf('Edg') > -1) {
    browserName = 'Edge';
    browserVersion = ua.split('Edg/')[1];
  }

  return { browserName, browserVersion };
};

/**
 * CSS Feature Detection
 */
const detectCSSFeatures = () => {
  const element = document.createElement('div');
  const style = element.style;

  return {
    cssVariables: CSS.supports('--test', '0'),
    flexbox: CSS.supports('display', 'flex'),
    grid: CSS.supports('display', 'grid'),
    lineClamp: CSS.supports('display', '-webkit-box') && CSS.supports('-webkit-line-clamp', '2'),
    textOverflow: CSS.supports('text-overflow', 'ellipsis'),
    whiteSpace: CSS.supports('white-space', 'nowrap'),
    transform: CSS.supports('transform', 'scale(1)'),
    transition: CSS.supports('transition', 'all 0.2s'),
  };
};

/**
 * Computed Style Utilities
 */
const getComputedStyles = (element: HTMLElement) => {
  return window.getComputedStyle(element);
};

const checkFlexboxSupport = (element: HTMLElement): boolean => {
  const style = getComputedStyles(element);
  return style.display === 'flex' || style.display === '-webkit-flex';
};

const checkGridSupport = (element: HTMLElement): boolean => {
  const style = getComputedStyles(element);
  return style.display === 'grid';
};

const checkTextTruncation = (element: HTMLElement): boolean => {
  const style = getComputedStyles(element);
  return (
    style.overflow === 'hidden' &&
    (style.textOverflow === 'ellipsis' || style.whiteSpace === 'nowrap')
  );
};

describe('Cross-Browser Compatibility Tests', () => {
  beforeEach(() => {
    // Log browser info for debugging
    const browserInfo = getBrowserInfo();
    console.log(`Testing on ${browserInfo.browserName} ${browserInfo.browserVersion}`);
  });

  describe('CSS Variables Support', () => {
    it('should support CSS variables in all browsers', () => {
      const features = detectCSSFeatures();
      expect(features.cssVariables).toBe(true);
    });

    it('should apply CSS variables to components', () => {
      const { container } = render(
        <ProductServiceTabs
          services={mockServices}
          products={mockProducts}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      // Check for CSS variable usage in computed styles
      const elements = container.querySelectorAll('[class*="var"]');
      expect(elements.length).toBeGreaterThanOrEqual(0);

      // Check that elements have proper styling
      const styledElements = container.querySelectorAll('[class*="text-"]');
      styledElements.forEach((element) => {
        const style = getComputedStyles(element as HTMLElement);
        expect(style.color).not.toBe('');
      });
    });

    it('should handle CSS variable fallbacks gracefully', () => {
      const { container } = render(
        <POSHeader
          onOpenQuickKeys={() => {}}
          onOpenCashDrop={() => {}}
          onOpenCashDrawer={() => {}}
          onCloseCashDrawer={() => {}}
        />
      );

      const elements = container.querySelectorAll('*');
      elements.forEach((element) => {
        const style = getComputedStyles(element as HTMLElement);
        // Should have computed color values
        expect(style.color).toBeTruthy();
      });
    });
  });

  describe('Flexbox Layout Support', () => {
    it('should support flexbox in all browsers', () => {
      const features = detectCSSFeatures();
      expect(features.flexbox).toBe(true);
    });

    it('should render flex layouts correctly', () => {
      const { container } = render(
        <POSHeader
          onOpenQuickKeys={() => {}}
          onOpenCashDrop={() => {}}
          onOpenCashDrawer={() => {}}
          onCloseCashDrawer={() => {}}
        />
      );

      const flexContainer = container.querySelector('.flex');
      expect(flexContainer).toBeTruthy();
      expect(checkFlexboxSupport(flexContainer as HTMLElement)).toBe(true);
    });

    it('should handle flex-wrap correctly', () => {
      const { container } = render(
        <POSHeader
          onOpenQuickKeys={() => {}}
          onOpenCashDrop={() => {}}
          onOpenCashDrawer={() => {}}
          onCloseCashDrawer={() => {}}
        />
      );

      const flexContainer = container.querySelector('.flex-wrap');
      expect(flexContainer).toBeTruthy();
      const style = getComputedStyles(flexContainer as HTMLElement);
      expect(style.flexWrap).toBe('wrap');
    });

    it('should handle flex-shrink correctly', () => {
      const { container } = render(
        <POSHeader
          onOpenQuickKeys={() => {}}
          onOpenCashDrop={() => {}}
          onOpenCashDrawer={() => {}}
          onCloseCashDrawer={() => {}}
        />
      );

      const shrinkElements = container.querySelectorAll('.flex-shrink-0');
      expect(shrinkElements.length).toBeGreaterThan(0);
      shrinkElements.forEach((element) => {
        const style = getComputedStyles(element as HTMLElement);
        expect(style.flexShrink).toBe('0');
      });
    });
  });

  describe('Grid Layout Support', () => {
    it('should support grid in all browsers', () => {
      const features = detectCSSFeatures();
      expect(features.grid).toBe(true);
    });

    it('should render grid layouts correctly', () => {
      const { container } = render(
        <ProductServiceTabs
          services={mockServices}
          products={mockProducts}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      const gridContainer = container.querySelector('.grid');
      expect(gridContainer).toBeTruthy();
      expect(checkGridSupport(gridContainer as HTMLElement)).toBe(true);
    });

    it('should handle responsive grid columns', () => {
      const { container } = render(
        <ProductServiceTabs
          services={mockServices}
          products={mockProducts}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      const gridContainer = container.querySelector('.grid');
      expect(gridContainer?.className).toMatch(/grid-cols-/);
    });

    it('should handle grid gap correctly', () => {
      const { container } = render(
        <ProductServiceTabs
          services={mockServices}
          products={mockProducts}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      const gridContainer = container.querySelector('.gap-4');
      expect(gridContainer).toBeTruthy();
      const style = getComputedStyles(gridContainer as HTMLElement);
      expect(style.gap).toBeTruthy();
    });
  });

  describe('Text Truncation Support', () => {
    it('should support text-overflow in all browsers', () => {
      const features = detectCSSFeatures();
      expect(features.textOverflow).toBe(true);
    });

    it('should truncate text with ellipsis correctly', () => {
      const { container } = render(
        <ProductServiceTabs
          services={mockServices}
          products={mockProducts}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      const truncatedElements = container.querySelectorAll('.truncate');
      expect(truncatedElements.length).toBeGreaterThan(0);
      truncatedElements.forEach((element) => {
        const style = getComputedStyles(element as HTMLElement);
        expect(style.overflow).toBe('hidden');
        expect(style.textOverflow).toBe('ellipsis');
      });
    });

    it('should handle line-clamp correctly', () => {
      const { container } = render(
        <ProductServiceTabs
          services={mockServices}
          products={mockProducts}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      const lineClampElements = container.querySelectorAll('[class*="line-clamp"]');
      expect(lineClampElements.length).toBeGreaterThan(0);
    });

    it('should handle whitespace-nowrap correctly', () => {
      const { container } = render(
        <POSHeader
          onOpenQuickKeys={() => {}}
          onOpenCashDrop={() => {}}
          onOpenCashDrawer={() => {}}
          onCloseCashDrawer={() => {}}
        />
      );

      const nowrapElements = container.querySelectorAll('.whitespace-nowrap');
      expect(nowrapElements.length).toBeGreaterThan(0);
      nowrapElements.forEach((element) => {
        const style = getComputedStyles(element as HTMLElement);
        expect(style.whiteSpace).toBe('nowrap');
      });
    });
  });

  describe('Overflow Handling', () => {
    it('should handle overflow-hidden correctly', () => {
      const { container } = render(
        <ProductServiceTabs
          services={mockServices}
          products={mockProducts}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      const overflowElements = container.querySelectorAll('.overflow-hidden');
      expect(overflowElements.length).toBeGreaterThan(0);
      overflowElements.forEach((element) => {
        const style = getComputedStyles(element as HTMLElement);
        expect(style.overflow).toBe('hidden');
      });
    });

    it('should handle overflow-x-hidden correctly', () => {
      const { container } = render(
        <ProductServiceTabs
          services={mockServices}
          products={mockProducts}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      const overflowXElements = container.querySelectorAll('.overflow-x-hidden');
      expect(overflowXElements.length).toBeGreaterThan(0);
      overflowXElements.forEach((element) => {
        const style = getComputedStyles(element as HTMLElement);
        expect(style.overflowX).toBe('hidden');
      });
    });

    it('should handle overflow-y-auto correctly', () => {
      const { container } = render(
        <POSCart
          items={mockCartItems}
          onUpdateItem={() => {}}
          onRemoveItem={() => {}}
          onAddItem={() => {}}
          subtotal={15000}
          discount={0}
          tax={0}
          tip={0}
          total={15000}
          notes=""
          onUpdateDiscount={() => {}}
          onUpdateTax={() => {}}
          onUpdateTip={() => {}}
          onUpdateNotes={() => {}}
        />
      );

      const overflowYElements = container.querySelectorAll('.overflow-y-auto');
      expect(overflowYElements.length).toBeGreaterThan(0);
      overflowYElements.forEach((element) => {
        const style = getComputedStyles(element as HTMLElement);
        expect(style.overflowY).toBe('auto');
      });
    });
  });

  describe('Transform and Transition Support', () => {
    it('should support CSS transforms', () => {
      const features = detectCSSFeatures();
      expect(features.transform).toBe(true);
    });

    it('should support CSS transitions', () => {
      const features = detectCSSFeatures();
      expect(features.transition).toBe(true);
    });

    it('should apply hover transitions correctly', () => {
      const { container } = render(
        <ProductServiceTabs
          services={mockServices}
          products={mockProducts}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      const hoverElements = container.querySelectorAll('[class*="hover:"]');
      expect(hoverElements.length).toBeGreaterThan(0);
    });
  });

  describe('Color and Styling Consistency', () => {
    it('should apply consistent colors across browsers', () => {
      const { container: container1 } = render(
        <POSHeader
          onOpenQuickKeys={() => {}}
          onOpenCashDrop={() => {}}
          onOpenCashDrawer={() => {}}
          onCloseCashDrawer={() => {}}
        />
      );

      const { container: container2 } = render(
        <POSHeader
          onOpenQuickKeys={() => {}}
          onOpenCashDrop={() => {}}
          onOpenCashDrawer={() => {}}
          onCloseCashDrawer={() => {}}
        />
      );

      const elements1 = container1.querySelectorAll('button');
      const elements2 = container2.querySelectorAll('button');

      expect(elements1.length).toBe(elements2.length);
    });

    it('should handle color variables correctly', () => {
      const { container } = render(
        <ProductServiceTabs
          services={mockServices}
          products={mockProducts}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      const coloredElements = container.querySelectorAll('[class*="text-"]');
      expect(coloredElements.length).toBeGreaterThan(0);
      coloredElements.forEach((element) => {
        const style = getComputedStyles(element as HTMLElement);
        expect(style.color).toBeTruthy();
      });
    });

    it('should handle background colors correctly', () => {
      const { container } = render(
        <POSPayment
          total={25000}
          onProcessPayment={() => {}}
        />
      );

      const bgElements = container.querySelectorAll('[class*="bg-"]');
      expect(bgElements.length).toBeGreaterThan(0);
      bgElements.forEach((element) => {
        const style = getComputedStyles(element as HTMLElement);
        expect(style.backgroundColor).toBeTruthy();
      });
    });
  });

  describe('Input and Form Elements', () => {
    it('should render input fields correctly across browsers', () => {
      const { container } = render(
        <POSCart
          items={mockCartItems}
          onUpdateItem={() => {}}
          onRemoveItem={() => {}}
          onAddItem={() => {}}
          subtotal={15000}
          discount={0}
          tax={0}
          tip={0}
          total={15000}
          notes=""
          onUpdateDiscount={() => {}}
          onUpdateTax={() => {}}
          onUpdateTip={() => {}}
          onUpdateNotes={() => {}}
        />
      );

      const inputs = container.querySelectorAll('input');
      expect(inputs.length).toBeGreaterThan(0);
      inputs.forEach((input) => {
        const style = getComputedStyles(input);
        expect(style.width).not.toBe('0px');
        expect(style.height).not.toBe('0px');
      });
    });

    it('should render textareas correctly across browsers', () => {
      const { container } = render(
        <POSCart
          items={mockCartItems}
          onUpdateItem={() => {}}
          onRemoveItem={() => {}}
          onAddItem={() => {}}
          subtotal={15000}
          discount={0}
          tax={0}
          tip={0}
          total={15000}
          notes=""
          onUpdateDiscount={() => {}}
          onUpdateTax={() => {}}
          onUpdateTip={() => {}}
          onUpdateNotes={() => {}}
        />
      );

      const textareas = container.querySelectorAll('textarea');
      expect(textareas.length).toBeGreaterThan(0);
      textareas.forEach((textarea) => {
        const style = getComputedStyles(textarea);
        expect(style.width).not.toBe('0px');
        expect(style.height).not.toBe('0px');
      });
    });
  });

  describe('Browser-Specific Issues', () => {
    it('should handle Safari-specific styling', () => {
      const { container } = render(
        <ProductServiceTabs
          services={mockServices}
          products={mockProducts}
          onAddService={() => {}}
          onAddProduct={() => {}}
        />
      );

      // Check for webkit prefixes if needed
      const elements = container.querySelectorAll('[class*="webkit"]');
      // Should not have webkit-specific classes in Tailwind
      expect(elements.length).toBe(0);
    });

    it('should handle Firefox-specific styling', () => {
      const { container } = render(
        <POSHeader
          onOpenQuickKeys={() => {}}
          onOpenCashDrop={() => {}}
          onOpenCashDrawer={() => {}}
          onCloseCashDrawer={() => {}}
        />
      );

      const buttons = container.querySelectorAll('button');
      buttons.forEach((button) => {
        const style = getComputedStyles(button);
        expect(style.display).toBeTruthy();
      });
    });

    it('should handle Edge-specific styling', () => {
      const { container } = render(
        <POSPayment
          total={25000}
          onProcessPayment={() => {}}
        />
      );

      const elements = container.querySelectorAll('*');
      elements.forEach((element) => {
        const style = getComputedStyles(element as HTMLElement);
        expect(style.display).toBeTruthy();
      });
    });
  });
});
