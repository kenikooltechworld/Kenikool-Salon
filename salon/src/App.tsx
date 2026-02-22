import React from "react";
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
import { Spinner } from "@/components/ui/spinner";
import { setNavigationCallback } from "@/lib/utils/api";

// Layouts
import { PublicLayout } from "@/layouts/PublicLayout";
import { AuthLayout } from "@/layouts/AuthLayout";
import { DashboardLayout } from "@/layouts/DashboardLayout";

// Home Page
import Home from "@/pages/Home";

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
import AccountSettings from "@/pages/auth/AccountSettings";

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
import Settings from "@/pages/settings/Settings";
import SystemSettings from "@/pages/settings/SystemSettings";
import { IntegrationSettings } from "@/pages/settings/IntegrationSettings";
import FinancialSettings from "@/pages/settings/FinancialSettings";
import { OperationalSettings } from "@/pages/settings/OperationalSettings";
import { SecurityPolicies } from "@/pages/settings/SecurityPolicies";
import { CommissionSettings } from "@/pages/settings/CommissionSettings";
import CacheSettings from "@/pages/settings/CacheSettings";
import { BillingDashboard } from "@/pages/settings/BillingDashboard";

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

// Public Booking Page
import PublicBookingPage from "@/pages/public/PublicBookingApp";

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
  React.useEffect(() => {
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

  // Show loading spinner while initializing auth
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <Spinner />
      </div>
    );
  }

  return (
    <Router>
      <NavigationSetup />
      <Routes>
        {/* Public Routes with PublicLayout */}
        <Route element={<PublicLayout />}>
          <Route path="/" element={<Home />} />
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
            path="/auth/account-settings"
            element={
              <ProtectedRoute>
                <AccountSettings />
              </ProtectedRoute>
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
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/manager" element={<Manager />} />
          <Route path="/my-account" element={<MyAccount />} />
          <Route path="/appointments" element={<Appointments />} />
          <Route path="/bookings" element={<Bookings />} />
          <Route path="/bookings/create" element={<CreateBooking />} />
          <Route
            path="/bookings/confirmation"
            element={<BookingConfirmationSuccess />}
          />
          <Route
            path="/payments/booking-payment"
            element={<BookingPayment />}
          />
          <Route path="/customers" element={<Customers />} />
          <Route path="/customers/:id" element={<CustomerDetail />} />
          <Route
            path="/customers/:id/appointments"
            element={<CustomerAppointments />}
          />
          <Route
            path="/customers/:id/appointments/:appointmentId"
            element={<AppointmentDetail />}
          />
          <Route path="/services" element={<Services />} />
          <Route path="/services/:id" element={<ServiceDetail />} />
          <Route path="/staff" element={<Staff />} />
          <Route path="/staff/:staffId" element={<StaffDetail />} />
          <Route path="/invoices" element={<Invoices />} />
          <Route path="/invoices/create" element={<CreateInvoice />} />
          <Route path="/invoices/:id" element={<InvoiceDetail />} />
          <Route path="/invoices/:id/edit" element={<EditInvoice />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/settings/system" element={<SystemSettings />} />
          <Route
            path="/settings/integrations"
            element={<IntegrationSettings />}
          />
          <Route path="/settings/financial" element={<FinancialSettings />} />
          <Route
            path="/settings/operational"
            element={<OperationalSettings />}
          />
          <Route path="/settings/security" element={<SecurityPolicies />} />
          <Route path="/settings/commission" element={<CommissionSettings />} />
          <Route path="/settings/cache" element={<CacheSettings />} />
          <Route path="/settings/billing" element={<BillingDashboard />} />

          {/* Phase 5 Routes */}
          <Route
            path="/notifications/preferences"
            element={<NotificationPreferences />}
          />
          <Route path="/waiting-room" element={<WaitingRoomManagement />} />
          <Route path="/resources" element={<ResourceManagement />} />

          {/* Phase 6 Routes */}
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/inventory/:id" element={<InventoryDetail />} />
          <Route path="/audit" element={<AuditLogs />} />
          <Route path="/backup" element={<Backups />} />

          {/* Phase 7 Routes (POS) */}
          <Route path="/pos" element={<POSDashboard />} />
          <Route path="/pos/reports" element={<POSReports />} />
          <Route path="/pos/commissions" element={<CommissionDashboard />} />
          <Route path="/pos/discounts" element={<DiscountManagement />} />
          <Route path="/pos/receipts" element={<ReceiptHistory />} />
        </Route>

        {/* Default Routes */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default function App() {
  // If accessing via public subdomain, render public booking app
  if (isPublicSubdomain()) {
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
