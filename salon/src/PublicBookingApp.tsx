/**
 * Public Booking App - Separate entry point for public booking via subdomain
 * This app is served when accessing the salon via its unique subdomain
 * e.g., acme-salon.kenikool.com
 */

import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/react-query";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { ToastProvider } from "@/components/ui/toast";
import PublicBookingPage from "@/pages/public/PublicBookingApp";

export default function PublicBookingApp() {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <PublicBookingPage />
        </ToastProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
