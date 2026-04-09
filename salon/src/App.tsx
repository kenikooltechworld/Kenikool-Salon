import React, { useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/react-query";
import { useAuthStore } from "@/stores/auth";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { ToastProvider } from "@/components/ui/toast";
import { useInitializeAuth } from "@/hooks/useInitializeAuth";
import { DashboardSkeleton } from "@/components/skeletons/DashboardSkeleton";
import { setNavigationCallback } from "@/lib/utils/api";

// Layouts
import { PublicLayout } from "@/layouts/PublicLayout";
import { AuthLayout } from "@/layouts/AuthLayout";
import { DashboardLayout } from "@/layouts/DashboardLayout";
import { StaffLayout } from "@/layouts/StaffLayout";

// Home Page
import Home from "@/pages/Home";
import Pricing from "@/pages/Pricing";

// Auth Pages
import Login from "@/pages/auth/Login";
import { Register } from "@/pages/auth/Register";
import { Verify } from "@/pages/auth/Verify";
import { RegisterSuccess } from "@/pages/auth/RegisterSuccess";
import ForgotPassword from "@/pages/auth/ForgotPassword";
import ResetPassword from "@/pages/auth/ResetPassword";
import MFASetup from "@/pages/auth/MFASetup";
import MFAVerify from "@/pages/auth/MFAVerify";
import ChangePassword from "@/pages/auth/ChangePassword";
import ChangePasswordRequired from "@/pages/auth/ChangePasswordRequired";
import AccountSettings from "@/pages/auth/AccountSettings";
import AccountRecovery from "@/pages/auth/AccountRecovery";

// Dashboard Pages
import Dashboard from "@/pages/dashboard/Dashboard";
import Appointments from "@/pages/appointments/Appointments";
import Bookings from "@/pages/bookings/Bookings";
import CreateBooking from "@/pages/bookings/CreateBooking";
import BookingConfirmationSuccess from "@/pages/bookings/BookingConfirmationSuccess";
import Customers from "@/pages/customers/Customers";
import CustomerDetail from "@/pages/customers/CustomerDetail";
import CustomerAppointments from "@/pages/customers/CustomerAppointments";
import AppointmentDetail from "@/pages/customers/AppointmentDetail";
import Services from "@/pages/services/Services";
import ServiceDetail from "@/pages/services/ServiceDetail";
import Staff from "@/pages/staff/Staff";
import StaffDetail from "@/pages/staff/StaffDetail";
import Invoices from "@/pages/invoices/Invoices";
import CreateInvoice from "@/pages/invoices/CreateInvoice";
import EditInvoice from "@/pages/invoices/EditInvoice";
import InvoiceDetail from "@/pages/invoices/InvoiceDetail";
import Settings from "@/pages/owner/Settings";
import GeneralSettings from "@/pages/owner/settings/GeneralSettings";
import SystemSettings from "@/pages/owner/settings/SystemSettings";
import { IntegrationSettings } from "@/pages/owner/settings/IntegrationSettings";
import FinancialSettings from "@/pages/owner/settings/FinancialSettings";
import { OperationalSettings } from "@/pages/owner/settings/OperationalSettings";
import { SecurityPolicies } from "@/pages/owner/settings/SecurityPolicies";
import { CommissionSettings } from "@/pages/owner/settings/CommissionSettings";
import CacheSettings from "@/pages/owner/settings/CacheSettings";
import { BillingDashboard } from "@/pages/owner/settings/BillingDashboard";
import EmailTemplates from "@/pages/owner/settings/EmailTemplates";
import StaffSettings from "@/pages/staff/Settings";

// Phase 5 Pages
import NotificationPreferences from "@/pages/notifications/NotificationPreferences";
import WaitingRoomManagement from "@/pages/waiting-room/WaitingRoomManagement";
import ResourceManagement from "@/pages/resources/ResourceManagement";

// Phase 6 Pages
import Inventory from "@/pages/inventory/Inventory";
import InventoryDetail from "@/pages/inventory/InventoryDetail";
import AuditLogs from "@/pages/audit/AuditLogs";
import Backups from "@/pages/backup/Backups";

// Phase 7 Pages (POS)
import POSDashboard from "@/pages/pos/POSDashboard";
import POSReports from "@/pages/pos/POSReports";
import CommissionDashboard from "@/pages/pos/CommissionDashboard";
import DiscountManagement from "@/pages/pos/DiscountManagement";
import ReceiptHistory from "@/pages/pos/ReceiptHistory";

// Role-Based Dashboards
import Manager from "@/pages/manager/Manager";
import MyAccount from "@/pages/customer/MyAccount";

// Staff Pages
import StaffDashboard from "@/pages/staff/Dashboard";
import StaffAppointments from "@/pages/staff/Appointments";
import StaffAppointmentDetail from "@/pages/staff/AppointmentDetail";
import StaffShifts from "@/pages/staff/Shifts";
import StaffShiftDetail from "@/pages/staff/ShiftDetail";
import StaffTimeOff from "@/pages/staff/TimeOff";
import StaffEarnings from "@/pages/staff/Earnings";
import StaffPerformance from "@/pages/staff/Performance";
import StaffAttendance from "@/pages/staff/Attendance";
import StaffDocuments from "@/pages/staff/Documents";
import StaffGoals from "@/pages/staff/Goals";
import StaffMessages from "@/pages/staff/Messages";

// Public Booking Pages
import PublicBookingPage from "@/pages/public/PublicBookingApp";
import CustomerRegister from "@/pages/public/CustomerRegister";
import CustomerLogin from "@/pages/public/CustomerLogin";
import CustomerPasswordSetup from "@/pages/public/CustomerPasswordSetup";
import CustomerPortal from "@/pages/public/CustomerPortal";
import Waitlist from "@/pages/public/Waitlist";
import ServicePackages from "@/pages/public/ServicePackages";
import GiftCards from "@/pages/public/GiftCards";
import GiftCardPurchase from "@/pages/public/GiftCardPurchase";
import Memberships from "@/pages/public/Memberships";
import GroupBooking from "@/pages/public/GroupBooking";
import GroupBookingConfirmation from "@/pages/public/GroupBookingConfirmation";

// Owner Pages
import OwnerServicePackages from "@/pages/owner/ServicePackages";
import OwnerGiftCards from "@/pages/owner/GiftCards";
import OwnerMemberships from "@/pages/owner/Memberships";
import OwnerGroupBookings from "@/pages/owner/GroupBookings";
import OwnerSocialProof from "@/pages/owner/SocialProof";

// Payment Pages
import { BookingPayment } from "@/pages/payments/BookingPayment";

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return <Navigate to="/auth/login" replace />;
  }

  return <>{children}</>;
}

