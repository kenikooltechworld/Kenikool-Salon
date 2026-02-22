import { Routes, Route, Navigate } from "react-router-dom";
import { lazy, Suspense } from "react";

// Layouts
import DashboardLayout from "@/pages/dashboard/layout";
import AuthLayout from "@/pages/auth/layout";

// Landing & Public Pages
import LandingPage from "@/pages/LandingPage";
import OfflinePage from "@/pages/offline/page";
import PrivacyPage from "@/pages/privacy/page";
import TermsPage from "@/pages/terms/page";
import RegisterSalonPage from "@/pages/register-salon/page";
import OnboardingPage from "@/pages/onboarding/page";
import AboutPage from "@/pages/about/page";
import ContactPage from "@/pages/contact/page";
import HelpPage from "@/pages/help/page";
import BlogPage from "@/pages/blog/page";
import PricingPublicPage from "@/pages/pricing/page";

// Auth Pages
import LoginPage from "@/pages/auth/login/page";
import RegisterPage from "@/pages/auth/register/page";
import ForgotPasswordPage from "@/pages/auth/forgot-password/page";
import VerifyPage from "@/pages/auth/verify/page";
import VerifyEmailPage from "@/pages/auth/verify-email/page";
import ResendVerificationPage from "@/pages/auth/resend-verification/page";

// Dashboard Pages - Lazy loaded
const DashboardPage = lazy(() => import("@/pages/dashboard/page"));
const BookingsPage = lazy(() => import("@/pages/dashboard/bookings/page"));
const NewBookingPage = lazy(
  () => import("@/pages/dashboard/bookings/new/page"),
);
const ClientsPage = lazy(() => import("@/pages/dashboard/clients/page"));
const ClientDetailsPage = lazy(
  () => import("@/pages/dashboard/clients/[id]/page"),
);
const ServicesPage = lazy(() => import("@/pages/dashboard/services/page"));
const ServiceDetailsPage = lazy(
  () => import("@/pages/dashboard/services/[id]/page"),
);
const StaffPage = lazy(() => import("@/pages/dashboard/staff/page"));
const StaffDetailsPage = lazy(
  () => import("@/pages/dashboard/staff/[id]/page"),
);
const StaffOnboardingPage = lazy(
  () => import("@/pages/dashboard/staff/onboarding/page"),
);
const InventoryPage = lazy(() => import("@/pages/dashboard/inventory/page"));
const PaymentsPage = lazy(() => import("@/pages/dashboard/payments/page"));
const PaymentVerifyPage = lazy(
  () => import("@/pages/dashboard/payments/verify/page"),
);
const ExpensesPage = lazy(() => import("@/pages/dashboard/expenses/page"));
const AnalyticsPage = lazy(() => import("@/pages/dashboard/analytics/page"));
const AnalyticsRevenuePage = lazy(
  () => import("@/pages/dashboard/analytics/revenue/page"),
);
const AnalyticsServicesPage = lazy(
  () => import("@/pages/dashboard/analytics/services/page"),
);
const AnalyticsStaffPage = lazy(
  () => import("@/pages/dashboard/analytics/staff/page"),
);
const AnalyticsClientsPage = lazy(
  () => import("@/pages/dashboard/analytics/clients/page"),
);
const AnalyticsPerformancePage = lazy(
  () => import("@/pages/dashboard/analytics/performance/page"),
);
const POSPage = lazy(() => import("@/pages/dashboard/pos/page"));
const POSTransactionsPage = lazy(
  () => import("@/pages/dashboard/pos/transactions/page"),
);
const POSReportsPage = lazy(() => import("@/pages/dashboard/pos/reports/page"));
const POSAnalyticsPage = lazy(
  () => import("@/pages/dashboard/pos/analytics/page"),
);
const POSCustomerDisplayPage = lazy(
  () => import("@/pages/dashboard/pos/customer-display/page"),
);
const WaitlistPage = lazy(() => import("@/pages/dashboard/waitlist/page"));
const ReviewsPage = lazy(() => import("@/pages/dashboard/reviews/page"));
const PackagesPage = lazy(() => import("@/pages/dashboard/packages/page"));
const PromoCodesPage = lazy(() => import("@/pages/dashboard/promo-codes/page"));
const GiftCardsPage = lazy(() => import("@/pages/dashboard/gift-cards/page"));
const MembershipsPage = lazy(
  () => import("@/pages/dashboard/memberships/page"),
);
const GroupBookingsPage = lazy(
  () => import("@/pages/dashboard/group-bookings/page"),
);
const GroupBookingDetailsPage = lazy(
  () => import("@/pages/dashboard/group-bookings/[id]/page"),
);
const CampaignsPage = lazy(() => import("@/pages/dashboard/campaigns/page"));
const ReferralsPage = lazy(() => import("@/pages/dashboard/referrals/page"));
const LocationsPage = lazy(() => import("@/pages/dashboard/locations/page"));
const DomainsPage = lazy(() => import("@/pages/dashboard/domains/page"));
const WhiteLabelPage = lazy(() => import("@/pages/dashboard/white-label/page"));
const IntegrationsPage = lazy(
  () => import("@/pages/dashboard/integrations/page"),
);
const QRCodePage = lazy(() => import("@/pages/dashboard/qr-code/page"));
const ReceiptsPage = lazy(() => import("@/pages/dashboard/receipts/page"));
const PricingPage = lazy(() => import("@/pages/dashboard/pricing/page"));
const AccountingPage = lazy(() => import("@/pages/dashboard/accounting/page"));
const TaxConfigurationPage = lazy(
  () => import("@/pages/dashboard/accounting/tax-configuration/page"),
);
const AIInsightsPage = lazy(() => import("@/pages/dashboard/ai-insights/page"));
const VoiceAssistantPage = lazy(
  () => import("@/pages/dashboard/voice-assistant/page"),
);
const NotificationsPage = lazy(
  () => import("@/pages/dashboard/notifications/page"),
);
const CheckoutPage = lazy(
  () => import("@/pages/dashboard/checkout/[bookingId]/page"),
);

