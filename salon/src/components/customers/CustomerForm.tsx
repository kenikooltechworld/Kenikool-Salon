import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { AlertCircleIcon, CheckCircleIcon } from "@/components/icons";

export interface CustomerFormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  address?: string;
  dateOfBirth?: string;
  communicationPreference?: "email" | "sms" | "phone" | "none";
  status?: "active" | "inactive";
}

interface CustomerFormProps {
  initialData?: CustomerFormData;
  isLoading?: boolean;
  onSubmit: (data: CustomerFormData) => Promise<void>;
  onCancel?: () => void;
}

export function CustomerForm({
  initialData,
  isLoading = false,
  onSubmit,
  onCancel,
}: CustomerFormProps) {
  const [formData, setFormData] = useState<CustomerFormData>(
    initialData || {
      firstName: "",
      lastName: "",
      email: "",
      phone: "",
      address: "",
      dateOfBirth: "",
      communicationPreference: "email",
      status: "active",
    },
  );

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitError, setSubmitError] = useState<string>("");
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.firstName.trim()) {
      newErrors.firstName = "First name is required";
    }
    if (!formData.lastName.trim()) {
      newErrors.lastName = "Last name is required";
    }
    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Invalid email format";
    }
    if (!formData.phone.trim()) {
      newErrors.phone = "Phone is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError("");
    setSubmitSuccess(false);

    if (!validateForm()) {
      return;
    }

    try {
      await onSubmit(formData);
      setSubmitSuccess(true);
      if (!initialData) {
        setFormData({
          firstName: "",
          lastName: "",
          email: "",
          phone: "",
          address: "",
          dateOfBirth: "",
          communicationPreference: "email",
          status: "active",
        });
      }
    } catch (error) {
      setSubmitError(
        error instanceof Error ? error.message : "Failed to save customer",
      );
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-3 xs:space-y-4 sm:space-y-5"
    >
      {/* Success Message */}
      {submitSuccess && (
        <div className="flex items-start gap-2 xs:gap-3 p-2 xs:p-3 sm:p-4 bg-green-50 border border-green-200 rounded-lg">
          <CheckCircleIcon
            size={16}
            className="text-green-600 flex-shrink-0 mt-0.5"
          />
          <p className="text-xs xs:text-sm sm:text-base text-green-800 font-medium">
            {initialData
              ? "Customer updated successfully"
              : "Customer created successfully"}
          </p>
        </div>
      )}

      {/* Error Message */}
      {submitError && (
        <div className="flex items-start gap-2 xs:gap-3 p-2 xs:p-3 sm:p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircleIcon
            size={16}
            className="text-red-600 flex-shrink-0 mt-0.5"
          />
          <p className="text-xs xs:text-sm sm:text-base text-red-800 font-medium">
            {submitError}
          </p>
        </div>
      )}

      {/* Name Fields */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 xs:gap-3 sm:gap-4">
        <div>
          <label className="block text-xs xs:text-sm sm:text-base font-semibold text-foreground mb-1 xs:mb-2">
            First Name *
          </label>
          <Input
            type="text"
            value={formData.firstName}
            onChange={(e) =>
              setFormData({ ...formData, firstName: e.target.value })
            }
            placeholder="John"
            className={`text-xs xs:text-sm sm:text-base py-2 xs:py-2.5 ${errors.firstName ? "border-red-500" : ""}`}
            disabled={isLoading}
          />
          {errors.firstName && (
            <p className="text-xs xs:text-sm text-red-500 mt-1">
              {errors.firstName}
            </p>
          )}
        </div>

        <div>
          <label className="block text-xs xs:text-sm sm:text-base font-semibold text-foreground mb-1 xs:mb-2">
            Last Name *
          </label>
          <Input
            type="text"
            value={formData.lastName}
            onChange={(e) =>
              setFormData({ ...formData, lastName: e.target.value })
            }
            placeholder="Doe"
            className={`text-xs xs:text-sm sm:text-base py-2 xs:py-2.5 ${errors.lastName ? "border-red-500" : ""}`}
            disabled={isLoading}
          />
          {errors.lastName && (
            <p className="text-xs xs:text-sm text-red-500 mt-1">
              {errors.lastName}
            </p>
          )}
        </div>
      </div>

      {/* Email & Phone */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 xs:gap-3 sm:gap-4">
        <div>
          <label className="block text-xs xs:text-sm sm:text-base font-semibold text-foreground mb-1 xs:mb-2">
            Email *
          </label>
          <Input
            type="email"
            value={formData.email}
            onChange={(e) =>
              setFormData({ ...formData, email: e.target.value })
            }
            placeholder="john@example.com"
            className={`text-xs xs:text-sm sm:text-base py-2 xs:py-2.5 ${errors.email ? "border-red-500" : ""}`}
            disabled={isLoading}
          />
          {errors.email && (
            <p className="text-xs xs:text-sm text-red-500 mt-1">
              {errors.email}
            </p>
          )}
        </div>

        <div>
          <label className="block text-xs xs:text-sm sm:text-base font-semibold text-foreground mb-1 xs:mb-2">
            Phone *
          </label>
          <Input
            type="tel"
            value={formData.phone}
            onChange={(e) =>
              setFormData({ ...formData, phone: e.target.value })
            }
            placeholder="+234 801 234 5678"
            className={`text-xs xs:text-sm sm:text-base py-2 xs:py-2.5 ${errors.phone ? "border-red-500" : ""}`}
            disabled={isLoading}
          />
          {errors.phone && (
            <p className="text-xs xs:text-sm text-red-500 mt-1">
              {errors.phone}
            </p>
          )}
        </div>
      </div>

      {/* Address */}
      <div>
        <label className="block text-xs xs:text-sm sm:text-base font-semibold text-foreground mb-1 xs:mb-2">
          Address
        </label>
        <Textarea
          value={formData.address || ""}
          onChange={(e) =>
            setFormData({ ...formData, address: e.target.value })
          }
          placeholder="123 Main Street, City, State"
          rows={2}
          disabled={isLoading}
          className="text-xs xs:text-sm sm:text-base py-2"
        />
      </div>

      {/* Date of Birth & Communication Preference */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 xs:gap-3 sm:gap-4">
        <div>
          <label className="block text-xs xs:text-sm sm:text-base font-semibold text-foreground mb-1 xs:mb-2">
            Date of Birth
          </label>
          <Input
            type="date"
            value={formData.dateOfBirth || ""}
            onChange={(e) =>
              setFormData({ ...formData, dateOfBirth: e.target.value })
            }
            disabled={isLoading}
            className="text-xs xs:text-sm sm:text-base py-2 xs:py-2.5"
          />
        </div>

        <div>
          <label className="block text-xs xs:text-sm sm:text-base font-semibold text-foreground mb-1 xs:mb-2">
            Communication Preference
          </label>
          <Select
            value={formData.communicationPreference || "email"}
            onValueChange={(value) =>
              setFormData({
                ...formData,
                communicationPreference: value as any,
              })
            }
            disabled={isLoading}
          >
            <SelectTrigger className="text-xs xs:text-sm sm:text-base py-2 xs:py-2.5">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="email">Email</SelectItem>
              <SelectItem value="sms">SMS</SelectItem>
              <SelectItem value="phone">Phone</SelectItem>
              <SelectItem value="none">None</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Status */}
      <div>
        <label className="block text-xs xs:text-sm sm:text-base font-semibold text-foreground mb-1 xs:mb-2">
          Status
        </label>
        <Select
          value={formData.status || "active"}
          onValueChange={(value) =>
            setFormData({ ...formData, status: value as any })
          }
          disabled={isLoading}
        >
          <SelectTrigger className="text-xs xs:text-sm sm:text-base py-2 xs:py-2.5">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Buttons */}
      <div className="flex flex-col xs:flex-row gap-2 xs:gap-3 justify-end pt-2 xs:pt-3">
        {onCancel && (
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
            className="text-xs xs:text-sm sm:text-base h-9 xs:h-10 w-full xs:w-auto px-3 xs:px-4"
          >
            Cancel
          </Button>
        )}
        <Button
          type="submit"
          disabled={isLoading}
          className="text-xs xs:text-sm sm:text-base h-9 xs:h-10 w-full xs:w-auto px-3 xs:px-4"
        >
          {isLoading
            ? "Saving..."
            : initialData
              ? "Update Customer"
              : "Create Customer"}
        </Button>
      </div>
    </form>
  );
}
