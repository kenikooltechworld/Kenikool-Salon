/**
 * Booking Form Component - Collect customer details for public booking
 */

import { useState } from "react";
import { Button, Input, Textarea, Spinner, Alert } from "@/components/ui";
import { isValidEmail, isValidPhone } from "@/lib/utils/validation";

interface BookingFormProps {
  onSubmit: (data: {
    customerName: string;
    customerEmail: string;
    customerPhone: string;
    notes?: string;
    paymentOption: "now" | "later";
  }) => Promise<void>;
}

export default function BookingForm({ onSubmit }: BookingFormProps) {
  const [formData, setFormData] = useState({
    customerName: "",
    customerEmail: "",
    customerPhone: "",
    notes: "",
    paymentOption: "later" as "now" | "later",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.customerName.trim()) {
      newErrors.customerName = "Name is required";
    } else if (formData.customerName.trim().length < 2) {
      newErrors.customerName = "Name must be at least 2 characters";
    }

    if (!formData.customerEmail.trim()) {
      newErrors.customerEmail = "Email is required";
    } else if (!isValidEmail(formData.customerEmail)) {
      newErrors.customerEmail = "Invalid email format";
    }

    if (!formData.customerPhone.trim()) {
      newErrors.customerPhone = "Phone is required";
    } else if (!isValidPhone(formData.customerPhone)) {
      newErrors.customerPhone = "Invalid phone format";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        customerName: formData.customerName.trim(),
        customerEmail: formData.customerEmail.trim(),
        customerPhone: formData.customerPhone.trim(),
        notes: formData.notes.trim() || undefined,
        paymentOption: formData.paymentOption,
      });
    } catch (error) {
      console.error("Form submission error:", error);
      setErrors({
        submit: "Failed to submit booking. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Your Information</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Please provide your contact details
        </p>
      </div>

      {errors.submit && (
        <Alert variant="error">
          <p>{errors.submit}</p>
        </Alert>
      )}

      <div>
        <label
          htmlFor="customerName"
          className="block text-sm font-medium mb-2"
        >
          Full Name *
        </label>
        <Input
          id="customerName"
          name="customerName"
          type="text"
          value={formData.customerName}
          onChange={handleChange}
          placeholder="John Doe"
          disabled={isSubmitting}
          className={errors.customerName ? "border-destructive" : ""}
        />
        {errors.customerName && (
          <p className="text-destructive text-sm mt-1">{errors.customerName}</p>
        )}
      </div>

      <div>
        <label
          htmlFor="customerEmail"
          className="block text-sm font-medium mb-2"
        >
          Email Address *
        </label>
        <Input
          id="customerEmail"
          name="customerEmail"
          type="email"
          value={formData.customerEmail}
          onChange={handleChange}
          placeholder="john@example.com"
          disabled={isSubmitting}
          className={errors.customerEmail ? "border-destructive" : ""}
        />
        {errors.customerEmail && (
          <p className="text-destructive text-sm mt-1">
            {errors.customerEmail}
          </p>
        )}
      </div>

      <div>
        <label
          htmlFor="customerPhone"
          className="block text-sm font-medium mb-2"
        >
          Phone Number *
        </label>
        <Input
          id="customerPhone"
          name="customerPhone"
          type="tel"
          value={formData.customerPhone}
          onChange={handleChange}
          placeholder="+234 123 456 7890"
          disabled={isSubmitting}
          className={errors.customerPhone ? "border-destructive" : ""}
        />
        {errors.customerPhone && (
          <p className="text-destructive text-sm mt-1">
            {errors.customerPhone}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="notes" className="block text-sm font-medium mb-2">
          Additional Notes (Optional)
        </label>
        <Textarea
          id="notes"
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          placeholder="Any special requests or information..."
          disabled={isSubmitting}
          rows={4}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-4">
          Payment Option *
        </label>
        <div className="space-y-3">
          <label className="flex items-center p-3 border border-border rounded-lg cursor-pointer hover:bg-muted transition">
            <input
              type="radio"
              name="paymentOption"
              value="later"
              checked={formData.paymentOption === "later"}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  paymentOption: e.target.value as "now" | "later",
                }))
              }
              disabled={isSubmitting}
              className="w-4 h-4"
            />
            <div className="ml-3">
              <p className="font-medium">Pay Later</p>
              <p className="text-sm text-muted-foreground">
                Pay when you arrive at the salon
              </p>
            </div>
          </label>

          <label className="flex items-center p-3 border border-border rounded-lg cursor-pointer hover:bg-muted transition">
            <input
              type="radio"
              name="paymentOption"
              value="now"
              checked={formData.paymentOption === "now"}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  paymentOption: e.target.value as "now" | "later",
                }))
              }
              disabled={isSubmitting}
              className="w-4 h-4"
            />
            <div className="ml-3">
              <p className="font-medium">Pay Now</p>
              <p className="text-sm text-muted-foreground">
                Secure your booking with immediate payment
              </p>
            </div>
          </label>
        </div>
      </div>

      <Alert>
        <p className="text-sm">
          <strong>Note:</strong> We'll send a confirmation email to the address
          you provide. Please make sure it's correct.
        </p>
      </Alert>

      <Button
        type="submit"
        variant="primary"
        disabled={isSubmitting}
        className="w-full"
      >
        {isSubmitting ? (
          <>
            <Spinner className="w-4 h-4 mr-2" />
            {formData.paymentOption === "now"
              ? "Processing..."
              : "Confirming..."}
          </>
        ) : formData.paymentOption === "now" ? (
          "Proceed to Payment"
        ) : (
          "Confirm Booking"
        )}
      </Button>
    </form>
  );
}
