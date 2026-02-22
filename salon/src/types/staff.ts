export interface Staff {
  id: string;
  user_id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  role_ids?: string[];
  specialties: string[];
  certifications: string[];
  certification_files: string[];
  payment_type: "hourly" | "daily" | "weekly" | "monthly" | "commission";
  payment_rate: number;
  hire_date: string | null;
  bio: string | null;
  profile_image_url: string | null;
  status: "active" | "inactive" | "on_leave" | "terminated";
  createdAt: string;
  updatedAt: string;
}

export interface Shift {
  id: string;
  staff_id: string;
  start_time: string;
  end_time: string;
  status: "scheduled" | "in_progress" | "completed" | "cancelled";
  labor_cost: number;
  created_at: string;
  updated_at: string;
}

export interface TimeOffRequest {
  id: string;
  staff_id: string;
  start_date: string;
  end_date: string;
  reason: string;
  status: "pending" | "approved" | "denied";
  created_at: string;
  updated_at: string;
}
