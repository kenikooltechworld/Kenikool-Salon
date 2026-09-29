// Class name utilities
export { cn } from "./cn";

// Formatting utilities
export {
  formatCurrency,
  formatPhone,
  formatDate,
  formatTime,
  formatDateTime,
  formatDuration,
} from "./format";

// Date utilities
export {
  addDays,
  addHours,
  addMinutes,
  isSameDay,
  isToday,
  isTomorrow,
  getWeekStart,
  getWeekEnd,
  getMonthStart,
  getMonthEnd,
  getDayName,
  getMonthName,
  getShortDayName,
  getShortMonthName,
  isPast,
  isFuture,
  getDaysDifference,
  getHoursDifference,
  getMinutesDifference,
} from "./date";

// Validation utilities
export {
  isValidEmail,
  isValidPhone,
  isValidURL,
  isValidCurrency,
  isValidDate,
  isStrongPassword,
  getPasswordStrength,
  isValidSalonName,
  isValidOwnerName,
  isValidAddress,
  isValidReferralCode,
} from "./validation";

// API utilities
export {
  createApiClient,
  apiClient,
  get,
  post,
  put,
  patch,
  del,
  getErrorMessage,
} from "./api";
