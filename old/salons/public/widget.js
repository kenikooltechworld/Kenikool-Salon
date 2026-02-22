/**
 * Salon Reviews Widget
 * Embeddable widget for displaying salon reviews on external websites
 * 
 * Usage:
 * <div id="salon-reviews-widget"></div>
 * <script>
 *   (function () {
 *     var script = document.createElement("script");
 *     script.src = "https://yourdomain.com/widget.js";
 *     script.setAttribute("data-tenant-id", "YOUR_TENANT_ID");
 *     script.setAttribute("data-max-reviews", "5");
 *     script.setAttribute("data-layout", "grid");
 *     document.body.appendChild(script);
 *   })();
 * </script>
 */

(function () {
  // Get script element and attributes
  const currentScript = document.currentScript || 
    document.querySelector('script[src*="widget.js"]');
  
  if (!currentScript) {
    console.error('Salon Reviews Widget: Could not find script element');
    return;
  }

  const tenantId = currentScript.getAttribute('data-tenant-id');
  const maxReviews = parseInt(currentScript.getAttribute('data-max-reviews') || '5', 10);
  const layout = currentScript.getAttribute('data-layout') || 'grid';
  const apiBaseUrl = currentScript.getAttribute('data-api-url') || 'https://api.yourdomain.com';
  
  // Color configuration
  const primaryColor = currentScript.getAttribute('data-primary-color') || '#3b82f6';
  const backgroundColor = currentScript.getAttribute('data-background-color') || '#ffffff';
  const textColor = currentScript.getAttribute('data-text-color') || '#1f2937';

  if (!tenantId) {
    console.error('Salon Reviews Widget: data-tenant-id attribute is required');
    return;
  }

  // Create container
  const container = document.getElementById('salon-reviews-widget');
  if (!container) {
    console.error('Salon Reviews Widget: Container element with id "salon-reviews-widget" not found');
    return;
  }

  // Add loading state
  container.innerHTML = '<div style="padding: 16px; text-align: center; color: #666;">Loading reviews...</div>';

  // Fetch reviews
  fetch(`${apiBaseUrl}/api/reviews/widget/${tenantId}?limit=${maxReviews}`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      const reviews = data.reviews || [];
      const stats = data.stats || { average_rating: 0, total_reviews: 0 };

      // Render widget
      renderWidget(container, reviews, stats, {
        primaryColor,
        backgroundColor,
        textColor,
        layout,
        tenantId,
        maxReviews
      });
    })
    .catch(error => {
      console.error('Salon Reviews Widget: Error fetching reviews', error);
      container.innerHTML = `<div style="padding: 16px; border: 1px solid #fca5a5; border-radius: 8px; background-color: ${backgroundColor}; color: #dc2626; font-size: 14px;">Error loading reviews</div>`;
    });

  /**
   * Render the widget HTML
   */
  function renderWidget(container, reviews, stats, config) {
    const {
      primaryColor,
      backgroundColor,
      textColor,
      layout,
      tenantId
    } = config;

    // Create widget HTML
    let html = `
      <div style="
        width: 100%;
        border-radius: 8px;
        overflow: hidden;
        background-color: ${backgroundColor};
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      ">
        <!-- Header -->
        <div style="
          padding: 16px;
          border-bottom: 1px solid ${primaryColor};
          background-color: ${primaryColor}10;
        ">
          <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
          ">
            <h3 style="
              font-weight: 600;
              font-size: 14px;
              color: ${textColor};
              margin: 0;
            ">Customer Reviews</h3>
            <div style="
              display: flex;
              align-items: center;
              gap: 8px;
            ">
              <div style="display: flex; gap: 2px;">
                ${renderStars(Math.round(stats.average_rating), primaryColor)}
              </div>
              <span style="
                font-size: 14px;
                font-weight: 500;
                color: ${textColor};
              ">${stats.average_rating.toFixed(1)}</span>
            </div>
          </div>
          <p style="
            font-size: 12px;
            color: ${textColor};
            opacity: 0.7;
            margin: 0;
          ">Based on ${stats.total_reviews} review${stats.total_reviews !== 1 ? 's' : ''}</p>
        </div>

        <!-- Reviews -->
        <div style="
          padding: 16px;
          display: ${layout === 'grid' ? 'grid' : 'flex'};
          ${layout === 'grid' ? 'grid-template-columns: 1fr; gap: 12px;' : 'flex-direction: column; gap: 12px;'}
        ">
    `;

    if (reviews.length > 0) {
      reviews.forEach(review => {
        html += `
          <div style="
            padding: 12px;
            border-radius: 6px;
            border: 1px solid ${primaryColor}30;
            background-color: ${primaryColor}05;
          ">
            <div style="
              display: flex;
              align-items: flex-start;
              justify-content: space-between;
              margin-bottom: 8px;
            ">
              <div style="flex: 1;">
                <div style="
                  display: flex;
                  gap: 4px;
                  margin-bottom: 4px;
                ">
                  ${renderStars(review.rating, primaryColor)}
                </div>
                <p style="
                  font-weight: 500;
                  font-size: 14px;
                  color: ${textColor};
                  margin: 0;
                ">${escapeHtml(review.client_name)}</p>
              </div>
            </div>
            ${review.comment ? `
              <p style="
                font-size: 12px;
                line-height: 1.5;
                margin-bottom: 8px;
                color: ${textColor};
                opacity: 0.8;
                margin: 0 0 8px 0;
              ">${escapeHtml(review.comment.length > 100 ? review.comment.substring(0, 100) + '...' : review.comment)}</p>
            ` : ''}
            ${review.service_name ? `
              <p style="
                font-size: 12px;
                color: ${textColor};
                opacity: 0.6;
                margin: 0;
              ">${escapeHtml(review.service_name)}</p>
            ` : ''}
          </div>
        `;
      });
    } else {
      html += `
        <p style="
          font-size: 14px;
          text-align: center;
          padding: 16px;
          color: ${textColor};
          opacity: 0.6;
          margin: 0;
        ">No reviews yet</p>
      `;
    }

    html += `
        </div>

        <!-- Footer -->
        <div style="
          padding: 12px 16px;
          border-top: 1px solid ${primaryColor};
          text-align: center;
        ">
          <a href="/salons/${tenantId}/reviews" target="_blank" rel="noopener noreferrer" style="
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            font-weight: 500;
            color: ${primaryColor};
            text-decoration: none;
            transition: opacity 0.2s;
          " onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
            View all reviews
            <span style="font-size: 10px;">↗</span>
          </a>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  /**
   * Render star rating
   */
  function renderStars(rating, color) {
    let stars = '';
    for (let i = 0; i < 5; i++) {
      if (i < rating) {
        stars += `<span style="color: ${color}; font-size: 12px;">★</span>`;
      } else {
        stars += `<span style="color: #d1d5db; font-size: 12px;">★</span>`;
      }
    }
    return stars;
  }

  /**
   * Escape HTML to prevent XSS
   */
  function escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
  }
})();
