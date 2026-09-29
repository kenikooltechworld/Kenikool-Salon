/**
 * Format utilities for currency, phone, dates, and durations
 */

/**
 * Format number as currency
 * @param amount - Amount to format
 * @param currency - Currency code (NGN, USD, etc.)
 * @param locale - Locale for formatting (default: en-NG)
 */
export function formatCurrency(
  amount: number,
  currency: string = "NGN",
  locale: string = "en-NG",
): string {
  const safeAmount = Number.isFinite(Number(amount)) ? Number(amount) : 0;
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(safeAmount);
}

/**
 * Format phone number
 * @param phone - Phone number to format
 */
export function formatPhone(phone: string): string {
  const cleaned = phone.replace(/\D/g, "");

  if (cleaned.length === 10) {
    return `+234 ${cleaned.slice(0, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6)}`;
  }

  if (cleaned.length === 11 && cleaned.startsWith("0")) {
    const withoutZero = cleaned.slice(1);
    return `+234 ${withoutZero.slice(0, 3)} ${withoutZero.slice(3, 6)} ${withoutZero.slice(6)}`;
  }

  if (cleaned.length === 12 && cleaned.startsWith("234")) {
    const withoutCountry = cleaned.slice(3);
    return `+234 ${withoutCountry.slice(0, 3)} ${withoutCountry.slice(3, 6)} ${withoutCountry.slice(6)}`;
  }

  return phone;
}

/**
 * Format date to readable string
 * @param date - Date to format
 * @param format - Format string (default: 'MMM DD, YYYY')
 * @param timezone - IANA timezone (default: 'Africa/Lagos' for GMT+1)
 */
export function formatDate(
  date: Date | string,
  format: string = "MMM DD, YYYY",
  timezone: string = "Africa/Lagos",
): string {
  const d = typeof date === "string" ? new Date(date) : date;

  if (isNaN(d.getTime())) {
    return "";
  }

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
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  try {
    const parts = new Intl.DateTimeFormat("en-US", {
      timeZone: timezone,
      day: "2-digit",
      month: "short",
      year: "numeric",
      weekday: "short",
    }).formatToParts(d);

    const getPart = (type: string) => parts.find((p) => p.type === type)?.value || "";

    const dayName = getPart("weekday");
    const month = getPart("month");
    const day = getPart("day");
    const year = getPart("year");

    const monthIndex = months.findIndex((m) => m === month);
    const dayIndex = days.findIndex((dy) => dy === dayName);

    const replacements: Record<string, string | number> = {
      YYYY: year,
      YY: String(year).slice(-2),
      MMMM: months[monthIndex] || month,
      MMM: months[monthIndex] || month,
      MM: String(monthIndex + 1).padStart(2, "0"),
      M: monthIndex + 1,
      DDDD: days[dayIndex] || dayName,
      DDD: days[dayIndex]?.slice(0, 3) || dayName.slice(0, 3),
      DD: day,
      D: String(parseInt(day, 10)),
    };

    let result = format;
    Object.entries(replacements).forEach(([key, value]) => {
      result = result.replace(new RegExp(key, "g"), String(value));
    });

    return result;
  } catch {
    return d.toLocaleDateString("en-US", {
      timeZone: timezone,
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }
}

/**
 * Format time to readable string
 * @param date - Date to format
 * @param format24 - Use 24-hour format (default: false)
 * @param timezone - IANA timezone (default: 'Africa/Lagos' for GMT+1)
 */
export function formatTime(
  date: Date | string,
  format24: boolean = false,
  timezone: string = "Africa/Lagos",
): string {
  const d = typeof date === "string" ? new Date(date) : date;

  if (isNaN(d.getTime())) {
    return "";
  }

  try {
    const parts = new Intl.DateTimeFormat("en-US", {
      timeZone: timezone,
      hour: "numeric",
      minute: "2-digit",
      second: "2-digit",
      hour12: !format24,
    }).formatToParts(d);

    const getPart = (type: string) => parts.find((p) => p.type === type)?.value || "";

    const hour = getPart("hour");
    const minute = getPart("minute");
    const dayPeriod = getPart("dayPeriod");

    if (format24) {
      return `${hour.padStart(2, "0")}:${minute}`;
    }

    return `${hour}:${minute} ${dayPeriod}`;
  } catch {
    return d.toLocaleTimeString("en-US", {
      timeZone: timezone,
      hour: "2-digit",
      minute: "2-digit",
    });
  }
}

/**
 * Format date and time together
 * @param date - Date to format
 * @param dateFormat - Date format string
 * @param timeFormat24 - Use 24-hour format
 * @param timezone - IANA timezone (default: 'Africa/Lagos' for GMT+1)
 */
export function formatDateTime(
  date: Date | string,
  dateFormat: string = "MMM DD, YYYY",
  timeFormat24: boolean = false,
  timezone: string = "Africa/Lagos",
): string {
  return `${formatDate(date, dateFormat, timezone)} ${formatTime(date, timeFormat24, timezone)}`;
}

/**
 * Format duration in minutes to readable string
 * @param minutes - Duration in minutes
 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}m`;
  }

  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (mins === 0) {
    return `${hours}h`;
  }

  return `${hours}h ${mins}m`;
}
