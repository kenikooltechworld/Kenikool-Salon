/**
 * Date utility functions for common date operations
 */

/**
 * Add days to a date
 */
export function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

/**
 * Add hours to a date
 */
export function addHours(date: Date, hours: number): Date {
  const result = new Date(date);
  result.setHours(result.getHours() + hours);
  return result;
}

/**
 * Add minutes to a date
 */
export function addMinutes(date: Date, minutes: number): Date {
  const result = new Date(date);
  result.setMinutes(result.getMinutes() + minutes);
  return result;
}

/**
 * Check if two dates are the same day
 */
export function isSameDay(date1: Date, date2: Date): boolean {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
}

/**
 * Check if date is today
 */
export function isToday(date: Date): boolean {
  return isSameDay(date, new Date());
}

/**
 * Check if date is tomorrow
 */
export function isTomorrow(date: Date): boolean {
  return isSameDay(date, addDays(new Date(), 1));
}

/**
 * Get start of week (Monday)
 */
export function getWeekStart(date: Date): Date {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  return new Date(d.setDate(diff));
}

/**
 * Get end of week (Sunday)
 */
export function getWeekEnd(date: Date): Date {
  const start = getWeekStart(date);
  return addDays(start, 6);
}

/**
 * Get start of month
 */
export function getMonthStart(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

/**
 * Get end of month
 */
export function getMonthEnd(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0);
}

/**
 * Get day name (Monday, Tuesday, etc.)
 */
export function getDayName(date: Date): string {
  const days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  return days[date.getDay()];
}

/**
 * Get month name (January, February, etc.)
 */
export function getMonthName(date: Date): string {
  const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  return months[date.getMonth()];
}

/**
 * Get short day name (Mon, Tue, etc.)
 */
export function getShortDayName(date: Date): string {
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  return days[date.getDay()];
}

/**
 * Get short month name (Jan, Feb, etc.)
 */
export function getShortMonthName(date: Date): string {
  const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];
  return months[date.getMonth()];
}

/**
 * Check if date is in the past
 */
export function isPast(date: Date): boolean {
  return date < new Date();
}

/**
 * Check if date is in the future
 */
export function isFuture(date: Date): boolean {
  return date > new Date();
}

/**
 * Get difference in days between two dates
 */
export function getDaysDifference(date1: Date, date2: Date): number {
  const msPerDay = 24 * 60 * 60 * 1000;
  return Math.floor((date2.getTime() - date1.getTime()) / msPerDay);
}

/**
 * Get difference in hours between two dates
 */
export function getHoursDifference(date1: Date, date2: Date): number {
  const msPerHour = 60 * 60 * 1000;
  return Math.floor((date2.getTime() - date1.getTime()) / msPerHour);
}

/**
 * Get difference in minutes between two dates
 */
export function getMinutesDifference(date1: Date, date2: Date): number {
  const msPerMinute = 60 * 1000;
  return Math.floor((date2.getTime() - date1.getTime()) / msPerMinute);
}

/**
 * Format distance to now (e.g., "2 hours ago", "in 3 days")
 */
export function formatDistanceToNow(
  date: Date,
  options?: { addSuffix?: boolean },
): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  let result = "";

  if (diffSecs < 60) {
    result =
      diffSecs === 0
        ? "just now"
        : `${diffSecs} second${diffSecs !== 1 ? "s" : ""}`;
  } else if (diffMins < 60) {
    result = `${diffMins} minute${diffMins !== 1 ? "s" : ""}`;
  } else if (diffHours < 24) {
    result = `${diffHours} hour${diffHours !== 1 ? "s" : ""}`;
  } else if (diffDays < 7) {
    result = `${diffDays} day${diffDays !== 1 ? "s" : ""}`;
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    result = `${weeks} week${weeks !== 1 ? "s" : ""}`;
  } else if (diffDays < 365) {
    const months = Math.floor(diffDays / 30);
    result = `${months} month${months !== 1 ? "s" : ""}`;
  } else {
    const years = Math.floor(diffDays / 365);
    result = `${years} year${years !== 1 ? "s" : ""}`;
  }

  if (options?.addSuffix) {
    result = diffMs >= 0 ? `${result} ago` : `in ${result}`;
  }

  return result;
}

/**
 * Format date as "MMM DD, YYYY" (e.g., "Jan 15, 2024")
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const month = getShortMonthName(d);
  const day = d.getDate();
  const year = d.getFullYear();
  return `${month} ${day}, ${year}`;
}

/**
 * Format time as "HH:MM AM/PM" (e.g., "02:30 PM")
 */
export function formatTime(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const hours = d.getHours();
  const minutes = d.getMinutes();
  const ampm = hours >= 12 ? "PM" : "AM";
  const displayHours = hours % 12 || 12;
  const displayMinutes = minutes.toString().padStart(2, "0");
  return `${displayHours}:${displayMinutes} ${ampm}`;
}
