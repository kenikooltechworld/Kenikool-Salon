/**
 * Security headers middleware for Vite.
 * Adds security headers to all responses during development and build.
 */

import type { Plugin } from "vite";

export function securityHeadersPlugin(): Plugin {
  return {
    name: "security-headers",
    transformIndexHtml: {
      order: "pre",
      handler(html) {
        // Add CSP meta tag - allow localhost and Docker internal network for development
        const cspMeta = `<meta http-equiv="Content-Security-Policy" content="default-src 'self' http://localhost:* http://127.0.0.1:* http://api:*; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https: http://localhost:* http://127.0.0.1:* http://api:* ws://localhost:* ws://127.0.0.1:* ws://api:*; frame-ancestors 'none'; base-uri 'self'; form-action 'self'">`;

        // Add X-UA-Compatible meta tag
        const uaCompatMeta = `<meta http-equiv="X-UA-Compatible" content="IE=edge">`;

        // Add viewport meta tag
        const viewportMeta = `<meta name="viewport" content="width=device-width, initial-scale=1.0">`;

        // Add referrer policy meta tag
        const referrerMeta = `<meta name="referrer" content="strict-origin-when-cross-origin">`;

        // Insert meta tags after <head>
        return html.replace(
          /<head>/i,
          `<head>
    ${cspMeta}
    ${uaCompatMeta}
    ${viewportMeta}
    ${referrerMeta}`,
        );
      },
    },
  };
}

/**
 * Security headers configuration for development server.
 * Returns middleware configuration for Vite dev server.
 */
export function getSecurityHeadersConfig() {
  return {
    headers: {
      // Prevent clickjacking attacks
      "X-Frame-Options": "DENY",

      // Prevent MIME type sniffing
      "X-Content-Type-Options": "nosniff",

      // Enable XSS protection in older browsers
      "X-XSS-Protection": "1; mode=block",

      // Force HTTPS for 1 year
      "Strict-Transport-Security":
        "max-age=31536000; includeSubDomains; preload",

      // Content Security Policy - allow localhost and Docker internal network for development
      "Content-Security-Policy":
        "default-src 'self' http://localhost:* http://127.0.0.1:* http://api:*; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https: http://localhost:* http://127.0.0.1:* http://api:* ws://localhost:* ws://127.0.0.1:* ws://api:*; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",

      // Referrer Policy
      "Referrer-Policy": "strict-origin-when-cross-origin",

      // Permissions Policy
      "Permissions-Policy":
        "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()",
    },
  };
}