// Role-Based Route Component - restricts access based on user roles
function RoleBasedRoute({
  children,
  allowedRoles,
}: {
  children: React.ReactNode;
  allowedRoles: string[];
}) {
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return <Navigate to="/auth/login" replace />;
  }

  // Get user's role names, default to empty array if not available
  const userRoleNames = user.roleNames || [];

  // Check if user has any of the allowed roles
  const hasAccess = userRoleNames.some((role) => allowedRoles.includes(role));

  if (!hasAccess) {
    // Redirect to appropriate dashboard based on user's role
    if (userRoleNames.includes("Owner")) {
      return <Navigate to="/dashboard" replace />;
    } else if (userRoleNames.includes("Manager")) {
      return <Navigate to="/manager" replace />;
    } else if (userRoleNames.includes("Staff")) {
      return <Navigate to="/appointments" replace />;
    } else if (userRoleNames.includes("Customer")) {
      return <Navigate to="/my-account" replace />;
    }
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

// Public Route Component (redirect to dashboard if already logged in)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((state) => state.user);

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

// Check if accessing via public subdomain
function isPublicSubdomain(): boolean {
  const hostname = window.location.hostname;
  // Check if hostname is a subdomain (not localhost, not main domain)
  // Public subdomains are like: acme-salon.kenikool.com
  // Main domain is: kenikool.com or www.kenikool.com
  const parts = hostname.split(".");

  // If it's localhost or has less than 2 parts, it's not a public subdomain
  if (
    hostname === "localhost" ||
    hostname.startsWith("localhost:") ||
    parts.length < 2
  ) {
    return false;
  }

  // If it's the main domain or www subdomain, it's not a public subdomain
  if (hostname === "kenikool.com" || hostname === "www.kenikool.com") {
    return false;
  }

  // Otherwise, it's a public subdomain
  return true;
}

// Navigation setup component (inside Router)
function NavigationSetup() {
  const { isLoading } = useInitializeAuth();
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();

  // Setup navigation callback after auth initialization
  useEffect(() => {
    if (!isLoading) {
      setNavigationCallback((path: string) => {
        // Only redirect if user is not authenticated
        if (!user) {
          navigate(path);
        }
      });
    }
  }, [isLoading, user, navigate]);

  return null;
}

// Main app content component
function AppContent() {
  const { isLoading } = useInitializeAuth();

  // Don't show loading state - let routes handle their own loading
  // Auth initialization happens in background
  return (
    <Router>
      <NavigationSetup />
      <Routes>
        {/* Public Routes with PublicLayout */}
        <Route element={<PublicLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/pricing" element={<Pricing />} />
        </Route>

        {/* Auth Routes with AuthLayout */}
        <Route element={<AuthLayout />}>
          <Route
            path="/auth/login"
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            }
          />
          <Route
            path="/auth/register"
            element={
              <PublicRoute>
                <Register />
              </PublicRoute>
            }
          />
          <Route path="/auth/verify" element={<Verify />} />
          <Route
            path="/auth/register-success"
            element={
              <PublicRoute>
                <RegisterSuccess />
              </PublicRoute>
            }
          />
          <Route
            path="/auth/forgot-password"
            element={
              <PublicRoute>
                <ForgotPassword />
              </PublicRoute>
            }
          />
          <Route
            path="/auth/reset-password"
            element={
              <PublicRoute>
                <ResetPassword />
              </PublicRoute>
            }
          />
          <Route
            path="/auth/mfa-setup"
            element={
              <ProtectedRoute>
                <MFASetup />
              </ProtectedRoute>
            }
          />
          <Route
            path="/auth/mfa-verify"
            element={
              <PublicRoute>
                <MFAVerify />
              </PublicRoute>
            }
          />
          <Route
            path="/auth/change-password"
            element={
              <ProtectedRoute>
                <ChangePassword />
              </ProtectedRoute>
            }
          />
          <Route
            path="/auth/change-password-required"
            element={
              <PublicRoute>
                <ChangePasswordRequired />
              </PublicRoute>
            }
          />
          <Route
            path="/auth/account-settings"
            element={
              <ProtectedRoute>
                <AccountSettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/auth/account-recovery"
            element={
              <PublicRoute>
                <AccountRecovery />
              </PublicRoute>
            }
          />
        </Route>

        {/* Dashboard Routes with DashboardLayout */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route
            path="/dashboard"
            element={
              <RoleBasedRoute allowedRoles={["Owner"]}>
                <Dashboard />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/manager"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <Manager />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/my-account"
            element={
              <RoleBasedRoute
                allowedRoles={["Owner", "Manager", "Staff", "Customer"]}
              >
                <MyAccount />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/appointments"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager", "Staff"]}>
                <Appointments />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/bookings"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <Bookings />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/bookings/create"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <CreateBooking />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/bookings/confirmation"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <BookingConfirmationSuccess />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/payments/booking-payment"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <BookingPayment />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/customers"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <Customers />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/customers/:id"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <CustomerDetail />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/customers/:id/appointments"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <CustomerAppointments />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/customers/:id/appointments/:appointmentId"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <AppointmentDetail />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/services"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <Services />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/services/:id"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <ServiceDetail />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/staff"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <Staff />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/staff/:staffId"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <StaffDetail />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/invoices"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <Invoices />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/invoices/create"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <CreateInvoice />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/invoices/:id"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <InvoiceDetail />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/invoices/:id/edit"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <EditInvoice />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <Settings />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/settings/general"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <GeneralSettings />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/settings/system"
            element={
              <RoleBasedRoute allowedRoles={["Owner"]}>
                <SystemSettings />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/settings/integrations"
            element={
              <RoleBasedRoute allowedRoles={["Owner"]}>
                <IntegrationSettings />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/settings/financial"
            element={
              <RoleBasedRoute allowedRoles={["Owner"]}>
                <FinancialSettings />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/settings/operational"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <OperationalSettings />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/settings/security"
            element={
              <RoleBasedRoute allowedRoles={["Owner"]}>
                <SecurityPolicies />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/settings/commission"
            element={
              <RoleBasedRoute allowedRoles={["Owner"]}>
                <CommissionSettings />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/settings/cache"
            element={
              <RoleBasedRoute allowedRoles={["Owner"]}>
                <CacheSettings />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/settings/billing"
            element={
              <RoleBasedRoute allowedRoles={["Owner"]}>
                <BillingDashboard />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/settings/email-templates"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <EmailTemplates />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/settings/staff"
            element={
              <RoleBasedRoute allowedRoles={["Staff"]}>
                <StaffSettings />
              </RoleBasedRoute>
            }
          />

          {/* Phase 5 Routes */}
          <Route
            path="/notifications/preferences"
            element={
              <RoleBasedRoute
                allowedRoles={["Owner", "Manager", "Staff", "Customer"]}
              >
                <NotificationPreferences />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/waiting-room"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <WaitingRoomManagement />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/resources"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <ResourceManagement />
              </RoleBasedRoute>
            }
          />

          {/* Phase 6 Routes */}
          <Route
            path="/inventory"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <Inventory />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/inventory/:id"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <InventoryDetail />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/audit"
            element={
              <RoleBasedRoute allowedRoles={["Owner"]}>
                <AuditLogs />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/backup"
            element={
              <RoleBasedRoute allowedRoles={["Owner"]}>
                <Backups />
              </RoleBasedRoute>
            }
          />

          {/* Phase 7 Routes (POS) */}
          <Route
            path="/pos"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <POSDashboard />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/pos/reports"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <POSReports />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/pos/commissions"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <CommissionDashboard />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/pos/discounts"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <DiscountManagement />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/pos/receipts"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <ReceiptHistory />
              </RoleBasedRoute>
            }
          />

          {/* Service Packages Routes */}
          <Route
            path="/owner/service-packages"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <OwnerServicePackages />
              </RoleBasedRoute>
            }
          />

          {/* Gift Cards Routes */}
          <Route
            path="/owner/gift-cards"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <OwnerGiftCards />
              </RoleBasedRoute>
            }
          />

          {/* Memberships Routes */}
          <Route
            path="/owner/memberships"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <OwnerMemberships />
              </RoleBasedRoute>
            }
          />

          {/* Group Bookings Routes */}
          <Route
            path="/owner/group-bookings"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <OwnerGroupBookings />
              </RoleBasedRoute>
            }
          />

          {/* Social Proof Routes */}
          <Route
            path="/owner/social-proof"
            element={
              <RoleBasedRoute allowedRoles={["Owner", "Manager"]}>
                <OwnerSocialProof />
              </RoleBasedRoute>
            }
          />
        </Route>

        {/* Staff Routes with StaffLayout */}
        <Route
          element={
            <ProtectedRoute>
              <RoleBasedRoute allowedRoles={["Staff"]}>
                <StaffLayout />
              </RoleBasedRoute>
            </ProtectedRoute>
          }
        >
          <Route path="/staff/dashboard" element={<StaffDashboard />} />
          <Route path="/staff/appointments" element={<StaffAppointments />} />
          <Route
            path="/staff/appointments/:id"
            element={<StaffAppointmentDetail />}
          />
          <Route path="/staff/shifts" element={<StaffShifts />} />
          <Route path="/staff/shifts/:id" element={<StaffShiftDetail />} />
          <Route path="/staff/time-off" element={<StaffTimeOff />} />
          <Route path="/staff/earnings" element={<StaffEarnings />} />
          <Route path="/staff/performance" element={<StaffPerformance />} />
          <Route path="/staff/attendance" element={<StaffAttendance />} />
          <Route path="/staff/documents" element={<StaffDocuments />} />
          <Route path="/staff/goals" element={<StaffGoals />} />
          <Route path="/staff/messages" element={<StaffMessages />} />
          <Route
            path="/staff/settings"
            element={
              <RoleBasedRoute allowedRoles={["Staff"]}>
                <StaffSettings />
              </RoleBasedRoute>
            }
          />
          <Route
            path="/staff"
            element={<Navigate to="/staff/dashboard" replace />}
          />
        </Route>

        {/* Default Routes */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

// Public Subdomain App Component
function PublicSubdomainApp() {
  return (
    <Router>
      <Routes>
        <Route path="/public/register" element={<CustomerRegister />} />
        <Route path="/public/login" element={<CustomerLogin />} />
        <Route
          path="/public/setup-password"
          element={<CustomerPasswordSetup />}
        />
        <Route path="/public/portal" element={<CustomerPortal />} />
        <Route path="/public/portal/*" element={<CustomerPortal />} />
        <Route path="/public/waitlist" element={<Waitlist />} />
        <Route path="/public/packages" element={<ServicePackages />} />
        <Route path="/public/gift-cards" element={<GiftCards />} />
        <Route
          path="/public/gift-cards/purchase"
          element={<GiftCardPurchase />}
        />
        <Route path="/public/memberships" element={<Memberships />} />
        <Route path="/public/group-booking" element={<GroupBooking />} />
        <Route
          path="/public/group-booking-confirmation/:id"
          element={<GroupBookingConfirmation />}
        />
        <Route path="*" element={<PublicBookingPage />} />
      </Routes>
    </Router>
  );
}

export default function App() {
  // If accessing via public subdomain, render public booking app with customer auth routes
  if (isPublicSubdomain()) {
    return (
      <ThemeProvider>
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <PublicSubdomainApp />
          </ToastProvider>
        </QueryClientProvider>
      </ThemeProvider>
    );
  }

  // Otherwise, render the main app with auth initialization
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <AppContent />
        </ToastProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