// Settings Pages - Lazy loaded
const SettingsPage = lazy(() => import("@/pages/dashboard/settings/page"));
const ProfileSettingsPage = lazy(
  () => import("@/pages/dashboard/settings/profile/page"),
);
const SalonSettingsPage = lazy(
  () => import("@/pages/dashboard/settings/salon/page"),
);
const SecuritySettingsPage = lazy(
  () => import("@/pages/dashboard/settings/security/page"),
);
const NotificationSettingsPage = lazy(
  () => import("@/pages/dashboard/settings/notifications/page"),
);
const AppearanceSettingsPage = lazy(
  () => import("@/pages/dashboard/settings/appearance/page"),
);
const BillingSettingsPage = lazy(
  () => import("@/pages/dashboard/settings/billing/page"),
);
const BillingSuccessPage = lazy(
  () => import("@/pages/dashboard/settings/billing/success/page"),
);

// Booking Page - Lazy loaded
const BookingPage = lazy(() => import("@/pages/book/[subdomain]/page"));

// Marketplace Pages - Lazy loaded
const MarketplacePage = lazy(() => import("@/pages/marketplace/page"));
const SalonDetailPage = lazy(
  () => import("@/pages/marketplace/salon-detail/[id]/page"),
);
const GuestBookingPage = lazy(
  () => import("@/pages/marketplace/guest-booking/page"),
);
const CommissionsPage = lazy(() => import("@/app/dashboard/commissions/page"));

// Loading fallback component
function LoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>
  );
}

