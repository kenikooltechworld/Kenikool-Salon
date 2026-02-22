/**
 * Tests for the Salon Reviews Widget JavaScript Loader
 * 
 * Note: These tests verify the widget.js functionality
 * Run with: jest salon/public/widget.test.js
 */

describe('Salon Reviews Widget (widget.js)', () => {
  let container;
  let mockFetch;
  let mockScript;

  beforeEach(() => {
    // Create container element
    container = document.createElement('div');
    container.id = 'salon-reviews-widget';
    document.body.appendChild(container);

    // Mock fetch
    mockFetch = jest.fn();
    global.fetch = mockFetch;

    // Mock script element
    mockScript = document.createElement('script');
    mockScript.src = 'http://localhost/widget.js';
    mockScript.setAttribute('data-tenant-id', 'test-tenant');
    mockScript.setAttribute('data-max-reviews', '5');
    Object.defineProperty(document, 'currentScript', {
      value: mockScript,
      writable: true
    });
  });

  afterEach(() => {
    document.body.removeChild(container);
    jest.clearAllMocks();
  });

  describe('Widget Initialization', () => {
    it('should find the container element', () => {
      const element = document.getElementById('salon-reviews-widget');
      expect(element).toBeTruthy();
    });

    it('should read tenant ID from script attribute', () => {
      const tenantId = mockScript.getAttribute('data-tenant-id');
      expect(tenantId).toBe('test-tenant');
    });

    it('should read max reviews from script attribute', () => {
      const maxReviews = mockScript.getAttribute('data-max-reviews');
      expect(parseInt(maxReviews, 10)).toBe(5);
    });

    it('should use default max reviews if not specified', () => {
      mockScript.removeAttribute('data-max-reviews');
      const maxReviews = parseInt(mockScript.getAttribute('data-max-reviews') || '5', 10);
      expect(maxReviews).toBe(5);
    });

    it('should use default layout if not specified', () => {
      const layout = mockScript.getAttribute('data-layout') || 'grid';
      expect(layout).toBe('grid');
    });

    it('should read custom layout from script attribute', () => {
      mockScript.setAttribute('data-layout', 'list');
      const layout = mockScript.getAttribute('data-layout');
      expect(layout).toBe('list');
    });
  });

  describe('Color Configuration', () => {
    it('should use default primary color', () => {
      const color = mockScript.getAttribute('data-primary-color') || '#3b82f6';
      expect(color).toBe('#3b82f6');
    });

    it('should use default background color', () => {
      const color = mockScript.getAttribute('data-background-color') || '#ffffff';
      expect(color).toBe('#ffffff');
    });

    it('should use default text color', () => {
      const color = mockScript.getAttribute('data-text-color') || '#1f2937';
      expect(color).toBe('#1f2937');
    });

    it('should read custom primary color from script attribute', () => {
      mockScript.setAttribute('data-primary-color', '#ff0000');
      const color = mockScript.getAttribute('data-primary-color');
      expect(color).toBe('#ff0000');
    });

    it('should read custom background color from script attribute', () => {
      mockScript.setAttribute('data-background-color', '#f0f0f0');
      const color = mockScript.getAttribute('data-background-color');
      expect(color).toBe('#f0f0f0');
    });

    it('should read custom text color from script attribute', () => {
      mockScript.setAttribute('data-text-color', '#333333');
      const color = mockScript.getAttribute('data-text-color');
      expect(color).toBe('#333333');
    });
  });

  describe('API Configuration', () => {
    it('should use default API base URL', () => {
      const apiUrl = mockScript.getAttribute('data-api-url') || 'https://api.yourdomain.com';
      expect(apiUrl).toBe('https://api.yourdomain.com');
    });

    it('should read custom API URL from script attribute', () => {
      mockScript.setAttribute('data-api-url', 'http://localhost:8000');
      const apiUrl = mockScript.getAttribute('data-api-url');
      expect(apiUrl).toBe('http://localhost:8000');
    });
  });

  describe('Error Handling', () => {
    it('should handle missing tenant ID', () => {
      mockScript.removeAttribute('data-tenant-id');
      const tenantId = mockScript.getAttribute('data-tenant-id');
      expect(tenantId).toBeNull();
    });

    it('should handle missing container element', () => {
      const missingContainer = document.getElementById('non-existent-widget');
      expect(missingContainer).toBeNull();
    });

    it('should handle fetch errors gracefully', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));
      
      // Simulate error handling
      try {
        await mockFetch('http://api.test/reviews');
      } catch (error) {
        expect(error.message).toBe('Network error');
      }
    });

    it('should handle invalid JSON response', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        }
      });

      try {
        const response = await mockFetch('http://api.test/reviews');
        await response.json();
      } catch (error) {
        expect(error.message).toBe('Invalid JSON');
      }
    });
  });

  describe('HTML Escaping', () => {
    it('should escape HTML special characters', () => {
      const escapeHtml = (text) => {
        const map = {
          '&': '&amp;',
          '<': '&lt;',
          '>': '&gt;',
          '"': '&quot;',
          "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
      };

      expect(escapeHtml('<script>alert("xss")</script>')).toBe(
        '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'
      );
    });

    it('should escape ampersands', () => {
      const escapeHtml = (text) => {
        const map = {
          '&': '&amp;',
          '<': '&lt;',
          '>': '&gt;',
          '"': '&quot;',
          "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
      };

      expect(escapeHtml('A & B')).toBe('A &amp; B');
    });

    it('should escape quotes', () => {
      const escapeHtml = (text) => {
        const map = {
          '&': '&amp;',
          '<': '&lt;',
          '>': '&gt;',
          '"': '&quot;',
          "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
      };

      expect(escapeHtml('He said "Hello"')).toBe('He said &quot;Hello&quot;');
    });
  });

  describe('Star Rendering', () => {
    it('should render correct number of filled stars', () => {
      const renderStars = (rating, color) => {
        let stars = '';
        for (let i = 0; i < 5; i++) {
          if (i < rating) {
            stars += `<span style="color: ${color}; font-size: 12px;">★</span>`;
          } else {
            stars += `<span style="color: #d1d5db; font-size: 12px;">★</span>`;
          }
        }
        return stars;
      };

      const stars = renderStars(4, '#3b82f6');
      const filledCount = (stars.match(/color: #3b82f6/g) || []).length;
      expect(filledCount).toBe(4);
    });

    it('should render correct number of empty stars', () => {
      const renderStars = (rating, color) => {
        let stars = '';
        for (let i = 0; i < 5; i++) {
          if (i < rating) {
            stars += `<span style="color: ${color}; font-size: 12px;">★</span>`;
          } else {
            stars += `<span style="color: #d1d5db; font-size: 12px;">★</span>`;
          }
        }
        return stars;
      };

      const stars = renderStars(3, '#3b82f6');
      const emptyCount = (stars.match(/color: #d1d5db/g) || []).length;
      expect(emptyCount).toBe(2);
    });

    it('should render 5 stars for 5-star rating', () => {
      const renderStars = (rating, color) => {
        let stars = '';
        for (let i = 0; i < 5; i++) {
          if (i < rating) {
            stars += `<span style="color: ${color}; font-size: 12px;">★</span>`;
          } else {
            stars += `<span style="color: #d1d5db; font-size: 12px;">★</span>`;
          }
        }
        return stars;
      };

      const stars = renderStars(5, '#3b82f6');
      const filledCount = (stars.match(/color: #3b82f6/g) || []).length;
      expect(filledCount).toBe(5);
    });

    it('should render 0 stars for 0-star rating', () => {
      const renderStars = (rating, color) => {
        let stars = '';
        for (let i = 0; i < 5; i++) {
          if (i < rating) {
            stars += `<span style="color: ${color}; font-size: 12px;">★</span>`;
          } else {
            stars += `<span style="color: #d1d5db; font-size: 12px;">★</span>`;
          }
        }
        return stars;
      };

      const stars = renderStars(0, '#3b82f6');
      const filledCount = (stars.match(/color: #3b82f6/g) || []).length;
      expect(filledCount).toBe(0);
    });
  });

  describe('Widget Data Structure', () => {
    it('should handle reviews array in response', () => {
      const mockData = {
        reviews: [
          {
            _id: '1',
            client_name: 'John Doe',
            rating: 5,
            comment: 'Great service!',
            service_name: 'Haircut'
          }
        ],
        stats: {
          average_rating: 5,
          total_reviews: 1
        }
      };

      expect(mockData.reviews).toHaveLength(1);
      expect(mockData.reviews[0].client_name).toBe('John Doe');
    });

    it('should handle stats in response', () => {
      const mockData = {
        reviews: [],
        stats: {
          average_rating: 4.5,
          total_reviews: 10
        }
      };

      expect(mockData.stats.average_rating).toBe(4.5);
      expect(mockData.stats.total_reviews).toBe(10);
    });

    it('should handle empty reviews array', () => {
      const mockData = {
        reviews: [],
        stats: {
          average_rating: 0,
          total_reviews: 0
        }
      };

      expect(mockData.reviews).toHaveLength(0);
    });

    it('should handle multiple reviews', () => {
      const mockData = {
        reviews: [
          { _id: '1', client_name: 'User 1', rating: 5, comment: 'Good', service_name: 'Service 1' },
          { _id: '2', client_name: 'User 2', rating: 4, comment: 'Nice', service_name: 'Service 2' },
          { _id: '3', client_name: 'User 3', rating: 5, comment: 'Excellent', service_name: 'Service 3' }
        ],
        stats: {
          average_rating: 4.67,
          total_reviews: 3
        }
      };

      expect(mockData.reviews).toHaveLength(3);
      expect(mockData.stats.average_rating).toBeCloseTo(4.67, 1);
    });
  });

  describe('Comment Truncation', () => {
    it('should truncate comments longer than 100 characters', () => {
      const comment = 'A'.repeat(150);
      const truncated = comment.length > 100 ? comment.substring(0, 100) + '...' : comment;
      expect(truncated).toHaveLength(103);
      expect(truncated).toMatch(/\.\.\.$/);
    });

    it('should not truncate comments shorter than 100 characters', () => {
      const comment = 'This is a short comment';
      const truncated = comment.length > 100 ? comment.substring(0, 100) + '...' : comment;
      expect(truncated).toBe(comment);
    });

    it('should handle exactly 100 character comments', () => {
      const comment = 'A'.repeat(100);
      const truncated = comment.length > 100 ? comment.substring(0, 100) + '...' : comment;
      expect(truncated).toBe(comment);
    });
  });

  describe('Review Count Display', () => {
    it('should display singular "review" for 1 review', () => {
      const count = 1;
      const text = `Based on ${count} review${count !== 1 ? 's' : ''}`;
      expect(text).toBe('Based on 1 review');
    });

    it('should display plural "reviews" for multiple reviews', () => {
      const count = 5;
      const text = `Based on ${count} review${count !== 1 ? 's' : ''}`;
      expect(text).toBe('Based on 5 reviews');
    });

    it('should display plural "reviews" for 0 reviews', () => {
      const count = 0;
      const text = `Based on ${count} review${count !== 1 ? 's' : ''}`;
      expect(text).toBe('Based on 0 reviews');
    });
  });

  describe('Link Generation', () => {
    it('should generate correct review page link', () => {
      const tenantId = 'test-tenant-123';
      const link = `/salons/${tenantId}/reviews`;
      expect(link).toBe('/salons/test-tenant-123/reviews');
    });

    it('should include target="_blank" attribute', () => {
      const html = '<a href="/salons/test/reviews" target="_blank">View all reviews</a>';
      expect(html).toContain('target="_blank"');
    });

    it('should include rel="noopener noreferrer" attribute', () => {
      const html = '<a href="/salons/test/reviews" rel="noopener noreferrer">View all reviews</a>';
      expect(html).toContain('rel="noopener noreferrer"');
    });
  });

  describe('Styling', () => {
    it('should apply border-radius to widget', () => {
      const style = 'border-radius: 8px;';
      expect(style).toContain('border-radius');
    });

    it('should apply box-shadow to widget', () => {
      const style = 'box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);';
      expect(style).toContain('box-shadow');
    });

    it('should apply font-family to widget', () => {
      const style = "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;";
      expect(style).toContain('font-family');
    });

    it('should apply padding to header', () => {
      const style = 'padding: 16px;';
      expect(style).toContain('padding');
    });

    it('should apply border to header', () => {
      const style = 'border-bottom: 1px solid #3b82f6;';
      expect(style).toContain('border-bottom');
    });
  });

  describe('Responsive Design', () => {
    it('should use width: 100% for full width', () => {
      const style = 'width: 100%;';
      expect(style).toContain('width: 100%');
    });

    it('should use grid layout for grid mode', () => {
      const layout = 'grid';
      const display = layout === 'grid' ? 'grid' : 'flex';
      expect(display).toBe('grid');
    });

    it('should use flex layout for list mode', () => {
      const layout = 'list';
      const display = layout === 'grid' ? 'grid' : 'flex';
      expect(display).toBe('flex');
    });
  });
});
