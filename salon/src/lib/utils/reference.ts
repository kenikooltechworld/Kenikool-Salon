export function generateSalonReference(): string {
  return `salon_${crypto.randomUUID().replace(/-/g, "").slice(0, 24)}`;
}
