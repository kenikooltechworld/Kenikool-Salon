/**
 * Authentication validation utilities
 */

export interface PasswordStrength {
  score: 0 | 1 | 2 | 3 | 4;
  label: "Very Weak" | "Weak" | "Fair" | "Good" | "Strong";
  color: "destructive" | "warning" | "secondary" | "primary" | "success";
  percentage: number;
}

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function calculatePasswordStrength(password: string): PasswordStrength {
  let score = 0;

  if (!password) {
    return {
      score: 0,
      label: "Very Weak",
      color: "destructive",
      percentage: 0,
    };
  }

  // Length checks
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;

  // Character variety checks
  if (/[a-z]/.test(password)) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^a-zA-Z0-9]/.test(password)) score++;

  // Cap score at 4
  score = Math.min(score, 4);

  const strengthMap: Record<number, PasswordStrength> = {
    0: {
      score: 0,
      label: "Very Weak",
      color: "destructive",
      percentage: 20,
    },
    1: {
      score: 1,
      label: "Weak",
      color: "destructive",
      percentage: 40,
    },
    2: {
      score: 2,
      label: "Fair",
      color: "warning",
      percentage: 60,
    },
    3: {
      score: 3,
      label: "Good",
      color: "primary",
      percentage: 80,
    },
    4: {
      score: 4,
      label: "Strong",
      color: "success",
      percentage: 100,
    },
  };

  return strengthMap[score];
}

export function getPasswordRequirements(password: string) {
  return {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[^a-zA-Z0-9]/.test(password),
  };
}

export function validatePasswordRequirements(password: string): boolean {
  const requirements = getPasswordRequirements(password);
  return (
    requirements.length &&
    requirements.uppercase &&
    requirements.lowercase &&
    requirements.number
  );
}
