/**
 * Validation utility functions
 */

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return pattern.test(email);
}

/**
 * Validate phone format (African numbers)
 */
export function isValidPhone(phone: string): boolean {
  const cleaned = phone.replace(/\s|-/g, "");

  if (cleaned.startsWith("+")) {
    // +[country code][number] - total 10-15 digits
    const pattern = /^\+[1-9]\d{9,14}$/;
    return pattern.test(cleaned);
  } else {
    // [country code][number] - total 10-15 digits
    const pattern = /^[1-9]\d{9,14}$/;
    return pattern.test(cleaned);
  }
}

/**
 * Validate URL format
 */
export function isValidURL(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate currency amount
 */
export function isValidCurrency(amount: number | string): boolean {
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  return !isNaN(num) && num >= 0 && num <= 999999999.99;
}

/**
 * Validate date format
 */
export function isValidDate(date: string | Date): boolean {
  const d = typeof date === "string" ? new Date(date) : date;
  return d instanceof Date && !isNaN(d.getTime());
}

/**
 * Validate password strength
 * Requirements: min 8 chars, uppercase, lowercase, digit, special char
 */
export function isStrongPassword(password: string): boolean {
  if (password.length < 8) return false;
  if (!/[A-Z]/.test(password)) return false;
  if (!/[a-z]/.test(password)) return false;
  if (!/\d/.test(password)) return false;
  if (!/[!@#$%^&*()_+\-=\[\]{};:'",.< >?/\\|`~]/.test(password)) return false;
  return true;
}

/**
 * Get password strength details
 */
export function getPasswordStrength(password: string): {
  score: number;
  level: "weak" | "fair" | "good" | "strong";
  feedback: string[];
} {
  const feedback: string[] = [];
  let score = 0;

  if (password.length >= 8) score += 1;
  else feedback.push("At least 8 characters");

  if (password.length >= 12) score += 1;
  else if (password.length >= 8)
    feedback.push("Consider 12+ characters for better security");

  if (/[a-z]/.test(password)) score += 1;
  else feedback.push("Add lowercase letters");

  if (/[A-Z]/.test(password)) score += 1;
  else feedback.push("Add uppercase letters");

  if (/\d/.test(password)) score += 1;
  else feedback.push("Add numbers");

  if (/[!@#$%^&*()_+\-=\[\]{};:'",.< >?/\\|`~]/.test(password)) score += 1;
  else feedback.push("Add special characters");

  let level: "weak" | "fair" | "good" | "strong" = "weak";
  if (score >= 5) level = "strong";
  else if (score >= 4) level = "good";
  else if (score >= 3) level = "fair";

  return { score, level, feedback };
}

/**
 * Validate salon name
 */
export function isValidSalonName(name: string): boolean {
  const trimmed = name.trim();
  return trimmed.length >= 3 && trimmed.length <= 255;
}

/**
 * Validate owner name
 */
export function isValidOwnerName(name: string): boolean {
  const trimmed = name.trim();
  return trimmed.length >= 2 && trimmed.length <= 100;
}

/**
 * Validate address
 */
export function isValidAddress(address: string): boolean {
  const trimmed = address.trim();
  return trimmed.length >= 5 && trimmed.length <= 500;
}

/**
 * Validate referral code
 */
export function isValidReferralCode(code: string): boolean {
  const pattern = /^[a-zA-Z0-9]+$/;
  return pattern.test(code) && code.length > 0;
}
