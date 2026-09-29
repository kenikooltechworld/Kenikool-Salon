/**
 * Security utilities for XSS prevention and input sanitization.
 */

import DOMPurify from "dompurify";

/**
 * Sanitize HTML to prevent XSS attacks.
 * @param dirty - HTML string to sanitize
 * @returns Sanitized HTML string
 */
export function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ["b", "i", "em", "strong", "a", "p", "br"],
    ALLOWED_ATTR: ["href", "title"],
    KEEP_CONTENT: true,
  });
}

/**
 * Escape HTML special characters to prevent XSS.
 * @param text - Text to escape
 * @returns Escaped text safe for HTML context
 */
export function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#x27;",
    "/": "&#x2F;",
  };

  return text.replace(/[&<>"'\/]/g, (char) => map[char]);
}

/**
 * Sanitize user input to prevent injection attacks.
 * @param input - User input to sanitize
 * @param maxLength - Maximum allowed length
 * @returns Sanitized input
 */
export function sanitizeInput(input: string, maxLength: number = 255): string {
  if (!input || typeof input !== "string") {
    return "";
  }

  // Remove null bytes
  let sanitized = input.replace(/\x00/g, "");

  // Trim whitespace
  sanitized = sanitized.trim();

  // Limit length
  if (sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength);
  }

  return sanitized;
}

/**
 * Validate and sanitize email address.
 * @param email - Email to validate
 * @returns Sanitized email or empty string if invalid
 */
export function sanitizeEmail(email: string): string {
  const sanitized = sanitizeInput(email, 255);

  // Basic email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(sanitized)) {
    return "";
  }

  return sanitized.toLowerCase();
}

/**
 * Validate and sanitize phone number.
 * @param phone - Phone number to validate
 * @returns Sanitized phone number or empty string if invalid
 */
export function sanitizePhone(phone: string): string {
  const sanitized = sanitizeInput(phone, 20);

  // Remove common formatting characters
  const cleaned = sanitized.replace(/[\s\-\(\)\.]+/g, "");

  // Check if it's a valid phone number (7-15 digits)
  if (!/^\+?1?\d{7,15}$/.test(cleaned)) {
    return "";
  }

  return cleaned;
}

/**
 * Validate and sanitize URL.
 * @param url - URL to validate
 * @returns Sanitized URL or empty string if invalid
 */
export function sanitizeUrl(url: string): string {
  const sanitized = sanitizeInput(url, 2048);

  try {
    const parsed = new URL(sanitized);

    // Only allow http and https protocols
    if (!["http:", "https:"].includes(parsed.protocol)) {
      return "";
    }

    return parsed.toString();
  } catch {
    return "";
  }
}

/**
 * Sanitize object to prevent injection attacks.
 * @param obj - Object to sanitize
 * @returns Sanitized object
 */
export function sanitizeObject(obj: Record<string, any>): Record<string, any> {
  const sanitized: Record<string, any> = {};

  for (const [key, value] of Object.entries(obj)) {
    // Skip keys that start with $ (MongoDB operators)
    if (key.startsWith("$")) {
      continue;
    }

    if (typeof value === "string") {
      sanitized[key] = sanitizeInput(value);
    } else if (typeof value === "object" && value !== null) {
      if (Array.isArray(value)) {
        sanitized[key] = value.map((item) =>
          typeof item === "string" ? sanitizeInput(item) : item,
        );
      } else {
        sanitized[key] = sanitizeObject(value);
      }
    } else {
      sanitized[key] = value;
    }
  }

  return sanitized;
}

/**
 * Validate file upload.
 * @param file - File to validate
 * @param allowedExtensions - Set of allowed file extensions
 * @param maxSize - Maximum file size in bytes
 * @returns true if valid, false otherwise
 */
export function validateFileUpload(
  file: File,
  allowedExtensions: Set<string>,
  maxSize: number = 10 * 1024 * 1024,
): boolean {
  // Check file size
  if (file.size > maxSize) {
    return false;
  }

  // Check file extension
  const filename = file.name.toLowerCase();
  if (!filename.includes(".")) {
    return false;
  }

  const ext = filename.split(".").pop();
  if (!ext || !allowedExtensions.has(ext)) {
    return false;
  }

  // Check for path traversal attempts
  if (
    filename.includes("..") ||
    filename.includes("/") ||
    filename.includes("\\")
  ) {
    return false;
  }

  return true;
}
