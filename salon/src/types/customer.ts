export interface Customer {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address?: string;
  date_of_birth?: string;
  preferred_staff_id?: string;
  preferred_services: string[];
  communication_preference: "email" | "sms" | "phone" | "none";
  status: "active" | "inactive";
  created_at: string;
  updated_at: string;
}

export interface CustomerPreference {
  id: string;
  customer_id: string;
  preferred_staff_ids: string[];
  preferred_service_ids: string[];
  communication_methods: ("email" | "sms" | "phone")[];
  preferred_time_slots: ("morning" | "afternoon" | "evening")[];
  language: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface AppointmentHistory {
  id: string;
  customer_id: string;
  appointment_id: string;
  service_id: string;
  staff_id: string;
  service_name: string;
  staff_name: string;
  appointment_date: string;
  appointment_time: string;
  notes: string;
  rating: number;
  feedback: string;
  created_at: string;
}
