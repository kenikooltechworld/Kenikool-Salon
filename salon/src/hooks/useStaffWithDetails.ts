import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useStaffMember } from "./useStaff";
import { useShifts } from "./useShifts";
import { useTimeOffRequests } from "./useTimeOffRequests";

export interface StaffWithShifts {
  id: string;
  email: string;
  phone: string;
  firstName: string;
  lastName: string;
  specialty?: string;
  status: "active" | "inactive" | "suspended";
  createdAt: string;
  updatedAt: string;
  shifts: Array<{
    id: string;
    start_time: string;
    end_time: string;
    status: string;
    labor_cost: number;
  }>;
}

export interface StaffWithTimeOff {
  id: string;
  email: string;
  phone: string;
  firstName: string;
  lastName: string;
  specialty?: string;
  status: "active" | "inactive" | "suspended";
  createdAt: string;
  updatedAt: string;
  timeOffRequests: Array<{
    id: string;
    start_date: string;
    end_date: string;
    reason: string;
    status: "pending" | "approved" | "denied";
  }>;
}

export interface StaffSchedule {
  id: string;
  email: string;
  phone: string;
  firstName: string;
  lastName: string;
  specialty?: string;
  status: "active" | "inactive" | "suspended";
  createdAt: string;
  updatedAt: string;
  shifts: Array<{
    id: string;
    start_time: string;
    end_time: string;
    status: string;
    labor_cost: number;
  }>;
  timeOffRequests: Array<{
    id: string;
    start_date: string;
    end_date: string;
    reason: string;
    status: "pending" | "approved" | "denied";
  }>;
}

/**
 * Fetch staff member with their shifts
 */
export function useStaffWithShifts(staffId: string) {
  const { data: staff } = useStaffMember(staffId);
  const { data: shifts } = useShifts({ staff_id: staffId });

  return {
    data: staff && shifts ? { ...staff, shifts } : null,
    isLoading: !staff || !shifts,
  };
}

/**
 * Fetch staff member with their time-off requests
 */
export function useStaffWithTimeOff(staffId: string) {
  const { data: staff } = useStaffMember(staffId);
  const { data: timeOffRequests } = useTimeOffRequests({ staff_id: staffId });

  return {
    data: staff && timeOffRequests ? { ...staff, timeOffRequests } : null,
    isLoading: !staff || !timeOffRequests,
  };
}

/**
 * Fetch staff member with complete schedule (shifts + time-off)
 */
export function useStaffSchedule(
  staffId: string,
  dateRange?: { start: string; end: string },
) {
  const { data: staff } = useStaffMember(staffId);
  const { data: shifts } = useShifts({ staff_id: staffId });
  const { data: timeOffRequests } = useTimeOffRequests({ staff_id: staffId });

  return {
    data:
      staff && shifts && timeOffRequests
        ? { ...staff, shifts, timeOffRequests }
        : null,
    isLoading: !staff || !shifts || !timeOffRequests,
  };
}
