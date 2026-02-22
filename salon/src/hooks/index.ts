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
  type Staff,
} from "./useStaff";

// Services
export {
  useServices,
  useService,
  useCreateService,
  useUpdateService,
  useDeleteService,
  type Service,
} from "./useServices";

// Invoices
export {
  useInvoices,
  useInvoice,
  useCreateInvoice,
  useUpdateInvoice,
  useDeleteInvoice,
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
} from "./useTenantSettings";
