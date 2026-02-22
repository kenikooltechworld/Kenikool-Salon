import { useState } from "react";
import { motion } from "framer-motion";

interface GuestInfo {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  notes?: string;
}

interface GuestInfoFormProps {
  onSubmit: (info: GuestInfo) => void;
}

export function GuestInfoForm({ onSubmit }: GuestInfoFormProps) {
  const [formData, setFormData] = useState<GuestInfo>({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    notes: "",
  });

  const [errors, setErrors] = useState<Partial<GuestInfo>>({});

  const validateForm = () => {
    const newErrors: Partial<GuestInfo> = {};

    if (!formData.firstName.trim()) {
      newErrors.firstName = "First name is required";
    }
    if (!formData.lastName.trim()) {
      newErrors.lastName = "Last name is required";
    }
    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Invalid email address";
    }
    if (!formData.phone.trim()) {
      newErrors.phone = "Phone number is required";
    } else if (!/^\+?[\d\s\-()]{10,}$/.test(formData.phone)) {
      newErrors.phone = "Invalid phone number";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error for this field
    if (errors[name as keyof GuestInfo]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const fields: Array<{
    name: keyof GuestInfo;
    label: string;
    type: string;
    placeholder: string;
    required: boolean;
  }> = [
    {
      name: "firstName",
      label: "First Name",
      type: "text",
      placeholder: "John",
      required: true,
    },
    {
      name: "lastName",
      label: "Last Name",
      type: "text",
      placeholder: "Doe",
      required: true,
    },
    {
      name: "email",
      label: "Email Address",
      type: "email",
      placeholder: "john@example.com",
      required: true,
    },
    {
      name: "phone",
      label: "Phone Number",
      type: "tel",
      placeholder: "+234 (0) 123 456 7890",
      required: true,
    },
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Your Information</h3>
        <div className="space-y-4">
          {fields.map((field, index) => (
            <motion.div
              key={field.name}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </label>
              <input
                type={field.type}
                name={field.name}
                value={formData[field.name]}
                onChange={handleChange}
                placeholder={field.placeholder}
                className={`w-full px-4 py-2 rounded-lg border-2 transition-colors focus:outline-none ${
                  errors[field.name]
                    ? "border-red-500 focus:border-red-600"
                    : "border-[var(--border)] focus:border-[var(--primary)]"
                }`}
              />
              {errors[field.name] && (
                <motion.p
                  className="text-sm text-red-500 mt-1"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  {errors[field.name]}
                </motion.p>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Notes Section */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
          Special Requests (Optional)
        </label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          placeholder="Any special requests or preferences?"
          rows={4}
          className="w-full px-4 py-2 rounded-lg border-2 border-[var(--border)] focus:border-[var(--primary)] focus:outline-none transition-colors resize-none"
        />
      </motion.div>

      {/* Info Box */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="bg-blue-50 border border-blue-200 p-4 rounded-lg"
      >
        <p className="text-sm text-blue-800">
          <span className="font-semibold">📧 Confirmation:</span> We'll send a
          confirmation email and SMS to the contact details provided.
        </p>
      </motion.div>

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="bg-[var(--muted)] p-4 rounded-lg"
      >
        <p className="text-sm text-[var(--muted-foreground)]">
          <span className="font-semibold">Name:</span>{" "}
          {formData.firstName && formData.lastName
            ? `${formData.firstName} ${formData.lastName}`
            : "Not provided"}
        </p>
        <p className="text-sm text-[var(--muted-foreground)] mt-2">
          <span className="font-semibold">Contact:</span>{" "}
          {formData.email || formData.phone
            ? `${formData.email} / ${formData.phone}`
            : "Not provided"}
        </p>
      </motion.div>
    </form>
  );
}