function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/offline" element={<OfflinePage />} />
      <Route path="/pricing" element={<PricingPublicPage />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/terms" element={<TermsPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/contact" element={<ContactPage />} />
      <Route path="/help" element={<HelpPage />} />
      <Route path="/blog" element={<BlogPage />} />
      <Route path="/register-salon" element={<RegisterSalonPage />} />
      <Route path="/onboarding" element={<OnboardingPage />} />
      <Route
        path="/book/:subdomain"
        element={
          <Suspense fallback={<LoadingFallback />}>
            <BookingPage />
          </Suspense>
        }
      />

      {/* Marketplace Routes */}
      <Route
        path="/marketplace"
        element={
          <Suspense fallback={<LoadingFallback />}>
            <MarketplacePage />
          </Suspense>
        }
      />
      <Route
        path="/marketplace/salon/:id"
        element={
          <Suspense fallback={<LoadingFallback />}>
            <SalonDetailPage />
          </Suspense>
        }
      />
      <Route
        path="/marketplace/guest-booking"
        element={
          <Suspense fallback={<LoadingFallback />}>
            <GuestBookingPage />
          </Suspense>
        }
      />

      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/verify" element={<VerifyPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route
          path="/resend-verification"
          element={<ResendVerificationPage />}
        />
      </Route>

      {/* Dashboard Routes */}
      <Route path="/dashboard" element={<DashboardLayout />}>
        <Route
          index
          element={
            <Suspense fallback={<LoadingFallback />}>
              <DashboardPage />
            </Suspense>
          }
        />
        <Route
          path="bookings"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <BookingsPage />
            </Suspense>
          }
        />
        <Route
          path="bookings/new"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <NewBookingPage />
            </Suspense>
          }
        />
        <Route
          path="clients"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <ClientsPage />
            </Suspense>
          }
        />
        <Route
          path="clients/:id"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <ClientDetailsPage />
            </Suspense>
          }
        />
        <Route
          path="services"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <ServicesPage />
            </Suspense>
          }
        />
        <Route
          path="services/:id"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <ServiceDetailsPage />
            </Suspense>
          }
        />
        <Route
          path="staff"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <StaffPage />
            </Suspense>
          }
        />
        <Route
          path="staff/:id"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <StaffDetailsPage />
            </Suspense>
          }
        />
        <Route
          path="staff/onboarding"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <StaffOnboardingPage />
            </Suspense>
          }
        />
        <Route
          path="inventory"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <InventoryPage />
            </Suspense>
          }
        />
        <Route
          path="payments"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <PaymentsPage />
            </Suspense>
          }
        />
        <Route
          path="payments/verify"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <PaymentVerifyPage />
            </Suspense>
          }
        />
        <Route
          path="expenses"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <ExpensesPage />
            </Suspense>
          }
        />

        {/* Analytics */}
        <Route
          path="analytics"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <AnalyticsPage />
            </Suspense>
          }
        />
        <Route
          path="analytics/revenue"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <AnalyticsRevenuePage />
            </Suspense>
          }
        />
        <Route
          path="analytics/services"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <AnalyticsServicesPage />
            </Suspense>
          }
        />
        <Route
          path="analytics/staff"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <AnalyticsStaffPage />
            </Suspense>
          }
        />
        <Route
          path="analytics/clients"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <AnalyticsClientsPage />
            </Suspense>
          }
        />
        <Route
          path="analytics/performance"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <AnalyticsPerformancePage />
            </Suspense>
          }
        />

        {/* POS */}
        <Route
          path="pos"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <POSPage />
            </Suspense>
          }
        />
        <Route
          path="pos/transactions"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <POSTransactionsPage />
            </Suspense>
          }
        />
        <Route
          path="pos/reports"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <POSReportsPage />
            </Suspense>
          }
        />
        <Route
          path="pos/analytics"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <POSAnalyticsPage />
            </Suspense>
          }
        />
        <Route
          path="pos/customer-display"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <POSCustomerDisplayPage />
            </Suspense>
          }
        />

        {/* Other Features */}
        <Route
          path="waitlist"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <WaitlistPage />
            </Suspense>
          }
        />
        <Route
          path="reviews"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <ReviewsPage />
            </Suspense>
          }
        />
        <Route
          path="packages"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <PackagesPage />
            </Suspense>
          }
        />
        <Route
          path="promo-codes"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <PromoCodesPage />
            </Suspense>
          }
        />
        <Route
          path="gift-cards"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <GiftCardsPage />
            </Suspense>
          }
        />
        <Route
          path="memberships"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <MembershipsPage />
            </Suspense>
          }
        />
        <Route
          path="group-bookings"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <GroupBookingsPage />
            </Suspense>
          }
        />
        <Route
          path="group-bookings/:id"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <GroupBookingDetailsPage />
            </Suspense>
          }
        />
        <Route
          path="campaigns"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <CampaignsPage />
            </Suspense>
          }
        />
        <Route
          path="referrals"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <ReferralsPage />
            </Suspense>
          }
        />
        <Route
          path="locations"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <LocationsPage />
            </Suspense>
          }
        />
        <Route
          path="domains"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <DomainsPage />
            </Suspense>
          }
        />
        <Route
          path="white-label"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <WhiteLabelPage />
            </Suspense>
          }
        />
        <Route
          path="integrations"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <IntegrationsPage />
            </Suspense>
          }
        />
        <Route
          path="qr-code"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <QRCodePage />
            </Suspense>
          }
        />
        <Route
          path="receipts"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <ReceiptsPage />
            </Suspense>
          }
        />
        <Route
          path="pricing"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <PricingPage />
            </Suspense>
          }
        />
        <Route
          path="accounting"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <AccountingPage />
            </Suspense>
          }
        />
        <Route
          path="accounting/tax-configuration"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <TaxConfigurationPage />
            </Suspense>
          }
        />
        <Route
          path="commissions"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <CommissionsPage />
            </Suspense>
          }
        />
        <Route
          path="ai-insights"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <AIInsightsPage />
            </Suspense>
          }
        />
        <Route
          path="voice-assistant"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <VoiceAssistantPage />
            </Suspense>
          }
        />
        <Route
          path="notifications"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <NotificationsPage />
            </Suspense>
          }
        />
        <Route
          path="checkout/:bookingId"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <CheckoutPage />
            </Suspense>
          }
        />

        {/* Settings */}
        <Route
          path="settings"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <SettingsPage />
            </Suspense>
          }
        />
        <Route
          path="settings/profile"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <ProfileSettingsPage />
            </Suspense>
          }
        />
        <Route
          path="settings/salon"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <SalonSettingsPage />
            </Suspense>
          }
        />
        <Route
          path="settings/security"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <SecuritySettingsPage />
            </Suspense>
          }
        />
        <Route
          path="settings/notifications"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <NotificationSettingsPage />
            </Suspense>
          }
        />
        <Route
          path="settings/appearance"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <AppearanceSettingsPage />
            </Suspense>
          }
        />
        <Route
          path="settings/billing"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <BillingSettingsPage />
            </Suspense>
          }
        />
        <Route
          path="settings/billing/success"
          element={
            <Suspense fallback={<LoadingFallback />}>
              <BillingSuccessPage />
            </Suspense>
          }
        />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
