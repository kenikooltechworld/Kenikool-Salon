// Appointments
export {
  useAppointments,
  useAppointment,
  useCreateAppointment,
  useUpdateAppointment,
  useDeleteAppointment,
  type Appointment,
} from "./useAppointments";

// Customers
export {
  useCustomers,
  useCustomer,
  useCreateCustomer,
  useUpdateCustomer,
  useDeleteCustomer,
  type Customer,
} from "./useCustomers";

// Staff
export {
  useStaff,
  useStaffMember,
  useCreateStaff,
  useUpdateStaff,
  useDeleteStaff,
} from "./useStaff";
export type { Staff } from "@/types/staff";

// Services
export {
  useServices,
  useService,
  useCreateService,
  useUpdateService,
  useDeleteService,
} from "./useServices";
export type { Service, ServiceFilters } from "@/types/service";

// Invoices
export {
  useInvoices,
  useInvoice,
  useCreateInvoice,
  useUpdateInvoice,
  useDeleteInvoice,
  useIssueInvoice,
  useMarkInvoicePaid,
  type Invoice,
} from "./useInvoices";

// Payments
export {
  usePayments,
  usePayment,
  useCreatePayment,
  useUpdatePayment,
  useRefundPayment,
  type Payment,
} from "./usePayments";

// Tenant Settings
export {
  useTenantSettings,
  useUpdateTenantSettings,
  type TenantSettingsData,
  type BusinessHours,
} from "./owner/useTenantSettings";
